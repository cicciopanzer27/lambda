#!/usr/bin/env python3
"""
WebSocket Communication System
Sistema di comunicazione real-time con WebSockets per sostituire il polling.
Risolve la criticità 3.5: Comunicazione Basata su Polling.
"""

import asyncio
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from pathlib import Path

# WebSocket dependencies
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = None

# Flask-SocketIO as alternative
try:
    from flask_socketio import SocketIO, emit, disconnect
    from flask import Flask
    FLASK_SOCKETIO_AVAILABLE = True
except ImportError:
    FLASK_SOCKETIO_AVAILABLE = False
    SocketIO = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Tipi di messaggi WebSocket."""
    # Client to Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    JOB_SUBMIT = "job_submit"
    JOB_CANCEL = "job_cancel"
    SYSTEM_STATUS = "system_status"
    PING = "ping"
    
    # Server to Client
    JOB_UPDATE = "job_update"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    SYSTEM_UPDATE = "system_update"
    ERROR = "error"
    PONG = "pong"
    
    # Bidirectional
    HEARTBEAT = "heartbeat"

class SubscriptionType(Enum):
    """Tipi di sottoscrizioni."""
    ALL_JOBS = "all_jobs"
    MY_JOBS = "my_jobs"
    SPECIFIC_JOB = "specific_job"
    SYSTEM_STATUS = "system_status"
    PERFORMANCE_METRICS = "performance_metrics"

@dataclass
class WebSocketMessage:
    """Messaggio WebSocket strutturato."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    message_id: str
    client_id: Optional[str] = None
    subscription_id: Optional[str] = None

@dataclass
class ClientConnection:
    """Informazioni su una connessione client."""
    client_id: str
    websocket: Any  # WebSocket connection
    connected_at: datetime
    last_heartbeat: datetime
    subscriptions: Set[str]
    metadata: Dict[str, Any]

class WebSocketManager:
    """Gestore delle connessioni WebSocket."""
    
    def __init__(self):
        self.clients: Dict[str, ClientConnection] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # subscription_id -> client_ids
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_task = None
        self.lock = threading.RLock()
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Registra gli handler di default per i messaggi."""
        
        self.message_handlers[MessageType.SUBSCRIBE] = self._handle_subscribe
        self.message_handlers[MessageType.UNSUBSCRIBE] = self._handle_unsubscribe
        self.message_handlers[MessageType.PING] = self._handle_ping
        self.message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat
        self.message_handlers[MessageType.SYSTEM_STATUS] = self._handle_system_status
    
    async def add_client(self, websocket: Any, client_metadata: Dict[str, Any] = None) -> str:
        """Aggiunge un nuovo client."""
        
        client_id = str(uuid.uuid4())
        
        with self.lock:
            self.clients[client_id] = ClientConnection(
                client_id=client_id,
                websocket=websocket,
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                subscriptions=set(),
                metadata=client_metadata or {}
            )
        
        logger.info(f"✅ Client connected: {client_id}")
        
        # Send welcome message
        await self.send_to_client(client_id, MessageType.SYSTEM_UPDATE, {
            "status": "connected",
            "client_id": client_id,
            "server_time": datetime.now().isoformat()
        })
        
        # Start heartbeat if this is the first client
        if len(self.clients) == 1 and not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        return client_id
    
    async def remove_client(self, client_id: str):
        """Rimuove un client."""
        
        with self.lock:
            if client_id in self.clients:
                client = self.clients[client_id]
                
                # Remove from all subscriptions
                for subscription_id in client.subscriptions:
                    if subscription_id in self.subscriptions:
                        self.subscriptions[subscription_id].discard(client_id)
                        if not self.subscriptions[subscription_id]:
                            del self.subscriptions[subscription_id]
                
                del self.clients[client_id]
                logger.info(f"❌ Client disconnected: {client_id}")
        
        # Stop heartbeat if no clients
        if not self.clients and self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
    
    async def handle_message(self, client_id: str, message: str):
        """Gestisce un messaggio ricevuto da un client."""
        
        try:
            data = json.loads(message)
            
            # Validate message structure
            if not all(key in data for key in ['type', 'data']):
                await self.send_error(client_id, "Invalid message format")
                return
            
            message_type = MessageType(data['type'])
            message_obj = WebSocketMessage(
                type=message_type,
                data=data['data'],
                timestamp=datetime.now(),
                message_id=data.get('message_id', str(uuid.uuid4())),
                client_id=client_id,
                subscription_id=data.get('subscription_id')
            )
            
            # Update heartbeat
            if client_id in self.clients:
                self.clients[client_id].last_heartbeat = datetime.now()
            
            # Handle message
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](message_obj)
            else:
                logger.warning(f"No handler for message type: {message_type}")
                await self.send_error(client_id, f"Unknown message type: {message_type.value}")
        
        except json.JSONDecodeError:
            await self.send_error(client_id, "Invalid JSON")
        except ValueError as e:
            await self.send_error(client_id, f"Invalid message type: {e}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self.send_error(client_id, "Internal server error")
    
    async def send_to_client(self, client_id: str, message_type: MessageType, 
                           data: Dict[str, Any], subscription_id: str = None):
        """Invia un messaggio a un client specifico."""
        
        if client_id not in self.clients:
            logger.warning(f"Attempted to send to non-existent client: {client_id}")
            return
        
        client = self.clients[client_id]
        
        message = {
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4())
        }
        
        if subscription_id:
            message["subscription_id"] = subscription_id
        
        try:
            await client.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            await self.remove_client(client_id)
    
    async def broadcast_to_subscription(self, subscription_id: str, 
                                      message_type: MessageType, data: Dict[str, Any]):
        """Invia un messaggio a tutti i client sottoscritti."""
        
        if subscription_id not in self.subscriptions:
            return
        
        client_ids = list(self.subscriptions[subscription_id])
        
        for client_id in client_ids:
            await self.send_to_client(client_id, message_type, data, subscription_id)
    
    async def broadcast_to_all(self, message_type: MessageType, data: Dict[str, Any]):
        """Invia un messaggio a tutti i client connessi."""
        
        client_ids = list(self.clients.keys())
        
        for client_id in client_ids:
            await self.send_to_client(client_id, message_type, data)
    
    async def send_error(self, client_id: str, error_message: str):
        """Invia un messaggio di errore a un client."""
        
        await self.send_to_client(client_id, MessageType.ERROR, {
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    # Message Handlers
    
    async def _handle_subscribe(self, message: WebSocketMessage):
        """Gestisce richieste di sottoscrizione."""
        
        client_id = message.client_id
        data = message.data
        
        subscription_type = data.get('subscription_type')
        subscription_params = data.get('params', {})
        
        # Generate subscription ID
        subscription_id = f"{subscription_type}_{str(uuid.uuid4())[:8]}"
        
        # Add to subscriptions
        with self.lock:
            if subscription_id not in self.subscriptions:
                self.subscriptions[subscription_id] = set()
            
            self.subscriptions[subscription_id].add(client_id)
            
            if client_id in self.clients:
                self.clients[client_id].subscriptions.add(subscription_id)
        
        logger.info(f"📡 Client {client_id} subscribed to {subscription_type}")
        
        # Send confirmation
        await self.send_to_client(client_id, MessageType.SYSTEM_UPDATE, {
            "status": "subscribed",
            "subscription_id": subscription_id,
            "subscription_type": subscription_type
        })
    
    async def _handle_unsubscribe(self, message: WebSocketMessage):
        """Gestisce richieste di disiscrizione."""
        
        client_id = message.client_id
        subscription_id = message.data.get('subscription_id')
        
        with self.lock:
            if subscription_id in self.subscriptions:
                self.subscriptions[subscription_id].discard(client_id)
                
                if not self.subscriptions[subscription_id]:
                    del self.subscriptions[subscription_id]
            
            if client_id in self.clients:
                self.clients[client_id].subscriptions.discard(subscription_id)
        
        logger.info(f"📡 Client {client_id} unsubscribed from {subscription_id}")
        
        await self.send_to_client(client_id, MessageType.SYSTEM_UPDATE, {
            "status": "unsubscribed",
            "subscription_id": subscription_id
        })
    
    async def _handle_ping(self, message: WebSocketMessage):
        """Gestisce ping dal client."""
        
        await self.send_to_client(message.client_id, MessageType.PONG, {
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_heartbeat(self, message: WebSocketMessage):
        """Gestisce heartbeat dal client."""
        
        client_id = message.client_id
        
        if client_id in self.clients:
            self.clients[client_id].last_heartbeat = datetime.now()
        
        # Echo heartbeat
        await self.send_to_client(client_id, MessageType.HEARTBEAT, {
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_system_status(self, message: WebSocketMessage):
        """Gestisce richieste di stato del sistema."""
        
        status = {
            "connected_clients": len(self.clients),
            "active_subscriptions": len(self.subscriptions),
            "server_uptime": time.time(),  # Simplified
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_to_client(message.client_id, MessageType.SYSTEM_UPDATE, status)
    
    async def _heartbeat_loop(self):
        """Loop di heartbeat per verificare connessioni."""
        
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = datetime.now()
                timeout_threshold = current_time.timestamp() - (self.heartbeat_interval * 2)
                
                # Check for stale connections
                stale_clients = []
                
                with self.lock:
                    for client_id, client in self.clients.items():
                        if client.last_heartbeat.timestamp() < timeout_threshold:
                            stale_clients.append(client_id)
                
                # Remove stale connections
                for client_id in stale_clients:
                    logger.warning(f"⚠️  Removing stale client: {client_id}")
                    await self.remove_client(client_id)
                
                # Send heartbeat to remaining clients
                await self.broadcast_to_all(MessageType.HEARTBEAT, {
                    "timestamp": current_time.isoformat()
                })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

class LambdaVisualizerWebSocketServer:
    """Server WebSocket per Lambda Visualizer."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.manager = WebSocketManager()
        self.server = None
        
        # Register Lambda Visualizer specific handlers
        self._register_lambda_handlers()
    
    def _register_lambda_handlers(self):
        """Registra handler specifici per Lambda Visualizer."""
        
        self.manager.message_handlers[MessageType.JOB_SUBMIT] = self._handle_job_submit
        self.manager.message_handlers[MessageType.JOB_CANCEL] = self._handle_job_cancel
    
    async def _handle_job_submit(self, message: WebSocketMessage):
        """Gestisce sottomissione di job."""
        
        client_id = message.client_id
        job_data = message.data
        
        # Validate job data
        required_fields = ['job_type', 'input_data']
        if not all(field in job_data for field in required_fields):
            await self.manager.send_error(client_id, "Missing required job fields")
            return
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Send job accepted
        await self.manager.send_to_client(client_id, MessageType.JOB_UPDATE, {
            "job_id": job_id,
            "status": "accepted",
            "message": "Job submitted successfully"
        })
        
        # Simulate job processing (in real implementation, this would integrate with job manager)
        asyncio.create_task(self._simulate_job_processing(client_id, job_id, job_data))
        
        logger.info(f"🚀 Job {job_id} submitted by client {client_id}")
    
    async def _handle_job_cancel(self, message: WebSocketMessage):
        """Gestisce cancellazione di job."""
        
        client_id = message.client_id
        job_id = message.data.get('job_id')
        
        if not job_id:
            await self.manager.send_error(client_id, "Missing job_id")
            return
        
        # Send cancellation confirmation
        await self.manager.send_to_client(client_id, MessageType.JOB_UPDATE, {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Job cancelled successfully"
        })
        
        logger.info(f"❌ Job {job_id} cancelled by client {client_id}")
    
    async def _simulate_job_processing(self, client_id: str, job_id: str, job_data: Dict[str, Any]):
        """Simula il processing di un job con aggiornamenti real-time."""
        
        try:
            # Job started
            await self.manager.send_to_client(client_id, MessageType.JOB_UPDATE, {
                "job_id": job_id,
                "status": "running",
                "progress": 0.0,
                "message": "Job started"
            })
            
            # Simulate progress updates
            for progress in [0.2, 0.4, 0.6, 0.8]:
                await asyncio.sleep(1)  # Simulate work
                
                await self.manager.send_to_client(client_id, MessageType.JOB_UPDATE, {
                    "job_id": job_id,
                    "status": "running",
                    "progress": progress,
                    "message": f"Processing... {int(progress * 100)}%"
                })
            
            await asyncio.sleep(1)  # Final processing
            
            # Job completed
            result = {
                "expression": job_data['input_data'].get('expression', 'λx.x'),
                "analysis": "Identity function",
                "complexity": 1,
                "visualization_url": f"/results/{job_id}.mp4"
            }
            
            await self.manager.send_to_client(client_id, MessageType.JOB_COMPLETED, {
                "job_id": job_id,
                "status": "completed",
                "progress": 1.0,
                "result": result,
                "message": "Job completed successfully"
            })
            
        except Exception as e:
            # Job failed
            await self.manager.send_to_client(client_id, MessageType.JOB_FAILED, {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
                "message": "Job processing failed"
            })
    
    async def handle_client(self, websocket, path):
        """Gestisce una nuova connessione client."""
        
        client_id = await self.manager.add_client(websocket)
        
        try:
            async for message in websocket:
                await self.manager.handle_message(client_id, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            await self.manager.remove_client(client_id)
    
    async def start_server(self):
        """Avvia il server WebSocket."""
        
        if not WEBSOCKETS_AVAILABLE:
            logger.error("❌ WebSockets library not available")
            return
        
        logger.info(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        logger.info(f"✅ WebSocket server started on ws://{self.host}:{self.port}")
    
    async def stop_server(self):
        """Ferma il server WebSocket."""
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("🛑 WebSocket server stopped")

class FlaskSocketIOIntegration:
    """Integrazione con Flask-SocketIO come alternativa."""
    
    def __init__(self, flask_app: Flask):
        if not FLASK_SOCKETIO_AVAILABLE:
            raise ImportError("Flask-SocketIO not available")
        
        self.app = flask_app
        self.socketio = SocketIO(flask_app, cors_allowed_origins="*")
        self.manager = WebSocketManager()
        
        self._register_socketio_handlers()
    
    def _register_socketio_handlers(self):
        """Registra handler per Flask-SocketIO."""
        
        @self.socketio.on('connect')
        def handle_connect():
            client_id = str(uuid.uuid4())
            # Store client_id in session or similar
            emit('connected', {'client_id': client_id})
            logger.info(f"SocketIO client connected: {client_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("SocketIO client disconnected")
        
        @self.socketio.on('message')
        def handle_message(data):
            # Handle message similar to WebSocket version
            logger.info(f"Received SocketIO message: {data}")
            
            # Echo back for demo
            emit('response', {'status': 'received', 'data': data})
    
    def run(self, host: str = "localhost", port: int = 5001, debug: bool = False):
        """Avvia il server Flask-SocketIO."""
        
        logger.info(f"🚀 Starting Flask-SocketIO server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Client example and testing
class WebSocketClient:
    """Client WebSocket di esempio per testing."""
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.client_id = None
    
    async def connect(self):
        """Connette al server WebSocket."""
        
        if not WEBSOCKETS_AVAILABLE:
            logger.error("❌ WebSockets library not available")
            return
        
        self.websocket = await websockets.connect(self.uri)
        logger.info(f"🔗 Connected to {self.uri}")
        
        # Listen for messages
        asyncio.create_task(self._listen_for_messages())
    
    async def _listen_for_messages(self):
        """Ascolta messaggi dal server."""
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data['type'] == 'system_update' and 'client_id' in data['data']:
                    self.client_id = data['data']['client_id']
                    logger.info(f"📋 Assigned client ID: {self.client_id}")
                
                logger.info(f"📨 Received: {data['type']} - {data['data']}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Connection closed")
    
    async def send_message(self, message_type: MessageType, data: Dict[str, Any]):
        """Invia un messaggio al server."""
        
        if not self.websocket:
            logger.error("❌ Not connected")
            return
        
        message = {
            "type": message_type.value,
            "data": data,
            "message_id": str(uuid.uuid4())
        }
        
        await self.websocket.send(json.dumps(message))
        logger.info(f"📤 Sent: {message_type.value}")
    
    async def submit_job(self, expression: str):
        """Sottomette un job di analisi lambda."""
        
        await self.send_message(MessageType.JOB_SUBMIT, {
            "job_type": "lambda_analysis",
            "input_data": {
                "expression": expression,
                "strategy": "normal_order"
            }
        })
    
    async def subscribe_to_jobs(self):
        """Si sottoscrive agli aggiornamenti dei job."""
        
        await self.send_message(MessageType.SUBSCRIBE, {
            "subscription_type": "my_jobs"
        })

# Test function
async def test_websocket_system():
    """Testa il sistema WebSocket."""
    
    print("🧪 Testing WebSocket Communication System")
    print("=" * 50)
    
    if not WEBSOCKETS_AVAILABLE:
        print("❌ WebSockets not available, skipping test")
        return
    
    # Start server
    server = LambdaVisualizerWebSocketServer()
    await server.start_server()
    
    # Give server time to start
    await asyncio.sleep(1)
    
    # Create client
    client = WebSocketClient()
    await client.connect()
    
    # Give connection time to establish
    await asyncio.sleep(1)
    
    # Test job submission
    await client.submit_job("λx.x")
    
    # Wait for job to complete
    await asyncio.sleep(6)
    
    # Stop server
    await server.stop_server()
    
    print("🎉 WebSocket tests completed!")

if __name__ == "__main__":
    if WEBSOCKETS_AVAILABLE:
        asyncio.run(test_websocket_system())
    else:
        print("❌ WebSockets library not available. Install with: pip install websockets")
        print("   Or use Flask-SocketIO alternative: pip install flask-socketio")
