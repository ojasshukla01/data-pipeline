# Deployment Guide

## Local Development Setup

### 1. Prerequisites
- Python 3.9 or higher
- Git
- (Optional) PostgreSQL or use DuckDB

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd data-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
# For DuckDB (no setup needed):
USE_DUCKDB=true

# For PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/gaming_pipeline
```

### 4. Database Setup

```bash
# Setup database schema
python src/database/setup_db.py
```

### 5. Run ETL Pipeline

```bash
# Run pipeline manually
python src/etl/run_pipeline.py
```

### 6. Generate Forecasts

```bash
# Generate forecasts
python src/ml/generate_forecasts.py
```

### 7. Start Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard/app.py
```

### 8. Run Orchestration (Optional)

```bash
# Start Prefect server
prefect server start

# In another terminal, run the flow
python orchestration/dags/gaming_pipeline_dag.py
```

## Production Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Set environment variables in Streamlit Cloud settings
5. Deploy!

### Railway

1. Create account on [Railway](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL service (or use DuckDB)
4. Set environment variables
5. Deploy

### Environment Variables

Set these in your deployment platform:

- `DATABASE_URL` (if using PostgreSQL)
- `USE_DUCKDB=true` (if using DuckDB)
- `STEAM_API_KEY` (optional)
- `RIOT_API_KEY` (optional)
- `MOCK_DATA_ENABLED=true`

## CI/CD

GitHub Actions automatically:
- Runs tests on push/PR
- Lints code
- Builds and tests pipeline

## Monitoring

- Check logs in `logs/pipeline.log`
- Monitor Prefect dashboard (if using)
- Streamlit dashboard shows data freshness
