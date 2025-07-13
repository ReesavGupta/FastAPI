from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from app.services.websocket_service import manager, WebSocketService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.core.security import verify_token
from app.core.database import get_db
from sqlalchemy.orm import Session
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token"""
    try:
        # Verify the token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def extract_token_from_query(query_params: str) -> Optional[str]:
    """Extract token from query string"""
    if not query_params:
        return None
    
    # Parse query parameters
    params = dict(param.split('=') for param in query_params.split('&') if '=' in param)
    return params.get('token')

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Get database session
        db = next(get_db())
        
        # Authenticate user
        if not token:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Authentication token required"
            }))
            await websocket.close()
            return
        
        user = await get_user_from_token(token, db)
        
        # Verify user_id matches token
        if user.id != user_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "User ID mismatch"
            }))
            await websocket.close()
            return
        
        # Determine user type
        user_type = "user"
        if user.role in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
            user_type = "admin"
        elif user.role == UserRole.DELIVERY_PARTNER:
            user_type = "delivery"
        
        # Connect to manager
        await manager.connect(websocket, user_id, user_type)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_confirmed",
            "user_id": user_id,
            "user_type": user_type,
            "role": user.role.value
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process message based on type
                await process_message(message, user_id, user_type, websocket)
                
            except WebSocketDisconnect:
                manager.disconnect(websocket, user_id, user_type)
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Connection failed"
            }))
        except:
            pass
        await websocket.close()

async def process_message(message: dict, user_id: int, user_type: str, websocket: WebSocket):
    """Process incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }))
    
    elif message_type == "location_update":
        # Handle location updates from delivery partners
        if user_type == "delivery":
            location_data = message.get("data", {})
            await WebSocketService.send_delivery_update(
                location_data.get("order_id"),
                {
                    "location": location_data.get("location"),
                    "status": "in_transit"
                }
            )
    
    elif message_type == "status_update":
        # Handle status updates
        status_data = message.get("data", {})
        await websocket.send_text(json.dumps({
            "type": "status_confirmed",
            "data": status_data
        }))
    
    elif message_type == "subscribe":
        # Handle subscription to specific channels
        channels = message.get("channels", [])
        await websocket.send_text(json.dumps({
            "type": "subscription_confirmed",
            "channels": channels
        }))
    
    else:
        # Unknown message type
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))

# WebSocket connection endpoint with query parameter for token
@router.websocket("/ws/connect")
async def websocket_connect(
    websocket: WebSocket
):
    """WebSocket connection with token authentication"""
    await websocket.accept()
    
    try:
        # Get database session
        db = next(get_db())
        
        # Extract token from query parameters
        query_string = str(websocket.query_params)
        logger.info(f"WebSocket query params: {query_string}")
        
        token = extract_token_from_query(query_string)
        logger.info(f"Extracted token: {token[:20] if token else 'None'}...")
        
        # Authenticate user
        if not token:
            logger.error("No token provided in WebSocket connection")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Authentication token required"
            }))
            await websocket.close()
            return
        
        try:
            user = await get_user_from_token(token, db)
            logger.info(f"User authenticated: {user.email}")
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid token"
            }))
            await websocket.close()
            return
        
        # Determine user type
        user_type = "user"
        if user.role in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
            user_type = "admin"
        elif user.role == UserRole.DELIVERY_PARTNER:
            user_type = "delivery"
        
        logger.info(f"Connecting user {user.id} as {user_type}")
        
        # Connect to manager
        await manager.connect(websocket, user.id, user_type)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_confirmed",
            "user_id": user.id,
            "user_type": user_type,
            "role": user.role.value,
            "full_name": user.full_name
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process message based on type
                await process_message(message, user.id, user_type, websocket)
                
            except WebSocketDisconnect:
                manager.disconnect(websocket, user.id, user_type)
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Connection failed"
            }))
        except:
            pass
        await websocket.close() 