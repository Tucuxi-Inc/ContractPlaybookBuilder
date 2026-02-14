"""
Configuration settings for Contract Playbook Builder
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Server settings
PORT = int(os.environ.get("PORT", 3005))
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

# File upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE", 50))
ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx"}

# AI Provider settings
# Primary: Anthropic Claude (preferred)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Google Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.environ.get("GOOGLE_MODEL", "gemini-2.5-pro")

# Which provider to use (anthropic, openai, or google)
AI_PROVIDER = os.environ.get(
    "AI_PROVIDER",
    "anthropic" if ANTHROPIC_API_KEY else ("openai" if OPENAI_API_KEY else ("google" if GOOGLE_API_KEY else ""))
)

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Available providers and models for the setup UI
AVAILABLE_PROVIDERS = {
    "anthropic": {
        "name": "Anthropic",
        "models": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
            {"id": "claude-opus-4-20250514", "name": "Claude Opus 4"},
        ],
        "key_env": "ANTHROPIC_API_KEY",
        "model_env": "ANTHROPIC_MODEL",
    },
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ],
        "key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
    },
    "google": {
        "name": "Google Gemini",
        "models": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
        ],
        "key_env": "GOOGLE_API_KEY",
        "model_env": "GOOGLE_MODEL",
    },
}


def reload_config():
    """Re-read .env and update module-level config variables."""
    load_dotenv(override=True)

    global ANTHROPIC_API_KEY, ANTHROPIC_MODEL
    global OPENAI_API_KEY, OPENAI_MODEL
    global GOOGLE_API_KEY, GOOGLE_MODEL
    global AI_PROVIDER

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    GOOGLE_MODEL = os.environ.get("GOOGLE_MODEL", "gemini-2.5-pro")
    AI_PROVIDER = os.environ.get(
        "AI_PROVIDER",
        "anthropic" if ANTHROPIC_API_KEY else ("openai" if OPENAI_API_KEY else ("google" if GOOGLE_API_KEY else ""))
    )
