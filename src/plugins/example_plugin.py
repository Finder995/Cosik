"""
Example plugin for extending Cosik AI Agent functionality.

This demonstrates the self-modification capability - the agent can load
and modify plugins to extend its capabilities.
"""

from loguru import logger


class ExamplePlugin:
    """Example plugin that adds custom functionality."""
    
    def __init__(self, agent):
        """
        Initialize plugin.
        
        Args:
            agent: Reference to main CosikAgent instance
        """
        self.agent = agent
        self.name = "example_plugin"
        logger.info(f"Plugin '{self.name}' initialized")
    
    async def execute(self, command: str, **kwargs):
        """
        Execute plugin-specific command.
        
        Args:
            command: Command to execute
            **kwargs: Additional parameters
            
        Returns:
            Result dictionary
        """
        logger.info(f"Plugin '{self.name}' executing: {command}")
        
        # Example custom functionality
        if command == "custom_action":
            return {
                'success': True,
                'message': 'Custom action executed',
                'plugin': self.name
            }
        
        return {
            'success': False,
            'error': f'Unknown command: {command}'
        }
    
    async def on_task_complete(self, task, result):
        """
        Hook called when a task completes.
        
        Args:
            task: The completed task
            result: Task result
        """
        logger.debug(f"Plugin '{self.name}' notified of task completion")
        # Custom post-processing can go here


# Plugin metadata
PLUGIN_INFO = {
    'name': 'example_plugin',
    'version': '1.0.0',
    'description': 'Example plugin for demonstration',
    'author': 'Cosik',
    'class': ExamplePlugin
}
