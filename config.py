"""
Configuration settings for the Medical Document AI Assistant
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Free tier model
EMBEDDING_MODEL = "models/text-embedding-004"  # Google's embedding model

# Alternative: Use sentence-transformers for fully local embeddings
USE_LOCAL_EMBEDDINGS = True
LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, free

# Vector Store Configuration
VECTOR_STORE_TYPE = "chroma"  # Using ChromaDB (free and open-source)
COLLECTION_NAME = "medical_documents"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Document Processing Configuration
MAX_FILE_SIZE_MB = 50
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.png', '.jpg', '.jpeg']

# RAG Configuration
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Agent Configuration
MAX_AGENT_ITERATIONS = 5
AGENT_TIMEOUT_SECONDS = 60

# Streamlit Configuration
PAGE_TITLE = "Medical Document AI Assistant"
PAGE_ICON = "🏥"
LAYOUT = "wide"

# PDF Report Configuration
REPORT_TEMPLATE = {
    "page_size": "A4",
    "margin": 72,  # 1 inch
    "title_font_size": 18,
    "heading_font_size": 14,
    "body_font_size": 11,
}

# Token Limits (Important for Gemini free tier)
# Gemini 2.0 Flash free tier: ~1M tokens per minute, 15 RPM
MAX_INPUT_TOKENS = 30000  # Conservative limit per request
MAX_OUTPUT_TOKENS = 8000
REQUEST_DELAY_SECONDS = 4  # To stay under 15 RPM

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log"
