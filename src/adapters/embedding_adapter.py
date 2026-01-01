"""Embedding model adapter for text embeddings"""

from typing import List, Optional
from pathlib import Path
import hashlib
import pickle


class EmbeddingAdapter:
    """Adapter for embedding model operations"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", cache_dir: Optional[Path] = None):
        """Initialize embedding adapter
        
        Args:
            model_name: Name of the embedding model
            cache_dir: Optional directory for caching embeddings
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model = None
        self._cache = {}
    
    def _load_model(self):
        """Lazy load embedding model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for a single text
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector as list of floats
        """
        if use_cache and self.cache_dir:
            cache_key = self._get_cache_key(text)
            cached = self._load_from_cache(cache_key)
            if cached is not None:
                return cached
        
        model = self._load_model()
        embedding = model.encode(text, convert_to_numpy=True).tolist()
        
        if use_cache and self.cache_dir:
            self._save_to_cache(cache_key, embedding)
        
        return embedding
    
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of embedding vectors
        """
        if use_cache and self.cache_dir:
            # Check cache for all texts
            cached_embeddings = []
            texts_to_embed = []
            indices_to_embed = []
            
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                cached = self._load_from_cache(cache_key)
                if cached is not None:
                    cached_embeddings.append((i, cached))
                else:
                    texts_to_embed.append(text)
                    indices_to_embed.append(i)
            
            # Embed texts not in cache
            if texts_to_embed:
                model = self._load_model()
                new_embeddings = model.encode(texts_to_embed, convert_to_numpy=True).tolist()
                
                # Save to cache
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    cache_key = self._get_cache_key(text)
                    self._save_to_cache(cache_key, embedding)
            
            # Combine cached and new embeddings
            all_embeddings = [None] * len(texts)
            for i, emb in cached_embeddings:
                all_embeddings[i] = emb
            for i, emb in zip(indices_to_embed, new_embeddings):
                all_embeddings[i] = emb
            
            return all_embeddings
        else:
            model = self._load_model()
            return model.encode(texts, convert_to_numpy=True).tolist()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(f"{self.model_name}:{text}".encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Load embedding from cache"""
        if not self.cache_dir:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float]) -> None:
        """Save embedding to cache"""
        if not self.cache_dir:
            return
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception:
            pass  # Ignore cache write errors

