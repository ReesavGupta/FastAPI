import asyncio
import json
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store connections by type (user, admin, delivery)
        self.connections_by_type: Dict[str, List[WebSocket]] = {
            "user": [],
            "admin": [],
            "delivery": []
        }
    
    async def connect(self, websocket: WebSocket, user_id: int, user_type: str = "user"):
        """Connect a new WebSocket client"""
        await websocket.accept()
        
        # Add to user-specific connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Add to type-specific connections
        if user_type not in self.connections_by_type:
            self.connections_by_type[user_type] = []
        self.connections_by_type[user_type].append(websocket)
        
        logger.info(f"WebSocket connected: User {user_id}, Type: {user_type}")
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": "Connected to MediDash real-time system",
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int, user_type: str = "user"):
        """Disconnect a WebSocket client"""
        # Remove from user-specific connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from type-specific connections
        if user_type in self.connections_by_type:
            if websocket in self.connections_by_type[user_type]:
                self.connections_by_type[user_type].remove(websocket)
        
        logger.info(f"WebSocket disconnected: User {user_id}, Type: {user_type}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[user_id].remove(connection)
    
    async def broadcast_to_type(self, user_type: str, message: dict):
        """Broadcast message to all connections of a specific type"""
        if user_type in self.connections_by_type:
            disconnected = []
            for connection in self.connections_by_type[user_type]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_type}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.connections_by_type[user_type].remove(connection)
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast message to all admin connections"""
        await self.broadcast_to_type("admin", message)
    
    async def broadcast_to_users(self, message: dict):
        """Broadcast message to all user connections"""
        await self.broadcast_to_type("user", message)
    
    async def broadcast_to_delivery(self, message: dict):
        """Broadcast message to all delivery partner connections"""
        await self.broadcast_to_type("delivery", message)

# Global connection manager instance
manager = ConnectionManager()

class WebSocketService:
    """Service for handling WebSocket operations"""
    
    @staticmethod
    async def send_order_update(user_id: int, order_data: dict):
        """Send order update to user"""
        message = {
            "type": "order_update",
            "data": order_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_to_user(user_id, message)
    
    @staticmethod
    async def send_inventory_update(medicine_id: int, stock_data: dict):
        """Send inventory update to admins"""
        message = {
            "type": "inventory_update",
            "data": {
                "medicine_id": medicine_id,
                **stock_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_admins(message)
    
    @staticmethod
    async def send_prescription_update(user_id: int, prescription_data: dict):
        """Send prescription update to user"""
        message = {
            "type": "prescription_update",
            "data": prescription_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_to_user(user_id, message)
    
    @staticmethod
    async def send_delivery_update(order_id: int, delivery_data: dict):
        """Send delivery update to user and delivery partner"""
        message = {
            "type": "delivery_update",
            "data": {
                "order_id": order_id,
                **delivery_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to user (we'll need to get user_id from order)
        # This will be implemented when we have order context
        
        # Send to delivery partners
        await manager.broadcast_to_delivery(message)
    
    @staticmethod
    async def send_emergency_alert(emergency_data: dict):
        """Send emergency alert to admins and delivery partners"""
        message = {
            "type": "emergency_alert",
            "data": emergency_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.broadcast_to_admins(message)
        await manager.broadcast_to_delivery(message)
    
    @staticmethod
    async def send_notification(user_id: int, notification_data: dict):
        """Send general notification to user"""
        message = {
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_to_user(user_id, message) 