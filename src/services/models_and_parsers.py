import spacy

from fastembed import TextEmbedding
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_parse import LlamaParse
from pymilvus import model
from services.services import llama_llm


print("Loading in Embedding Models...")
bge_embed_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")
llama_openai_embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
splade_embed_model = model.sparse.SpladeEmbeddingFunction(
    model_name="naver/splade-cocondenser-ensembledistil",
    device="cpu",
)

print("Loading in Parsers...")
# instantiate doc parser
parser = LlamaParse(
    result_type="markdown",
    num_workers=4,
    verbose = False,
    show_progress=True,
    ignore_errors=True,
    language="en",
)

# instantiate node parser
node_parser = MarkdownElementNodeParser(llm=llama_llm, num_workers=8)

print("Loading in NLP Models...")
coref_nlp = spacy.load('en_core_web_lg')
coref_nlp.add_pipe('coreferee')