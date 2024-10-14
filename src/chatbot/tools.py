import os

from abc import abstractmethod
from crawl4ai import AsyncWebCrawler

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.tools import StructuredTool
from langchain.prompts import PromptTemplate

from pymilvus import (
   AnnSearchRequest, RRFRanker,
)
from serpapi import GoogleSearch
from typing import Callable

from prompts.prompts import GENERATE_ANSWER_PROMPT, GRADE_ANSWER_PROMPT, REFINE_ANSWER_PROMPT
from src.services.services import collection, kg_retriever, llm
from src.services.embedding_models import bge_embed_model, splade_embed_model

class BaseTool:
    def __init__(self):
        self.name = "BaseTool"
        self.description = "Base class for all tools"
    
    @abstractmethod
    def get_tool(self) -> StructuredTool:
        pass

class BaseRetrievalTool(BaseTool):
    def __init__(self, name: str = "BaseRetrievalTool", 
                 description: str = "Base class for Retrieval tools"):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_tool(self) -> StructuredTool:
        pass

class BaseGenerationTool(BaseTool):
    def __init__(self, prompt: str, 
                 llm: ChatAnthropic = llm, 
                 name: str = "BaseGenerationTool", 
                 description: str = "Base class for Generation tools"):
        self.name = name
        self.description = description
        self.llm = llm
        self.prompt = prompt
        self.prompt_template = None
        self.chain = None
    
    @abstractmethod
    def get_tool(self) -> StructuredTool:
        pass

class DBRetrievalTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Vector DB", description="Retrieves context from a conventional Vector DB, given a query.")
        
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
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            func=self.retrieve_db, 
            coroutine=self.retrieve_db_async,
            name=self.name,
            description=self.description
        )
        
class KGRetrievalTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Knowledge Graph", description="Retrieves context from a Knowledge Graph, given a query.")
        
    def retrieve_kg(query: str) -> str:
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

    async def retrieve_kg_async(query: str) -> str:
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
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            func=self.retrieve_kg, 
            coroutine=self.retrieve_kg_async,
            name=self.name,
            description=self.description
        )

class WebSearchTool(BaseRetrievalTool):
    def __init__(self):
        super().__init__(name="Retrieve from Web Search", description="Retrieves context from a Web Search, given a query.")
        
    async def websearch(query: str, num_results: int = 3) -> str:
        """
        Retrieves context from the web using SerpAPI for search and AsyncWebCrawler for content

        Args:
            query (str): The user query
            num_results (int): Number of top results to crawl (default: 3)
            
        Returns:
            str: The formatted context retrieved from the websearch
        """
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
        for url in urls:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(url=url)
            
            # Extract relevant information from the crawled content
            content = result.markdown[:3000]  # Limit to first 1000 characters
            contents.append(f"URL: {url}\n\nContent:\n{content}\n\n")

        return "\n".join(contents)
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.websearch,
            coroutine=self.websearch,
            name=self.name,
            description=self.description
        )
        
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
    
    async def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer to the user query from the Vector DB context

        Args:
            query (str): The user query
            context (str): The context retrieved from the Vector DB

        Returns:
            str: The answer generated by the agent
        """
        
        response = await self.chain.ainvoke({"query": query, "context": context})
        return response
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            func=self.generate_answer, 
            coroutine=self.generate_answer,
            name=self.name,
            description=self.description
        )

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
    
    async def grade_answer(self, query: str, answer: str) -> dict:
        """
        Grades the answer based on relevancy, completeness, coherence, and correctness

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent

        Returns:
            dict: The evaluation metrics and reasoning for the graded answer
        """
        
        response = await self.chain.ainvoke({"query": query, "answer": answer})
        return response
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            func=self.grade_answer, 
            coroutine=self.grade_answer,
            name=self.name,
            description=self.description
        )

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
    
    async def refine_answer(self, query: str, answer: str, websearch_context: str) -> str:
        """
        Refines the answer based on user feedback

        Args:
            query (str): The user query
            answer (str): The answer generated by the agent
            feedback (str): The user feedback on the answer

        Returns:
            str: The refined answer based on the user feedback
        """
        
        response = await self.chain.ainvoke({"query": query, "answer": answer, "websearch_context": websearch_context})
        return response
    
    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            func=self.refine_answer, 
            coroutine=self.refine_answer,
            name=self.name,
            description=self.description
        )