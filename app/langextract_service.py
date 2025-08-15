"""LangExtract service for document processing and information extraction."""

import time
from typing import List, Dict, Any, Optional, Tuple
import langextract as lx

from app.config import settings
from app.models import ExtractionEntity


class LangExtractService:
    """Service for processing documents with LangExtract."""
    
    def __init__(self):
        """Initialize the LangExtract service."""
        self.api_key = settings.langextract_api_key or settings.openai_api_key
    
    def create_examples_from_classes(self, extraction_classes: List[str], sample_text: str = None) -> List[lx.data.ExampleData]:
        """Create example data for LangExtract based on extraction classes."""
        if not sample_text:
            sample_text = "John Smith visited New York on January 15, 2024, to meet with Dr. Sarah Johnson."
        
        # Create sample extractions based on the requested classes
        sample_extractions = []
        
        # Common extraction patterns
        class_patterns = {
            'person': {'text': 'John Smith', 'attributes': {'type': 'full_name'}},
            'name': {'text': 'John Smith', 'attributes': {'type': 'person_name'}},
            'location': {'text': 'New York', 'attributes': {'type': 'city'}},
            'place': {'text': 'New York', 'attributes': {'type': 'city'}},
            'date': {'text': 'January 15, 2024', 'attributes': {'format': 'full_date'}},
            'time': {'text': 'January 15, 2024', 'attributes': {'type': 'date'}},
            'organization': {'text': 'Dr. Sarah Johnson', 'attributes': {'type': 'professional_title'}},
            'title': {'text': 'Dr.', 'attributes': {'type': 'professional_title'}},
            'email': {'text': 'example@email.com', 'attributes': {'type': 'contact'}},
            'phone': {'text': '(555) 123-4567', 'attributes': {'type': 'contact'}},
            'address': {'text': 'New York', 'attributes': {'type': 'location'}},
            'company': {'text': 'Company Name', 'attributes': {'type': 'business'}},
            'product': {'text': 'Product Name', 'attributes': {'type': 'item'}},
            'money': {'text': '$100', 'attributes': {'currency': 'USD'}},
            'amount': {'text': '$100', 'attributes': {'type': 'monetary'}},
        }
        
        for extraction_class in extraction_classes:
            class_lower = extraction_class.lower()
            if class_lower in class_patterns:
                pattern = class_patterns[class_lower]
                sample_extractions.append(
                    lx.data.Extraction(
                        extraction_class=extraction_class,
                        extraction_text=pattern['text'],
                        attributes=pattern['attributes']
                    )
                )
            else:
                # Generic example for unknown classes
                sample_extractions.append(
                    lx.data.Extraction(
                        extraction_class=extraction_class,
                        extraction_text="example_text",
                        attributes={"type": "generic"}
                    )
                )
        
        return [
            lx.data.ExampleData(
                text=sample_text,
                extractions=sample_extractions
            )
        ]
    
    def process_document(
        self,
        text: str,
        prompt_description: str,
        extraction_classes: List[str],
        model_id: Optional[str] = None,
        max_workers: Optional[int] = None,
        extraction_passes: Optional[int] = None
    ) -> Tuple[List[ExtractionEntity], Dict[str, Any]]:
        """
        Process document with LangExtract and return extracted entities.
        
        Returns:
            Tuple of (entities, metadata)
        """
        start_time = time.time()
        
        # Use defaults from settings if not provided
        model_id = model_id or settings.default_model
        max_workers = max_workers or settings.max_workers
        extraction_passes = extraction_passes or settings.extraction_passes
        
        # Create examples based on extraction classes
        examples = self.create_examples_from_classes(extraction_classes, text[:200])
        
        try:
            # Configure API key
            api_key = self.api_key
            if not api_key:
                raise ValueError("No API key configured. Please set LANGEXTRACT_API_KEY or OPENAI_API_KEY")
            
            # Determine if we're using OpenAI
            use_openai = model_id.startswith(('gpt-', 'text-', 'davinci', 'curie', 'babbage', 'ada'))
            
            # Configure extraction parameters
            extract_params = {
                'text_or_documents': text,
                'prompt_description': prompt_description,
                'examples': examples,
                'model_id': model_id,
                'max_workers': max_workers,
                'extraction_passes': extraction_passes,
                'max_char_buffer': settings.max_char_buffer,
            }
            
            # Add API key
            if use_openai:
                extract_params['api_key'] = settings.openai_api_key
                extract_params['fence_output'] = True
                extract_params['use_schema_constraints'] = False
            else:
                extract_params['api_key'] = settings.langextract_api_key
            
            # Run extraction
            result = lx.extract(**extract_params)
            
            # Convert result to our format
            entities = []
            if hasattr(result, 'extractions') and result.extractions:
                for extraction in result.extractions:
                    entity = ExtractionEntity(
                        extraction_class=extraction.extraction_class,
                        extraction_text=extraction.extraction_text,
                        start_char=getattr(extraction, 'start_char', 0),
                        end_char=getattr(extraction, 'end_char', len(extraction.extraction_text)),
                        attributes=getattr(extraction, 'attributes', {})
                    )
                    entities.append(entity)
            
            # Generate visualization HTML
            visualization_html = None
            try:
                # Save to temporary JSONL and generate visualization
                if result and hasattr(result, 'extractions') and result.extractions:
                    # Save results to temporary JSONL file
                    import tempfile
                    import os

                    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
                        temp_file = f.name

                    try:
                        lx.io.save_annotated_documents([result], output_name=temp_file.replace('.jsonl', ''), output_dir='.')
                        html_content = lx.visualize(temp_file)
                        if hasattr(html_content, 'data'):
                            visualization_html = html_content.data
                        else:
                            visualization_html = str(html_content)
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
            except Exception as viz_error:
                print(f"Warning: Could not generate visualization: {viz_error}")
            
            processing_time = time.time() - start_time
            
            metadata = {
                'model_used': model_id,
                'processing_time_seconds': processing_time,
                'extraction_passes': extraction_passes,
                'max_workers': max_workers,
                'text_length': len(text),
                'visualization_html': visualization_html
            }
            
            return entities, metadata
            
        except Exception as e:
            raise ValueError(f"LangExtract processing failed: {str(e)}")
    
    def check_availability(self) -> Tuple[bool, bool]:
        """
        Check if LangExtract is available and API key is configured.
        
        Returns:
            Tuple of (langextract_available, api_key_configured)
        """
        try:
            import langextract
            langextract_available = True
        except ImportError:
            langextract_available = False
        
        api_key_configured = bool(self.api_key)
        
        return langextract_available, api_key_configured
