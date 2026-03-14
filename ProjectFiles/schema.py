from pydantic import BaseModel
from typing import Optional, Dict, Any

class RequestData(BaseModel):
    prompt: str
    content_type: str
    max_length: Optional[int] = 150
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    context: Optional[str] = ""

class GenerateResponse(BaseModel):
    success: bool = True
    generated_text: Optional[str] = None
    prompt: Optional[str] = None
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
