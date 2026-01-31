"""
Auto-Refresh Service
Automatically refreshes data every 2 minutes
"""
import time
import threading
from datetime import datetime, timedelta
from src.etl.run_pipeline import ETLPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutoRefreshService:
    """Service to automatically refresh data"""
    
    def __init__(self, refresh_interval_minutes: int = 2):
        self.refresh_interval = refresh_interval_minutes * 60  # Convert to seconds
        self.last_refresh = None
        self.is_running = False
        self.thread = None
        self.pipeline = ETLPipeline()
    
    def start(self):
        """Start auto-refresh service"""
        if self.is_running:
            logger.warning("Auto-refresh service already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.thread.start()
        logger.info(f"Auto-refresh service started (interval: {self.refresh_interval/60} minutes)")
    
    def stop(self):
        """Stop auto-refresh service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Auto-refresh service stopped")
    
    def _refresh_loop(self):
        """Main refresh loop"""
        while self.is_running:
            try:
                logger.info("Starting automatic data refresh...")
                result = self.pipeline.run(limit_per_game=10)
                self.last_refresh = datetime.now()
                logger.info(f"Auto-refresh complete: {result}")
            except Exception as e:
                logger.error(f"Error during auto-refresh: {str(e)}")
            
            # Wait for next refresh
            time.sleep(self.refresh_interval)
    
    def get_status(self) -> Dict:
        """Get refresh service status"""
        return {
            "is_running": self.is_running,
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "next_refresh": (self.last_refresh + timedelta(seconds=self.refresh_interval)).isoformat() if self.last_refresh else None,
            "interval_minutes": self.refresh_interval / 60,
        }
