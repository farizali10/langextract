"""Test script for the LangExtract FastAPI application."""

import requests
import json
from pathlib import Path


def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_models_endpoint():
    """Test the models endpoint."""
    print("Testing models endpoint...")
    response = requests.get("http://localhost:8000/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_text_extraction():
    """Test text extraction endpoint."""
    print("Testing text extraction...")
    
    data = {
        "text": "John Smith visited New York on January 15, 2024, to meet with Dr. Sarah Johnson at Microsoft Corporation.",
        "prompt_description": "Extract person names, locations, dates, and organizations from the text",
        "extraction_classes": "person,location,date,organization",
        "model_id": "gemini-2.5-flash"
    }
    
    response = requests.post("http://localhost:8000/extract-text", data=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Entities found: {result['entity_count']}")
        print(f"Processing time: {result['processing_time_seconds']:.2f}s")
        print("Entities:")
        for entity in result['entities']:
            print(f"  - {entity['extraction_class']}: '{entity['extraction_text']}'")
    else:
        print(f"Error: {response.text}")
    print()


def test_file_upload():
    """Test file upload endpoint."""
    print("Testing file upload...")
    
    # Create a sample text file
    sample_text = """
    Medical Report
    
    Patient: John Doe
    Date: March 15, 2024
    Doctor: Dr. Emily Smith
    
    The patient presented with symptoms of fever and headache.
    Prescribed medication: Ibuprofen 400mg twice daily.
    Follow-up appointment scheduled for March 22, 2024.
    """
    
    # Save to temporary file
    temp_file = Path("temp_test.txt")
    temp_file.write_text(sample_text)
    
    try:
        with open(temp_file, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "prompt_description": "Extract patient information, medications, and appointments from medical text",
                "extraction_classes": "patient,doctor,date,medication,appointment",
                "model_id": "gemini-2.5-flash"
            }
            
            response = requests.post("http://localhost:8000/extract", files=files, data=data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result['success']}")
                print(f"File type: {result['file_type']}")
                print(f"Text length: {result['text_length']}")
                print(f"Entities found: {result['entity_count']}")
                print(f"Processing time: {result['processing_time_seconds']:.2f}s")
                print("Entities:")
                for entity in result['entities']:
                    print(f"  - {entity['extraction_class']}: '{entity['extraction_text']}'")
            else:
                print(f"Error: {response.text}")
    
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()
    
    print()


def main():
    """Run all tests."""
    print("LangExtract FastAPI Test Suite")
    print("=" * 40)
    print()
    
    try:
        test_health_endpoint()
        test_models_endpoint()
        test_text_extraction()
        test_file_upload()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
