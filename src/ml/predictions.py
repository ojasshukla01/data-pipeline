"""
Predictions Module
Generates predictions for match outcomes and player performance
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy import text
from src.database.db_utils import db_manager
from src.ml.models import MatchOutcomePredictor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictionService:
    """Service for generating predictions"""
    
    def __init__(self):
        self.predictor = MatchOutcomePredictor()
    
    def predict_match_outcome(self, player_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict match outcome based on player statistics"""
        if not player_stats:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Prepare features
        df = pd.DataFrame(player_stats)
        
        # Feature engineering
        df["team_kills"] = df["kills"].sum()
        df["team_deaths"] = df["deaths"].sum()
        df["team_kdr"] = df["team_kills"] / (df["team_deaths"] + 1)
        df["avg_score"] = df["score"].mean()
        
        # Select features for prediction
        feature_cols = ["kills", "deaths", "assists", "score", "team_kdr", "avg_score"]
        X = df[feature_cols].iloc[:1]  # Use first row (aggregated)
        
        # Predict (using score as proxy for win probability)
        try:
            if not self.predictor.is_trained:
                # Train on historical data
                self._train_on_historical_data()
            
            predicted_score = self.predictor.predict(X)[0]
            
            # Convert score to win probability (simple heuristic)
            win_probability = min(max(predicted_score / 10000, 0), 1)
            
            return {
                "prediction": "win" if win_probability > 0.5 else "loss",
                "win_probability": float(win_probability),
                "confidence": float(abs(win_probability - 0.5) * 2),  # Distance from 0.5
                "predicted_score": float(predicted_score),
            }
        
        except Exception as e:
            logger.error(f"Error predicting match outcome: {str(e)}")
            return {"prediction": "error", "confidence": 0.0}
    
    def _train_on_historical_data(self):
        """Train predictor on historical data"""
        logger.info("Training predictor on historical data...")
        
        # Get historical player stats
        session = db_manager.get_session()
        
        try:
            query = text("""
                SELECT 
                    ps.kills,
                    ps.deaths,
                    ps.assists,
                    ps.score,
                    m.match_id,
                    m.duration_minutes
                FROM player_stats ps
                JOIN matches m ON ps.match_id = m.match_id
                WHERE ps.kills IS NOT NULL
                    AND ps.deaths IS NOT NULL
                    AND ps.score IS NOT NULL
                LIMIT 1000
            """)
            
            result = session.execute(query)
            data = [dict(row._mapping) for row in result]
            
            if len(data) < 10:
                logger.warning("Insufficient data for training")
                return
            
            df = pd.DataFrame(data)
            
            # Aggregate by match
            match_stats = df.groupby("match_id").agg({
                "kills": "sum",
                "deaths": "sum",
                "assists": "sum",
                "score": "sum",
                "duration_minutes": "first",
            }).reset_index()
            
            # Feature engineering
            match_stats["kdr"] = match_stats["kills"] / (match_stats["deaths"] + 1)
            match_stats["total_actions"] = match_stats["kills"] + match_stats["deaths"] + match_stats["assists"]
            
            # Prepare X and y
            X = match_stats[["kills", "deaths", "assists", "kdr", "total_actions"]]
            y = match_stats["score"]  # Use score as target
            
            # Train
            self.predictor.train(X, y)
        
        except Exception as e:
            logger.error(f"Error training predictor: {str(e)}")
        finally:
            session.close()
    
    def predict_player_performance(self, player_id: str, game_id: str) -> Dict[str, Any]:
        """Predict player performance for next match"""
        session = db_manager.get_session()
        
        try:
            query = text("""
                SELECT 
                    kills,
                    deaths,
                    assists,
                    score
                FROM player_stats
                WHERE player_id = :player_id
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            result = session.execute(query, {"player_id": player_id})
            data = [dict(row._mapping) for row in result]
            
            if not data:
                return {
                    "player_id": player_id,
                    "predicted_kills": 5,
                    "predicted_deaths": 5,
                    "predicted_score": 1000,
                    "confidence": "low",
                }
            
            df = pd.DataFrame(data)
            
            # Simple prediction: use average of recent matches
            predictions = {
                "player_id": player_id,
                "predicted_kills": float(df["kills"].mean()),
                "predicted_deaths": float(df["deaths"].mean()),
                "predicted_assists": float(df["assists"].mean()),
                "predicted_score": float(df["score"].mean()),
                "confidence": "medium" if len(data) >= 5 else "low",
            }
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error predicting player performance: {str(e)}")
            return {"player_id": player_id, "error": str(e)}
        finally:
            session.close()
