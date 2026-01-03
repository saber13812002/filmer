"""Test script for ChromaDB verification"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.adapters.chromadb_adapter import ChromaDBAdapter


def main():
    print("=== Testing ChromaDB ===\n")
    
    # Initialize adapter
    test_dir = Path("test_chroma")
    print(f"ChromaDB directory: {test_dir}")
    
    adapter = ChromaDBAdapter(persist_directory=test_dir)
    
    # Create collection
    collection_name = "test_collection"
    print(f"\nCreating collection: {collection_name}")
    collection = adapter.get_or_create_collection(collection_name)
    
    # Add test data
    print("Adding test data...")
    adapter.add_chunks(
        collection_name=collection_name,
        chunks=["This is a test document about movies"],
        embeddings=[[0.1] * 384],  # 384 = dimension of all-MiniLM-L6-v2
        metadatas=[{"test": True, "type": "movie"}],
        ids=["test_1"]
    )
    
    # Query
    print("Querying collection...")
    results = adapter.query(
        collection_name=collection_name,
        query_embeddings=[[0.1] * 384],
        n_results=1
    )
    
    # Check results
    result_ids = results.get('ids', [[]])[0]
    result_count = len(result_ids)
    
    print(f"\n[RESULTS]")
    print(f"  Collection created: {collection is not None}")
    print(f"  Query results: {result_count} result(s)")
    print(f"  Result ID: {result_ids[0] if result_ids else 'None'}")
    
    # Validation
    if collection is not None and result_count > 0:
        print("\n[OK] ChromaDB is working correctly!")
        
        # Cleanup
        print("\nCleaning up test data...")
        adapter.delete_collection(collection_name)
        return 0
    else:
        print("\n[ERROR] ChromaDB test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

