#!/bin/bash
# Simple script to run the gaming data pipeline

echo "🎮 Gaming Data Pipeline"
echo "========================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please activate it first:"
    echo "  source venv/bin/activate  # Mac/Linux"
    echo "  venv\Scripts\activate     # Windows"
    exit 1
fi

# Run ETL pipeline
echo ""
echo "📥 Running ETL Pipeline..."
python src/etl/run_pipeline.py

# Generate forecasts
echo ""
echo "🔮 Generating Forecasts..."
python src/ml/generate_forecasts.py

echo ""
echo "✅ Pipeline Complete!"
echo ""
echo "To view the dashboard, run:"
echo "  streamlit run dashboard/app.py"
