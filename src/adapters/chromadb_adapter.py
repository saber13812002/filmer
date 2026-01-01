"""ChromaDB adapter for vector database operations"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings


class ChromaDBAdapter:
    """Adapter for ChromaDB operations"""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize ChromaDB adapter
        
        Args:
            persist_directory: Optional directory for persistent storage
        """
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=str(persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.client = chromadb.Client(settings=Settings(anonymized_telemetry=False))
    
    def get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """Get or create a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB Collection object
        """
        return self.client.get_or_create_collection(name=collection_name)
    
    def add_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add chunks to collection
        
        Args:
            collection_name: Name of the collection
            chunks: List of chunk text content
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs
        """
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query collection for similar chunks
        
        Args:
            collection_name: Name of the collection
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
        return results
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
        except ValueError:
            # Collection doesn't exist, ignore
            pass

