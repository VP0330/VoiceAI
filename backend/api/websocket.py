"""
WebSocket endpoint for real-time transcript streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# Store active connections per session
active_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming transcript turns.
    
    Connection URL: /ws/session/{session_id}
    
    Expected message format:
        {
            "type": "transcript_turn",
            "speaker": "interviewer" | "interviewee",
            "text": "...",
            "timestamp_ms": 1234
        }
    
    In Phase 1, this is a no-op (WebSocket accepts connections but doesn't stream).
    Phase 2 (Pipecat voice agent) will inject transcript turns via this endpoint.
    """
    await websocket.accept()
    
    # Register connection
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)
    
    logger.info(f"WebSocket client connected to session {session_id}")
    logger.info(f"Active connections for {session_id}: {len(active_connections[session_id])}")
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"[{session_id}] Received message: {message.get('type', 'unknown')}")
            
            # In Phase 1, just echo received messages back
            # Phase 2 will broadcast to all clients in the session
            await websocket.send_json({
                "type": "ack",
                "session_id": session_id,
                "message": "Message received"
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from session {session_id}")
        active_connections[session_id].remove(websocket)
        if not active_connections[session_id]:
            del active_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error on session {session_id}: {str(e)}")
        try:
            await websocket.close()
        except:
            pass
        if session_id in active_connections and websocket in active_connections[session_id]:
            active_connections[session_id].remove(websocket)


async def broadcast_transcript_turn(session_id: str, speaker: str, text: str, timestamp_ms: int):
    """
    Broadcast a transcript turn to all clients connected to a session.
    (This will be called by Phase 2 Pipecat agent)
    """
    if session_id not in active_connections:
        return
    
    message = {
        "type": "transcript_turn",
        "speaker": speaker,
        "text": text,
        "timestamp_ms": timestamp_ms
    }
    
    # Send to all connected clients for this session
    for connection in active_connections[session_id]:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to client: {str(e)}")
