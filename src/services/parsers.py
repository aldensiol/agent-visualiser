from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_parse import LlamaParse
from src.services.services import llama_llm

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