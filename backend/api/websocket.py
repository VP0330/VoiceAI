"""
WebSocket endpoint for real-time transcript streaming with Phase 2 voice agent integration.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from typing import Dict, Set

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# Store active connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections per session"""
    
    @staticmethod
    async def connect(session_id: str, websocket: WebSocket):
        """Accept connection and add to session group"""
        await websocket.accept()
        if session_id not in active_connections:
            active_connections[session_id] = set()
        active_connections[session_id].add(websocket)
        logger.info(f"[WebSocket] Client connected to session {session_id}")
        logger.info(f"[WebSocket] Active connections for {session_id}: {len(active_connections[session_id])}")
    
    @staticmethod
    def disconnect(session_id: str, websocket: WebSocket):
        """Remove connection from session group"""
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]
        logger.info(f"[WebSocket] Client disconnected from session {session_id}")
    
    @staticmethod
    async def broadcast_to_session(session_id: str, message: dict):
        """Broadcast message to all clients in session"""
        if session_id not in active_connections:
            logger.warning(f"[WebSocket] No connections for session {session_id}")
            return
        
        disconnected = set()
        for connection in active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"[WebSocket] Send error: {e}")
                disconnected.add(connection)
        
        # Clean up failed connections
        for conn in disconnected:
            active_connections[session_id].discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time transcript streaming.
    
    **Phase 1 (Current):** Accepts connections, echoes messages.
    **Phase 2 (Voice Agent):** Will receive transcript turns from Pipecat agent.
    
    Message types:
    - `transcript_turn`: User/agent speech (from voice agent)
    - `audio_chunk`: Raw audio for STT processing
    - `control`: Start/stop/reset commands
    
    Example:
        {
            "type": "transcript_turn",
            "speaker": "user",
            "text": "...",
            "timestamp_ms": 1234
        }
    """
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type", "transcript_turn")
            logger.info(f"[{session_id}] Received {msg_type}")
            
            if msg_type == "transcript_turn":
                # Broadcast transcript to all clients in session
                speaker = message.get("speaker", "user")
                text = message.get("text", "")
                timestamp_ms = message.get("timestamp_ms", 0)
                
                logger.info(f"[{session_id}] {speaker}: {text[:50]}...")
                
                # Acknowledge receipt
                ack = {
                    "type": "transcript_turn_received",
                    "session_id": session_id,
                    "speaker": speaker,
                    "text": text,
                    "timestamp_ms": timestamp_ms
                }
                await manager.broadcast_to_session(session_id, ack)
            
            elif msg_type == "audio_chunk":
                # Handle raw audio for STT (Phase 2)
                logger.info(f"[{session_id}] Received audio chunk")
                await websocket.send_json({
                    "type": "audio_chunk_ack",
                    "status": "received"
                })
            
            elif msg_type == "control":
                # Control messages (start, stop, reset)
                action = message.get("action", "")
                logger.info(f"[{session_id}] Control: {action}")
                
                response = {
                    "type": "control_ack",
                    "action": action,
                    "status": "ok"
                }
                await manager.broadcast_to_session(session_id, response)
            
            else:
                # Echo unknown message types
                await websocket.send_json({
                    "type": "ack",
                    "session_id": session_id,
                    "message": "Message received"
                })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.error(f"[WebSocket] Error on session {session_id}: {str(e)}")
        manager.disconnect(session_id, websocket)


async def broadcast_transcript_turn(session_id: str, speaker: str, text: str, timestamp_ms: int):
    """
    Public API to broadcast transcript turn from voice agent.
    Called by Pipecat agent during processing (Phase 2).
    
    Args:
        session_id: Session identifier
        speaker: "user" or "agent"
        text: Transcript text
        timestamp_ms: Timestamp in milliseconds
    """
    message = {
        "type": "transcript_turn_broadcast",
        "session_id": session_id,
        "speaker": speaker,
        "text": text,
        "timestamp_ms": timestamp_ms
    }
    await manager.broadcast_to_session(session_id, message)
