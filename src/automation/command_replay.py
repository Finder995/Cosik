"""
Command Replay System for Saving and Replaying Workflows.

Features:
- Save command sequences as workflows
- Replay workflows with parameters
- Workflow templates and variables
- Batch operations
- Import/export workflows
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from loguru import logger


@dataclass
class Command:
    """Represents a single command in a workflow."""
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    timeout: Optional[float] = None
    retry_on_failure: bool = True
    continue_on_error: bool = False


@dataclass
class Workflow:
    """Represents a workflow (sequence of commands)."""
    name: str
    commands: List[Command] = field(default_factory=list)
    description: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'commands': [asdict(cmd) for cmd in self.commands],
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'author': self.author,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create workflow from dictionary."""
        commands = [Command(**cmd) for cmd in data.get('commands', [])]
        
        return cls(
            name=data['name'],
            description=data.get('description'),
            commands=commands,
            variables=data.get('variables', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            tags=data.get('tags', []),
            author=data.get('author'),
            version=data.get('version', '1.0')
        )


class WorkflowRecorder:
    """Record commands as they are executed to create workflows."""
    
    def __init__(self):
        self.is_recording = False
        self.current_workflow: Optional[Workflow] = None
        self.recorded_commands: List[Command] = []
    
    def start_recording(self, workflow_name: str, description: Optional[str] = None):
        """Start recording commands."""
        self.is_recording = True
        self.current_workflow = Workflow(name=workflow_name, description=description)
        self.recorded_commands = []
        logger.info(f"Started recording workflow: {workflow_name}")
    
    def record_command(self, command: str, parameters: Optional[Dict[str, Any]] = None, description: Optional[str] = None):
        """Record a command."""
        if not self.is_recording:
            return
        
        cmd = Command(
            command=command,
            parameters=parameters or {},
            description=description
        )
        self.recorded_commands.append(cmd)
        logger.debug(f"Recorded command: {command}")
    
    def stop_recording(self) -> Optional[Workflow]:
        """Stop recording and return the workflow."""
        if not self.is_recording or not self.current_workflow:
            return None
        
        self.is_recording = False
        self.current_workflow.commands = self.recorded_commands
        self.current_workflow.updated_at = datetime.now()
        
        workflow = self.current_workflow
        self.current_workflow = None
        self.recorded_commands = []
        
        logger.info(f"Stopped recording workflow: {workflow.name} ({len(workflow.commands)} commands)")
        return workflow
    
    def cancel_recording(self):
        """Cancel current recording."""
        self.is_recording = False
        self.current_workflow = None
        self.recorded_commands = []
        logger.info("Recording cancelled")


class WorkflowLibrary:
    """
    Manage a library of reusable workflows.
    
    Features:
    - Save/load workflows
    - Search workflows by tags
    - Import/export workflows
    - Workflow templates with variables
    """
    
    def __init__(self, library_path: str = "./data/workflows"):
        """
        Initialize workflow library.
        
        Args:
            library_path: Path to store workflows
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        self.workflows: Dict[str, Workflow] = {}
        
        # Load existing workflows
        self._load_all_workflows()
        
        logger.info(f"Workflow Library initialized ({len(self.workflows)} workflows loaded)")
    
    def _load_all_workflows(self):
        """Load all workflows from disk."""
        for file_path in self.library_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    workflow = Workflow.from_dict(data)
                    self.workflows[workflow.name] = workflow
            except Exception as e:
                logger.error(f"Failed to load workflow from {file_path}: {e}")
    
    def save_workflow(self, workflow: Workflow) -> bool:
        """
        Save a workflow to the library.
        
        Args:
            workflow: Workflow to save
            
        Returns:
            True if saved successfully
        """
        try:
            # Update timestamp
            workflow.updated_at = datetime.now()
            
            # Save to disk
            file_path = self.library_path / f"{workflow.name}.json"
            with open(file_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            # Add to library
            self.workflows[workflow.name] = workflow
            
            logger.info(f"Workflow saved: {workflow.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            return False
    
    def load_workflow(self, name: str) -> Optional[Workflow]:
        """
        Load a workflow from the library.
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow or None if not found
        """
        return self.workflows.get(name)
    
    def delete_workflow(self, name: str) -> bool:
        """
        Delete a workflow from the library.
        
        Args:
            name: Workflow name
            
        Returns:
            True if deleted successfully
        """
        if name not in self.workflows:
            return False
        
        try:
            file_path = self.library_path / f"{name}.json"
            if file_path.exists():
                file_path.unlink()
            
            del self.workflows[name]
            logger.info(f"Workflow deleted: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            return False
    
    def search_workflows(self, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Workflow]:
        """
        Search workflows by name/description or tags.
        
        Args:
            query: Search query (searches name and description)
            tags: Filter by tags
            
        Returns:
            List of matching workflows
        """
        results = list(self.workflows.values())
        
        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                w for w in results
                if query_lower in w.name.lower() or
                (w.description and query_lower in w.description.lower())
            ]
        
        # Filter by tags
        if tags:
            results = [
                w for w in results
                if any(tag in w.tags for tag in tags)
            ]
        
        return results
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with basic info."""
        return [
            {
                'name': w.name,
                'description': w.description,
                'commands_count': len(w.commands),
                'tags': w.tags,
                'created_at': w.created_at.isoformat(),
                'updated_at': w.updated_at.isoformat()
            }
            for w in self.workflows.values()
        ]
    
    def export_workflow(self, name: str, export_path: str) -> bool:
        """Export a workflow to a file."""
        workflow = self.load_workflow(name)
        if not workflow:
            return False
        
        try:
            with open(export_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            logger.info(f"Workflow exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export workflow: {e}")
            return False
    
    def import_workflow(self, import_path: str) -> Optional[str]:
        """Import a workflow from a file."""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                workflow = Workflow.from_dict(data)
                self.save_workflow(workflow)
                logger.info(f"Workflow imported: {workflow.name}")
                return workflow.name
        except Exception as e:
            logger.error(f"Failed to import workflow: {e}")
            return None


class WorkflowPlayer:
    """
    Execute workflows with variable substitution.
    
    Features:
    - Execute workflows
    - Variable substitution
    - Error handling and recovery
    - Progress tracking
    """
    
    def __init__(self, agent):
        """
        Initialize workflow player.
        
        Args:
            agent: CosikAgent instance
        """
        self.agent = agent
        self.current_workflow: Optional[Workflow] = None
        self.current_step: int = 0
        self.is_playing = False
    
    async def play_workflow(
        self,
        workflow: Workflow,
        variables: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            variables: Variable values to substitute
            progress_callback: Optional callback for progress updates
            
        Returns:
            Execution results
        """
        self.current_workflow = workflow
        self.current_step = 0
        self.is_playing = True
        
        # Merge workflow variables with provided variables
        runtime_vars = {**workflow.variables, **(variables or {})}
        
        results = []
        errors = []
        
        logger.info(f"Starting workflow: {workflow.name} ({len(workflow.commands)} commands)")
        
        for i, command in enumerate(workflow.commands):
            if not self.is_playing:
                logger.info("Workflow playback stopped")
                break
            
            self.current_step = i + 1
            
            try:
                # Substitute variables in command
                command_text = self._substitute_variables(command.command, runtime_vars)
                
                # Report progress
                if progress_callback:
                    await progress_callback(self.current_step, len(workflow.commands), command.description or command_text)
                
                logger.info(f"Step {self.current_step}/{len(workflow.commands)}: {command_text[:50]}...")
                
                # Execute command
                result = await self.agent.run(command_text)
                
                results.append({
                    'step': self.current_step,
                    'command': command_text,
                    'success': True,
                    'result': result
                })
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Step {self.current_step} failed: {error_msg}")
                
                errors.append({
                    'step': self.current_step,
                    'command': command.command,
                    'error': error_msg
                })
                
                # Handle error
                if command.retry_on_failure:
                    # Could implement retry logic here
                    pass
                
                if not command.continue_on_error:
                    logger.error("Workflow stopped due to error")
                    break
        
        self.is_playing = False
        self.current_workflow = None
        self.current_step = 0
        
        success_rate = len(results) / len(workflow.commands) * 100 if workflow.commands else 0
        
        logger.info(f"Workflow completed: {len(results)}/{len(workflow.commands)} steps successful ({success_rate:.1f}%)")
        
        return {
            'workflow_name': workflow.name,
            'total_steps': len(workflow.commands),
            'completed_steps': len(results),
            'failed_steps': len(errors),
            'success_rate': f"{success_rate:.1f}%",
            'results': results,
            'errors': errors
        }
    
    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in text using ${variable} syntax."""
        result = text
        for key, value in variables.items():
            result = result.replace(f"${{{key}}}", str(value))
        return result
    
    async def pause_workflow(self):
        """Pause workflow playback."""
        self.is_playing = False
        logger.info("Workflow paused")
    
    async def resume_workflow(self):
        """Resume workflow playback."""
        if self.current_workflow:
            self.is_playing = True
            logger.info("Workflow resumed")
    
    async def stop_workflow(self):
        """Stop workflow playback."""
        self.is_playing = False
        self.current_workflow = None
        self.current_step = 0
        logger.info("Workflow stopped")


class CommandReplaySystem:
    """
    Complete command replay system combining recording, library, and playback.
    """
    
    def __init__(self, agent, library_path: str = "./data/workflows"):
        """
        Initialize command replay system.
        
        Args:
            agent: CosikAgent instance
            library_path: Path to workflow library
        """
        self.agent = agent
        self.recorder = WorkflowRecorder()
        self.library = WorkflowLibrary(library_path)
        self.player = WorkflowPlayer(agent)
        
        logger.info("Command Replay System initialized")
    
    # Convenient methods that delegate to components
    
    def start_recording(self, workflow_name: str, description: Optional[str] = None):
        """Start recording a new workflow."""
        self.recorder.start_recording(workflow_name, description)
    
    def record(self, command: str, parameters: Optional[Dict[str, Any]] = None):
        """Record a command."""
        self.recorder.record_command(command, parameters)
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and save workflow."""
        workflow = self.recorder.stop_recording()
        if workflow:
            self.library.save_workflow(workflow)
            return workflow.name
        return None
    
    async def replay(self, workflow_name: str, variables: Optional[Dict[str, Any]] = None):
        """Replay a workflow."""
        workflow = self.library.load_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_name}")
        
        return await self.player.play_workflow(workflow, variables)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return self.library.list_workflows()
    
    def search(self, query: str) -> List[Workflow]:
        """Search workflows."""
        return self.library.search_workflows(query=query)
