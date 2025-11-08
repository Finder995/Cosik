"""System management module for file operations and system access."""

import os
import shutil
import winreg
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from loguru import logger


class SystemManager:
    """Manage system-level operations including file I/O and registry access."""
    
    def __init__(self, config):
        """Initialize system manager."""
        self.config = config
        self.backup_path = Path(config.get('file_operations.backup_path', './data/backups'))
        self.backup_enabled = config.get('file_operations.backup_enabled', True)
        self.safe_mode = config.get('system.safe_mode', False)
        
        # Create backup directory
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    async def read_file(self, file_path: str) -> Optional[str]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None if failed
        """
        try:
            logger.info(f"Reading file: {file_path}")
            
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def write_file(self, file_path: str, content: str, 
                        backup: bool = True) -> bool:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file
            content: Content to write
            backup: Whether to backup existing file
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Writing to file: {file_path}")
            
            path = Path(file_path)
            
            # Backup existing file
            if backup and self.backup_enabled and path.exists():
                await self.backup_file(file_path)
            
            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote {len(content)} characters to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    async def modify_file(self, file_path: str, changes: Dict[str, Any]) -> bool:
        """
        Modify a file based on changes specification.
        
        Args:
            file_path: Path to file
            changes: Dictionary of changes to apply
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Modifying file: {file_path}")
            
            # Read current content
            content = await self.read_file(file_path)
            if content is None:
                return False
            
            # Backup
            if self.backup_enabled:
                await self.backup_file(file_path)
            
            # Apply changes
            modified_content = content
            
            # Handle different change types
            if 'replacements' in changes:
                for old, new in changes['replacements'].items():
                    modified_content = modified_content.replace(old, new)
            
            if 'insertions' in changes:
                for line_num, text in changes['insertions'].items():
                    lines = modified_content.split('\n')
                    lines.insert(int(line_num), text)
                    modified_content = '\n'.join(lines)
            
            if 'deletions' in changes:
                for line_num in changes['deletions']:
                    lines = modified_content.split('\n')
                    del lines[int(line_num)]
                    modified_content = '\n'.join(lines)
            
            # Write modified content
            return await self.write_file(file_path, modified_content, backup=False)
        except Exception as e:
            logger.error(f"Error modifying file {file_path}: {e}")
            return False
    
    async def backup_file(self, file_path: str) -> Optional[str]:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Cannot backup non-existent file: {file_path}")
                return None
            
            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{path.stem}_{timestamp}{path.suffix}"
            backup_file = self.backup_path / backup_name
            
            # Copy file
            shutil.copy2(path, backup_file)
            
            logger.info(f"Backed up {file_path} to {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Error backing up file {file_path}: {e}")
            return None
    
    async def delete_file(self, file_path: str, backup: bool = True) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file
            backup: Whether to backup before deleting
            
        Returns:
            True if successful
        """
        if self.safe_mode:
            logger.warning("Safe mode enabled, file deletion blocked")
            return False
        
        try:
            logger.info(f"Deleting file: {file_path}")
            
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return False
            
            # Backup before deletion
            if backup and self.backup_enabled:
                await self.backup_file(file_path)
            
            path.unlink()
            logger.info(f"Deleted {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def list_directory(self, dir_path: str, 
                           pattern: str = "*") -> List[str]:
        """
        List files in a directory.
        
        Args:
            dir_path: Directory path
            pattern: File pattern (e.g., "*.txt")
            
        Returns:
            List of file paths
        """
        try:
            path = Path(dir_path)
            if not path.exists() or not path.is_dir():
                logger.error(f"Directory not found: {dir_path}")
                return []
            
            files = [str(f) for f in path.glob(pattern)]
            logger.info(f"Found {len(files)} files in {dir_path}")
            return files
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            return []
    
    async def create_directory(self, dir_path: str) -> bool:
        """
        Create a directory.
        
        Args:
            dir_path: Directory path
            
        Returns:
            True if successful
        """
        try:
            path = Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    
    async def get_registry_value(self, key_path: str, value_name: str) -> Optional[Any]:
        """
        Read a value from Windows registry.
        
        Args:
            key_path: Registry key path
            value_name: Value name
            
        Returns:
            Registry value or None
        """
        if not self.config.get('system.allow_registry_access', False):
            logger.warning("Registry access disabled")
            return None
        
        try:
            # Parse key path
            parts = key_path.split('\\')
            root_key_name = parts[0]
            sub_key = '\\'.join(parts[1:])
            
            # Map root key name to constant
            root_keys = {
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
            }
            
            root_key = root_keys.get(root_key_name)
            if root_key is None:
                logger.error(f"Invalid root key: {root_key_name}")
                return None
            
            # Open key and read value
            with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                logger.info(f"Read registry value: {key_path}\\{value_name}")
                return value
        except FileNotFoundError:
            logger.warning(f"Registry key not found: {key_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading registry: {e}")
            return None
    
    async def set_registry_value(self, key_path: str, value_name: str, 
                                value: Any, value_type: int = winreg.REG_SZ) -> bool:
        """
        Write a value to Windows registry.
        
        Args:
            key_path: Registry key path
            value_name: Value name
            value: Value to write
            value_type: Registry value type
            
        Returns:
            True if successful
        """
        if not self.config.get('system.allow_registry_access', False):
            logger.warning("Registry access disabled")
            return False
        
        if self.safe_mode:
            logger.warning("Safe mode enabled, registry modification blocked")
            return False
        
        try:
            # Parse key path
            parts = key_path.split('\\')
            root_key_name = parts[0]
            sub_key = '\\'.join(parts[1:])
            
            # Map root key name to constant
            root_keys = {
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
            }
            
            root_key = root_keys.get(root_key_name)
            if root_key is None:
                logger.error(f"Invalid root key: {root_key_name}")
                return False
            
            # Open/create key and set value
            with winreg.CreateKey(root_key, sub_key) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value)
                logger.info(f"Set registry value: {key_path}\\{value_name}")
                return True
        except Exception as e:
            logger.error(f"Error writing registry: {e}")
            return False
    
    async def execute_powershell(self, script: str) -> Dict[str, Any]:
        """
        Execute a PowerShell script.
        
        Args:
            script: PowerShell script content
            
        Returns:
            Result dictionary
        """
        if self.safe_mode:
            logger.warning("Safe mode enabled, PowerShell execution blocked")
            return {'success': False, 'error': 'Safe mode enabled'}
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"PowerShell execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
