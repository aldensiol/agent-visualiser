import nest_asyncio
import os
import pickle
import re
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.core import Document
from src.services.services import parser, node_parser
from typing import List, Tuple, Optional

nest_asyncio.apply()

def remove_table_of_contents(text):
    pattern = r"TABLE OF CONTENTS.*?(?=#)"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
    return cleaned_text.strip()

# Reset the index whenever you want to re-index the documents
idx = [0]

def convert_nodes_to_documents(text_nodes, object_nodes, source):
    """
    Converts nodes to Documents

    Args:
        text_nodes (List[Nodes]): List of text nodes
        object_nodes (List[Nodes]): List of object nodes
        source (str): Source of the document

    Returns:
        documents (List[Documents]): List of Documents
    """
    documents = []
    for node in text_nodes:
        text = node.text
        doc_id = str(uuid.uuid4())
        doc = Document(
            text= text,
            metadata = {
                "id": f"node_{idx[0]}_{doc_id}",
                "start_char_idx": node.start_char_idx,
                "end_char_idx": node.end_char_idx,
                "is_table": False,
                "source": source
            }
        )
        documents.append(doc)
        idx[0] += 1
        
    for node in object_nodes:
        text = node.text
        doc_id = str(uuid.uuid4())
        doc = Document(
            text= text,
            metadata = {
                "id": f"node_{idx[0]}_{doc_id}",
                "start_char_idx": node.start_char_idx,
                "end_char_idx": node.end_char_idx,
                "is_table": True,
                "source": source
            }
        )
        documents.append(doc)
        idx[0] += 1
        
    return documents

def make_dir(data_folder):
    os.makedirs(data_folder, exist_ok=True)

def parse_docs(file_location: str, data_folder: Optional[str] = None) -> List[Document]:
    all_docs = []
    for file_name in os.listdir(file_location):
        if not file_name.endswith(".pdf"):
            continue

        print("File: " + str(file_name))
        doc_path = os.path.join(file_location, file_name)
        modified_file_name = os.path.splitext(file_name)[0].lower().replace(' ', '_')

        # results in a list of Document Objects
        documents = parser.load_data(doc_path)
        
        for idx, doc in enumerate(documents):
            doc.text = remove_table_of_contents(doc.text)
            if idx > 4:
                break

        raw_nodes = node_parser.get_nodes_from_documents(documents)
        # list of text_nodes, list of objects
        text_nodes, objects = node_parser.get_nodes_and_objects(raw_nodes)
        
        final_docs = convert_nodes_to_documents(text_nodes, objects, modified_file_name)
        all_docs.append(final_docs)
        
        if data_folder:
            data_path = os.path.join(data_folder, modified_file_name + '.pkl')
            pickle.dump(final_docs, open(data_path, "wb"))
    
    return [item for sublist in all_docs for item in sublist]

def read_pickles(data_folder: str) -> List[Document]:
    doc_list = []
    for file_name in os.listdir(data_folder):
        doc_path = os.path.join(data_folder, file_name)
        if file_name.endswith(".pkl"):
            with open(doc_path, 'rb') as file:
                # data will be a doc_list
                data = pickle.load(file)
                doc_list.append(data)
                
    # since doc_list is a list of list of documents, we need to flatten it
    doc_list = [item for sublist in doc_list for item in sublist]
    return doc_list

def further_split_long_docs(doc_list: List[Document]) -> Tuple[List[Document], List[Document]]:
    long_docs, short_docs = [], []
    for doc in doc_list:
        is_table = doc.metadata["is_table"]
        if not is_table:
            if len(doc.text) > 1500:
                long_docs.append(doc)
            else:
                short_docs.append(doc)
    return long_docs, short_docs
                
def chunk_doc(doc: Document, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
    chunks = text_splitter.split_text(doc.text)
    return [
        Document(
            text=chunk,
            metadata={
                **doc.metadata,
                'chunk_id': f"{doc.metadata.get('id', '')}_{i}",
                'parent_id': doc.metadata.get('id', ''),
            }
        )
        for i, chunk in enumerate(chunks)
    ]
    
def recursive_chunk_documents(long_docs: List[Document],
                              short_docs: List[Document], 
                              chunk_size: int = 512, 
                              chunk_overlap: int = 64,
                              separators: List[str] = ["\n\n", "\n", " ", ""]) -> List[Document]:
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )

    for doc in long_docs:
        short_docs.extend(chunk_doc(doc, text_splitter))

    return short_docs

def get_final_docs(data_folder: Optional[str] = None, doc_list: Optional[List[Document]] = None) -> List[Document]:
    if doc_list is None:
        if data_folder is None:
            raise ValueError("Either data_folder or doc_list must be provided")
        doc_list = read_pickles(data_folder)
    
    long_docs, short_docs = further_split_long_docs(doc_list)
    final_docs = recursive_chunk_documents(long_docs, short_docs)
    return final_docs
        
def parse_and_process_docs(file_location, data_folder: Optional[str] = None) -> List[Document]:
    if data_folder:
        make_dir(data_folder)
        all_docs = parse_docs(file_location=file_location, data_folder=data_folder)
    else:
        all_docs = parse_docs(file_location=file_location)
        
    final_docs = get_final_docs(doc_list=all_docs)
    return final_docs