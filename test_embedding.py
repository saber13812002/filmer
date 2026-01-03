"""Test script for embedding model verification"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.adapters.embedding_adapter import EmbeddingAdapter
import numpy as np


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    print("=== Testing Embedding Model ===\n")
    
    # Initialize adapter
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading model: {model_name}")
    
    adapter = EmbeddingAdapter(
        model_name=model_name,
        cache_dir=Path("test_cache")
    )
    
    # Test texts
    text1 = "This is a test sentence about movies"
    text2 = "This is another test sentence about films"
    text3 = "Completely different topic about cooking recipes"
    
    print("\nGenerating embeddings...")
    emb1 = adapter.embed_text(text1)
    emb2 = adapter.embed_text(text2)
    emb3 = adapter.embed_text(text3)
    
    # Check model
    print(f"\n[INFO] Embedding dimension: {len(emb1)}")
    print(f"[INFO] Model loaded: {adapter._model is not None}")
    
    # Calculate similarities
    sim_12 = cosine_similarity(emb1, emb2)
    sim_13 = cosine_similarity(emb1, emb3)
    
    print(f"\n[RESULTS]")
    print(f"  Similarity 1-2 (movies/films - should be high): {sim_12:.3f}")
    print(f"  Similarity 1-3 (movies/cooking - should be low): {sim_13:.3f}")
    
    # Validation
    if sim_12 > 0.7 and sim_13 < 0.5:
        print("\n[OK] Embedding model is working correctly!")
        return 0
    else:
        print("\n[WARNING] Embedding model may not be working correctly")
        print("  Expected: sim_12 > 0.7, sim_13 < 0.5")
        return 1


if __name__ == "__main__":
    sys.exit(main())

