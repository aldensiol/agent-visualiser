from abc import abstractmethod
from langchain_core.tools import StructuredTool
from pymilvus import (
   AnnSearchRequest, RRFRanker,
)
from src.services.services import collection
from src.services.embedding_models import bge_embed_model, splade_embed_model
from typing import Callable

class BaseTool:
    def __init__(self):
        self.name = "BaseTool"
        self.description = "Base class for all tools"
    
    @abstractmethod
    def get_tool(self) -> StructuredTool:
        pass
    

class DBRetrieval(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "Retrieve from Vector DB"
        self.description = "Retrieves context from a conventional Vector DB, given a queries."
    
    def retrieve_db(self, query: str) -> str:
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