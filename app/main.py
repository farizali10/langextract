"""FastAPI application for document processing with LangExtract."""

import time
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.models import (
    ExtractionRequest, ExtractionResponse, ErrorResponse, 
    HealthResponse, ExtractionEntity
)
from app.file_processor import FileProcessor
from app.langextract_service import LangExtractService

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
file_processor = FileProcessor()
langextract_service = LangExtractService()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>LangExtract Document Processing API</title>
        </head>
        <body>
            <h1>LangExtract Document Processing API</h1>
            <p>Welcome to the LangExtract Document Processing API!</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/docs">API Documentation (Swagger UI)</a></li>
                <li><a href="/redoc">API Documentation (ReDoc)</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
            <h2>Supported File Types:</h2>
            <p>TXT, PDF, DOCX, XLSX, PNG, JPG, JPEG</p>
            <h2>Features:</h2>
            <ul>
                <li>Text extraction from multiple file formats</li>
                <li>OCR for images using Tesseract</li>
                <li>Structured information extraction using LangExtract</li>
                <li>Support for Gemini and OpenAI models</li>
                <li>Interactive visualization of results</li>
            </ul>
        </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    langextract_available, api_key_configured = langextract_service.check_availability()
    
    return HealthResponse(
        status="healthy" if langextract_available and api_key_configured else "degraded",
        version=settings.app_version,
        langextract_available=langextract_available,
        api_key_configured=api_key_configured
    )


@app.post("/extract", response_model=ExtractionResponse)
async def extract_from_file(
    file: UploadFile = File(..., description="Document file to process"),
    prompt_description: str = Form(..., description="Description of what to extract"),
    extraction_classes: str = Form(..., description="Comma-separated list of entity types to extract"),
    model_id: str = Form(default=None, description="LLM model to use"),
    max_workers: int = Form(default=None, description="Number of parallel workers"),
    extraction_passes: int = Form(default=None, description="Number of extraction passes")
):
    """
    Extract structured information from uploaded document.
    
    This endpoint accepts various file formats and extracts structured information
    based on the provided prompt and extraction classes.
    """
    start_time = time.time()
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        is_valid, error_message = file_processor.validate_file(file.filename, content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Extract text from file
        try:
            text, file_type = file_processor.extract_text(file.filename, content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Parse extraction classes
        extraction_classes_list = [cls.strip() for cls in extraction_classes.split(",")]
        
        # Process with LangExtract
        try:
            entities, metadata = langextract_service.process_document(
                text=text,
                prompt_description=prompt_description,
                extraction_classes=extraction_classes_list,
                model_id=model_id,
                max_workers=max_workers,
                extraction_passes=extraction_passes
            )
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        # Calculate total processing time
        total_processing_time = time.time() - start_time
        
        return ExtractionResponse(
            success=True,
            message="Extraction completed successfully",
            filename=file.filename,
            file_type=file_type,
            text_length=len(text),
            entities=entities,
            entity_count=len(entities),
            model_used=metadata['model_used'],
            processing_time_seconds=total_processing_time,
            visualization_html=metadata.get('visualization_html')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/extract-text", response_model=ExtractionResponse)
async def extract_from_text(
    text: str = Form(..., description="Text content to process"),
    prompt_description: str = Form(..., description="Description of what to extract"),
    extraction_classes: str = Form(..., description="Comma-separated list of entity types to extract"),
    model_id: str = Form(default=None, description="LLM model to use"),
    max_workers: int = Form(default=None, description="Number of parallel workers"),
    extraction_passes: int = Form(default=None, description="Number of extraction passes")
):
    """
    Extract structured information from provided text.
    
    This endpoint processes raw text input and extracts structured information
    based on the provided prompt and extraction classes.
    """
    start_time = time.time()
    
    try:
        # Validate text length
        if len(text) > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=400, 
                detail=f"Text length exceeds {settings.max_file_size_mb}MB limit"
            )
        
        # Parse extraction classes
        extraction_classes_list = [cls.strip() for cls in extraction_classes.split(",")]
        
        # Process with LangExtract
        try:
            entities, metadata = langextract_service.process_document(
                text=text,
                prompt_description=prompt_description,
                extraction_classes=extraction_classes_list,
                model_id=model_id,
                max_workers=max_workers,
                extraction_passes=extraction_passes
            )
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        # Calculate total processing time
        total_processing_time = time.time() - start_time
        
        return ExtractionResponse(
            success=True,
            message="Extraction completed successfully",
            filename="text_input",
            file_type="text",
            text_length=len(text),
            entities=entities,
            entity_count=len(entities),
            model_used=metadata['model_used'],
            processing_time_seconds=total_processing_time,
            visualization_html=metadata.get('visualization_html')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/models")
async def get_available_models():
    """Get list of available models."""
    return {
        "gemini_models": [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ],
        "openai_models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ],
        "default_model": settings.default_model,
        "note": "Gemini models require LANGEXTRACT_API_KEY, OpenAI models require OPENAI_API_KEY"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
