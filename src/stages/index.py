"""Stage 2: Movie subtitle indexing"""

from pathlib import Path
from typing import Dict, Any, Optional
import json

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.stage_outputs import IndexOutput
from src.utils.srt_parser import parse_srt_file
from src.core.chunking import chunk_srt_entries
from src.adapters.chromadb_adapter import ChromaDBAdapter
from src.adapters.embedding_adapter import EmbeddingAdapter


class IndexStage(BaseStage):
    """Index stage: chunks and indexes movie subtitles in ChromaDB"""
    
    def __init__(self, project_root: Optional[Path] = None, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__(project_root)
        self.embedding_model = embedding_model
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute index stage"""
        # Load ingest output
        ingest_data = self.load_input(project_id)
        
        movie_srt_path = ingest_data.get("movie_srt_path")
        if not movie_srt_path:
            raise StageExecutionError("Movie SRT path not found in ingest output")
        
        # Parse SRT file
        srt_entries = parse_srt_file(Path(movie_srt_path))
        
        # Use 3-sentence chunking strategy (prev + current + next)
        from src.core.chunking import chunk_srt_entries_3_sentence
        chunks = chunk_srt_entries_3_sentence(srt_entries)
        
        # Initialize adapters
        index_path = self.get_project_path(project_id) / "index" / "chroma"
        chroma_adapter = ChromaDBAdapter(persist_directory=index_path)
        
        cache_dir = self.get_project_path(project_id) / "index" / "embeddings_cache"
        embedding_adapter = EmbeddingAdapter(
            model_name=self.embedding_model,
            cache_dir=cache_dir
        )
        
        # Prepare data for ChromaDB
        collection_name = f"movie_subtitles_{project_id}"
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = embedding_adapter.embed_texts(chunk_texts)
        
        metadatas = []
        ids = []
        for i, chunk in enumerate(chunks):
            # Calculate center time (middle entry time)
            center_entry = chunk.entries[len(chunk.entries) // 2] if chunk.entries else None
            center_time = center_entry.start_time if center_entry else chunk.start_time
            
            metadatas.append({
                "start_time": chunk.start_time,
                "end_time": chunk.end_time,
                "center_time": center_time,
                "duration": chunk.duration,
                "word_count": chunk.word_count,
                "sentence_index": i,  # Index of center sentence
                "sentence_count": len(chunk.entries)  # Number of sentences in chunk (1-3)
            })
            ids.append(f"movie_{i:06d}")
        
        # Add to ChromaDB
        chroma_adapter.add_chunks(
            collection_name=collection_name,
            chunks=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        total_duration = sum(chunk.duration for chunk in chunks)
        
        output = IndexOutput(
            collection_name=collection_name,
            chunks_indexed=len(chunks),
            total_duration=total_duration
        )
        
        return output.model_dump()
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load ingest stage output"""
        ingest_output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        
        if not ingest_output_path.exists():
            raise StageExecutionError(f"Ingest output not found: {ingest_output_path}")
        
        with open(ingest_output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save index output"""
        output_path = self.get_outputs_path(project_id) / "index_output.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate index configuration"""
        return True

