import nest_asyncio
import os
import spacy

from dotenv import load_dotenv
from fastembed import TextEmbedding
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from llama_index.llms.anthropic import Anthropic
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.extractors.relik.base import RelikPathExtractor
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_parse import LlamaParse
from pymilvus import (
    model, connections, Collection
)

nest_asyncio.apply()

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = CLAUDE_API_KEY
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_API_KEY

ENDPOINT = os.getenv('ZILLIS_ENDPOINT')
TOKEN = os.getenv('ZILLIS_TOKEN')

connections.connect(uri=ENDPOINT, token=TOKEN)

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_DATABASE = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    max_tokens=4096,
    temperature=0.0,
    stop=["\n\nHuman"],
)

llama_llm = Anthropic(
    model="claude-3-5-sonnet-20240620",
    max_tokens=4096,
    temperature=0.0
)

print("Loading in Embedding Models...")
bge_embed_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")
llama_openai_embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")

splade_embed_model = model.sparse.SpladeEmbeddingFunction(
    model_name="naver/splade-cocondenser-ensembledistil",
    device="cpu",
)

# instantiate doc parser
parser = LlamaParse(
    result_type="markdown",
    num_workers=4,
    verbose = False,
    show_progress=True,
    ignore_errors=True,
    language="en",
)

coref_nlp = spacy.load('en_core_web_lg')
coref_nlp.add_pipe('coreferee')

# instantiate node parser
node_parser = MarkdownElementNodeParser(llm=llama_llm, num_workers=8)

relik = RelikPathExtractor(
    model="relik-ie/relik-relation-extraction-small"
)

# Change name as needed
COLLECTION_NAME = "vector_index"
collection = Collection(name=COLLECTION_NAME)

graph_store = Neo4jPropertyGraphStore(
    username=NEO4J_USER,
    password=NEO4J_PASSWORD,
    url=NEO4J_URL,
    refresh_schema=False,
)