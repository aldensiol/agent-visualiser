import os
import sys
import uvicorn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app import upload_router

app = FastAPI(title="UpdateDocumentsToAWS", version="fastapi:1.0")

environment = os.getenv(
    "ENVIRONMENT_NAME", "dev"   
)

if environment == "dev":
    print("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
app.include_router(upload_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8001, reload=True)