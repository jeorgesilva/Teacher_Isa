"""
RAG (Retrieval-Augmented Generation) module for Teacher Isa AI.
Manages ChromaDB vector store with Sentence-Transformers embeddings.
"""

import logging
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Retrieval-Augmented Generation system using ChromaDB and Sentence-Transformers.
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG system with persistent ChromaDB storage.
        
        Args:
            embedding_model: Sentence-Transformers model name for embeddings
        """
        try:
            logger.info(f"Initializing Sentence-Transformers with model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            
            logger.info("Initializing ChromaDB PersistentClient")
            self.client = chromadb.PersistentClient(path="data/knowledge_base")
            
            self.collection = self.client.get_or_create_collection(
                name="grammar_reference",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts to embed and store
            metadata: Optional list of metadata dicts (one per document)
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        try:
            logger.info(f"Adding {len(documents)} documents to ChromaDB")
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Prepare metadata
            if metadata is None:
                metadata = [{"source": "unknown"} for _ in documents]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadata,
                ids=ids or [f"doc_{i}" for i in range(len(documents))]
            )
            
            logger.info(f"✅ {len(documents)} documents added successfully")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search_docs(self, query: str, top_k: int = 3) -> Optional[str]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            Formatted string with relevant documents, or None if no results
        """
        try:
            logger.info(f"Searching for documents matching query: {query[:50]}...")
            
            # Encode query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            if not results or not results.get("documents") or not results["documents"][0]:
                logger.info("No documents found for query")
                return None
            
            documents = results["documents"][0]
            distances = results.get("distances", [[]])[0] if results.get("distances") else []
            
            # Build context string
            context_parts = []
            for i, doc in enumerate(documents):
                distance = distances[i] if i < len(distances) else 0
                relevance = max(0, 1 - distance)  # Convert distance to relevance
                context_parts.append(f"• {doc}")
            
            context = "\n".join(context_parts)
            logger.info(f"✅ Found {len(documents)} relevant documents")
            
            return context
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return None
    
    def delete_all_documents(self) -> None:
        """Delete all documents from the collection."""
        try:
            logger.info("Deleting all documents from collection")
            self.client.delete_collection(name="grammar_reference")
            self.collection = self.client.get_or_create_collection(
                name="grammar_reference",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("✅ All documents deleted")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise


# Global RAG instance
try:
    rag_system = RAGSystem()
except Exception as e:
    logger.error(f"Failed to initialize global RAG system: {str(e)}")
    rag_system = None
