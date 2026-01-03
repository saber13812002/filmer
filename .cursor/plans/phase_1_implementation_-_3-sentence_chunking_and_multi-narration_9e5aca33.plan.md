---
name: Phase 1 Implementation - 3-Sentence Chunking and Multi-Narration
overview: Implement Phase 1 with 3-sentence chunking strategy (previous+current+next), support for multiple narration SRT files, enhanced project model with movie metadata, and copyright-compliant overlap prevention.
todos:
  - id: update_project_model
    content: Extend ProjectConfig model with movie_duration, movie_language, movie_video_path (nullable), and narration_srt_files (list)
    status: completed
  - id: implement_3sentence_chunking
    content: Implement chunk_srt_entries_3_sentence() function - creates chunks with previous+current+next sentences
    status: completed
  - id: update_index_stage
    content: Modify index stage to use 3-sentence chunking strategy and store enhanced metadata
    status: completed
    dependencies:
      - implement_3sentence_chunking
  - id: update_search_stage
    content: Modify search stage to support multiple narration SRT files and use 3-sentence window for queries
    status: completed
    dependencies:
      - implement_3sentence_chunking
  - id: implement_copyright_compliance
    content: Implement prevent_consecutive_segments() function with min_time_gap logic for copyright compliance
    status: completed
  - id: update_timeline_builder
    content: Update timeline builder to support 3-5 second intervals and integrate copyright compliance
    status: completed
    dependencies:
      - implement_copyright_compliance
  - id: update_ingest_stage
    content: Modify ingest stage to accept and validate multiple narration SRT files
    status: completed
    dependencies:
      - update_project_model
  - id: create_project_tool
    content: Create CLI tool for project creation with all required fields and file uploads
    status: completed
    dependencies:
      - update_project_model
      - update_ingest_stage
---

# Phase 1 Implementation - 3-Sentence Chunking and Multi-Narration Support

## Overview

This phase implements the core value proposition: processing movie SRT (2 hours) and critique narration SRT files (10-20 minutes each, multiple files) using a 3-sentence chunking strategy with copyright-compliant segment selection.

## Key Requirements

1. **Project Definition**: Enhanced project model with movie metadata (IMDb ID, duration, language)
2. **3-Sentence Chunking**: Previous + Current + Next sentence strategy for both movie and narration
3. **Multiple Narration Files**: Support for multiple critique SRT files per project
4. **Copyright Compliance**: Prevent consecutive segments from same time period
5. **Output**: JSON with segments for every 3-5 seconds of narration

## Changes Required

### 1. Enhanced Project Model

**File**: `src/contracts/models/project.py`Add new fields to `ProjectConfig`:

- `movie_duration`: float (required) - Movie duration in seconds
- `movie_language`: str (required) - Original language (e.g., "en", "fa")
- `movie_video_path`: Optional[str] - Path to video file (nullable)
- `narration_srt_files`: List[str] - Multiple narration SRT file paths

**New Schema**: `src/contracts/schemas/project.schema.json` updated

### 2. New Chunking Strategy: 3-Sentence Window

**File**: `src/core/chunking.py`Add new function:

```python
def chunk_srt_entries_3_sentence(entries: List[SRTEntry]) -> List[Chunk]:
    """Chunk SRT entries using 3-sentence window (prev + current + next)
    
    For each entry, creates a chunk containing:
                - Previous entry (if exists)
                - Current entry
                - Next entry (if exists)
    
    This provides better context for semantic matching.
    """
```

**Strategy**:

- For movie SRT: Each entry becomes a chunk with prev+current+next
- For narration SRT: Same strategy for search queries
- Store in ChromaDB with time metadata

### 3. Enhanced Index Stage

**File**: `src/stages/index.py`Modify to:

- Use 3-sentence chunking for movie SRT
- Store each chunk with metadata:
- `start_time`: First entry start
- `end_time`: Last entry end
- `center_time`: Current entry time (for reference)
- `sentence_index`: Index of center sentence

### 4. Enhanced Search Stage

**File**: `src/stages/search.py`Modify to:

- Support multiple narration SRT files
- Process each narration file separately
- Use 3-sentence window for each narration entry
- Query ChromaDB for each 3-sentence chunk
- Return matches with narration file identifier

### 5. Copyright-Compliant Overlap Prevention

**File**: `src/core/filtering.py`Add new function:

```python
def prevent_consecutive_segments(
    matches: List[Match],
    min_time_gap: float = 30.0
) -> List[Match]:
    """Prevent consecutive segments from same time period
    
    Ensures segments are distributed across different parts of the movie
    to comply with copyright requirements.
    
    Args:
        matches: List of matches sorted by narration time
        min_time_gap: Minimum time gap between consecutive segments in seconds
        
    Returns:
        Filtered list with distributed segments
    """
```

**Logic**:

- Sort matches by narration time
- For each match, check if previous match is too close in movie time
- If too close, select second-best match that has sufficient time gap
- Ensure segments come from different parts of the movie

### 6. Timeline Generation for 3-5 Second Intervals

**File**: `src/core/timeline_builder.py`Add function:

```python
def build_timeline_for_narration_intervals(
    narration_entries: List[SRTEntry],
    matches: Dict[int, Match],  # Map narration entry index to match
    interval_seconds: float = 4.0
) -> Timeline:
    """Build timeline with segments for every 3-5 seconds of narration
    
    Creates segments that align with narration timing while ensuring
    movie segments are distributed (copyright compliance).
    """
```



### 7. Enhanced Ingest Stage

**File**: `src/stages/ingest.py`Modify to:

- Accept multiple narration SRT files
- Validate all files exist
- Return list of narration file paths

### 8. Project Creation API/CLI

**New File**: `scripts/create_project.py`CLI tool to create new project:

```bash
python scripts/create_project.py \
  --project-id tt0133093 \
  --movie-duration 7200 \
  --movie-language en \
  --movie-srt path/to/movie.srt \
  --narration-srt path/to/narration1.srt \
  --narration-srt path/to/narration2.srt \
  [--movie-video path/to/movie.mp4]
```



## Implementation Steps

### Step 1: Update Project Model

- Extend `ProjectConfig` with new fields
- Update JSON schema
- Add validation

### Step 2: Implement 3-Sentence Chunking

- Add `chunk_srt_entries_3_sentence()` function
- Test with sample SRT data
- Ensure backward compatibility with existing chunking

### Step 3: Update Index Stage

- Modify to use 3-sentence chunking
- Update ChromaDB metadata structure
- Test indexing with sample movie SRT

### Step 4: Update Search Stage

- Support multiple narration files
- Use 3-sentence window for queries
- Return matches with narration file context

### Step 5: Implement Copyright Compliance

- Add `prevent_consecutive_segments()` function
- Integrate into timeline generation
- Test with overlapping matches

### Step 6: Update Timeline Builder

- Support 3-5 second interval generation
- Integrate copyright compliance
- Test end-to-end

### Step 7: Update Ingest Stage

- Support multiple narration files
- Validate all inputs

### Step 8: Create Project Creation Tool

- CLI script for project creation
- Validate all inputs
- Create project structure

## Data Flow

```javascript
1. Create Project
            - Define: IMDb ID, duration, language
            - Upload: Movie SRT (required)
            - Upload: Narration SRT files (multiple, required)
            - Upload: Movie video (optional)

2. Index Movie SRT
            - Parse movie SRT
            - Create 3-sentence chunks (prev+current+next)
            - Generate embeddings
            - Store in ChromaDB with time metadata

3. Search Narration
            - For each narration SRT file:
                    - Parse narration SRT
                    - Create 3-sentence chunks
                    - Generate embeddings
                    - Query ChromaDB
                    - Get top matches

4. Generate Timeline
            - For each 3-5 seconds of narration:
                    - Select best match from movie
                    - Apply copyright compliance (prevent consecutive)
                    - If consecutive, use second-best with time gap
            - Generate timeline.json

5. Render Video
            - Use timeline.json with FFmpeg
            - Produce final video
```



## Copyright Compliance Rules

1. **Time Gap Requirement**: Minimum 30 seconds between consecutive segments in movie time
2. **Distribution**: Segments should be distributed across different parts of movie
3. **Fallback**: If best match violates rules, use second-best match
4. **Priority**: Copyright compliance > similarity score

## Testing Strategy

1. **Unit Tests**: 3-sentence chunking function
2. **Integration Tests**: Index + Search with 3-sentence chunks
3. **Copyright Tests**: Verify no consecutive segments
4. **End-to-End**: Full pipeline with real data

## Backward Compatibility

- Keep existing 10-20 second chunking as option
- Allow configuration of chunking strategy