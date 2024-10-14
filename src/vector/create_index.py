import pickle
import uuid

from alive_progress import alive_bar
from llama_index.core import Document
from pymilvus import Collection
from src.services.embedding_models import bge_embed_model, splade_embed_model
from typing import List, Tuple

def get_required_data(final_docs: List[Document]) -> Tuple[List[str], List[str], List[str]]:
    all_ids, all_texts, all_sources = [], [], []

    with alive_bar(len(final_docs), title='Metadata', force_tty=True) as bar:
        for doc in final_docs:
            doc_id = str(uuid.uuid4())
            text = doc.text
            source = doc.metadata['source']
            
            all_ids.append(doc_id)
            all_texts.append(text)
            all_sources.append(source)
            bar()
    
    return all_ids, all_texts, all_sources

def get_dense_and_sparse_embeddings(all_texts: List[str]):
    dense_embeddings_list = list(bge_embed_model.embed(all_texts))
    sparse_embeddings_list = splade_embed_model.encode_documents(all_texts)
    
    return dense_embeddings_list, sparse_embeddings_list

def save_embeddings(data_folder, dense_embeddings_list, sparse_embeddings_list) -> None:
    with open(f'{data_folder}/dense_embeddings.pkl', 'wb') as f:
        pickle.dump(dense_embeddings_list, f)
        
    with open(f'{data_folder}/sparse_embeddings.pkl', 'wb') as f:
        pickle.dump(sparse_embeddings_list, f)

def batch_ingestion(collection, final_docs):
    # Get required data
    all_ids, all_texts, all_sources = get_required_data(final_docs)
    # Get dense and sparse embeddings
    dense_embeddings_list, sparse_embeddings_list = get_dense_and_sparse_embeddings(all_texts)
    
    # Start ingestion process
    data = [
        all_ids,
        all_texts,
        all_sources,
        dense_embeddings_list,
        sparse_embeddings_list
    ]
    # Set batch size
    batch_size = 10
    total_elements = len(data[0])  # All lists have the same length

    # Calculate the total number of batches
    total_batches = (total_elements + batch_size - 1) // batch_size

    # Initialize alive_bar with the total number of batches
    with alive_bar(total_batches, force_tty=True) as bar:
        for start in range(0, total_elements, batch_size):
            end = min(start + batch_size, total_elements)
            batch = [sublist[start:end] for sublist in data]
            collection.insert(batch)
            bar()
            
def drop_indexes(collection: Collection, index_names: List[str]) -> None:
    # Release or drop the existing collection index
    collection.release()
    for name in index_names:
        collection.drop_index(index_name=name)
        print(f"Index '{name}' has been dropped")

def create_all_indexes(collection: Collection) -> None:
    # Dense embeddings index
    collection.create_index(
        field_name="dense_embeddings",
        index_params={
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {
                "M": 5,
                "efConstruction": 512
            }
        },
        index_name="dense_embeddings_index"
    )
    
    print("Dense embeddings index created")

    # Sparse embeddings index
    collection.create_index(
        field_name="sparse_embeddings",
        index_params={
            "metric_type": "IP",
            "index_type": "SPARSE_INVERTED_INDEX",
            "params": {
                "drop_ratio_build": 0.2
            }
        },
        index_name="sparse_embeddings_index"
    )
    
    print("Sparse embeddings index created")
    collection.load()
    print("Collection loaded")