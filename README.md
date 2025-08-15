# LangExtract FastAPI Application

A FastAPI application that uses Google's LangExtract library for document processing and structured information extraction. This application provides REST API endpoints to extract structured data from various document formats using Large Language Models (LLMs).

## 🚀 Features

- **Multiple File Format Support**: TXT, PDF, DOCX, XLSX, PNG, JPG, JPEG
- **OCR Capabilities**: Extract text from images using Tesseract OCR
- **LLM Integration**: Support for Google Gemini and OpenAI models
- **Structured Extraction**: Extract specific entity types with custom prompts
- **Interactive Visualization**: Generate HTML visualizations of extracted entities
- **Parallel Processing**: Optimized for large documents with chunking and parallel processing
- **REST API**: Easy-to-use HTTP endpoints with comprehensive documentation

## 📋 Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for image processing)
- API key for Google Gemini or OpenAI

### Installing Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or using chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd langextract-fastapi
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

## 🔑 API Key Setup

### Google Gemini API Key (Recommended)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file:
```
LANGEXTRACT_API_KEY=your_gemini_api_key_here
```

### OpenAI API Key (Alternative)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to your `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Running the Application

1. **Start the server:**
```bash
python -m uvicorn app.main:app --reload
```

2. **Access the application:**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 📖 API Endpoints

### Health Check
```http
GET /health
```
Check if the service is running and properly configured.

### Extract from File
```http
POST /extract
```
Upload a file and extract structured information.

**Parameters:**
- `file`: Document file (multipart/form-data)
- `prompt_description`: Description of what to extract
- `extraction_classes`: Comma-separated entity types
- `model_id`: LLM model to use (optional)
- `max_workers`: Parallel workers (optional)
- `extraction_passes`: Number of passes (optional)

### Extract from Text
```http
POST /extract-text
```
Process raw text input.

**Parameters:**
- `text`: Text content to process
- `prompt_description`: Description of what to extract
- `extraction_classes`: Comma-separated entity types
- `model_id`: LLM model to use (optional)

### Available Models
```http
GET /models
```
Get list of supported LLM models.

## 💡 Usage Examples

### Basic Text Extraction
```python
import requests

data = {
    "text": "John Smith visited New York on January 15, 2024.",
    "prompt_description": "Extract person names, locations, and dates",
    "extraction_classes": "person,location,date"
}

response = requests.post("http://localhost:8000/extract-text", data=data)
print(response.json())
```

### File Upload
```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f, "application/pdf")}
    data = {
        "prompt_description": "Extract key information from the document",
        "extraction_classes": "person,organization,date,location"
    }
    
    response = requests.post("http://localhost:8000/extract", files=files, data=data)
    print(response.json())
```

## 📁 Supported File Formats

| Format | Extension | Description | OCR Support |
|--------|-----------|-------------|-------------|
| Text | .txt | Plain text files | N/A |
| PDF | .pdf | PDF documents | Text extraction only* |
| Word | .docx | Microsoft Word documents | N/A |
| Excel | .xlsx | Microsoft Excel spreadsheets | N/A |
| Images | .png, .jpg, .jpeg | Image files | ✅ Yes (Tesseract) |

*Note: PDF OCR for scanned documents is not currently supported. Only text-based PDFs work.*

## ⚙️ Configuration

Edit the `.env` file to customize settings:

```env
# API Keys
LANGEXTRACT_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=txt,pdf,docx,xlsx,png,jpg,jpeg

# LangExtract Settings
DEFAULT_MODEL=gemini-2.5-flash
```

## 🧪 Testing

Run the test suite:
```bash
# Start the server first
python -m uvicorn app.main:app --reload

# In another terminal, run tests
python test_api.py

# Or run example requests
python examples/sample_requests.py
```

## 🔍 LangExtract Capabilities

### What LangExtract Does:
- ✅ Extracts structured information from text using LLMs
- ✅ Maps extractions to exact source locations
- ✅ Supports custom entity types and prompts
- ✅ Optimized for long documents with chunking
- ✅ Generates interactive visualizations
- ✅ Works with multiple LLM providers

### What LangExtract Doesn't Do:
- ❌ Built-in OCR for scanned PDFs
- ❌ Direct image/binary file processing
- ❌ Real-time streaming processing
- ❌ Document format conversion

## 🚨 Limitations

1. **OCR Dependency**: Image text extraction requires Tesseract OCR
2. **Text-Only Processing**: LangExtract works with text, not binary formats
3. **API Rate Limits**: Subject to LLM provider rate limits
4. **File Size Limits**: Default 10MB limit (configurable)
5. **Scanned PDFs**: No built-in OCR for scanned PDF documents

## 🛡️ Error Handling

The API provides detailed error responses:

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "File size exceeds 10MB limit",
  "details": {
    "file_size": "15MB",
    "max_allowed": "10MB"
  }
}
```

## 📊 Response Format

Successful extractions return:

```json
{
  "success": true,
  "message": "Extraction completed successfully",
  "filename": "document.pdf",
  "file_type": "pdf",
  "text_length": 1500,
  "entities": [
    {
      "extraction_class": "person",
      "extraction_text": "John Smith",
      "start_char": 0,
      "end_char": 10,
      "attributes": {"type": "full_name"}
    }
  ],
  "entity_count": 1,
  "model_used": "gemini-2.5-flash",
  "processing_time_seconds": 2.5,
  "visualization_html": "<html>...</html>"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues:

1. **"No API key configured"**
   - Ensure you've set `LANGEXTRACT_API_KEY` or `OPENAI_API_KEY` in `.env`

2. **"Tesseract not found"**
   - Install Tesseract OCR and ensure it's in your PATH

3. **"File type not supported"**
   - Check the supported file formats list above

4. **"Rate limit exceeded"**
   - Wait and retry, or upgrade your API plan

For more help, check the [LangExtract documentation](https://github.com/google/langextract) or open an issue.
