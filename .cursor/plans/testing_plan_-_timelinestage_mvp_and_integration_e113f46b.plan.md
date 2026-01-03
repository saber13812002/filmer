---
name: Testing Plan - TimelineStage MVP and Integration
overview: Plan for testing TimelineStage MVP, Legacy Cutter integration, stage integration, and real data testing
todos:
  - id: test_timeline_mvp
    content: Run TimelineStage MVP test - verify timeline.json generation
    status: completed
  - id: test_legacy_cutter
    content: Test legacy cutter with generated timeline.json - verify video generation
    status: completed
    dependencies:
      - test_timeline_mvp
  - id: test_stage_integration
    content: Test integration between stages (ingest -> index -> search -> timeline)
    status: completed
    dependencies:
      - test_timeline_mvp
  - id: test_real_data
    content: Test with real movie and narration SRT files
    status: completed
    dependencies:
      - test_stage_integration
---

# Testing Plan - TimelineStage MVP and Integration

## Test 1: TimelineStage MVP (Simple)

**Goal**: Verify TimelineStage MVP works independently**Steps**:

1. Run TimelineStage MVP with test project
2. Verify timeline.json is generated correctly
3. Check both full and minimal versions are created

**Command**:

```bash
python scripts/run_timeline_mvp.py --project-id test_project
```

**Expected Results**:

- `projects/test_project/outputs/timeline.json` (full version)
- `timeline.json` in root (minimal version, legacy compatible)
- 4 mock segments generated

---

## Test 2: Legacy Cutter Integration

**Goal**: Verify timeline.json works with legacy cutter**Steps**:

1. Update timeline.json with real file paths
2. Run legacy cutter
3. Verify video is generated

**Prerequisites**:

- Real video file: `films/input/3034981-0-FoxandHareSavetheForest-1080.mp4`
- Real narration: `films/narration/imdb123123.m4a`

**Command**:

```bash
python legacy/cut_video.py
```

**Expected Results**:

- Video file generated at output path
- No errors from FFmpeg

---

## Test 3: Stage Integration

**Goal**: Test integration between stages**Steps**:

1. Run ingest stage (validate files)
2. Run index stage (if SRT files available)
3. Run search stage (if index completed)
4. Run timeline stage (using search output)
5. Verify end-to-end flow

**Prerequisites**:

- Movie SRT file in `projects/{project_id}/data/movie.srt`
- Narration SRT file in `projects/{project_id}/data/narration.srt`

**Commands**:

```bash
python scripts/run_stage.py ingest --project-id test_project
python scripts/run_stage.py index --project-id test_project
python scripts/run_stage.py search --project-id test_project
python scripts/run_stage.py timeline --project-id test_project
```

**Expected Results**:

- Each stage completes successfully
- Output files are created in correct locations
- Data flows correctly between stages

---

## Test 4: Real Data Testing

**Goal**: Test with actual movie and narration files**Steps**:

1. Create project with real movie ID
2. Place real SRT files in project data directory
3. Run full pipeline
4. Verify output quality

**Prerequisites**:

- Real movie SRT file
- Real narration SRT file
- Optional: Real video file for reference

**Expected Results**:

- Semantic search finds relevant segments
- Timeline contains meaningful matches
- Video output is coherent

---

## Test Execution Order

1. **Test 1** (TimelineStage MVP) - Can run immediately, no dependencies
2. **Test 2** (Legacy Cutter) - Requires Test 1 completion + real file paths
3. **Test 3** (Stage Integration) - Requires SRT files
4. **Test 4** (Real Data) - Requires all previous tests + real data

---

## Success Criteria

- ✅ TimelineStage MVP generates valid timeline.json
- ✅ Legacy cutter accepts and processes timeline.json
- ✅ Stages can run independently and in sequence
- ✅ Real data produces meaningful results
- ✅ No errors in any stage execution
- ✅ Output files are in correct locations
- ✅ Timeline JSON is backward compatible

---

## Notes