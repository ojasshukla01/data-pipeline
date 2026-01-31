# Architecture Documentation

## System Architecture

### Overview
The Gaming Data Pipeline is a comprehensive data engineering solution built entirely with free and open-source tools. It collects, processes, stores, and visualizes gaming data from multiple sources.

### Components

#### 1. Data Ingestion Layer
- **Steam API Connector**: Fetches data for Dota 2, CS:GO, GTA 5
- **OpenDota API Connector**: Detailed Dota 2 statistics
- **Riot API Connector**: Valorant match data
- **Mock Data Generator**: Generates realistic data for PUBG, COD when APIs unavailable

#### 2. ETL Pipeline
- **Extract**: Fetches data from APIs
- **Transform**: Cleans, validates, and normalizes data
- **Load**: Stores data in database

#### 3. Data Warehouse
- **PostgreSQL/DuckDB**: Stores all gaming data
- **Schema**: Games, Players, Matches, Player Stats, Events, Forecasts

#### 4. Analytics & ML
- **Analytics Service**: Aggregations, trends, top players
- **Forecasting**: Player count predictions
- **Predictions**: Match outcome predictions

#### 5. Dashboard
- **Streamlit**: Interactive web dashboard
- **Real-time Updates**: Refreshes every 15 minutes
- **Visualizations**: Charts, graphs, tables

#### 6. Orchestration
- **Prefect**: Workflow orchestration
- **Scheduled Runs**: Every 15 minutes
- **Error Handling**: Retry mechanisms

### Data Flow

```
APIs → Extract → Transform → Load → Database
                                    ↓
                            Analytics & ML
                                    ↓
                              Dashboard
```

### Technology Stack

- **Language**: Python 3.9+
- **Database**: PostgreSQL / DuckDB
- **Orchestration**: Prefect
- **Dashboard**: Streamlit
- **ML**: scikit-learn
- **Visualization**: Plotly

### Deployment

- **Development**: Local
- **Production**: Streamlit Cloud / Railway
- **CI/CD**: GitHub Actions
