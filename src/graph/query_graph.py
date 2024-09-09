from llama_index.core import PropertyGraphIndex
from src.services.services import graph_store, llama_llm, llama_openai_embed_model

def load_index():
    index = PropertyGraphIndex.from_existing(
        llm = llama_llm,
        embed_model=llama_openai_embed_model,
        property_graph_store=graph_store,
    )
    return index