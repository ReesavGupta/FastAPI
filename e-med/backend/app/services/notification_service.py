from typing import Dict, List, Optional, Any
from datetime import datetime
from app.services.websocket_service import WebSocketService
from app.models.user import UserRole
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling real-time notifications"""
    
    @staticmethod
    async def send_order_status_update(user_id: int, order_id: int, status: str, details: dict = None):
        """Send order status update notification"""
        notification_data = {
            "order_id": order_id,
            "status": status,
            "details": details or {},
            "message": f"Order #{order_id} status updated to {status}"
        }
        
        await WebSocketService.send_order_update(user_id, notification_data)
        logger.info(f"Order status update sent to user {user_id}: {status}")
    
    @staticmethod
    async def send_stock_alert(medicine_id: int, medicine_name: str, current_stock: int, threshold: int = 10):
        """Send stock alert to admins when inventory is low"""
        if current_stock <= threshold:
            alert_data = {
                "medicine_id": medicine_id,
                "medicine_name": medicine_name,
                "current_stock": current_stock,
                "threshold": threshold,
                "message": f"Low stock alert: {medicine_name} (Quantity: {current_stock})"
            }
            
            await WebSocketService.send_inventory_update(medicine_id, alert_data)
            logger.info(f"Stock alert sent for {medicine_name}: {current_stock} remaining")
    
    @staticmethod
    async def send_prescription_verification_update(user_id: int, prescription_id: int, status: str, notes: str = None):
        """Send prescription verification update"""
        notification_data = {
            "prescription_id": prescription_id,
            "status": status,
            "notes": notes,
            "message": f"Prescription #{prescription_id} {status}"
        }
        
        await WebSocketService.send_prescription_update(user_id, notification_data)
        logger.info(f"Prescription update sent to user {user_id}: {status}")
    
    @staticmethod
    async def send_delivery_update(user_id: int, order_id: int, delivery_status: str, location: dict = None):
        """Send delivery status update"""
        delivery_data = {
            "order_id": order_id,
            "status": delivery_status,
            "location": location,
            "message": f"Delivery update for order #{order_id}: {delivery_status}"
        }
        
        await WebSocketService.send_delivery_update(order_id, delivery_data)
        logger.info(f"Delivery update sent for order {order_id}: {delivery_status}")
    
    @staticmethod
    async def send_emergency_alert(order_id: int, emergency_type: str, details: dict = None):
        """Send emergency alert to admins and delivery partners"""
        emergency_data = {
            "order_id": order_id,
            "type": emergency_type,
            "details": details or {},
            "message": f"Emergency alert: {emergency_type} for order #{order_id}",
            "priority": "high"
        }
        
        await WebSocketService.send_emergency_alert(emergency_data)
        logger.info(f"Emergency alert sent: {emergency_type} for order {order_id}")
    
    @staticmethod
    async def send_system_notification(user_id: int, notification_type: str, message: str, data: dict = None):
        """Send general system notification"""
        notification_data = {
            "type": notification_type,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await WebSocketService.send_notification(user_id, notification_data)
        logger.info(f"System notification sent to user {user_id}: {notification_type}")
    
    @staticmethod
    async def send_bulk_notification(user_ids: List[int], notification_type: str, message: str, data: dict = None):
        """Send notification to multiple users"""
        notification_data = {
            "type": notification_type,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_id in user_ids:
            await WebSocketService.send_notification(user_id, notification_data)
        
        logger.info(f"Bulk notification sent to {len(user_ids)} users: {notification_type}")

# Global notification service instance
notification_service = NotificationService() 