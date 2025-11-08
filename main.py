"""
Cosik AI Agent - Core Module

An advanced AI agent for Windows 10 with GUI automation capabilities.
Supports natural language understanding, task automation, and self-modification.
"""

import os
import sys
import asyncio
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime

from src.nlp.language_processor import LanguageProcessor
from src.automation.gui_controller import GUIController
from src.memory.memory_manager import MemoryManager
from src.tasks.task_executor import TaskExecutor
from src.system.system_manager import SystemManager
from src.config.config_loader import ConfigLoader
from src.ai.ai_engine import AIEngine
from src.plugins.plugin_manager import PluginManager
from src.vision.computer_vision import ComputerVision


class CosikAgent:
    """
    Main AI Agent class that orchestrates all components.
    
    Features:
    - Natural language understanding
    - GUI automation
    - Persistent memory
    - Auto-continuation
    - Self-modification
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Cosik AI Agent."""
        logger.info("Initializing Cosik AI Agent...")
        
        # Load configuration
        self.config = ConfigLoader(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize AI engine first
        self.ai_engine = AIEngine(self.config)
        
        # Initialize computer vision
        self.vision = ComputerVision(self.config)
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager(self.config)
        self.plugin_manager.load_all_plugins()
        
        # Initialize components
        self.nlp = LanguageProcessor(self.config, ai_engine=self.ai_engine)
        self.gui = GUIController(self.config, vision=self.vision)
        self.memory = MemoryManager(self.config)
        self.task_executor = TaskExecutor(self.config, self.gui, self.memory, ai_engine=self.ai_engine)
        self.system = SystemManager(self.config)
        
        # Agent state
        self.is_running = False
        self.current_task = None
        self.task_queue = []
        
        logger.info("Cosik AI Agent initialized successfully")
    
    def _setup_logging(self):
        """Configure logging system."""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file_path', './logs/agent.log')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logger
        logger.remove()
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        logger.add(
            log_file,
            rotation=log_config.get('max_size', '10 MB'),
            retention=log_config.get('backup_count', 5),
            level=log_level
        )
    
    async def process_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Process natural language input and extract tasks/commands.
        
        Args:
            text: Natural language text from user
            
        Returns:
            Parsed command structure with intent and parameters
        """
        logger.info(f"Processing natural language: {text[:50]}...")
        
        # Parse the natural language
        parsed = await self.nlp.parse(text)
        
        # Store in memory
        await self.memory.add_interaction(
            input_text=text,
            parsed_result=parsed,
            timestamp=datetime.now()
        )
        
        return parsed
    
    async def execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Execute a single task.
        
        Args:
            task: Task dictionary with type, parameters, etc.
            
        Returns:
            True if task completed successfully, False otherwise
        """
        self.current_task = task
        logger.info(f"Executing task: {task.get('intent', 'unknown')}")
        
        try:
            result = await self.task_executor.execute(task)
            
            # Store result in memory
            await self.memory.add_task_result(task, result)
            
            # Check if task needs continuation
            if result.get('needs_continuation', False):
                continuation_tasks = result.get('continuation_tasks', [])
                self.task_queue.extend(continuation_tasks)
                logger.info(f"Task requires continuation with {len(continuation_tasks)} sub-tasks")
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            await self.memory.add_error(task, str(e))
            return False
        finally:
            self.current_task = None
    
    async def run(self, command: Optional[str] = None):
        """
        Main run loop for the agent.
        
        Args:
            command: Initial command to execute (optional)
        """
        self.is_running = True
        logger.info("Starting Cosik AI Agent...")
        
        if command:
            # Process initial command
            parsed = await self.process_natural_language(command)
            self.task_queue.append(parsed)
        
        # Main execution loop
        while self.is_running:
            try:
                # Check if there are tasks to execute
                if not self.task_queue:
                    # Check for auto-continuation
                    if self.config.get('agent.auto_continuation', True):
                        # Analyze memory to see if there are incomplete tasks
                        incomplete = await self.memory.get_incomplete_tasks()
                        if incomplete:
                            logger.info(f"Found {len(incomplete)} incomplete tasks for auto-continuation")
                            self.task_queue.extend(incomplete)
                        else:
                            # No more tasks, wait for input
                            logger.info("No pending tasks. Waiting for input...")
                            break
                    else:
                        break
                
                # Get next task
                task = self.task_queue.pop(0)
                
                # Execute task
                success = await self.execute_task(task)
                
                if not success:
                    # Handle failure with retries
                    max_retries = self.config.get('agent.max_retries', 3)
                    retry_count = task.get('retry_count', 0)
                    
                    if retry_count < max_retries:
                        task['retry_count'] = retry_count + 1
                        self.task_queue.insert(0, task)  # Re-add to front of queue
                        logger.warning(f"Task failed, retrying ({retry_count + 1}/{max_retries})")
                    else:
                        logger.error(f"Task failed after {max_retries} retries")
                
                # Small delay between tasks
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
        
        logger.info("Cosik AI Agent stopped")
    
    async def stop(self):
        """Stop the agent gracefully."""
        logger.info("Stopping agent...")
        self.is_running = False
        
        # Save state
        await self.memory.save_state()
    
    async def self_modify(self, modification_request: Dict[str, Any]) -> bool:
        """
        Perform self-modification based on request.
        
        Args:
            modification_request: Details about what to modify
            
        Returns:
            True if modification successful
        """
        if not self.config.get('self_modification.enabled', False):
            logger.warning("Self-modification is disabled")
            return False
        
        logger.info("Performing self-modification...")
        
        try:
            mod_type = modification_request.get('type')
            
            if mod_type == 'code':
                # Modify code files
                file_path = modification_request.get('file_path')
                changes = modification_request.get('changes')
                
                # Backup first
                if self.config.get('self_modification.backup_before_modify', True):
                    await self.system.backup_file(file_path)
                
                # Apply changes
                await self.system.modify_file(file_path, changes)
                
            elif mod_type == 'config':
                # Modify configuration
                config_changes = modification_request.get('changes')
                await self.config.update(config_changes)
            
            # Store modification in memory
            await self.memory.add_self_modification(modification_request)
            
            logger.info("Self-modification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Self-modification failed: {e}")
            return False


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cosik AI Agent for Windows 10')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--command', help='Initial command to execute')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Create agent
    agent = CosikAgent(config_path=args.config)
    
    try:
        if args.interactive:
            # Interactive mode
            print("Cosik AI Agent - Interactive Mode")
            print("Type 'exit' to quit\n")
            
            while True:
                command = input("Cosik> ")
                if command.lower() in ['exit', 'quit']:
                    break
                
                if command.strip():
                    await agent.run(command)
        else:
            # Single command mode
            await agent.run(args.command)
    
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
