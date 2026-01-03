"""Stage 3: Narration search"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.stage_outputs import SearchOutput, SearchMatch
from src.utils.srt_parser import parse_srt_file, SRTEntry
from src.adapters.chromadb_adapter import ChromaDBAdapter
from src.adapters.embedding_adapter import EmbeddingAdapter


class SearchStage(BaseStage):
    """Search stage: semantic search for narration in movie subtitles"""
    
    def __init__(self, project_root: Optional[Path] = None, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__(project_root)
        self.embedding_model = embedding_model
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute search stage"""
        # Load ingest and index outputs
        ingest_data = self.load_input(project_id)
        
        # Get multiple narration SRT files
        narration_srt_files = ingest_data.get("narration_srt_files", [])
        if not narration_srt_files:
            # Fallback to single file for backward compatibility
            narration_srt_path = ingest_data.get("narration_srt_path")
            if narration_srt_path:
                narration_srt_files = [narration_srt_path]
        
        if not narration_srt_files:
            raise StageExecutionError("No narration SRT files found in ingest output")
        
        # Initialize adapters (reuse for all narration files)
        index_path = self.get_project_path(project_id) / "index" / "chroma"
        chroma_adapter = ChromaDBAdapter(persist_directory=index_path)
        
        cache_dir = self.get_project_path(project_id) / "index" / "embeddings_cache"
        embedding_adapter = EmbeddingAdapter(
            model_name=self.embedding_model,
            cache_dir=cache_dir
        )
        
        # Get collection name from index output
        index_output_path = self.get_outputs_path(project_id) / "index_output.json"
        with open(index_output_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        collection_name = index_data["collection_name"]
        
        # Process each narration file
        all_matches = []
        
        for narration_file_idx, narration_srt_path in enumerate(narration_srt_files):
            # Parse narration SRT
            narration_entries = parse_srt_file(Path(narration_srt_path))
            
            # Use 3-sentence window for each entry (prev + current + next)
            from src.core.chunking import chunk_srt_entries_3_sentence
            narration_chunks = chunk_srt_entries_3_sentence(narration_entries)
            
            # Search for each 3-sentence chunk
            for chunk_idx, chunk in enumerate(narration_chunks):
                # Get center entry for narration time
                center_entry = chunk.entries[len(chunk.entries) // 2] if chunk.entries else None
                narration_time = center_entry.start_time if center_entry else chunk.start_time
                
                # Embed query chunk
                query_embedding = embedding_adapter.embed_text(chunk.text)
                
                # Query ChromaDB (get top 3 results for fallback options)
                results = chroma_adapter.query(
                    collection_name=collection_name,
                    query_embeddings=[query_embedding],
                    n_results=3
                )
                
                # Process results
                if results.get("ids") and len(results["ids"][0]) > 0:
                    for i, (id_val, metadata, distance) in enumerate(zip(
                        results["ids"][0],
                        results["metadatas"][0],
                        results["distances"][0]
                    )):
                        similarity_score = 1.0 - distance  # Convert distance to similarity
                        
                        match = SearchMatch(
                            segment_id=id_val,
                            start_time=metadata["start_time"],
                            end_time=metadata["end_time"],
                            similarity_score=similarity_score,
                            narration_text=chunk.text
                        )
                        # Add narration file identifier
                        match_dict = match.model_dump()
                        match_dict["narration_file_id"] = f"narration_{narration_file_idx}"
                        match_dict["narration_time"] = narration_time
                        match_dict["chunk_index"] = chunk_idx
                        match_dict["result_rank"] = i  # 0=best, 1=second, 2=third
                        
                        all_matches.append(match_dict)
        
        output = SearchOutput(matches=all_matches)
        return output.model_dump()
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load ingest output"""
        ingest_output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        
        if not ingest_output_path.exists():
            raise StageExecutionError(f"Ingest output not found: {ingest_output_path}")
        
        with open(ingest_output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save search output"""
        output_path = self.get_outputs_path(project_id) / "search_output.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate search configuration"""
        return True

