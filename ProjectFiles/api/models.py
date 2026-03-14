"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    """Content type enumeration"""
    EXPLANATION = "explanation"
    SUMMARY = "summary"
    QUIZ = "quiz"
    LESSON = "lesson"
    EXAMPLE = "example"
    DEFINITION = "definition"

class GenerateRequest(BaseModel):
    """Request model for text generation"""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The educational content prompt"
    )
    
    content_type: Optional[ContentType] = Field(
        default=ContentType.EXPLANATION,
        description="Type of educational content to generate"
    )
    
    context: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional context for content generation"
    )
    
    max_length: Optional[int] = Field(
        default=None,
        ge=50,
        le=1000,
        description="Maximum length of generated content"
    )
    
    temperature: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=2.0,
        description="Temperature for text generation"
    )
    
    top_p: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=1.0,
        description="Top-p value for text generation"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt content"""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()
    
    @validator('context')
    def validate_context(cls, v):
        """Validate context content"""
        if v is not None:
            return v.strip()
        return v

class GenerateResponse(BaseModel):
    """Response model for text generation"""
    
    success: bool = Field(description="Whether the generation was successful")
    generated_text: Optional[str] = Field(description="Generated educational content")
    prompt: Optional[str] = Field(description="Original prompt")
    context: Optional[str] = Field(description="Context used")
    content_type: Optional[ContentType] = Field(description="Type of content generated")
    parameters: Optional[Dict[str, Any]] = Field(description="Generation parameters used")
    error: Optional[str] = Field(description="Error message if generation failed")
    processing_time: Optional[float] = Field(description="Processing time in seconds")

class HealthResponse(BaseModel):
    """Response model for health check"""
    
    status: str = Field(description="Service status")
    service: str = Field(description="Service name")
    model_loaded: bool = Field(description="Whether the AI model is loaded")
    timestamp: Optional[str] = Field(description="Response timestamp")

class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(description="Detailed error information")
    code: Optional[str] = Field(description="Error code")
