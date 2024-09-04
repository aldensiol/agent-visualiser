from pydantic import BaseModel
from typing import Optional

class CreateIndexRequest(BaseModel):
    collection_name: Optional[str] = None
    pdf_dir: Optional[str] = None
    metadata_dir: Optional[str] = None
    bucket_name: Optional[str] = None