from pydantic import BaseModel
from typing import Optional

class CreateIndexRequest(BaseModel):
    file_location: str 
    data_folder: Optional[str] = None