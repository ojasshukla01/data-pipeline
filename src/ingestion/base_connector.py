"""
Base connector class for all API connectors
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseConnector(ABC):
    """Base class for all API connectors"""
    
    def __init__(self, base_url: str, rate_limit: int = 60, retry_count: int = 3):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.retry_count = retry_count
        self.session = self._create_session()
        self.last_request_time = 0
        self.min_request_interval = 60 / rate_limit  # seconds between requests
    
    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.retry_count,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _rate_limit_check(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with rate limiting and error handling"""
        self._rate_limit_check()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from the API - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_game_name(self) -> str:
        """Get the game name this connector handles"""
        pass
