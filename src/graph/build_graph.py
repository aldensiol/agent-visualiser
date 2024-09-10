import logging

from llama_index.core import Document, PropertyGraphIndex
from typing import List

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

def build_graph(documents: List[Document], llm, embed_model, graph_store):
    from llama_index.extractors.relik.base import RelikPathExtractor
    relik = RelikPathExtractor(
        model="relik-ie/relik-relation-extraction-small"
    )
    
    try:
        index = PropertyGraphIndex.from_documents(
            documents,
            kg_extractors=[relik],
            llm=llm,
            embed_model=embed_model,
            property_graph_store=graph_store,
            show_progress=True,
        )
        logging.debug("PropertyGraphIndex.from_documents() completed successfully.")
    except Exception as e:
        logging.error(f"Error during PropertyGraphIndex.from_documents(): {e}")
        raise e
        
    return index