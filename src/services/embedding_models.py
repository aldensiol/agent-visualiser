from fastembed import TextEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from pymilvus import model

print("Loading in Embedding Models...")
bge_embed_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")
llama_openai_embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
splade_embed_model = model.sparse.SpladeEmbeddingFunction(
    model_name="naver/splade-cocondenser-ensembledistil",
    device="cpu",
)