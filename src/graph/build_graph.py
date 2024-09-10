from llama_index.core import Document, PropertyGraphIndex
from src.services.services import llama_llm, llama_openai_embed_model, graph_store, relik
from typing import List

def delete_all_nodes(graph_store):
    graph_store.structured_query("""
    MATCH (n)
    DETACH DELETE n
    """)
    print("All nodes deleted")
    
def remove_all_neo4j_restrictions(graph_store):
    graph_store.structured_query("""
    CALL apoc.schema.assert({}, {});
    """)

def build_graph(documents: List[Document]):
    index = PropertyGraphIndex.from_documents(
        documents,
        kg_extractors=[relik],
        llm=llama_llm,
        embed_model=llama_openai_embed_model,
        property_graph_store=graph_store,
        show_progress=True,
    )
    return index