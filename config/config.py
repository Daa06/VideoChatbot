import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
VIDEOS_DIR = BASE_DIR / "videos"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "videochat"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# Model configurations
CAPTION_MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"
ASR_MODEL_ID = "facebook/wav2vec2-base-960h"
EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

# Video processing
N_FRAMES = 29
DEVICE = "cuda" if os.getenv("USE_CUDA", "false").lower() == "true" else "cpu"

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyA0SE7DQNatZqYjTAA7pF102R45EHjME74"
