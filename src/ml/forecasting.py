"""
Forecasting Module
Generates forecasts for gaming metrics
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
from src.database.db_utils import db_manager
from src.ml.models import PlayerCountForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ForecastingService:
    """Service for generating forecasts"""
    
    def __init__(self):
        self.forecaster = PlayerCountForecaster()
    
    def generate_player_count_forecasts(self, game_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Generate player count forecasts for a game"""
        logger.info(f"Generating player count forecasts for {game_id} (next {days} days)")
        
        # Get historical data
        historical_data = self._get_historical_match_data(game_id)
        
        if len(historical_data) < 7:
            logger.warning(f"Insufficient data for {game_id}, generating simple forecasts")
            return self._generate_simple_forecasts(game_id, days)
        
        # Prepare data
        df = pd.DataFrame(historical_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.groupby("date").agg({
            "match_count": "sum"
        }).reset_index()
        df["player_count"] = df["match_count"] * 10  # Estimate players from matches
        
        # Train model if needed
        if not self.forecaster.is_trained:
            try:
                self.forecaster.train(df, target_col="player_count", date_col="date")
            except Exception as e:
                logger.error(f"Error training forecaster: {str(e)}")
                return self._generate_simple_forecasts(game_id, days)
        
        # Generate forecasts
        try:
            forecast_df = self.forecaster.forecast(df, periods=days, date_col="date")
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            return self._generate_simple_forecasts(game_id, days)
        
        # Convert to list of dicts
        forecasts = []
        for _, row in forecast_df.iterrows():
            forecasts.append({
                "forecast_id": f"forecast_{game_id}_{row['date'].strftime('%Y%m%d')}",
                "game_id": game_id,
                "forecast_date": row["date"].date(),
                "predicted_metric": "player_count",
                "predicted_value": float(row["predicted_value"]),
                "confidence_interval_lower": float(row["confidence_interval_lower"]),
                "confidence_interval_upper": float(row["confidence_interval_upper"]),
                "model_version": "1.0",
            })
        
        return forecasts
    
    def _get_historical_match_data(self, game_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical match data from database"""
        session = db_manager.get_session()
        
        try:
            query = text("""
                SELECT 
                    DATE(match_date) as date,
                    COUNT(*) as match_count
                FROM matches
                WHERE game_id = :game_id
                    AND match_date >= :start_date
                GROUP BY DATE(match_date)
                ORDER BY date
            """)
            
            start_date = datetime.now() - timedelta(days=days)
            
            result = session.execute(query, {
                "game_id": game_id,
                "start_date": start_date
            })
            
            data = [
                {
                    "date": row[0].isoformat() if isinstance(row[0], datetime) else str(row[0]),
                    "match_count": row[1]
                }
                for row in result
            ]
            
            return data
        
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return []
        finally:
            session.close()
    
    def _generate_simple_forecasts(self, game_id: str, days: int) -> List[Dict[str, Any]]:
        """Generate simple forecasts using average"""
        forecasts = []
        base_date = datetime.now().date()
        base_value = 1000  # Default estimate
        
        for i in range(1, days + 1):
            forecast_date = base_date + timedelta(days=i)
            forecasts.append({
                "forecast_id": f"forecast_{game_id}_{forecast_date.strftime('%Y%m%d')}",
                "game_id": game_id,
                "forecast_date": forecast_date,
                "predicted_metric": "player_count",
                "predicted_value": float(base_value),
                "confidence_interval_lower": float(base_value * 0.8),
                "confidence_interval_upper": float(base_value * 1.2),
                "model_version": "1.0",
            })
        
        return forecasts
    
    def save_forecasts(self, forecasts: List[Dict[str, Any]]):
        """Save forecasts to database"""
        session = db_manager.get_session()
        
        try:
            from src.database.models import Forecast
            
            for forecast_data in forecasts:
                # Check if forecast exists
                existing = session.query(Forecast).filter(
                    Forecast.forecast_id == forecast_data["forecast_id"]
                ).first()
                
                if existing:
                    # Update
                    for key, value in forecast_data.items():
                        if key != "forecast_id":
                            setattr(existing, key, value)
                else:
                    # Insert
                    forecast = Forecast(**forecast_data)
                    session.add(forecast)
            
            session.commit()
            logger.info(f"Saved {len(forecasts)} forecasts to database")
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving forecasts: {str(e)}")
            raise
        finally:
            session.close()
