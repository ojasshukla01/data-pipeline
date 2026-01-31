"""
Database Configuration
Supports both PostgreSQL and DuckDB (embedded)
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Database configuration settings"""
    
    # Database URL (PostgreSQL)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Use DuckDB (embedded, no server needed)
    USE_DUCKDB: bool = os.getenv("USE_DUCKDB", "false").lower() == "true"
    DUCKDB_PATH: str = os.getenv("DUCKDB_PATH", "data/gaming_pipeline.duckdb")
    
    # Connection pool settings
    POOL_SIZE: int = int(os.getenv("POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("MAX_OVERFLOW", "10"))
    
    # Connection timeout
    CONNECT_TIMEOUT: int = int(os.getenv("CONNECT_TIMEOUT", "30"))
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Get database connection string"""
        if cls.USE_DUCKDB:
            return f"duckdb:///{cls.DUCKDB_PATH}"
        elif cls.DATABASE_URL:
            return cls.DATABASE_URL
        else:
            # Default to DuckDB if no PostgreSQL URL provided
            return f"duckdb:///{cls.DUCKDB_PATH}"
    
    @classmethod
    def is_duckdb(cls) -> bool:
        """Check if using DuckDB"""
        return cls.USE_DUCKDB or cls.DATABASE_URL is None
