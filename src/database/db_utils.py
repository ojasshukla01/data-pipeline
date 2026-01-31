"""
Database utility functions
"""
import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from config.database_config import DatabaseConfig
from src.database.models import Base
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection and management"""
    
    def __init__(self):
        self.config = DatabaseConfig
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine"""
        if self.config.is_duckdb():
            # DuckDB connection - use duckdb-engine
            try:
                import duckdb_engine
                db_path = self.config.DUCKDB_PATH
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                # Create DuckDB connection string
                self.engine = create_engine(
                    f"duckdb:///{db_path}",
                    poolclass=NullPool,
                )
                logger.info(f"Initialized DuckDB connection: {db_path}")
            except ImportError:
                logger.warning("duckdb-engine not installed. Trying direct DuckDB connection...")
                try:
                    # Try direct DuckDB connection as fallback
                    import duckdb
                    db_path = self.config.DUCKDB_PATH
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
                    
                    # Create a simple connection for now
                    # Note: This is a workaround - ideally use duckdb-engine
                    conn = duckdb.connect(db_path)
                    conn.close()
                    
                    # Use SQLite-compatible connection string as workaround
                    self.engine = create_engine(
                        f"sqlite:///{db_path.replace('.duckdb', '.db')}",
                        poolclass=NullPool,
                    )
                    logger.warning(f"Using SQLite fallback. For full DuckDB support, install: pip install duckdb-engine")
                except ImportError:
                    raise ImportError(
                        "DuckDB not available. Please install: pip install duckdb duckdb-engine\n"
                        "Or use PostgreSQL by setting DATABASE_URL in .env"
                    )
        else:
            # PostgreSQL connection
            self.engine = create_engine(
                self.config.get_connection_string(),
                pool_size=self.config.POOL_SIZE,
                max_overflow=self.config.MAX_OVERFLOW,
                pool_pre_ping=True,
            )
            logger.info("Initialized PostgreSQL connection")
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
            # Insert initial game data
            self._insert_initial_data()
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def _insert_initial_data(self):
        """Insert initial game data"""
        session = self.get_session()
        try:
            # Check if games already exist
            result = session.execute(text("SELECT COUNT(*) FROM games"))
            count = result.scalar()
            
            if count == 0:
                games = [
                    {"game_id": "dota2", "game_name": "Dota 2", "platform": "steam", "genre": "MOBA"},
                    {"game_id": "csgo", "game_name": "Counter-Strike: Global Offensive", "platform": "steam", "genre": "FPS"},
                    {"game_id": "valorant", "game_name": "Valorant", "platform": "riot", "genre": "FPS"},
                    {"game_id": "gta5", "game_name": "Grand Theft Auto V", "platform": "steam", "genre": "Action"},
                    {"game_id": "pubg", "game_name": "PlayerUnknown's Battlegrounds", "platform": "steam", "genre": "Battle Royale"},
                    {"game_id": "cod", "game_name": "Call of Duty", "platform": "activision", "genre": "FPS"},
                ]
                
                for game in games:
                    session.execute(
                        text("""
                            INSERT INTO games (game_id, game_name, platform, genre)
                            VALUES (:game_id, :game_name, :platform, :genre)
                        """),
                        game
                    )
                
                session.commit()
                logger.info("Initial game data inserted")
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting initial data: {str(e)}")
        finally:
            session.close()
    
    def execute_sql_file(self, file_path: str):
        """Execute SQL file"""
        try:
            with open(file_path, 'r') as f:
                sql = f.read()
            
            with self.engine.connect() as conn:
                # Split by semicolon and execute each statement
                statements = [s.strip() for s in sql.split(';') if s.strip()]
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                conn.commit()
            
            logger.info(f"Executed SQL file: {file_path}")
        except Exception as e:
            logger.error(f"Error executing SQL file: {str(e)}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()
