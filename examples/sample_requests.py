"""Sample requests for the LangExtract FastAPI application."""

import requests
import json


# Base URL for the API
BASE_URL = "http://localhost:8000"


def example_1_basic_text_extraction():
    """Example 1: Basic text extraction from a simple sentence."""
    print("Example 1: Basic Text Extraction")
    print("-" * 40)
    
    data = {
        "text": "Apple Inc. was founded by Steve Jobs in Cupertino, California on April 1, 1976.",
        "prompt_description": "Extract company names, person names, locations, and dates",
        "extraction_classes": "company,person,location,date"
    }
    
    response = requests.post(f"{BASE_URL}/extract-text", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['entity_count']} entities:")
        for entity in result['entities']:
            print(f"  {entity['extraction_class']}: '{entity['extraction_text']}'")
    else:
        print(f"✗ Error: {response.text}")
    
    print()


def example_2_medical_text():
    """Example 2: Medical text processing."""
    print("Example 2: Medical Text Processing")
    print("-" * 40)
    
    medical_text = """
    Patient: Maria Rodriguez
    DOB: 05/15/1985
    Date of Visit: 12/08/2024
    
    Chief Complaint: Persistent headache and dizziness
    
    History: 38-year-old female presents with a 3-day history of severe headaches 
    accompanied by dizziness and nausea. No fever reported.
    
    Medications: 
    - Ibuprofen 600mg every 6 hours as needed
    - Ondansetron 4mg twice daily for nausea
    
    Assessment: Tension headache, likely stress-related
    Plan: Continue current medications, follow up in 1 week
    """
    
    data = {
        "text": medical_text,
        "prompt_description": "Extract patient information, symptoms, medications, and medical assessments",
        "extraction_classes": "patient,symptom,medication,diagnosis,date",
        "model_id": "gemini-2.5-flash"
    }
    
    response = requests.post(f"{BASE_URL}/extract-text", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['entity_count']} entities:")
        for entity in result['entities']:
            print(f"  {entity['extraction_class']}: '{entity['extraction_text']}'")
            if entity['attributes']:
                print(f"    Attributes: {entity['attributes']}")
    else:
        print(f"✗ Error: {response.text}")
    
    print()


def example_3_business_document():
    """Example 3: Business document processing."""
    print("Example 3: Business Document Processing")
    print("-" * 40)
    
    business_text = """
    SALES REPORT - Q4 2024
    
    Regional Manager: John Thompson
    Territory: West Coast
    Report Date: December 31, 2024
    
    Key Accounts:
    - Microsoft Corporation: $2.5M revenue
    - Google LLC: $1.8M revenue  
    - Apple Inc.: $3.2M revenue
    
    Top Performing Products:
    - CloudSync Pro: $1.2M
    - DataVault Enterprise: $950K
    - SecureLink Premium: $780K
    
    Next Quarter Goals:
    - Increase revenue by 15%
    - Expand into Oregon and Washington markets
    - Launch new product line in February 2025
    """
    
    data = {
        "text": business_text,
        "prompt_description": "Extract companies, people, financial amounts, products, and business goals",
        "extraction_classes": "company,person,money,product,goal,location",
        "model_id": "gemini-2.5-flash"
    }
    
    response = requests.post(f"{BASE_URL}/extract-text", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['entity_count']} entities:")
        for entity in result['entities']:
            print(f"  {entity['extraction_class']}: '{entity['extraction_text']}'")
    else:
        print(f"✗ Error: {response.text}")
    
    print()


def example_4_file_upload():
    """Example 4: File upload processing."""
    print("Example 4: File Upload Processing")
    print("-" * 40)
    
    # Create a sample document
    sample_content = """
    RESEARCH PAPER ABSTRACT
    
    Title: Machine Learning Applications in Healthcare
    Authors: Dr. Sarah Chen, Prof. Michael Rodriguez, Dr. Lisa Wang
    Institution: Stanford University Medical Center
    Publication Date: November 2024
    
    Abstract:
    This study examines the implementation of machine learning algorithms 
    in clinical decision support systems. We analyzed data from 10,000 
    patient records across three major hospitals: Johns Hopkins, Mayo Clinic, 
    and Cleveland Clinic.
    
    Key findings include a 23% improvement in diagnostic accuracy and 
    15% reduction in treatment time when using AI-assisted diagnosis.
    
    Keywords: machine learning, healthcare, diagnosis, clinical decision support
    """
    
    # Save to temporary file
    with open("temp_research.txt", "w") as f:
        f.write(sample_content)
    
    try:
        with open("temp_research.txt", "rb") as f:
            files = {"file": ("research_paper.txt", f, "text/plain")}
            data = {
                "prompt_description": "Extract research paper metadata, authors, institutions, and key findings",
                "extraction_classes": "title,author,institution,date,finding,keyword",
                "model_id": "gemini-2.5-flash"
            }
            
            response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Processed {result['filename']} ({result['file_type']})")
                print(f"✓ Text length: {result['text_length']} characters")
                print(f"✓ Found {result['entity_count']} entities:")
                for entity in result['entities']:
                    print(f"  {entity['extraction_class']}: '{entity['extraction_text']}'")
            else:
                print(f"✗ Error: {response.text}")
    
    finally:
        # Clean up
        import os
        if os.path.exists("temp_research.txt"):
            os.remove("temp_research.txt")
    
    print()


def main():
    """Run all examples."""
    print("LangExtract FastAPI - Sample Requests")
    print("=" * 50)
    print()
    
    try:
        example_1_basic_text_extraction()
        example_2_medical_text()
        example_3_business_document()
        example_4_file_upload()
        
        print("All examples completed!")
        print("\nNote: Make sure you have set up your API keys in the .env file")
        print("and that the server is running on http://localhost:8000")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running:")
        print("  python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
