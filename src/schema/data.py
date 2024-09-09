from pydantic import BaseModel
from typing import List, Optional

class CreateIndexRequest(BaseModel):
    file_location: str 
    data_folder: Optional[str] = None
    
class DeleteIndexRequest(BaseModel):
    index_names: List[str]