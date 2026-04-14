"""
Central configuration for Teacher Isa (RAG + LLM).
Place this file at: src/config.py
"""

from pathlib import Path
import os
from typing import Final

# -------------------------
# Model selection / keys
# -------------------------
# Choose provider: "groq" or "huggingface"

LLM_MODEL: str = "llama-3.3-70b-versatile"
LLM_MAX_NEW_TOKENS: int = 768
LLM_TEMPERATURE: float = 0.01
LLM_TOP_P: float = 0.95
LLM_REPETITION_PENALTY: float = 1.03
LLM_QUESTION: str = "What is the capital of France?"

# LLM_PROVIDER = "huggingface"
LLM_PROVIDER = "groq"

LLM_PROVIDER: Final[str] = os.getenv("LLM_PROVIDER", "groq").lower()

# Groq settings (if using Groq)
GROQ_API_KEY_ENV: Final[str] = "GROQ_API_KEY"
GROQ_MODEL: Final[str] = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# HuggingFace settings (if using HuggingFace)
HUGGINGFACE_API_KEY_ENV: Final[str] = "HUGGINGFACEHUB_API_TOKEN"
HUGGINGFACE_MODEL: Final[str] = os.getenv("HUGGINGFACE_MODEL", "mistral-7b-instruct")

# System prompt used for chat engines
LLM_SYSTEM_PROMPT: Final[str] = os.getenv(
    "LLM_SYSTEM_PROMPT",
    "You are Teacher Isa, an experienced multilingual language teacher fluent in English, German, and Portuguese. "
    "Your mission is to help students practice English in a natural, motivating, and effective way. "
    "When interacting, strictly apply the following pedagogical techniques: "
    "1. Pedagogical Recasting: Subtly correct the student's errors by embedding the correct form within your natural conversational response. "
    "2. Scaffolding: Provide progressive hints and supportive prompts to help the student build independence step-by-step. "
    "3. Positive Reinforcement: Consistently celebrate the student's effort and progress to maintain high motivation. "
    "4. Contextual Learning: Use real-world English examples from movies, literature, and authentic conversations. "
    "Maintain an encouraging tone and adapt your language complexity to the student's specific level and needs."
)

# -------------------------
# Embedding settings
# -------------------------
EMBEDDING_MODEL_NAME: Final[str] = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------------
# RAG settings
# -------------------------

# How many top similar chunks to retrieve
SIMILARITY_TOP_K: Final[int] = int(os.getenv("SIMILARITY_TOP_K", "3"))

# Chunking parameters (tokens or approximate characters depending on splitter)
CHUNK_SIZE: Final[int] = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP: Final[int] = int(os.getenv("CHUNK_OVERLAP", "50"))
    
# Memory / chat history
CHAT_MEMORY_TOKEN_LIMIT: Final[int] = int(os.getenv("CHAT_MEMORY_TOKEN_LIMIT", "3900"))

# LLM generation defaults (can be overridden per-call)
LLM_MAX_NEW_TOKENS: Final[int] = int(os.getenv("LLM_MAX_NEW_TOKENS", "768"))
LLM_TEMPERATURE: Final[float] = float(os.getenv("LLM_TEMPERATURE", "0.01"))
LLM_TOP_P: Final[float] = float(os.getenv("LLM_TOP_P", "0.95"))
LLM_REPETITION_PENALTY: Final[float] = float(os.getenv("LLM_REPETITION_PENALTY", "1.03"))

# -------------------------
# Paths and persistence
# -------------------------
ROOT_PATH: Final[Path] = Path(__file__).resolve().parent.parent
DATA_PATH: Final[Path] = ROOT_PATH / "data"
LOCAL_STORAGE_PATH: Final[Path] = ROOT_PATH / "local_storage"
EMBEDDING_CACHE_PATH: Final[Path] = LOCAL_STORAGE_PATH / "embedding_model"
VECTOR_STORE_PATH: Final[Path] = LOCAL_STORAGE_PATH / "vector_store"

# -------------------------
# App / runtime settings
# -------------------------
# Port and host for future FastAPI server
API_HOST: Final[str] = os.getenv("API_HOST", "0.0.0.0")
API_PORT: Final[int] = int(os.getenv("API_PORT", "8000"))

# Logging level
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")

# Development flags
REBUILD_INDEX_ON_START: Final[bool] = os.getenv("REBUILD_INDEX_ON_START", "false").lower() in ("1", "true", "yes")

# -------------------------
# Helper utilities
# -------------------------
def ensure_paths_exist() -> None:
    """
    Create required directories if they don't exist.
    Call this early in startup (model_loader or engine).
    """
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    EMBEDDING_CACHE_PATH.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

def get_api_key() -> str | None:
    """
    Return the configured API key for the selected provider.
    """
    if LLM_PROVIDER.lower() == "groq":
        return os.getenv(GROQ_API_KEY_ENV)
    return os.getenv(HUGGINGFACE_API_KEY_ENV)

# -------------------------
# Small runtime validation
# -------------------------
def validate_config() -> None:
    """
    Basic checks to help developers catch common misconfigurations early.
    Raises ValueError on fatal issues.
    """
    if not DATA_PATH.exists() or not any(DATA_PATH.iterdir()):
        # Not fatal by design; data can be added later. Log or warn in your app.
        pass

    api_key = get_api_key()
    if api_key is None:
        # Do not raise here if you want to support local-only workflows without remote LLMs.
        # Raise in model_loader if you require an API key at startup.
        pass

# Run ensure_paths_exist on import to simplify local dev
ensure_paths_exist()
