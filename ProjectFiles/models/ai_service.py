"""
AI Service for handling IBM Granite model interactions
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import threading
from concurrent.futures import ThreadPoolExecutor

from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI model operations"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._lock = threading.Lock()
        self._ready = False
    
    async def initialize(self):
        """Initialize the AI model and tokenizer"""
        logger.info("Initializing AI service...")
        
        try:
            # Determine device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # Load model and tokenizer in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._load_model)
            
            self._ready = True
            logger.info("AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise
    
    def _load_model(self):
        """Load the model and tokenizer (runs in thread)"""
        try:
            logger.info(f"Loading model: {settings.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.model_name,
                token=settings.hf_token,
                cache_dir=settings.model_cache_dir
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.model_name,
                token=settings.hf_token,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                cache_dir=settings.model_cache_dir
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if the service is ready"""
        return self._ready and self.pipeline is not None
    
    async def generate_text(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using the AI model"""
        
        if not self.is_ready():
            raise RuntimeError("AI service is not ready")
        
        try:
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Set generation parameters
            max_length = max_length or settings.max_length
            temperature = temperature or settings.temperature
            top_p = top_p or settings.top_p
            
            # Generate text in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._generate_text_sync,
                full_prompt,
                max_length,
                temperature,
                top_p
            )
            
            return {
                "generated_text": result,
                "prompt": prompt,
                "context": context,
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "top_p": top_p
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def _prepare_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Prepare the prompt for educational content generation"""
        
        system_prompt = """You are an expert educator and content creator. Your task is to generate high-quality educational content that is:
- Clear and easy to understand
- Accurate and factual
- Engaging and informative
- Appropriate for the target audience
- Well-structured with examples when helpful

Please provide educational content based on the following request:"""
        
        if context:
            full_prompt = f"{system_prompt}\n\nContext: {context}\n\nRequest: {prompt}\n\nResponse:"
        else:
            full_prompt = f"{system_prompt}\n\nRequest: {prompt}\n\nResponse:"
        
        return full_prompt
    
    def _generate_text_sync(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        top_p: float
    ) -> str:
        """Synchronous text generation (runs in thread)"""
        
        with self._lock:
            try:
                # Generate text
                outputs = self.pipeline(
                    prompt,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1,
                    return_full_text=False
                )
                
                # Extract generated text
                generated_text = outputs[0]['generated_text']
                
                # Clean up the output
                generated_text = generated_text.strip()
                
                return generated_text
                
            except Exception as e:
                logger.error(f"Error in text generation: {e}")
                raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AI service...")
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        # Clear model from memory
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.pipeline:
            del self.pipeline
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self._ready = False
        logger.info("AI service cleanup completed") 
