import asyncio
import os
import re
import time

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.tools import StructuredTool
from langchain.prompts import PromptTemplate
from pymilvus import (
   AnnSearchRequest, RRFRanker,
)
from serpapi import GoogleSearch
from tenacity import retry, stop_after_attempt, wait_exponential
from typing_extensions import override

from src.chatbot.prompts.prompts import GENERATE_ANSWER_PROMPT, GRADE_ANSWER_PROMPT, REFINE_ANSWER_PROMPT
from src.services.services import collection, kg_retriever, llm
from src.services.embedding_models import bge_embed_model, splade_embed_model

class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def func(self, *args, **kwargs):
        pass

    @abstractmethod
    async def coroutine(self, *args, **kwargs):
        pass

    def get_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.func,
            coroutine=self.coroutine,
            name=self.name,
            description=self.description
        )

class BaseRetrievalTool(BaseTool):
    pass

class BaseGenerationTool(BaseTool):
    def __init__(self, prompt: str, 
                 llm: ChatAnthropic = llm, 
                 name: str = "Base Generation Tool", 
                 description: str = "Base Class for Generation Tools"):
        super().__init__(name, description)
        self.llm = llm
        self.prompt = prompt
        self.prompt_template = None
        self.chain = None

class DBRetrievalTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Vector DB", 
                         description="Retrieves context from a conventional Vector DB, given a query.")

    def retrieve_db(self, query: str) -> str:
        """
        Retrieves context from a conventional Vector DB, given a query.

        Args:
            query (str): The user query

        Returns:
            str: The formatted context retrieved from Vector DB
        """
        
        dense_embedding = list(bge_embed_model.query_embed(query))[0]
        sparse_embedding = list(splade_embed_model.encode_queries([query]))
        
        search_results = collection.hybrid_search(
                reqs=[
                    AnnSearchRequest(
                        data=[dense_embedding],  # content vector embedding
                        anns_field='dense_embeddings',  # content vector field
                        param={"metric_type": "COSINE", "params": {"M": 64, "efConstruction": 512}}, # Search parameters
                        limit=3
                    ),
                    AnnSearchRequest(
                        data=list(sparse_embedding),  # keyword vector embedding
                        anns_field='sparse_embeddings',  # keyword vector field
                        param={"metric_type": "IP", "params": {"drop_ratio_build": 0.2}}, # Search parameters
                        limit=3
                    )
                ],
                output_fields=['doc_id', 'text', 'doc_source'],
                rerank=RRFRanker(),
                limit=3
                )
        
        hits = search_results[0]
        
        context = []
        for res in hits:
            text = res.text
            source = res.doc_source
            context.append(f"Source: {source}\nContext: {text}")
        
        return "\n\n".join(context)

    async def retrieve_db_async(self, query: str) -> str:
        """
        Retrieves context from a conventional Vector DB, given a list of queries.

        Args:
            query (str): The user query

        Returns:
            str: The formatted context retrieved from Vector DB
        """
        
        dense_embedding = list(bge_embed_model.query_embed(query))[0]
        sparse_embedding = list(splade_embed_model.encode_queries([query]))
        
        search_results = collection.hybrid_search(
                reqs=[
                    AnnSearchRequest(
                        data=[dense_embedding],  # content vector embedding
                        anns_field='dense_embeddings',  # content vector field
                        param={"metric_type": "COSINE", "params": {"M": 64, "efConstruction": 512}}, # Search parameters
                        limit=3
                    ),
                    AnnSearchRequest(
                        data=list(sparse_embedding),  # keyword vector embedding
                        anns_field='sparse_embeddings',  # keyword vector field
                        param={"metric_type": "IP", "params": {"drop_ratio_build": 0.2}}, # Search parameters
                        limit=3
                    )
                ],
                output_fields=['doc_id', 'text', 'doc_source'],
                rerank=RRFRanker(),
                limit=3
                )
        
        hits = search_results[0]
        
        context = []
        for res in hits:
            text = res.text
            source = res.doc_source
            context.append(f"Source: {source}\nContext: {text}")
        
        return "\n\n".join(context)
    
    @override
    def func(self, query: str) -> str:
        return self.retrieve_db(query)

    @override
    async def coroutine(self, query: str) -> str:
        return await self.retrieve_db_async(query)
        
class KGRetrievalTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Knowledge Graph", 
                         description="Retrieves context from a Knowledge Graph, given a query.")
        
    def retrieve_kg(self, query: str) -> str:
        """
        Retrieves context from the ingested knowledge graph, given a list of queries.
        Processes queries in parallel using ThreadPoolExecutor.

        Args:
            query (str): The user query

        Returns:
            str: The formatted context retrieved from the knowledge graph
        """
        
        nodes = kg_retriever.retrieve(query)
        context = '\n\n'.join([node.text for node in nodes])
        return context

    async def retrieve_kg_async(self, query: str) -> str:
        """
        Retrieves context from the ingested knowledge graph, given a list of queries.
        Processes queries in parallel using ThreadPoolExecutor.

        Args:
            query (str): The user query

        Returns:
            str: The formatted context retrieved from the knowledge graph
        """
        
        nodes = kg_retriever.retrieve(query)
        context = '\n\n'.join([node.text for node in nodes])
        return context
    
    @override
    def func(self, query: str) -> str:
        return self.retrieve_kg(query)

    @override
    async def coroutine(self, query: str) -> str:
        return await self.retrieve_kg_async(query)

class WebSearchTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Web Search", 
                         description="Retrieves context from a Web Search, given a query.")

    def clean_content(self, content: str) -> str:
        """
        Clean the content by removing boilerplate text, headers, and irrelevant information.
        """
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script, style, and nav elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract text from remaining HTML
        text = soup.get_text(separator=' ', strip=True)

        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove common boilerplate phrases (case-insensitive)
        boilerplate_patterns = [
            r'copyright ©.*',
            r'all rights reserved',
            r'terms (of use|and conditions)',
            r'privacy policy',
            r'cookie policy',
            r'(log|sign) (in|out|up)',
            r'subscribe to our newsletter',
            r'follow us on social media',
        ]
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Remove common email patterns
        text = re.sub(r'\S+@\S+\.\S+', '', text)

        # Remove patterns like "page X of Y"
        text = re.sub(r'page \d+ of \d+', '', text)

        # Remove patterns like "last updated: date"
        text = re.sub(r'last updated:?\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', '', text)

        # Remove very short lines (likely to be menu items, etc.)
        text = '\n'.join(line for line in text.split('\n') if len(line.split()) > 3)

        # Final cleanup: remove any leading/trailing whitespace and multiple consecutive spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

        
    async def websearch(self, query: str, num_results: int = 3) -> str:
       """
       Retrieves context from the web using SerpAPI for search and AsyncWebCrawler for content

       Args:
           query (str): The user query
           num_results (int): Number of top results to crawl (default: 3)
           
       Returns:
           str: The formatted context retrieved from the websearch
       """
       print("------- Retrieving Context Via Web Search -------")
       # Use SerpAPI to get search results
       params = {
           "q": query,
           "num": num_results,
           "api_key": os.getenv("SERPAPI_API_KEY")
       }
       search = GoogleSearch(params)
       results = search.get_dict()
       
       # Extract URLs from search results
       urls = [result['link'] for result in results.get('organic_results', [])[:num_results]]
       
       # Crawl each URL using AsyncWebCrawler
       contents = []
       async with AsyncWebCrawler(verbose=True) as crawler:
           tasks = [crawler.arun(url=url) for url in urls]
           results = await asyncio.gather(*tasks)
       
       for url, result in zip(urls, results):
           # Extract relevant information from the crawled content
           content = self.clean_content(result.markdown)
           
           # Truncate content to ~1000 words
           words = content.split()
           if len(words) > 1000:
               content = ' '.join(words[:1000]) + '...'
           
           contents.append(f"URL: {url}\nContent:\n{content}\n\n")

       return "".join(contents)
   
    @override
    def func(self, query: str) -> str:
        return self.websearch(query)
    
    @override
    async def coroutine(self, query: str) -> str:
        return await self.websearch(query)
        
class AnswerGenerationTool(BaseGenerationTool):
    def __init__(self):
        super().__init__(prompt=GENERATE_ANSWER_PROMPT, 
                         name="Answer Generator", 
                         description="Generates an answer to the user query from the Vector DB + KG Context")
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template=self.prompt
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer to the user query from the Vector DB context

        Args:
            query (str): The user query
            context (str): The context retrieved from the Vector DB

        Returns:
            str: The answer generated by the agent
        """
        try:
            response = self.chain.invoke({"query": query, "context": context})
            return response
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_answer_async(self, query: str, context: str) -> str:
        """
        Generates an answer to the user query from the Vector DB context

        Args:
            query (str): The user query
            context (str): The context retrieved from the Vector DB

        Returns:
            str: The answer generated by the agent
        """
        try:
            response = await self.chain.ainvoke({"query": query, "context": context})
            return response
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @override
    def func(self, query: str, context: str) -> str:
        return self.generate_answer(query, context)
    
    @override
    async def coroutine(self, query: str, context: str) -> str:
        return await self.generate_answer_async(query, context)

class GradeAnswerTool(BaseGenerationTool):
    def __init__(self):
        super().__init__(prompt=GRADE_ANSWER_PROMPT, 
                         name="Answer Grader", 
                         description="Grades the answer based on relevancy, completeness, coherence, and correctness")
        self.prompt_template = PromptTemplate(
            input_variables=["query", "answer"],
            template=self.prompt
        )
        self.chain = self.prompt_template | self.llm | JsonOutputParser()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def grade_answer(self, query: str, answer: str) -> dict:
        """
        Grades the answer based on relevancy, completeness, coherence, and correctness

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent

        Returns:
            dict: The evaluation metrics and reasoning for the graded answer
        """
        try:
            response = self.chain.invoke({"query": query, "answer": answer})
            return response
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def grade_answer_async(self, query: str, answer: str) -> dict:
        """
        Grades the answer based on relevancy, completeness, coherence, and correctness

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent

        Returns:
            dict: The evaluation metrics and reasoning for the graded answer
        """
        try:
            response = await self.chain.ainvoke({"query": query, "answer": answer})
            return response
        
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @override
    def func(self, query: str, answer: str) -> dict:
        return self.grade_answer(query, answer)
    
    @override
    async def coroutine(self, query: str, answer: str) -> dict:
        return await self.grade_answer_async(query, answer)

class RefineAnswerTool(BaseGenerationTool):
    def __init__(self):
        super().__init__(prompt=REFINE_ANSWER_PROMPT, 
                         name="Answer Refiner", 
                         description="Refines the initial answer using context retrieved from Websearch")
        self.prompt_template = PromptTemplate(
            input_variables=["query", "answer", "websearch_context"],
            template=self.prompt
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def refine_answer(self, query: str, answer: str, websearch_context: str) -> str:
        """
        Refines the answer based on user feedback

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent
            feedback (str): The user feedback on the answer

        Returns:
            str: The refined answer based on the user feedback
        """
        try:
            response = self.chain.invoke({"query": query, "answer": answer, "websearch_context": websearch_context})
            return response
        
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def refine_answer_async(self, query: str, answer: str, websearch_context: str) -> str:
        """
        Refines the answer based on user feedback

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent
            feedback (str): The user feedback on the answer

        Returns:
            str: The refined answer based on the user feedback
        """
        
        try:
            response = await self.chain.ainvoke({"query": query, "answer": answer, "websearch_context": websearch_context})
            return response
    
        except Exception as e:
            if "overloaded_error" in str(e):
                print("Anthropic API is overloaded. Retrying...")
                time.sleep(2)  # Add a small delay before retry
                raise # Re-raise the exception to trigger a retry
            
            else:
                raise
    
    @override
    def func(self, query: str, answer: str, websearch_context: str) -> str:
        return self.refine_answer(query, answer, websearch_context)
    
    @override
    async def coroutine(self, query: str, answer: str, websearch_context: str) -> str:
        return await self.refine_answer(query, answer, websearch_context)