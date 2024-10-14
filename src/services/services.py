import os

from langchain_anthropic import ChatAnthropic
from llama_index.llms.anthropic import Anthropic
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from pymilvus import (
    connections, Collection
)

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

print("Loading in Milvus Collection...")
# Change name as needed
COLLECTION_NAME = "vector_index"
collection = Collection(name=COLLECTION_NAME)

print("Loading in Graph Store...")
graph_store = Neo4jPropertyGraphStore(
    username=NEO4J_USER,
    password=NEO4J_PASSWORD,
    url=NEO4J_URL,
    refresh_schema=False,
)