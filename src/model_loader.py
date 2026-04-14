"""
src/model_loader.py

Responsibility:
- Load environment variables
- Initialise and return LLM client (Groq or HuggingFace) based on config
- Initialise and return embedding model (HuggingFace / Sentence-Transformers wrapper)
- Keep initialisation logic isolated so engine.py can import and reuse components
"""

from typing import Any, Optional
import os
import logging
from dotenv import load_dotenv

# Resolver do LlamaIndex para transformar configs em objetos LLM
from llama_index.core.llms.utils import resolve_llm

from src.config import (
    LLM_PROVIDER,
    GROQ_API_KEY_ENV,
    GROQ_MODEL,
    HUGGINGFACE_API_KEY_ENV,
    HUGGINGFACE_MODEL,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_CACHE_PATH,
    ensure_paths_exist,
)

# Load .env early
load_dotenv()
# Ensure local folders exist
ensure_paths_exist()

_logger = logging.getLogger(__name__)

# Internal singletons
_llm_singleton: Optional[Any] = None
_embed_singleton: Optional[Any] = None


# ---- Helpers to import provider SDKs lazily ----
def _import_groq() -> Any:
    try:
        from llama_index.llms.groq import Groq  # type: ignore
        return Groq
    except Exception as exc:
        raise ImportError(
            "Groq LLM client is not available. Install the required package "
            "or switch to HuggingFace in src/config.py."
        ) from exc


def _import_hf_embedding() -> Any:
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # type: ignore
        return HuggingFaceEmbedding
    except Exception as exc:
        raise ImportError(
            "HuggingFace embedding wrapper is not available. Install the required package."
        ) from exc


def _import_hf_llm() -> Any:
    """
    Se você tiver um wrapper específico do HuggingFace (por exemplo HuggingFaceLLM),
    importe e retorne a classe aqui. Se não, deixamos None e usamos resolve_llm.
    """
    try:
        # Exemplo (descomente se usar): from llama_index.llms.huggingface import HuggingFaceLLM; return HuggingFaceLLM
        return None
    except Exception:
        return None


# ---- Public factory functions ----
def initialise_llm() -> Any:
    """
    Initialise and return an LLM client according to LLM_PROVIDER.
    Supported providers: "groq", "huggingface".
    Prefer explicit LlamaIndex LLM wrappers; fallback to resolve_llm.
    """
    provider = (LLM_PROVIDER or "huggingface").lower()

    if provider == "groq":
        api_key = os.getenv(GROQ_API_KEY_ENV)
        if not api_key:
            raise ValueError(f"Missing {GROQ_API_KEY_ENV} in environment.")
        Groq = _import_groq()
        return Groq(api_key=api_key, model=GROQ_MODEL)

    if provider == "huggingface":
        api_key = os.getenv(HUGGINGFACE_API_KEY_ENV)
        if not api_key:
            raise ValueError(f"Missing {HUGGINGFACE_API_KEY_ENV} in environment.")

        # 1) Tentar importar um wrapper explícito do llama_index (vários caminhos possíveis)
        hf_llm_cls = None
        for candidate in (
            "llama_index.llms.huggingface.HuggingFaceLLM",
            "llama_index.llms.huggingface.HuggingFace",
            "llama_index.llms.hf.HuggingFaceLLM",
        ):
            try:
                module_path, cls_name = candidate.rsplit(".", 1)
                mod = __import__(module_path, fromlist=[cls_name])
                hf_llm_cls = getattr(mod, cls_name)
                break
            except Exception:
                hf_llm_cls = None

        if hf_llm_cls is not None:
            # instanciar com os parâmetros mais comuns; ajuste se seu wrapper exigir outros nomes
            try:
                return hf_llm_cls(model_name=HUGGINGFACE_MODEL, api_token=api_key)
            except TypeError:
                # alguns wrappers usam 'model' e 'api_key' em vez de model_name/api_token
                return hf_llm_cls(model=HUGGINGFACE_MODEL, api_key=api_key)

        # 2) Fallback: tentar resolver via resolve_llm (mas validar o retorno)
        cfg = {"provider": "huggingface", "model": HUGGINGFACE_MODEL, "api_key": api_key}
        try:
            _logger.info("Attempting to resolve HF LLM via resolve_llm.")
            llm_obj = resolve_llm(cfg)
            # validação: deve ser um objeto com atributo callback_manager ou método chat/complete
            if isinstance(llm_obj, dict) or not hasattr(llm_obj, "__class__"):
                raise TypeError("resolve_llm returned an unexpected type (dict).")
            return llm_obj
        except Exception as exc:
            _logger.exception("Failed to create/resolve HuggingFace LLM: %s", exc)
            raise RuntimeError(
                "Could not initialise a HuggingFace LLM. "
                "Ensure a compatible llama_index HF wrapper is installed or adjust model_loader."
            ) from exc

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

def get_embedding_model() -> Any:
    """
    Initialise and return the embedding model used for RAG.
    Uses HuggingFaceEmbedding (llama_index wrapper) by default.
    """
    HuggingFaceEmbedding = _import_hf_embedding()
    
    # Nas versões novas, usamos cache_dir em vez de cache_folder
    # E garantimos que o caminho seja uma string
    cache_dir = EMBEDDING_CACHE_PATH.as_posix()
    
    try:
        # Tenta o novo padrão (cache_dir)
        return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME, cache_dir=cache_dir)
    except TypeError:
        # Fallback para o padrão antigo ou sem cache se der erro de argumento
        _logger.warning("Failed to use cache_dir, falling back to default.")
        return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

# ---- Optional convenience singletons ----
def get_llm_singleton() -> Any:
    global _llm_singleton
    if _llm_singleton is None:
        _llm_singleton = initialise_llm()
    return _llm_singleton


def get_embedding_singleton() -> Any:
    global _embed_singleton
    if _embed_singleton is None:
        _embed_singleton = get_embedding_model()
    return _embed_singleton
