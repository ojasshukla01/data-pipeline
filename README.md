# 🎮 Gaming Data Pipeline

A comprehensive, real-time gaming analytics pipeline for popular games (Dota 2, CS:GO, Valorant, GTA 5, PUBG, COD) with forecasting and predictions. Built entirely with free/open-source tools.

## 🚀 Features

- **Real-time Data Collection**: Automated API polling from multiple gaming platforms
- **ETL Pipeline**: Extract, Transform, Load with data validation
- **Data Warehouse**: PostgreSQL/DuckDB for efficient data storage
- **Analytics & ML**: Forecasting, predictions, and trend analysis
- **Interactive Dashboard**: Streamlit-based real-time visualizations
- **CI/CD**: Automated testing and deployment via GitHub Actions
- **Orchestration**: Prefect for workflow management

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Orchestration**: Prefect
- **Database**: PostgreSQL / DuckDB / SQLite
- **Dashboard**: Streamlit
- **CI/CD**: GitHub Actions
- **ML**: scikit-learn, Prophet

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL (optional, DuckDB/SQLite works out of the box)
- Git

## 🏗️ Project Structure

```
data-pipeline/
├── src/                    # Source code
│   ├── analytics/         # Analytics and aggregations
│   ├── database/          # Database models and utilities
│   ├── etl/               # ETL pipeline (extract, transform, load)
│   ├── ingestion/         # API connectors
│   ├── ml/                # Machine learning models
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── data/                  # Data storage (databases, raw, processed)
├── dashboard/             # Streamlit dashboard
│   ├── app.py            # Main dashboard
│   ├── components/       # UI components
│   └── pages/            # Dashboard pages
├── orchestration/         # Prefect workflows
├── tests/                 # Test suite
├── docs/                  # Documentation
└── logs/                  # Application logs
```

## 🚦 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd data-pipeline
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python src/database/setup_db.py
```

### 3. Configure API Keys (Optional)

```bash
python setup_api_keys.py
```

**Note**: OpenDota API works without a key. Steam and Riot API keys are optional but recommended for full functionality.

See [docs/api_keys.md](docs/api_keys.md) for detailed API setup instructions.

### 4. Run ETL Pipeline

```bash
# Windows
run_pipeline.bat

# Linux/Mac
./run_pipeline.sh

# Or directly
python src/etl/run_pipeline.py
```

### 5. Launch Dashboard

```bash
python -m streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

## 📖 Documentation

- **[API Keys Setup](docs/api_keys.md)** - Guide for setting up API keys
- **[Architecture](docs/architecture.md)** - System architecture and design
- **[Deployment](docs/deployment.md)** - Deployment instructions

## 🎯 Usage

### Running the Pipeline

The ETL pipeline can be run manually or scheduled:

```bash
# Manual run
python src/etl/run_pipeline.py

# With Prefect orchestration
python orchestration/run_prefect.py
```

### Dashboard Features

- **Overview Page**: System status, overall statistics, games overview
- **Main Dashboard**: Game-specific analytics, trends, forecasts
- **Time Period Filtering**: View data for last 7/30/90 days
- **Auto-refresh**: Dashboard updates every 2 minutes
- **Data Export**: Export data as CSV, Excel, or JSON

### Supported Games

- **Dota 2**: Real-time data via OpenDota API (no key needed)
- **CS:GO**: Via Steam API (key required)
- **Valorant**: Via Riot Games API (key required)
- **GTA 5**: Via Steam API (key required)
- **PUBG**: Mock data (no public API available)
- **Call of Duty**: Mock data (no public API available)

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_imports.py
pytest tests/test_dashboard.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Configuration

Configuration files are in the `config/` directory:

- `api_config.py`: API endpoints and rate limits
- `database_config.py`: Database connection settings

Environment variables can be set in `.env` file:

```env
STEAM_API_KEY=your_key_here
RIOT_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 📊 Data Flow

1. **Extract**: Fetch data from APIs (OpenDota, Steam, Riot)
2. **Transform**: Clean, validate, and normalize data
3. **Load**: Store in database (DuckDB/PostgreSQL)
4. **Analyze**: Generate analytics and aggregations
5. **Forecast**: ML predictions and trend analysis
6. **Visualize**: Display in Streamlit dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Database Connection Issues
- Ensure database is set up: `python src/database/setup_db.py`
- Check `config/database_config.py` for correct settings
- DuckDB/SQLite works out of the box, no setup needed

### API Errors
- Verify API keys in `.env` file
- Check API status in dashboard sidebar
- See [API Keys Guide](docs/api_keys.md) for setup help

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path and project structure

## 🔒 Security

**IMPORTANT**: This is a public repository. Never commit API keys, passwords, or sensitive data.

- Use `.env` file for all secrets (see `.env.example`)
- `.env` is automatically ignored by git
- See [SECURITY.md](SECURITY.md) for detailed security guidelines

## 📧 Support

For issues and questions:
- Check the [documentation](docs/)
- Review existing issues on GitHub
- Create a new issue with detailed information

---

**Built with ❤️ using free and open-source tools**
