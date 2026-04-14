"""
src/engine.py

RAG orchestration and chat engine assembly.

Provides:
- _create_new_vector_store(embed_model)
- get_vector_store(embed_model)
- get_chat_engine(llm, embed_model)
- main_chat_loop() for local REPL testing
- build_index() helper to force reindexing from data/
"""

from __future__ import annotations

import logging
import shutil
from typing import Any

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_PATH,
    LLM_SYSTEM_PROMPT,
    SIMILARITY_TOP_K,
    VECTOR_STORE_PATH,
    CHAT_MEMORY_TOKEN_LIMIT,
    REBUILD_INDEX_ON_START,
)

# Imports específicos para a versão instalada do llama_index
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.indices import load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.memory import ChatMemoryBuffer

# Logging (only configure if no handlers exist to avoid reconfiguring in other modules)
logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)


def _create_new_vector_store(embed_model: Any) -> VectorStoreIndex:
    """
    Create a new VectorStoreIndex from files in DATA_PATH.
    This reads documents, splits into chunks, embeds them and persists the index.
    """
    logger.info("Creating new vector store from files in %s", DATA_PATH)
    documents = SimpleDirectoryReader(input_dir=DATA_PATH).load_data()
    if not documents:
        raise ValueError(f"No documents found in {DATA_PATH}. Add files before indexing.")

    text_splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[text_splitter],
        embed_model=embed_model,
    )

    persist_dir = VECTOR_STORE_PATH.as_posix()
    index.storage_context.persist(persist_dir=persist_dir)
    logger.info("Vector store created and persisted to %s", persist_dir)
    return index


def get_vector_store(embed_model: Any) -> VectorStoreIndex:
    """
    Load an existing vector store from disk if present; otherwise create a new one.
    If loading fails (corrupt index), attempt to rebuild.
    """
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

    if any(VECTOR_STORE_PATH.iterdir()):
        logger.info("Attempting to load existing vector store from %s", VECTOR_STORE_PATH)
        try:
            storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_PATH.as_posix())
            return load_index_from_storage(storage_context, embed_model=embed_model)
        except Exception:
            logger.exception("Failed to load existing vector store; rebuilding from data/...")
            # fallthrough to create new index

    # Otherwise create a new index
    return _create_new_vector_store(embed_model)


def get_chat_engine(llm: Any, embed_model: Any):
    """
    Assemble and return a chat engine built from the vector index.
    The returned object implements a chat interface (chat_repl / chat).
    """
    logger.info("Initialising chat engine (RAG orchestrator)...")
    vector_index = get_vector_store(embed_model)

    memory = ChatMemoryBuffer.from_defaults(token_limit=CHAT_MEMORY_TOKEN_LIMIT)

    chat_engine = vector_index.as_chat_engine(
        memory=memory,
        llm=llm,
        system_prompt=LLM_SYSTEM_PROMPT,
        similarity_top_k=SIMILARITY_TOP_K,
    )
    logger.info("Chat engine initialised.")
    return chat_engine


def build_index(force: bool = False) -> None:
    """
    Convenience function to (re)build the vector store.
    If force is False and an index exists, it will be left intact.
    """
    # lazy import to avoid import circularity
    from src.model_loader import get_embedding_singleton

    embed_model = get_embedding_singleton()

    if force:
        logger.info("Forcing index rebuild...")
        if VECTOR_STORE_PATH.exists():
            try:
                shutil.rmtree(VECTOR_STORE_PATH)
                logger.info("Removed existing vector store at %s", VECTOR_STORE_PATH)
            except Exception as exc:
                logger.warning("Failed to remove %s: %s", VECTOR_STORE_PATH, exc)
        VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

    # Create or load index (this will create if missing)
    _ = get_vector_store(embed_model)
    logger.info("Index build complete.")


def main_chat_loop() -> None:
    """
    Local REPL for testing the RAG chatbot.
    Initializes singletons lazily and starts chat_repl().
    """
    # lazy imports to avoid import circularity at module import time
    from src.model_loader import get_embedding_singleton, get_llm_singleton

    logger.info("Starting local RAG chat loop...")
    llm = get_llm_singleton()
    embed_model = get_embedding_singleton()

    if REBUILD_INDEX_ON_START:
        logger.info("REBUILD_INDEX_ON_START is enabled; rebuilding index.")
        build_index(force=True)

    chat_engine = get_chat_engine(llm=llm, embed_model=embed_model)
    try:
        chat_engine.chat_repl()
    except KeyboardInterrupt:
        logger.info("Chat loop interrupted by user. Exiting.")


if __name__ == "__main__":
    main_chat_loop()
