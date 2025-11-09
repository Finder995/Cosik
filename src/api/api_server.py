"""
REST API Server for Remote Control of Cosik AI Agent.

Features:
- RESTful API for remote agent control
- WebSocket support for real-time updates
- API authentication and authorization
- Task submission and monitoring
- Health and status endpoints
- Webhook support for event notifications
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import secrets
import hashlib
from loguru import logger

try:
    from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Header
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not available - REST API will not work. Install with: pip install fastapi uvicorn websockets")


# Pydantic models for request/response
if FASTAPI_AVAILABLE:
    class TaskRequest(BaseModel):
        """Task submission request."""
        command: str
        priority: Optional[int] = 2
        timeout: Optional[float] = None
        metadata: Optional[Dict[str, Any]] = None
    
    class TaskResponse(BaseModel):
        """Task submission response."""
        task_id: str
        status: str
        message: str
    
    class TaskStatusResponse(BaseModel):
        """Task status response."""
        task_id: str
        status: str
        created_at: str
        started_at: Optional[str] = None
        completed_at: Optional[str] = None
        result: Optional[Any] = None
        error: Optional[str] = None
    
    class AgentStatusResponse(BaseModel):
        """Agent status response."""
        is_running: bool
        active_tasks: int
        completed_tasks: int
        failed_tasks: int
        uptime_seconds: float
        performance: Dict[str, Any]


@dataclass
class APIKey:
    """API key with metadata."""
    key: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None
    permissions: List[str] = None


class APIAuthentication:
    """API key authentication system."""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.master_key: Optional[str] = None
    
    def generate_master_key(self) -> str:
        """Generate master API key."""
        self.master_key = secrets.token_urlsafe(32)
        logger.info("Master API key generated")
        return self.master_key
    
    def create_api_key(self, name: str, permissions: Optional[List[str]] = None) -> str:
        """Create a new API key."""
        key = secrets.token_urlsafe(32)
        api_key = APIKey(
            key=key,
            name=name,
            created_at=datetime.now(),
            permissions=permissions or ['read', 'write']
        )
        self.api_keys[key] = api_key
        logger.info(f"API key created: {name}")
        return key
    
    def validate_key(self, key: str) -> bool:
        """Validate an API key."""
        if key == self.master_key:
            return True
        
        if key in self.api_keys:
            self.api_keys[key].last_used = datetime.now()
            return True
        
        return False
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key."""
        if key in self.api_keys:
            del self.api_keys[key]
            logger.info(f"API key revoked")
            return True
        return False
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all API keys."""
        return [
            {
                'name': api_key.name,
                'created_at': api_key.created_at.isoformat(),
                'last_used': api_key.last_used.isoformat() if api_key.last_used else None,
                'permissions': api_key.permissions
            }
            for api_key in self.api_keys.values()
        ]


class WebhookManager:
    """Manage webhooks for event notifications."""
    
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}  # event_type -> [urls]
    
    def register_webhook(self, event_type: str, url: str):
        """Register a webhook URL for an event type."""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        if url not in self.webhooks[event_type]:
            self.webhooks[event_type].append(url)
            logger.info(f"Webhook registered: {event_type} -> {url}")
    
    def unregister_webhook(self, event_type: str, url: str):
        """Unregister a webhook URL."""
        if event_type in self.webhooks and url in self.webhooks[event_type]:
            self.webhooks[event_type].remove(url)
            logger.info(f"Webhook unregistered: {event_type} -> {url}")
    
    async def trigger_webhook(self, event_type: str, data: Dict[str, Any]):
        """Trigger webhooks for an event."""
        if event_type not in self.webhooks:
            return
        
        try:
            import aiohttp
            
            for url in self.webhooks[event_type]:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            url,
                            json={
                                'event_type': event_type,
                                'timestamp': datetime.now().isoformat(),
                                'data': data
                            },
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                logger.info(f"Webhook delivered: {url}")
                            else:
                                logger.warning(f"Webhook failed: {url} (status={response.status})")
                except Exception as e:
                    logger.error(f"Webhook error for {url}: {e}")
        except ImportError:
            logger.warning("aiohttp not available - webhooks disabled")


class APIServer:
    """
    REST API server for remote control of Cosik AI Agent.
    
    Features:
    - Task submission and monitoring
    - Agent status and control
    - Real-time WebSocket updates
    - Authentication and authorization
    - Webhook notifications
    """
    
    def __init__(self, agent, host: str = "127.0.0.1", port: int = 8000):
        """
        Initialize API server.
        
        Args:
            agent: CosikAgent instance
            host: Server host
            port: Server port
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for API server. Install with: pip install fastapi uvicorn websockets")
        
        self.agent = agent
        self.host = host
        self.port = port
        
        # Initialize components
        self.auth = APIAuthentication()
        self.webhook_manager = WebhookManager()
        
        # Generate master key
        self.master_key = self.auth.generate_master_key()
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Server startup time
        self.start_time = datetime.now()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Cosik AI Agent API",
            description="REST API for remote control of Cosik AI Agent",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Security
        self.security = HTTPBearer()
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"API Server initialized (http://{host}:{port})")
        logger.info(f"Master API Key: {self.master_key}")
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Verify API token."""
        if not self.auth.validate_key(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return credentials.credentials
    
    def _setup_routes(self):
        """Setup API routes."""
        
        # Health check (no auth required)
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }
        
        # Agent status
        @self.app.get("/api/status", response_model=AgentStatusResponse)
        async def get_status(token: str = Depends(self.verify_token)):
            """Get agent status."""
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Get queue stats if available
            queue_stats = {}
            if hasattr(self.agent, 'task_queue'):
                queue_stats = self.agent.task_queue.get_queue_stats()
            
            # Get performance stats if available
            perf_stats = {}
            if hasattr(self.agent, 'performance_monitor'):
                perf_stats = self.agent.performance_monitor.get_performance_summary()
            
            return AgentStatusResponse(
                is_running=self.agent.is_running,
                active_tasks=queue_stats.get('running', 0),
                completed_tasks=queue_stats.get('completed', 0),
                failed_tasks=queue_stats.get('failed', 0),
                uptime_seconds=uptime,
                performance=perf_stats
            )
        
        # Submit task
        @self.app.post("/api/tasks", response_model=TaskResponse)
        async def submit_task(
            task: TaskRequest,
            token: str = Depends(self.verify_token)
        ):
            """Submit a new task."""
            try:
                # Parse command and create task
                parsed = await self.agent.process_natural_language(task.command)
                
                # Add to queue
                task_id = f"task_{datetime.now().timestamp()}"
                await self.agent.task_queue.append(parsed)
                
                # Trigger webhook
                await self.webhook_manager.trigger_webhook('task_submitted', {
                    'task_id': task_id,
                    'command': task.command
                })
                
                # Notify WebSocket clients
                await self._broadcast_websocket({
                    'event': 'task_submitted',
                    'task_id': task_id,
                    'command': task.command
                })
                
                return TaskResponse(
                    task_id=task_id,
                    status="submitted",
                    message="Task submitted successfully"
                )
            except Exception as e:
                logger.error(f"Task submission error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Get task status
        @self.app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
        async def get_task_status(
            task_id: str,
            token: str = Depends(self.verify_token)
        ):
            """Get task status."""
            # This would integrate with task queue to get real status
            # For now, return mock data
            return TaskStatusResponse(
                task_id=task_id,
                status="completed",
                created_at=datetime.now().isoformat(),
                started_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                result={"success": True}
            )
        
        # Stop agent
        @self.app.post("/api/stop")
        async def stop_agent(token: str = Depends(self.verify_token)):
            """Stop the agent."""
            await self.agent.stop()
            return {"status": "stopping", "message": "Agent shutdown initiated"}
        
        # API key management
        @self.app.post("/api/keys")
        async def create_key(
            name: str,
            permissions: Optional[List[str]] = None,
            token: str = Depends(self.verify_token)
        ):
            """Create a new API key (requires master key)."""
            if token != self.master_key:
                raise HTTPException(status_code=403, detail="Master key required")
            
            key = self.auth.create_api_key(name, permissions)
            return {"key": key, "name": name}
        
        @self.app.get("/api/keys")
        async def list_keys(token: str = Depends(self.verify_token)):
            """List API keys (requires master key)."""
            if token != self.master_key:
                raise HTTPException(status_code=403, detail="Master key required")
            
            return {"keys": self.auth.list_keys()}
        
        @self.app.delete("/api/keys/{key}")
        async def revoke_key(
            key: str,
            token: str = Depends(self.verify_token)
        ):
            """Revoke an API key (requires master key)."""
            if token != self.master_key:
                raise HTTPException(status_code=403, detail="Master key required")
            
            success = self.auth.revoke_key(key)
            if success:
                return {"status": "revoked"}
            else:
                raise HTTPException(status_code=404, detail="Key not found")
        
        # Webhook management
        @self.app.post("/api/webhooks")
        async def register_webhook(
            event_type: str,
            url: str,
            token: str = Depends(self.verify_token)
        ):
            """Register a webhook."""
            self.webhook_manager.register_webhook(event_type, url)
            return {"status": "registered", "event_type": event_type, "url": url}
        
        @self.app.delete("/api/webhooks")
        async def unregister_webhook(
            event_type: str,
            url: str,
            token: str = Depends(self.verify_token)
        ):
            """Unregister a webhook."""
            self.webhook_manager.unregister_webhook(event_type, url)
            return {"status": "unregistered"}
        
        # WebSocket endpoint
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                # Send welcome message
                await websocket.send_json({
                    'event': 'connected',
                    'message': 'Connected to Cosik AI Agent',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep connection alive
                while True:
                    data = await websocket.receive_text()
                    # Echo back for now
                    await websocket.send_json({
                        'event': 'echo',
                        'data': data
                    })
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                logger.info("WebSocket client disconnected")
    
    async def _broadcast_websocket(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")
    
    async def start(self):
        """Start the API server."""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the API server (blocking)."""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port
        )
