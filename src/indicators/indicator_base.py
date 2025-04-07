"""
Base Indicator module for PocketBotX57.
Provides the foundation for all trading indicators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import logging

# Setup logging
logger = logging.getLogger("pocketbotx57.indicators.base")

class IndicatorBase(ABC):
    """
    Abstract base class for all trading indicators.
    All indicators must inherit from this class and implement required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the indicator.
        
        Args:
            config (Dict[str, Any], optional): Indicator parameters. Defaults to None.
        """
        self.config = config or {}
        self.name = self.config.get("name", "indicator")
        self.min_confidence = self.config.get("min_confidence", 0.85)
        logger.info(f"IndicatorBase initialized for {self.name}")

    @abstractmethod
    async def generate_signal(self, asset: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate a trading signal for the given asset and market data.
        
        Args:
            asset (str): Asset symbol (e.g., 'BTC/USD')
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            Optional[Dict]: Signal dictionary with 'action', 'confidence', 'duration', etc., or None if no signal
        """
        pass

    def _validate_data(self, data: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """
        Validate that required data is present.
        
        Args:
            data (pd.DataFrame): Market data DataFrame
            required_columns (List[str], optional): List of required column names. Defaults to ['close']
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        if required_columns is None:
            required_columns = ["close"]

        if data is None or data.empty:
            logger.warning("Empty dataset provided")
            return False

        # Check for required columns
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False

        # Need sufficient data points (at least 50 for most indicators)
        if len(data) < 50:
            logger.warning(f"Insufficient data points: {len(data)} < 50")
            return False

        return True

    def _calculate_confidence(self, value: float, min_val: float, max_val: float) -> float:
        """
        Calculate confidence based on a value within a range.
        
        Args:
            value (float): The value to evaluate (e.g., RSI oversold difference)
            min_val (float): Minimum value for scaling
            max_val (float): Maximum value for scaling
            
        Returns:
            float: Confidence score between 0.5 and 1.0
        """
        if max_val == min_val:
            return 0.5
        confidence = 0.5 + (value - min_val) / (max_val - min_val)
        return min(1.0, max(0.5, confidence))