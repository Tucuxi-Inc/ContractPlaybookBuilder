"""
Configuration settings for Contract Playbook Builder
"""
import os

# Server settings
PORT = int(os.environ.get("PORT", 3005))
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

# File upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE", 50))
ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx"}

# OpenAI settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
