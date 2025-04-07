"""
Bollinger Bands Strategy for PocketBotX57 (MVP + AI Lite)
Simple, fast Bollinger Bands for signal generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from pandas_ta import bbands

logger = logging.getLogger("pocketbotx57.indicators.bollinger")

class BollingerBandsStrategy:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = "bollinger"
        self.period = self.config.get('period', 20)
        self.std_dev = self.config.get('std_dev', 2.0)
        self.min_confidence = self.config.get('min_confidence', 0.85)
        logger.info(f"BollingerBandsStrategy initialized: period={self.period}, std_dev={self.std_dev}")

    def _validate_data(self, data: pd.DataFrame) -> bool:
        if data is None or data.empty or 'close' not in data.columns or len(data) < self.period:
            logger.warning("Invalid or insufficient data for Bollinger Bands")
            return False
        return True

    async def generate_signal(self, asset: str, data: pd.DataFrame) -> Optional[Dict]:
        """Generate async trading signal for SignalEngine."""
        if not self._validate_data(data):
            return None

        # Use pandas_ta for fast Bollinger Bands
        bb = bbands(data['close'], length=self.period, std=self.std_dev)
        if bb is None or bb.empty:
            return None

        upper = bb[f'BBU_{self.period}_{self.std_dev}'].iloc[-1]
        middle = bb[f'BBM_{self.period}_{self.std_dev}'].iloc[-1]
        lower = bb[f'BBL_{self.period}_{self.std_dev}'].iloc[-1]
        current_close = data['close'].iloc[-1]

        signal = None
        if current_close <= lower:
            signal = {
                'action': 'BUY',
                'confidence': 0.85 if current_close < lower * 0.98 else 0.75,  # Extreme < 2% below
                'duration': 5,  # Default 5m trade
                'indicators': {'upper': upper, 'middle': middle, 'lower': lower}
            }
        elif current_close >= upper:
            signal = {
                'action': 'SELL',
                'confidence': 0.85 if current_close > upper * 1.02 else 0.75,  # Extreme > 2% above
                'duration': 5,
                'indicators': {'upper': upper, 'middle': middle, 'lower': lower}
            }

        if signal and signal['confidence'] >= self.min_confidence:
            logger.info(f"Bollinger signal for {asset}: {signal['action']} ({signal['confidence']:.2f})")
            return signal
        return None