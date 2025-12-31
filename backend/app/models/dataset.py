from pydantic import BaseModel

class DatasetResponse(BaseModel):
    dataset_id: str
    filename: str
    status: str

class DatasetListResponse(BaseModel):
    dataset_id: str
    filename: str
    status: str
