"""
Clipboard Plugin for managing clipboard operations.
Allows the AI agent to read, write, and monitor clipboard content.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    logger.warning("pyperclip not installed. Install with: pip install pyperclip")


class ClipboardPlugin:
    """Plugin for clipboard management and monitoring."""
    
    def __init__(self, config):
        """Initialize clipboard plugin."""
        self.config = config
        self.history = []
        self.max_history = config.get('plugins.clipboard.max_history', 100)
        self.monitoring = False
        self.monitor_task = None
        
        if not CLIPBOARD_AVAILABLE:
            logger.warning("Clipboard plugin initialized but pyperclip is not available")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute clipboard command.
        
        Commands:
        - copy: Copy text to clipboard
        - paste: Get current clipboard content
        - history: Get clipboard history
        - clear: Clear clipboard
        - monitor_start: Start monitoring clipboard changes
        - monitor_stop: Stop monitoring clipboard changes
        """
        if not CLIPBOARD_AVAILABLE:
            return {
                'success': False,
                'error': 'pyperclip not installed',
                'message': 'Install pyperclip to use clipboard features'
            }
        
        try:
            if command == 'copy':
                return await self._copy(**kwargs)
            elif command == 'paste':
                return await self._paste(**kwargs)
            elif command == 'history':
                return await self._get_history(**kwargs)
            elif command == 'clear':
                return await self._clear(**kwargs)
            elif command == 'monitor_start':
                return await self._start_monitoring(**kwargs)
            elif command == 'monitor_stop':
                return await self._stop_monitoring(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}',
                    'available_commands': self.get_capabilities()
                }
        except Exception as e:
            logger.error(f"Clipboard plugin error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _copy(self, text: str, **kwargs) -> Dict[str, Any]:
        """Copy text to clipboard."""
        try:
            pyperclip.copy(text)
            self._add_to_history(text, 'copy')
            
            logger.info(f"Copied to clipboard: {text[:50]}...")
            return {
                'success': True,
                'message': 'Text copied to clipboard',
                'text': text
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to copy to clipboard: {e}'
            }
    
    async def _paste(self, **kwargs) -> Dict[str, Any]:
        """Get current clipboard content."""
        try:
            content = pyperclip.paste()
            self._add_to_history(content, 'paste')
            
            logger.info(f"Retrieved from clipboard: {content[:50]}...")
            return {
                'success': True,
                'content': content,
                'length': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to read clipboard: {e}'
            }
    
    async def _get_history(self, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """Get clipboard history."""
        history_items = self.history[-limit:] if limit > 0 else self.history
        
        return {
            'success': True,
            'history': history_items,
            'total_items': len(self.history),
            'returned_items': len(history_items)
        }
    
    async def _clear(self, **kwargs) -> Dict[str, Any]:
        """Clear clipboard."""
        try:
            pyperclip.copy('')
            self._add_to_history('', 'clear')
            
            logger.info("Clipboard cleared")
            return {
                'success': True,
                'message': 'Clipboard cleared'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to clear clipboard: {e}'
            }
    
    async def _start_monitoring(self, interval: float = 1.0, **kwargs) -> Dict[str, Any]:
        """Start monitoring clipboard for changes."""
        if self.monitoring:
            return {
                'success': False,
                'message': 'Monitoring already active'
            }
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        
        logger.info(f"Started clipboard monitoring (interval: {interval}s)")
        return {
            'success': True,
            'message': f'Started monitoring clipboard every {interval}s'
        }
    
    async def _stop_monitoring(self, **kwargs) -> Dict[str, Any]:
        """Stop monitoring clipboard."""
        if not self.monitoring:
            return {
                'success': False,
                'message': 'Monitoring not active'
            }
        
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped clipboard monitoring")
        return {
            'success': True,
            'message': 'Stopped clipboard monitoring'
        }
    
    async def _monitor_loop(self, interval: float):
        """Monitor clipboard for changes."""
        last_content = ""
        
        try:
            while self.monitoring:
                try:
                    current_content = pyperclip.paste()
                    
                    if current_content != last_content and current_content:
                        logger.info(f"Clipboard changed: {current_content[:50]}...")
                        self._add_to_history(current_content, 'detected')
                        last_content = current_content
                    
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in clipboard monitoring: {e}")
                    await asyncio.sleep(interval)
                    
        except asyncio.CancelledError:
            logger.info("Clipboard monitoring cancelled")
    
    def _add_to_history(self, content: str, operation: str):
        """Add item to clipboard history."""
        entry = {
            'content': content,
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'length': len(content)
        }
        
        self.history.append(entry)
        
        # Trim history if it exceeds max size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_capabilities(self) -> List[str]:
        """Return list of available commands."""
        return [
            'copy',
            'paste',
            'history',
            'clear',
            'monitor_start',
            'monitor_stop'
        ]
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_task:
                self.monitor_task.cancel()
        
        logger.info("Clipboard plugin cleaned up")


# Plugin metadata
PLUGIN_INFO = {
    'name': 'clipboard',
    'version': '1.0.0',
    'class': ClipboardPlugin,
    'description': 'Clipboard management and monitoring',
    'author': 'Cosik Team',
    'requires': ['pyperclip']
}
