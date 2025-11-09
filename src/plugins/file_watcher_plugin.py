"""
File Watcher Plugin for monitoring file system changes.
Allows the AI agent to watch directories and files for changes.
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime
from loguru import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
    
    class FileChangeHandler(FileSystemEventHandler):
        """Handler for file system events."""
        
        def __init__(self, callback):
            """Initialize handler with callback."""
            super().__init__()
            self.callback = callback
        
        def on_any_event(self, event: 'FileSystemEvent'):
            """Handle any file system event."""
            if not event.is_directory:
                asyncio.create_task(self.callback(event))
                
except ImportError:
    WATCHDOG_AVAILABLE = False
    FileSystemEventHandler = None
    FileSystemEvent = None
    FileChangeHandler = None
    logger.warning("watchdog not installed. Install with: pip install watchdog")


class FileWatcherPlugin:
    """Plugin for watching file system changes."""
    
    def __init__(self, config):
        """Initialize file watcher plugin."""
        self.config = config
        self.observers = {}
        self.event_history = []
        self.max_history = config.get('plugins.file_watcher.max_history', 500)
        self.watched_paths = set()
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("File watcher plugin initialized but watchdog is not available")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute file watcher command.
        
        Commands:
        - watch: Start watching a path
        - unwatch: Stop watching a path
        - list: List watched paths
        - history: Get event history
        - clear_history: Clear event history
        """
        if not WATCHDOG_AVAILABLE:
            return {
                'success': False,
                'error': 'watchdog not installed',
                'message': 'Install watchdog to use file watching features'
            }
        
        try:
            if command == 'watch':
                return await self._watch(**kwargs)
            elif command == 'unwatch':
                return await self._unwatch(**kwargs)
            elif command == 'list':
                return await self._list_watched(**kwargs)
            elif command == 'history':
                return await self._get_history(**kwargs)
            elif command == 'clear_history':
                return await self._clear_history(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}',
                    'available_commands': self.get_capabilities()
                }
        except Exception as e:
            logger.error(f"File watcher plugin error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _watch(self, path: str, recursive: bool = True, **kwargs) -> Dict[str, Any]:
        """Start watching a path for changes."""
        try:
            path_obj = Path(path).resolve()
            
            if not path_obj.exists():
                return {
                    'success': False,
                    'error': f'Path does not exist: {path}'
                }
            
            path_str = str(path_obj)
            
            if path_str in self.watched_paths:
                return {
                    'success': False,
                    'message': f'Already watching: {path}'
                }
            
            # Create observer
            observer = Observer()
            handler = FileChangeHandler(self._on_file_event)
            observer.schedule(handler, path_str, recursive=recursive)
            observer.start()
            
            self.observers[path_str] = observer
            self.watched_paths.add(path_str)
            
            logger.info(f"Started watching: {path_str} (recursive: {recursive})")
            return {
                'success': True,
                'message': f'Started watching {path}',
                'path': path_str,
                'recursive': recursive
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to watch path: {e}'
            }
    
    async def _unwatch(self, path: str, **kwargs) -> Dict[str, Any]:
        """Stop watching a path."""
        try:
            path_obj = Path(path).resolve()
            path_str = str(path_obj)
            
            if path_str not in self.watched_paths:
                return {
                    'success': False,
                    'message': f'Not watching: {path}'
                }
            
            # Stop observer
            observer = self.observers[path_str]
            observer.stop()
            observer.join(timeout=2)
            
            del self.observers[path_str]
            self.watched_paths.remove(path_str)
            
            logger.info(f"Stopped watching: {path_str}")
            return {
                'success': True,
                'message': f'Stopped watching {path}',
                'path': path_str
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to unwatch path: {e}'
            }
    
    async def _list_watched(self, **kwargs) -> Dict[str, Any]:
        """List all watched paths."""
        return {
            'success': True,
            'watched_paths': list(self.watched_paths),
            'count': len(self.watched_paths)
        }
    
    async def _get_history(self, limit: int = 50, event_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get file event history."""
        history = self.event_history
        
        # Filter by event type if specified
        if event_type:
            history = [e for e in history if e['event_type'] == event_type]
        
        # Limit results
        history_items = history[-limit:] if limit > 0 else history
        
        return {
            'success': True,
            'events': history_items,
            'total_events': len(self.event_history),
            'returned_events': len(history_items),
            'filtered_by': event_type
        }
    
    async def _clear_history(self, **kwargs) -> Dict[str, Any]:
        """Clear event history."""
        count = len(self.event_history)
        self.event_history.clear()
        
        logger.info(f"Cleared {count} events from history")
        return {
            'success': True,
            'message': f'Cleared {count} events from history',
            'cleared_count': count
        }
    
    async def _on_file_event(self, event: 'FileSystemEvent'):
        """Handle file system event."""
        event_data = {
            'event_type': event.event_type,
            'src_path': event.src_path,
            'is_directory': event.is_directory,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add dest_path for moved events
        if hasattr(event, 'dest_path'):
            event_data['dest_path'] = event.dest_path
        
        self.event_history.append(event_data)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        logger.debug(f"File event: {event.event_type} - {event.src_path}")
    
    def get_capabilities(self) -> List[str]:
        """Return list of available commands."""
        return [
            'watch',
            'unwatch',
            'list',
            'history',
            'clear_history'
        ]
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        # Stop all observers
        for path, observer in self.observers.items():
            try:
                observer.stop()
                observer.join(timeout=2)
                logger.info(f"Stopped watching: {path}")
            except Exception as e:
                logger.error(f"Error stopping observer for {path}: {e}")
        
        self.observers.clear()
        self.watched_paths.clear()
        logger.info("File watcher plugin cleaned up")


# Plugin metadata
PLUGIN_INFO = {
    'name': 'file_watcher',
    'version': '1.0.0',
    'class': FileWatcherPlugin,
    'description': 'Monitor file system changes in real-time',
    'author': 'Cosik Team',
    'requires': ['watchdog']
}
