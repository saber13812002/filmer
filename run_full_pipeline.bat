@echo off
REM Complete pipeline execution script for Windows

REM Configuration
set PROJECT_ID=%1
if "%PROJECT_ID%"=="" set PROJECT_ID=tt0133093

set EMBEDDING_MODEL=%2
if "%EMBEDDING_MODEL%"=="" set EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

echo ==========================================
echo Running Complete Pipeline
echo ==========================================
echo Project ID: %PROJECT_ID%
echo Embedding Model: %EMBEDDING_MODEL%
echo ==========================================
echo.

REM Step 1: Ingest
echo === Step 1: Ingest ===
python scripts\run_stage.py ingest --project-id "%PROJECT_ID%"
if errorlevel 1 (
    echo [ERROR] Ingest stage failed
    exit /b 1
)
echo.

REM Step 2: Index
echo === Step 2: Index ===
python scripts\run_stage.py index --project-id "%PROJECT_ID%" --embedding-model "%EMBEDDING_MODEL%"
if errorlevel 1 (
    echo [ERROR] Index stage failed
    exit /b 1
)
echo.

REM Step 3: Search
echo === Step 3: Search ===
python scripts\run_stage.py search --project-id "%PROJECT_ID%" --embedding-model "%EMBEDDING_MODEL%"
if errorlevel 1 (
    echo [ERROR] Search stage failed
    exit /b 1
)
echo.

REM Step 4: Timeline
echo === Step 4: Timeline ===
python scripts\run_stage.py timeline --project-id "%PROJECT_ID%"
if errorlevel 1 (
    echo [ERROR] Timeline stage failed
    exit /b 1
)
echo.

echo ==========================================
echo [OK] Pipeline completed successfully!
echo ==========================================
echo Timeline output: projects\%PROJECT_ID%\outputs\timeline.json
echo.

