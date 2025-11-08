"""Task execution module for the AI agent."""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger


class TaskExecutor:
    """Execute tasks based on parsed intents."""
    
    def __init__(self, config, gui_controller, memory_manager, ai_engine=None):
        """
        Initialize task executor.
        
        Args:
            config: Configuration object
            gui_controller: GUI controller instance
            memory_manager: Memory manager instance
            ai_engine: AI engine instance for advanced features
        """
        self.config = config
        self.gui = gui_controller
        self.memory = memory_manager
        self.ai_engine = ai_engine
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task based on its intent.
        
        Args:
            task: Task dictionary with intent and parameters
            
        Returns:
            Result dictionary with success status and any data
        """
        intent = task.get('intent', 'unknown')
        parameters = task.get('parameters', {})
        
        logger.info(f"Executing task: {intent}")
        
        try:
            # Route to appropriate handler
            if intent == 'open_application':
                return await self._open_application(parameters)
            elif intent == 'close_application':
                return await self._close_application(parameters)
            elif intent == 'click':
                return await self._click(parameters)
            elif intent == 'type_text':
                return await self._type_text(parameters)
            elif intent == 'read_file':
                return await self._read_file(parameters)
            elif intent == 'write_file':
                return await self._write_file(parameters)
            elif intent == 'modify_file':
                return await self._modify_file(parameters)
            elif intent == 'system_command':
                return await self._system_command(parameters)
            elif intent == 'change_setting':
                return await self._change_setting(parameters)
            elif intent == 'search':
                return await self._search(parameters)
            elif intent == 'move_mouse':
                return await self._move_mouse(parameters)
            elif intent == 'take_screenshot':
                return await self._take_screenshot(parameters)
            elif intent == 'wait':
                return await self._wait(parameters)
            elif intent == 'complex_task':
                return await self._complex_task(parameters)
            else:
                logger.warning(f"Unknown intent: {intent}")
                return {
                    'success': False,
                    'error': f'Unknown intent: {intent}'
                }
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open an application."""
        app_name = params.get('application', '')
        
        logger.info(f"Opening application: {app_name}")
        
        # Use Windows Run dialog
        await self.gui.hotkey('win', 'r')
        await asyncio.sleep(0.5)
        await self.gui.type_text(app_name)
        await self.gui.press_key('enter')
        
        # Wait for application to open
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'message': f'Opened {app_name}'
        }
    
    async def _close_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close an application."""
        app_name = params.get('application', '')
        
        logger.info(f"Closing application: {app_name}")
        
        success = await self.gui.close_window(app_name)
        
        return {
            'success': success,
            'message': f'Closed {app_name}' if success else f'Failed to close {app_name}'
        }
    
    async def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a click action."""
        target = params.get('target', '')
        
        logger.info(f"Clicking: {target}")
        
        # This is simplified - in a real implementation, you would use 
        # image recognition or UI element detection
        success = await self.gui.click()
        
        return {
            'success': success,
            'message': 'Click performed'
        }
    
    async def _type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Type text."""
        text = params.get('text', '')
        
        logger.info(f"Typing text: {text[:30]}...")
        
        success = await self.gui.type_text(text)
        
        return {
            'success': success,
            'message': 'Text typed successfully'
        }
    
    async def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file."""
        file_path = params.get('file_path', '')
        
        logger.info(f"Reading file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'message': f'Read {len(content)} characters from {file_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file."""
        file_path = params.get('file_path', '')
        content = params.get('content', '')
        
        logger.info(f"Writing to file: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f'Wrote {len(content)} characters to {file_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _modify_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify a file."""
        file_path = params.get('file_path', '')
        modifications = params.get('modifications', [])
        
        logger.info(f"Modifying file: {file_path}")
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply modifications (simplified)
            # In a real implementation, this would parse the modifications
            # and apply them intelligently
            
            return {
                'success': True,
                'message': f'Modified {file_path}',
                'needs_continuation': True,
                'continuation_tasks': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _system_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a system command."""
        command = params.get('command', '')
        
        logger.info(f"Executing system command: {command}")
        
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _change_setting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Change a system setting."""
        setting = params.get('setting', '')
        
        logger.info(f"Changing setting: {setting}")
        
        # This would integrate with Windows registry or settings API
        # For now, return a placeholder
        
        return {
            'success': True,
            'message': f'Setting change requested: {setting}',
            'needs_continuation': True
        }
    
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a search."""
        query = params.get('query', '')
        
        logger.info(f"Searching for: {query}")
        
        # Open Windows search
        await self.gui.hotkey('win', 's')
        await asyncio.sleep(0.5)
        await self.gui.type_text(query)
        
        return {
            'success': True,
            'message': f'Search initiated for: {query}'
        }
    
    async def _move_mouse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move the mouse."""
        target = params.get('target', '')
        
        # Parse coordinates if numeric
        # This is simplified - real implementation would parse targets better
        
        logger.info(f"Moving mouse to: {target}")
        
        return {
            'success': True,
            'message': 'Mouse moved'
        }
    
    async def _take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot."""
        logger.info("Taking screenshot")
        
        filename = await self.gui.take_screenshot()
        
        return {
            'success': filename is not None,
            'filename': filename,
            'message': f'Screenshot saved to {filename}' if filename else 'Screenshot failed'
        }
    
    async def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for specified duration."""
        duration = params.get('duration', 1)
        
        logger.info(f"Waiting for {duration} seconds")
        await asyncio.sleep(duration)
        
        return {
            'success': True,
            'message': f'Waited {duration} seconds'
        }
    
    async def _complex_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex tasks that need AI planning."""
        description = params.get('description', '')
        
        logger.info(f"Processing complex task: {description}")
        
        # Use AI engine to create a task plan
        if self.ai_engine:
            logger.info("Using AI engine to create task plan")
            try:
                plan = await self.ai_engine.create_task_plan(description)
                
                if plan:
                    logger.info(f"AI created plan with {len(plan)} steps")
                    # Convert plan steps to tasks
                    continuation_tasks = []
                    for step in plan:
                        continuation_tasks.append({
                            'intent': step.get('intent', 'unknown'),
                            'parameters': step.get('parameters', {}),
                            'description': step.get('description', '')
                        })
                    
                    return {
                        'success': True,
                        'message': f'Created plan with {len(plan)} steps',
                        'needs_continuation': True,
                        'continuation_tasks': continuation_tasks
                    }
            except Exception as e:
                logger.error(f"AI planning failed: {e}")
        
        # Fallback if AI not available
        return {
            'success': True,
            'message': 'Complex task requires AI planning (not fully implemented)',
            'needs_continuation': False
        }
