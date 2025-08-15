"""Pydantic models for request/response schemas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request model for text extraction."""
    
    prompt_description: str = Field(
        ...,
        description="Description of what information to extract",
        example="Extract person names, locations, and dates mentioned in the text"
    )
    
    extraction_classes: List[str] = Field(
        ...,
        description="List of entity types to extract",
        example=["person", "location", "date"]
    )
    
    model_id: Optional[str] = Field(
        default=None,
        description="LLM model to use (defaults to gemini-2.5-flash)",
        example="gemini-2.5-flash"
    )
    
    max_workers: Optional[int] = Field(
        default=None,
        description="Number of parallel workers for processing",
        example=10
    )
    
    extraction_passes: Optional[int] = Field(
        default=None,
        description="Number of extraction passes for better recall",
        example=2
    )


class ExtractionEntity(BaseModel):
    """Model for a single extracted entity."""
    
    extraction_class: str = Field(..., description="Type/class of the extracted entity")
    extraction_text: str = Field(..., description="The actual extracted text")
    start_char: int = Field(..., description="Start character position in source text")
    end_char: int = Field(..., description="End character position in source text")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")


class ExtractionResponse(BaseModel):
    """Response model for extraction results."""
    
    success: bool = Field(..., description="Whether extraction was successful")
    message: str = Field(..., description="Status message")
    
    # File information
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Detected file type")
    text_length: int = Field(..., description="Length of extracted text")
    
    # Extraction results
    entities: List[ExtractionEntity] = Field(default_factory=list, description="Extracted entities")
    entity_count: int = Field(..., description="Total number of entities extracted")
    
    # Processing metadata
    model_used: str = Field(..., description="LLM model used for extraction")
    processing_time_seconds: float = Field(..., description="Time taken for processing")
    
    # Optional: visualization URL or HTML content
    visualization_html: Optional[str] = Field(default=None, description="HTML visualization content")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    langextract_available: bool = Field(..., description="Whether LangExtract is available")
    api_key_configured: bool = Field(..., description="Whether API key is configured")
