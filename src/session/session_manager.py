"""Session management for persistent state across agent runs."""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import pickle


class SessionManager:
    """
    Manages agent sessions with persistent state storage and recovery.
    Handles session lifecycle, state snapshots, and recovery from interruptions.
    """
    
    def __init__(self, config, memory_manager=None):
        """Initialize session manager."""
        self.config = config
        self.memory = memory_manager
        self.sessions_dir = config.get('session.storage_dir', './data/sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.current_session = None
        self.session_id = None
        self.auto_save = config.get('session.auto_save', True)
        self.save_interval = config.get('session.save_interval', 60)
        self.auto_save_task = None
        self.session_history = []
        
    async def start_session(self, session_id: Optional[str] = None, initial_state: Optional[Dict] = None) -> str:
        """Start a new session or resume existing one."""
        if session_id:
            logger.info(f"Attempting to resume session: {session_id}")
            resumed = await self.resume_session(session_id)
            if resumed:
                return session_id
            else:
                logger.warning(f"Could not resume session {session_id}, starting new one")
        
        new_session_id = self._generate_session_id()
        logger.info(f"Starting new session: {new_session_id}")
        
        self.session_id = new_session_id
        self.current_session = {
            'session_id': new_session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'state': initial_state or {},
            'snapshots': [],
            'events': [],
            'metadata': {'version': '1.0', 'agent_version': self.config.get('agent.version', '1.0')}
        }
        
        await self.save_session()
        
        if self.auto_save:
            await self._start_auto_save()
        
        return new_session_id
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"session_{timestamp}"
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume a previous session."""
        logger.info(f"Resuming session: {session_id}")
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            logger.warning(f"Session file not found: {session_file}")
            return False
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            self.session_id = session_id
            self.current_session = session_data
            self.current_session['last_updated'] = datetime.now().isoformat()
            
            await self.add_event('session_resumed', {'resumed_at': datetime.now().isoformat()})
            logger.info(f"Session resumed successfully: {session_id}")
            
            if self.auto_save:
                await self._start_auto_save()
            
            return True
        except Exception as e:
            logger.error(f"Failed to resume session: {e}")
            return False
    
    async def save_session(self) -> bool:
        """Save current session to disk."""
        if not self.current_session:
            logger.warning("No active session to save")
            return False
        
        try:
            self.current_session['last_updated'] = datetime.now().isoformat()
            session_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")
            
            with open(session_file, 'w') as f:
                json.dump(self.current_session, f, indent=2, default=str)
            
            logger.debug(f"Session saved: {session_file}")
            
            if self.memory:
                await self.memory.store_session(self.current_session)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    async def _start_auto_save(self) -> None:
        """Start auto-save background task."""
        if self.auto_save_task:
            self.auto_save_task.cancel()
        
        async def auto_save_loop():
            while True:
                try:
                    await asyncio.sleep(self.save_interval)
                    await self.save_session()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Auto-save error: {e}")
        
        self.auto_save_task = asyncio.create_task(auto_save_loop())
        logger.info(f"Auto-save started (interval: {self.save_interval}s)")
    
    async def create_snapshot(self, description: str = "") -> str:
        """Create a snapshot of current session state."""
        if not self.current_session:
            raise ValueError("No active session")
        
        snapshot_id = f"snapshot_{len(self.current_session['snapshots'])}"
        snapshot = {
            'id': snapshot_id,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'state': self.current_session['state'].copy()
        }
        
        self.current_session['snapshots'].append(snapshot)
        logger.info(f"Snapshot created: {snapshot_id}")
        await self.save_session()
        
        return snapshot_id
    
    async def update_state(self, key: str, value: Any) -> None:
        """Update session state."""
        if not self.current_session:
            raise ValueError("No active session")
        self.current_session['state'][key] = value
        logger.debug(f"State updated: {key}")
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get session state value."""
        if not self.current_session:
            return default
        return self.current_session['state'].get(key, default)
    
    async def add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Add an event to session history."""
        if not self.current_session:
            raise ValueError("No active session")
        
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.current_session['events'].append(event)
        max_events = self.config.get('session.max_events', 1000)
        if len(self.current_session['events']) > max_events:
            self.current_session['events'] = self.current_session['events'][-max_events:]
    
    async def end_session(self, save_final: bool = True) -> Dict[str, Any]:
        """End current session."""
        if not self.current_session:
            logger.warning("No active session to end")
            return {}
        
        logger.info(f"Ending session: {self.session_id}")
        
        if self.auto_save_task:
            self.auto_save_task.cancel()
            self.auto_save_task = None
        
        await self.add_event('session_ended', {'ended_at': datetime.now().isoformat()})
        
        created_at = datetime.fromisoformat(self.current_session['created_at'])
        duration = (datetime.now() - created_at).total_seconds()
        
        summary = {
            'session_id': self.session_id,
            'duration_seconds': duration,
            'events_count': len(self.current_session['events']),
            'snapshots_count': len(self.current_session['snapshots']),
            'final_state': self.current_session['state'].copy()
        }
        
        if save_final:
            await self.save_session()
        
        self.session_history.append(summary)
        self.current_session = None
        self.session_id = None
        
        logger.info(f"Session ended: {duration:.0f}s duration, {summary['events_count']} events")
        return summary
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        sessions = []
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            session_data = json.load(f)
                        sessions.append({
                            'session_id': session_data['session_id'],
                            'created_at': session_data['created_at'],
                            'last_updated': session_data['last_updated'],
                            'events_count': len(session_data.get('events', [])),
                            'snapshots_count': len(session_data.get('snapshots', []))
                        })
                    except Exception as e:
                        logger.warning(f"Error reading session file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
        
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self.session_id
