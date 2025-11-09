"""Context management system for maintaining awareness and intelligent decision making."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from datetime import datetime, timedelta
from collections import deque
import json


class ContextManager:
    """
    Manages context awareness including current state, history,
    environment information, and user preferences.
    """
    
    def __init__(self, config, memory_manager=None):
        """
        Initialize context manager.
        
        Args:
            config: Configuration object
            memory_manager: Optional memory manager for persistence
        """
        self.config = config
        self.memory = memory_manager
        
        # Context state
        self.current_context = {
            'session_id': None,
            'start_time': None,
            'current_goal': None,
            'active_tasks': [],
            'environment': {},
            'user_preferences': {},
            'constraints': []
        }
        
        # Short-term working memory
        self.working_memory = deque(maxlen=config.get('context.working_memory_size', 20))
        
        # Recent interactions
        self.recent_interactions = deque(maxlen=config.get('context.interaction_history_size', 50))
        
        # Application state tracking
        self.app_states = {}
        
        # Performance tracking
        self.performance_metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'avg_task_duration': 0.0,
            'success_rate': 0.0
        }
        
    async def start_session(self, session_id: str, initial_context: Optional[Dict] = None) -> None:
        """
        Start a new session with fresh context.
        
        Args:
            session_id: Unique session identifier
            initial_context: Optional initial context data
        """
        logger.info(f"Starting new session: {session_id}")
        
        self.current_context = {
            'session_id': session_id,
            'start_time': datetime.now(),
            'current_goal': None,
            'active_tasks': [],
            'environment': await self._capture_environment(),
            'user_preferences': initial_context.get('preferences', {}) if initial_context else {},
            'constraints': initial_context.get('constraints', []) if initial_context else []
        }
        
        # Load previous session context if available
        if self.memory:
            previous = await self.memory.get_previous_session_context()
            if previous:
                self.current_context['user_preferences'].update(
                    previous.get('user_preferences', {})
                )
        
        logger.info("Session started successfully")
    
    async def _capture_environment(self) -> Dict[str, Any]:
        """Capture current environment state."""
        env = {
            'timestamp': datetime.now().isoformat(),
            'os': 'windows',  # Assuming Windows for this project
            'active_windows': [],
            'clipboard_content': None,
            'screen_resolution': None
        }
        
        # Could be extended to capture more details
        # For now, basic structure
        
        return env
    
    async def update_goal(self, goal: str, metadata: Optional[Dict] = None) -> None:
        """
        Update current goal.
        
        Args:
            goal: New goal description
            metadata: Optional metadata about the goal
        """
        logger.info(f"Updating goal: {goal}")
        
        self.current_context['current_goal'] = {
            'description': goal,
            'start_time': datetime.now(),
            'metadata': metadata or {},
            'status': 'active'
        }
        
        # Add to working memory
        self.working_memory.append({
            'type': 'goal_update',
            'goal': goal,
            'timestamp': datetime.now()
        })
    
    async def add_task(self, task: Dict[str, Any]) -> None:
        """Add a task to active tasks."""
        task_with_meta = {
            **task,
            'added_at': datetime.now(),
            'status': 'pending'
        }
        self.current_context['active_tasks'].append(task_with_meta)
        
        # Add to working memory
        self.working_memory.append({
            'type': 'task_added',
            'task': task,
            'timestamp': datetime.now()
        })
    
    async def update_task_status(self, task_id: str, status: str, result: Optional[Dict] = None) -> None:
        """Update status of an active task."""
        for task in self.current_context['active_tasks']:
            if task.get('id') == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now()
                if result:
                    task['result'] = result
                
                # Update performance metrics
                if status == 'completed':
                    self.performance_metrics['tasks_completed'] += 1
                elif status == 'failed':
                    self.performance_metrics['tasks_failed'] += 1
                
                # Calculate success rate
                total = (self.performance_metrics['tasks_completed'] + 
                        self.performance_metrics['tasks_failed'])
                if total > 0:
                    self.performance_metrics['success_rate'] = (
                        self.performance_metrics['tasks_completed'] / total
                    )
                
                break
    
    async def add_interaction(
        self,
        interaction_type: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Record an interaction.
        
        Args:
            interaction_type: Type of interaction (user_input, system_output, etc.)
            data: Interaction data
        """
        interaction = {
            'type': interaction_type,
            'data': data,
            'timestamp': datetime.now(),
            'context_snapshot': self._create_context_snapshot()
        }
        
        self.recent_interactions.append(interaction)
        
        # Also add to working memory if relevant
        if interaction_type in ['user_input', 'critical_event']:
            self.working_memory.append({
                'type': 'interaction',
                'interaction': interaction,
                'timestamp': datetime.now()
            })
    
    def _create_context_snapshot(self) -> Dict[str, Any]:
        """Create a lightweight snapshot of current context."""
        return {
            'goal': self.current_context.get('current_goal', {}).get('description'),
            'active_task_count': len(self.current_context['active_tasks']),
            'recent_events': len(self.working_memory)
        }
    
    async def get_relevant_context(
        self,
        query: str,
        max_items: int = 10
    ) -> Dict[str, Any]:
        """
        Get context relevant to a query.
        
        Args:
            query: Query or task description
            max_items: Maximum number of context items to return
            
        Returns:
            Relevant context information
        """
        logger.info(f"Retrieving relevant context for: {query[:50]}...")
        
        context = {
            'current_goal': self.current_context.get('current_goal'),
            'active_tasks': self.current_context.get('active_tasks', []),
            'recent_history': list(self.working_memory)[-max_items:],
            'environment': self.current_context.get('environment'),
            'constraints': self.current_context.get('constraints', []),
            'performance': self.performance_metrics
        }
        
        # Add semantic search from memory if available
        if self.memory:
            relevant_history = await self.memory.find_similar_tasks(query, limit=5)
            context['similar_past_tasks'] = relevant_history
        
        return context
    
    async def check_constraints(self, proposed_action: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if a proposed action violates any constraints.
        
        Args:
            proposed_action: Action to check
            
        Returns:
            Tuple of (is_allowed, list_of_violations)
        """
        violations = []
        constraints = self.current_context.get('constraints', [])
        
        for constraint in constraints:
            constraint_type = constraint.get('type')
            
            if constraint_type == 'forbidden_action':
                forbidden = constraint.get('actions', [])
                action_type = proposed_action.get('intent', '')
                if action_type in forbidden:
                    violations.append(f"Action '{action_type}' is forbidden")
            
            elif constraint_type == 'time_limit':
                max_duration = constraint.get('max_duration', 3600)
                estimated_duration = proposed_action.get('estimated_duration', 0)
                if estimated_duration > max_duration:
                    violations.append(f"Action exceeds time limit ({estimated_duration}s > {max_duration}s)")
            
            elif constraint_type == 'resource_limit':
                # Check resource constraints
                pass
        
        is_allowed = len(violations) == 0
        return is_allowed, violations
    
    async def update_user_preference(self, key: str, value: Any) -> None:
        """Update a user preference."""
        logger.info(f"Updating user preference: {key} = {value}")
        self.current_context['user_preferences'][key] = value
        
        # Persist if memory available
        if self.memory:
            await self.memory.store_user_preference(key, value)
    
    async def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.current_context['user_preferences'].get(key, default)
    
    async def track_application_state(
        self,
        app_name: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Track state of an application.
        
        Args:
            app_name: Application name
            state: Current state information
        """
        self.app_states[app_name] = {
            'state': state,
            'last_updated': datetime.now()
        }
        
        # Add to working memory
        self.working_memory.append({
            'type': 'app_state_update',
            'app': app_name,
            'state': state,
            'timestamp': datetime.now()
        })
    
    async def get_application_state(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get tracked state of an application."""
        app_state = self.app_states.get(app_name)
        if app_state:
            return app_state['state']
        return None
    
    async def infer_intent(self, partial_information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer user intent from partial information using context.
        
        Args:
            partial_information: Partial or ambiguous input
            
        Returns:
            Inferred intent with confidence
        """
        logger.info("Inferring intent from context")
        
        inference = {
            'intent': 'unknown',
            'confidence': 0.0,
            'reasoning': []
        }
        
        # Use current goal
        if self.current_context.get('current_goal'):
            goal_desc = self.current_context['current_goal'].get('description', '')
            # Simple matching - could be enhanced with ML
            if any(word in partial_information.get('text', '').lower() 
                   for word in goal_desc.lower().split()):
                inference['confidence'] += 0.3
                inference['reasoning'].append("Aligns with current goal")
        
        # Use recent interactions
        recent_types = [i['type'] for i in list(self.recent_interactions)[-5:]]
        if 'user_input' in recent_types:
            inference['confidence'] += 0.2
            inference['reasoning'].append("Follows recent user input")
        
        # Use active tasks
        if self.current_context['active_tasks']:
            last_task = self.current_context['active_tasks'][-1]
            if last_task.get('status') == 'pending':
                inference['intent'] = last_task.get('intent', 'unknown')
                inference['confidence'] += 0.4
                inference['reasoning'].append("Continues pending task")
        
        return inference
    
    async def suggest_next_action(self) -> Optional[Dict[str, Any]]:
        """
        Suggest next action based on context.
        
        Returns:
            Suggested action or None
        """
        # Check if there's a current goal
        if not self.current_context.get('current_goal'):
            return None
        
        goal = self.current_context['current_goal']
        
        # Check for pending tasks
        pending_tasks = [
            t for t in self.current_context['active_tasks']
            if t.get('status') == 'pending'
        ]
        
        if pending_tasks:
            return {
                'action': 'execute_task',
                'task': pending_tasks[0],
                'reasoning': 'Continue with pending task'
            }
        
        # Check if goal is complete
        completed_tasks = [
            t for t in self.current_context['active_tasks']
            if t.get('status') == 'completed'
        ]
        
        if completed_tasks and not pending_tasks:
            return {
                'action': 'goal_complete',
                'reasoning': 'All tasks completed'
            }
        
        # Suggest decomposing goal if no tasks
        if not self.current_context['active_tasks']:
            return {
                'action': 'decompose_goal',
                'goal': goal['description'],
                'reasoning': 'Goal needs to be broken down into tasks'
            }
        
        return None
    
    async def get_context_summary(self) -> str:
        """
        Get a human-readable summary of current context.
        
        Returns:
            Context summary string
        """
        summary_parts = []
        
        # Session info
        if self.current_context.get('session_id'):
            session_duration = (datetime.now() - self.current_context['start_time']).total_seconds()
            summary_parts.append(
                f"Session: {self.current_context['session_id']} "
                f"(running for {session_duration:.0f}s)"
            )
        
        # Current goal
        if self.current_context.get('current_goal'):
            goal = self.current_context['current_goal']
            summary_parts.append(f"Goal: {goal['description']}")
        
        # Task status
        active_count = len(self.current_context.get('active_tasks', []))
        if active_count > 0:
            summary_parts.append(f"Active tasks: {active_count}")
        
        # Performance
        perf = self.performance_metrics
        summary_parts.append(
            f"Performance: {perf['tasks_completed']} completed, "
            f"{perf['tasks_failed']} failed, "
            f"{perf['success_rate']:.1%} success rate"
        )
        
        return " | ".join(summary_parts)
    
    async def end_session(self) -> Dict[str, Any]:
        """
        End current session and save context.
        
        Returns:
            Session summary
        """
        logger.info("Ending session")
        
        session_duration = (
            datetime.now() - self.current_context['start_time']
        ).total_seconds() if self.current_context.get('start_time') else 0
        
        summary = {
            'session_id': self.current_context.get('session_id'),
            'duration': session_duration,
            'goal': self.current_context.get('current_goal'),
            'tasks_executed': len(self.current_context.get('active_tasks', [])),
            'performance': self.performance_metrics.copy(),
            'final_context': self.current_context.copy()
        }
        
        # Save to persistent memory
        if self.memory:
            await self.memory.store_session_context(summary)
        
        logger.info(f"Session ended: {summary['tasks_executed']} tasks, "
                   f"{summary['duration']:.0f}s duration")
        
        return summary
