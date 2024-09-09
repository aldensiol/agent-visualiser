import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, status
from src.graph.build_graph import build_graph
from src.schema.data import CreateIndexRequest
from src.services.services import collection
from src.utils.utils import parse_and_process_docs
from src.vector.create_index import batch_ingestion, create_all_indexes

upload_vector_router = APIRouter()
upload_graph_router = APIRouter()

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