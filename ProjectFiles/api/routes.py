import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse 
import logging

from api.models import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ErrorResponse,
    ContentType
)

logger = logging.getLogger(__name__)

router = APIRouter()

def get_ai_service(request: Request):
    """Dependency to get AI service from request state"""
    ai_service = getattr(request.state, 'ai_service', None)
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    return ai_service

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    ai_service = Depends(get_ai_service)
):
    """Generate educational content using AI"""
    start_time = time.time()

    try:
        logger.info(f"Generating content for prompt: {request.prompt[:50]}...")

        if not ai_service.is_ready():
            raise HTTPException(status_code=503, detail="AI model is not ready. Please try again later.")

        enhanced_prompt = _enhance_prompt_by_type(request.prompt, request.content_type)

        result = await ai_service.generate_text(
            prompt=enhanced_prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            context=request.context
        )

        processing_time = time.time() - start_time

        logger.info(f"Content generated successfully in {processing_time:.2f}s")

        return GenerateResponse(
            success=True,
            generated_text=result.get("generated_text", ""),
            prompt=request.prompt,
            context=request.context,
            content_type=request.content_type,
            parameters=result.get("parameters", {}),
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        logger.error(f"Error generating content: {error_msg}")

        return GenerateResponse(
            success=False,
            error=error_msg,
            prompt=request.prompt,
            context=request.context,
            content_type=request.content_type,
            processing_time=processing_time
        )

@router.get("/health", response_model=HealthResponse)
async def health_check(ai_service = Depends(get_ai_service)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="EducatorAI",
        model_loaded=ai_service.is_ready() if ai_service else False,
        timestamp=datetime.now().isoformat()
    )

@router.get("/content-types")
async def get_content_types():
    """Get available content types"""
    return {
        "content_types": [
            {
                "value": content_type.value,
                "label": content_type.value.replace("_", " ").title(),
                "description": _get_content_type_description(content_type)
            }
            for content_type in ContentType
        ]
    }

def _enhance_prompt_by_type(prompt: str, content_type: ContentType) -> str:
    """Enhance prompt based on content type"""
    type_instructions = {
        ContentType.EXPLANATION: "Provide a clear, detailed explanation of the following topic. Include examples and break down complex concepts into understandable parts:",
        ContentType.SUMMARY: "Create a concise summary of the following topic, highlighting the key points and main ideas:",
        ContentType.QUIZ: "Generate quiz questions and answers about the following topic. Include multiple choice, true/false, and short answer questions:",
        ContentType.LESSON: "Create a structured lesson plan for teaching the following topic. Include objectives, activities, and assessment methods:",
        ContentType.EXAMPLE: "Provide practical examples and real-world applications of the following concept:",
        ContentType.DEFINITION: "Provide a clear definition and explanation of the following term or concept, including its significance and context:"
    }
    instruction = type_instructions.get(content_type, type_instructions[ContentType.EXPLANATION])
    return f"{instruction}\n\n{prompt}"

def _get_content_type_description(content_type: ContentType) -> str:
    """Get description for content type"""
    descriptions = {
        ContentType.EXPLANATION: "Detailed explanations with examples",
        ContentType.SUMMARY: "Concise summaries of key points",
        ContentType.QUIZ: "Quiz questions and answers",
        ContentType.LESSON: "Structured lesson plans",
        ContentType.EXAMPLE: "Practical examples and applications",
        ContentType.DEFINITION: "Clear definitions and explanations"
    }
    return descriptions.get(content_type, "Educational content")
