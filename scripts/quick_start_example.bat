@echo off
REM Quick start script for example project (Windows)

set PROJECT_ID=imdb123123
set MOVIE_SRT=films\input\3034981-0-FoxandHareSavetheForest-1080.srt
set NARRATION_SRT=films\narration\imdb123123.srt
set MOVIE_VIDEO=films\input\3034981-0-FoxandHareSavetheForest-1080.mp4

REM Step 1: Get movie duration (you need to replace this with actual duration)
set MOVIE_DURATION=3600

echo === Creating Project ===
python scripts\create_project.py ^
  --project-id "%PROJECT_ID%" ^
  --movie-duration %MOVIE_DURATION% ^
  --movie-language en ^
  --movie-srt "%MOVIE_SRT%" ^
  --narration-srt "%NARRATION_SRT%" ^
  --movie-video "%MOVIE_VIDEO%" ^
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 ^
  --similarity-threshold 0.75 ^
  --copyright-min-gap 30.0

echo.
echo === Running Pipeline ===
python scripts\run_stage.py ingest --project-id "%PROJECT_ID%"
python scripts\run_stage.py index --project-id "%PROJECT_ID%"
python scripts\run_stage.py search --project-id "%PROJECT_ID%"
python scripts\run_stage.py timeline --project-id "%PROJECT_ID%"

echo.
echo === Converting to Legacy Format ===
python scripts\convert_timeline_to_legacy.py --project-id "%PROJECT_ID%"

echo.
echo === [OK] Complete! ===
echo Timeline: projects\%PROJECT_ID%\outputs\timeline.json
echo Legacy: projects\%PROJECT_ID%\outputs\timeline_legacy.json

