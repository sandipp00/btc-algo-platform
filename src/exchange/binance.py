"""Binance exchange integration."""

import logging
from typing import Dict, List, Optional, Tuple

try:
    import ccxt.async_support as ccxt
except ImportError:
    import ccxt

from src.utils.logger import setup_logging
from src.utils.config import settings
from src.exchange.base import BaseExchange

logger = setup_logging(__name__)


class BinanceExchange(BaseExchange):
    """Binance exchange integration using CCXT."""
    
    def __init__(self, symbol: str, testnet: bool = False):
        super().__init__(symbol, testnet)
        self.exchange = None
        self._setup_exchange(testnet)
    
    def _setup_exchange(self, testnet: bool) -> None:
        """Setup CCXT exchange instance."""
        exchange_config = {
            "enableRateLimit": True,
            "apiKey": settings.EXCHANGE_API_KEY,
            "secret": settings.EXCHANGE_API_SECRET,
        }
        
        if testnet:
            exchange_config["urls"] = {
                "api": "https://testnet.binance.vision/api",
            }
        
        self.exchange = ccxt.binance(exchange_config)
        logger.info(f"Binance exchange configured (testnet={testnet})")
    
    async def connect(self) -> None:
        """Connect to Binance."""
        try:
            # Fetch exchange info to verify connection
            markets = await self.exchange.fetch_markets()
            self.is_connected = True
            logger.info(f"Connected to Binance ({len(markets)} markets)")
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Binance."""
        if self.exchange:
            await self.exchange.close()
            self.is_connected = False
            logger.info("Disconnected from Binance")
    
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> List[Tuple]:
        """Fetch OHLCV candle data from Binance."""
        try:
            candles = await self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
            )
            return candles
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {symbol}: {e}")
            raise
    
    async def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch current ticker data."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Failed to fetch ticker for {symbol}: {e}")
            raise
    
    async def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict:
        """Create an order on Binance."""
        try:
            if order_type.upper() == "MARKET":
                order = await self.exchange.create_market_order(
                    symbol=symbol,
                    side=side.lower(),
                    amount=quantity,
                )
            elif order_type.upper() == "LIMIT":
                if price is None:
                    raise ValueError("Price required for LIMIT order")
                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side.lower(),
                    amount=quantity,
                    price=price,
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            logger.info(f"Order created: {order['id']} ({side} {quantity} {symbol})")
            return order
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an open order."""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    async def get_balance(self) -> Dict:
        """Get account balance."""
        try:
            balance = await self.exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            raise
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders."""
        try:
            if symbol:
                orders = await self.exchange.fetch_open_orders(symbol)
            else:
                orders = await self.exchange.fetch_open_orders()
            return orders
        except Exception as e:
            logger.error(f"Failed to fetch open orders: {e}")
            raise
