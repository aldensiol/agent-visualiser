import os

from dotenv import load_dotenv
from fastembed import TextEmbedding
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from llama_index.llms.anthropic import Anthropic
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_parse import LlamaParse
from pymilvus import (
    model, connections, Collection
)

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

bge_embed_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")

openai_embed_model = OpenAIEmbeddings(model_name="text-embedding-3-large")

spalde_embed_model = model.sparse.SpladeEmbeddingFunction(
    model_name="naver/splade-cocondenser-ensembledistil",
    device="cpu",
)

# instantiate doc parser
parser = LlamaParse(
    result_type="markdown",
    num_workers=8,
    verbose = True,
    language="en",
)

# instantiate node parser
node_parser = MarkdownElementNodeParser(llm=llama_llm, num_workers=8)

# Change name as needed
COLLECTION_NAME = "vector_index"
collection = Collection(name=COLLECTION_NAME)