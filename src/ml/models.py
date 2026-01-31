"""
Machine Learning Models for Forecasting and Predictions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MatchOutcomePredictor:
    """Predict match outcomes based on player stats"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.model_path = Path("data/models/match_predictor.pkl")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction"""
        features = df.copy()
        
        # Feature engineering
        if "kills" in features.columns and "deaths" in features.columns:
            features["kdr"] = features["kills"] / (features["deaths"] + 1)  # Avoid division by zero
            features["total_actions"] = features["kills"] + features["deaths"] + features.get("assists", 0)
        
        if "score" in features.columns:
            features["score_per_minute"] = features["score"] / (features.get("duration_minutes", 1) + 1)
        
        # Fill missing values
        features = features.fillna(0)
        
        return features
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model"""
        logger.info("Training match outcome predictor...")
        
        X_processed = self.prepare_features(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MAE: {mae:.2f}, MSE: {mse:.2f}, R²: {r2:.2f}")
        
        self.is_trained = True
        self.save_model()
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict match outcomes"""
        if not self.is_trained:
            logger.warning("Model not trained, loading from file...")
            self.load_model()
        
        X_processed = self.prepare_features(X)
        return self.model.predict(X_processed)
    
    def save_model(self):
        """Save model to disk"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
        else:
            logger.warning("Model file not found")


class PlayerCountForecaster:
    """Forecast player counts using time series"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.model_path = Path("data/models/player_count_forecaster.pkl")
    
    def prepare_time_series_features(self, df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
        """Prepare time series features"""
        features = df.copy()
        features[date_col] = pd.to_datetime(features[date_col])
        
        # Time-based features
        features["day_of_week"] = features[date_col].dt.dayofweek
        features["day_of_month"] = features[date_col].dt.day
        features["month"] = features[date_col].dt.month
        features["is_weekend"] = features["day_of_week"].isin([5, 6]).astype(int)
        
        # Lag features
        if "player_count" in features.columns:
            features["lag_1"] = features["player_count"].shift(1)
            features["lag_7"] = features["player_count"].shift(7)
            features["rolling_mean_7"] = features["player_count"].rolling(7).mean()
        
        features = features.fillna(0)
        return features
    
    def train(self, df: pd.DataFrame, target_col: str = "player_count", date_col: str = "date"):
        """Train the forecaster"""
        logger.info("Training player count forecaster...")
        
        features = self.prepare_time_series_features(df, date_col)
        
        # Prepare X and y
        feature_cols = [col for col in features.columns if col not in [target_col, date_col]]
        X = features[feature_cols]
        y = features[target_col]
        
        # Remove rows with NaN in target
        valid_idx = ~y.isna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) == 0:
            logger.warning("No valid data for training")
            return
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Forecaster trained - MAE: {mae:.2f}, R²: {r2:.2f}")
        
        self.is_trained = True
        self.save_model()
    
    def forecast(self, df: pd.DataFrame, periods: int = 7, date_col: str = "date") -> pd.DataFrame:
        """Generate forecasts"""
        if not self.is_trained:
            logger.warning("Model not trained, loading from file...")
            self.load_model()
        
        # Generate future dates
        last_date = pd.to_datetime(df[date_col]).max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq="D")
        
        # Create future dataframe
        future_df = pd.DataFrame({date_col: future_dates})
        
        # Prepare features
        combined_df = pd.concat([df, future_df], ignore_index=True)
        features = self.prepare_time_series_features(combined_df, date_col)
        
        # Predict
        feature_cols = [col for col in features.columns if col not in ["player_count", date_col]]
        future_features = features.tail(periods)[feature_cols]
        
        predictions = self.model.predict(future_features)
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            date_col: future_dates,
            "predicted_value": predictions,
        })
        
        # Add confidence intervals (simple approximation)
        std_dev = np.std(predictions) if len(predictions) > 1 else predictions[0] * 0.1
        forecast_df["confidence_interval_lower"] = forecast_df["predicted_value"] - 1.96 * std_dev
        forecast_df["confidence_interval_upper"] = forecast_df["predicted_value"] + 1.96 * std_dev
        
        return forecast_df
    
    def save_model(self):
        """Save model to disk"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
        else:
            logger.warning("Model file not found")
