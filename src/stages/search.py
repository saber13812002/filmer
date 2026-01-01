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
        
        narration_srt_path = ingest_data.get("narration_srt_path")
        if not narration_srt_path:
            raise StageExecutionError("Narration SRT path not found in ingest output")
        
        # Parse narration SRT
        narration_entries = parse_srt_file(Path(narration_srt_path))
        
        # Group narration entries (sliding window: 1-2 sentences)
        query_groups = self._create_sliding_window(narration_entries)
        
        # Initialize adapters
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
        
        # Search for each query group
        all_matches = []
        for group_text, group_entries in query_groups:
            # Embed query
            query_embedding = embedding_adapter.embed_text(group_text)
            
            # Query ChromaDB
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
                        narration_text=group_text
                    )
                    all_matches.append(match)
        
        output = SearchOutput(matches=[m.model_dump() for m in all_matches])
        return output.model_dump()
    
    def _create_sliding_window(self, entries: List[SRTEntry], window_size: int = 2) -> List[tuple[str, List[SRTEntry]]]:
        """Create sliding window groups from narration entries"""
        groups = []
        
        for i in range(len(entries) - window_size + 1):
            window_entries = entries[i:i+window_size]
            group_text = ' '.join(entry.text for entry in window_entries)
            groups.append((group_text, window_entries))
        
        return groups
    
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

