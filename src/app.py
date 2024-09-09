import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import APIRouter, HTTPException, status
from src.graph.build_graph import build_graph
from src.schema.data import CreateIndexRequest, DeleteIndexRequest
from src.services.services import collection
from src.utils.utils import parse_and_process_docs
from src.vector.create_index import batch_ingestion, drop_indexes, create_all_indexes

delete_vector_router = APIRouter()
upload_vector_router = APIRouter()
upload_graph_router = APIRouter()
upload_all_router = APIRouter()

@delete_vector_router.delete("/delete-vector")
def delete_vector(request: DeleteIndexRequest):
    index_names = request.index_names
    try:
        print("Dropping Indexes for Vector DB...")
        drop_indexes(collection=collection, index_names=index_names)
        return {
            "message": "Indexes have been successfully dropped."
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@upload_vector_router.post("/upload-vector")
def upload_vector(request: CreateIndexRequest):
    file_location = request.file_location
    data_folder = request.data_folder
    try:
        print("Parsing and Processing Documents...")
        final_docs = parse_and_process_docs(file_location=file_location, data_folder=data_folder)
        print(f"Final Docs Retrieved!")
        print("Starting Ingestion Process!")
        batch_ingestion(collection=collection, final_docs=final_docs)
        print("Ingestion Process Completed!")
        print("Creating Indexes for Vector DB...")
        create_all_indexes(collection=collection)
        return {
            "message": "Documents have been successfully ingested, indexed, and loaded."
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@upload_graph_router.post("/upload-graph")
def upload_graph(request: CreateIndexRequest):
    file_location = request.file_location
    data_folder = request.data_folder
    try:
        print("Parsing and Processing Documents...")
        final_docs = parse_and_process_docs(file_location=file_location, data_folder=data_folder)
        print(f"Final Docs Retrieved!")
        print("Starting Ingestion Process!")
        index = build_graph(documents=final_docs)
        print("Ingestion Process Completed!")
        return {
            "message": "Documents have been successfully ingested, indexed, and loaded."
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# Function to handle ingestion to Vector DB
def ingest_vector_db(final_docs):
    print("Starting Ingestion Process for Vector DB...")
    batch_ingestion(collection=collection, final_docs=final_docs)
    print("Vector DB Ingestion Process Completed!")
    print("Creating Indexes for Vector DB...")
    create_all_indexes(collection=collection)
    print("Vector DB Indexes Created!")

# Function to handle ingestion to KG DB
def ingest_kg_db(final_docs):
    print("Starting Ingestion Process for KG DB...")
    build_graph(documents=final_docs)
    print("KG DB Ingestion Process Completed!")
    
@upload_all_router.post("/upload-all")
def upload_all(request: CreateIndexRequest):
    file_location = request.file_location
    data_folder = request.data_folder
    try:
        print("Parsing and Processing Documents...")
        final_docs = parse_and_process_docs(file_location=file_location, data_folder=data_folder)
        print(f"Final Docs Retrieved!")
        
        # Using ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(ingest_vector_db, final_docs): "Vector DB",
                executor.submit(ingest_kg_db, final_docs): "KG DB"
            }

            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    future.result()  # Get the result of the future; just checking for exceptions
                except Exception as e:
                    print(f"Exception in {task_name}: {str(e)}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{task_name} Ingestion Error: {str(e)}")

        return {
            "message": "Documents have been successfully ingested, indexed, and loaded."
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))