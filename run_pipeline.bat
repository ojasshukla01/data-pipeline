@echo off
REM Simple script to run the gaming data pipeline (Windows)

echo 🎮 Gaming Data Pipeline
echo ========================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Virtual environment not activated!
    echo Please activate it first:
    echo   venv\Scripts\activate
    exit /b 1
)

REM Run ETL pipeline
echo.
echo 📥 Running ETL Pipeline...
python src/etl/run_pipeline.py

REM Generate forecasts
echo.
echo 🔮 Generating Forecasts...
python src/ml/generate_forecasts.py

echo.
echo ✅ Pipeline Complete!
echo.
echo To view the dashboard, run:
echo   streamlit run dashboard/app.py
