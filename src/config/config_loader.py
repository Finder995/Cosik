"""Configuration loader for Cosik AI Agent."""

import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from loguru import logger


class ConfigLoader:
    """Load and manage configuration for the agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'agent': {
                'name': 'Cosik',
                'version': '1.0.0',
                'auto_continuation': True,
                'max_retries': 3
            },
            'ai': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7
            },
            'memory': {
                'enabled': True,
                'storage_path': './data/memory'
            },
            'logging': {
                'level': 'INFO',
                'file_path': './logs/agent.log'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'agent.name')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    async def update(self, changes: Dict[str, Any]) -> bool:
        """
        Update configuration and save to file.
        
        Args:
            changes: Dictionary of changes to apply
            
        Returns:
            True if successful
        """
        try:
            # Apply changes
            self._apply_changes(self.config, changes)
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info("Configuration updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
    
    def _apply_changes(self, config: Dict, changes: Dict):
        """Recursively apply changes to configuration."""
        for key, value in changes.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                self._apply_changes(config[key], value)
            else:
                config[key] = value
