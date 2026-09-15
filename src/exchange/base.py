"""Base exchange interface."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from src.utils.logger import setup_logging

logger = setup_logging(__name__)


class BaseExchange(ABC):
    """Base class for exchange integrations."""
    
    def __init__(self, symbol: str, testnet: bool = False):
        self.symbol = symbol
        self.testnet = testnet
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to exchange."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from exchange."""
        pass
    
    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> List[Tuple]:
        """Fetch OHLCV candle data.
        
        Returns: List of [timestamp, open, high, low, close, volume]
        """
        pass
    
    @abstractmethod
    async def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch current ticker data."""
        pass
    
    @abstractmethod
    async def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict:
        """Create an order on the exchange.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            order_type: 'MARKET' or 'LIMIT'
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Price (required for LIMIT orders)
        
        Returns: Order details
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an open order."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict:
        """Get account balance."""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders."""
        pass
