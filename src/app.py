import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, status
from src.services.services import collection
from src.vector.utils import process_pdfs
from src.vector.create_index import batch_ingestion, create_all_indexes

upload_router = APIRouter()

@upload_router.post("/upload-and-index-pdfs")
def upload_and_index_pdfs(file_location: str, data_folder: str):
    try:
        final_docs = process_pdfs(file_location=file_location, data_folder=data_folder)
        print(f"Final Docs Retrieved!")
        print("Starting Ingestion Process!")
        batch_ingestion(collection=collection, final_docs=final_docs)
        print("Ingestion Process Completed!")
        print("Creating Indexes...")
        create_all_indexes(collection=collection)
        return {
            "message": "Documents have been successfully ingested, indexed, and loaded."
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))