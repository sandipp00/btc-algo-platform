"""WebSocket handlers for real-time updates."""

import logging
import asyncio
import json
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.utils.logger import setup_logging

logger = setup_logging(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected: {len(self.active_connections)} active")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active")
    
    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


# Global connection manager
manager = ConnectionManager()


def setup_websocket(app: FastAPI) -> None:
    """Setup WebSocket routes."""
    
    @app.websocket("/ws/trades")
    async def websocket_trades(websocket: WebSocket):
        """WebSocket endpoint for real-time trade updates."""
        await manager.connect(websocket)
        try:
            while True:
                # Receive data from client
                data = await websocket.receive_text()
                logger.debug(f"WebSocket trade message: {data}")
                
                # Echo back or process
                await manager.send_personal(
                    websocket,
                    {"type": "trade_update", "data": data}
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("Trade WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    @app.websocket("/ws/portfolio")
    async def websocket_portfolio(websocket: WebSocket):
        """WebSocket endpoint for portfolio updates."""
        await manager.connect(websocket)
        try:
            while True:
                # Send portfolio updates periodically
                await asyncio.sleep(5)
                await manager.send_personal(
                    websocket,
                    {"type": "portfolio_update", "timestamp": str(asyncio.get_event_loop().time())}
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("Portfolio WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    @app.websocket("/ws/market")
    async def websocket_market(websocket: WebSocket):
        """WebSocket endpoint for market data stream."""
        await manager.connect(websocket)
        try:
            while True:
                # Send market updates periodically
                await asyncio.sleep(10)
                await manager.send_personal(
                    websocket,
                    {"type": "market_update", "timestamp": str(asyncio.get_event_loop().time())}
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("Market WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
