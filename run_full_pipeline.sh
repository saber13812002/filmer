#!/bin/bash
# Complete pipeline execution script

# Configuration
PROJECT_ID="${1:-tt0133093}"
EMBEDDING_MODEL="${2:-sentence-transformers/all-MiniLM-L6-v2}"

echo "=========================================="
echo "Running Complete Pipeline"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Embedding Model: $EMBEDDING_MODEL"
echo "=========================================="
echo ""

# Step 1: Ingest
echo "=== Step 1: Ingest ==="
python scripts/run_stage.py ingest --project-id "$PROJECT_ID" || {
    echo "[ERROR] Ingest stage failed"
    exit 1
}
echo ""

# Step 2: Index
echo "=== Step 2: Index ==="
python scripts/run_stage.py index \
  --project-id "$PROJECT_ID" \
  --embedding-model "$EMBEDDING_MODEL" || {
    echo "[ERROR] Index stage failed"
    exit 1
}
echo ""

# Step 3: Search
echo "=== Step 3: Search ==="
python scripts/run_stage.py search \
  --project-id "$PROJECT_ID" \
  --embedding-model "$EMBEDDING_MODEL" || {
    echo "[ERROR] Search stage failed"
    exit 1
}
echo ""

# Step 4: Timeline
echo "=== Step 4: Timeline ==="
python scripts/run_stage.py timeline --project-id "$PROJECT_ID" || {
    echo "[ERROR] Timeline stage failed"
    exit 1
}
echo ""

echo "=========================================="
echo "[OK] Pipeline completed successfully!"
echo "=========================================="
echo "Timeline output: projects/$PROJECT_ID/outputs/timeline.json"
echo ""

