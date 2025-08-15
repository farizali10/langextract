#!/usr/bin/env python3
"""Quick start script for the LangExtract FastAPI application."""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.split('\n')[0]
        print(f"✅ Tesseract OCR: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR not found")
        print("Please install Tesseract OCR:")
        print("  Windows: choco install tesseract")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        return False


def check_env_file():
    """Check if .env file exists and has API keys."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("Creating .env file from template...")
        
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env and add your API keys")
            return False
        else:
            print("❌ .env.example file not found")
            return False
    
    # Check if API keys are configured
    with open(env_file, 'r') as f:
        content = f.read()
    
    has_langextract_key = 'LANGEXTRACT_API_KEY=' in content and 'your_' not in content
    has_openai_key = 'OPENAI_API_KEY=' in content and 'your_' not in content
    
    if has_langextract_key or has_openai_key:
        print("✅ .env file exists with API keys")
        return True
    else:
        print("⚠️  .env file exists but API keys need to be configured")
        print("Please edit .env and add your API keys:")
        print("  - LANGEXTRACT_API_KEY (get from https://aistudio.google.com/app/apikey)")
        print("  - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


def main():
    """Main setup and start function."""
    print("LangExtract FastAPI - Quick Start")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_tesseract():
        print("\n⚠️  Tesseract OCR is required for image processing")
        print("You can still use the API for text and PDF files without it")
    
    # Check environment setup
    env_ready = check_env_file()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    if not env_ready:
        print("\n⚠️  Please configure your API keys in .env file before starting")
        print("Then run: python start.py")
        return
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()
