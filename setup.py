"""
Setup script for the gaming data pipeline
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_project():
    """Set up the project"""
    print("=" * 50)
    print("Gaming Data Pipeline Setup")
    print("=" * 50)
    
    # Create necessary directories
    directories = [
        "data/raw",
        "data/processed",
        "data/models",
        "logs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Check for .env file
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("\n⚠ .env file not found!")
            print("Please copy .env.example to .env and configure it:")
            print("  cp .env.example .env")
        else:
            print("\n⚠ .env.example not found!")
    else:
        print("\n✓ .env file found")
    
    # Setup database
    print("\nSetting up database...")
    try:
        from src.database.setup_db import setup_database
        setup_database()
        print("✓ Database setup complete")
    except Exception as e:
        print(f"⚠ Database setup error: {str(e)}")
        print("Make sure your database configuration is correct in .env")
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Configure API keys (optional): python setup_api_keys.py")
    print("2. Run ETL pipeline: python src/etl/run_pipeline.py")
    print("3. Generate forecasts: python src/ml/generate_forecasts.py")
    print("4. Start dashboard: python -m streamlit run dashboard/app.py")


if __name__ == "__main__":
    setup_project()
