"""
Advanced Task Queue System with Priority, Dependencies, and Parallel Execution.

Features:
- Priority-based task scheduling
- Task dependencies and execution order
- Parallel task execution
- Task cancellation and timeout
- Queue persistence
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from loguru import logger


class TaskPriority(IntEnum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(IntEnum):
    """Task execution status."""
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4
    TIMEOUT = 5


@dataclass
class Task:
    """Represents a single task with metadata."""
    id: str
    intent: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        data = data.copy()
        data['priority'] = TaskPriority(data.get('priority', TaskPriority.NORMAL))
        data['status'] = TaskStatus(data.get('status', TaskStatus.PENDING))
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class AdvancedTaskQueue:
    """
    Advanced task queue with priority scheduling, dependencies, and parallel execution.
    
    Features:
    - Priority-based scheduling
    - Task dependencies resolution
    - Parallel execution with concurrency limit
    - Task timeout and cancellation
    - Queue persistence to disk
    """
    
    def __init__(self, max_concurrent: int = 5, persist_path: Optional[str] = None):
        """
        Initialize the advanced task queue.
        
        Args:
            max_concurrent: Maximum number of concurrent tasks
            persist_path: Path to persist queue state (optional)
        """
        self.max_concurrent = max_concurrent
        self.persist_path = persist_path
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.pending_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        
        # Dependency tracking
        self.dependents: Dict[str, Set[str]] = defaultdict(set)  # task_id -> tasks that depend on it
        
        # Event handlers
        self.on_task_complete: Optional[Callable] = None
        self.on_task_failed: Optional[Callable] = None
        
        # Running task futures
        self.task_futures: Dict[str, asyncio.Task] = {}
        
        # Load persisted state if available
        if persist_path:
            self._load_state()
        
        logger.info(f"Advanced Task Queue initialized (max_concurrent={max_concurrent})")
    
    async def add_task(self, task: Task) -> str:
        """
        Add a task to the queue.
        
        Args:
            task: Task to add
            
        Returns:
            Task ID
        """
        # Store task
        self.tasks[task.id] = task
        
        # Track dependencies
        for dep_id in task.dependencies:
            self.dependents[dep_id].add(task.id)
        
        # Add to pending queue if no dependencies or all deps are completed
        if self._can_execute(task):
            await self.pending_queue.put((task.priority.value, task.id))
            logger.info(f"Task {task.id} added to queue (priority={task.priority.name})")
        else:
            logger.info(f"Task {task.id} waiting for dependencies: {task.dependencies}")
        
        # Persist state
        self._persist_state()
        
        return task.id
    
    def _can_execute(self, task: Task) -> bool:
        """Check if a task can be executed (all dependencies met)."""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        
        return True
    
    async def execute_task(self, task_id: str, executor: Callable) -> Any:
        """
        Execute a specific task.
        
        Args:
            task_id: ID of task to execute
            executor: Async function to execute the task
            
        Returns:
            Task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        # Mark as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.running_tasks.add(task_id)
        
        logger.info(f"Executing task {task_id} ({task.intent})")
        
        try:
            # Execute with timeout if specified
            if task.timeout:
                result = await asyncio.wait_for(
                    executor(task),
                    timeout=task.timeout
                )
            else:
                result = await executor(task)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            self.running_tasks.remove(task_id)
            self.completed_tasks.add(task_id)
            
            logger.info(f"Task {task_id} completed successfully")
            
            # Trigger callback
            if self.on_task_complete:
                await self.on_task_complete(task)
            
            # Check if any dependent tasks can now run
            await self._check_dependent_tasks(task_id)
            
            return result
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = f"Task timed out after {task.timeout}s"
            self.running_tasks.remove(task_id)
            logger.error(f"Task {task_id} timed out")
            
            if self.on_task_failed:
                await self.on_task_failed(task)
            
            raise
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.retry_count += 1
            self.running_tasks.remove(task_id)
            
            logger.error(f"Task {task_id} failed: {e}")
            
            # Retry if allowed
            if task.retry_count < task.max_retries:
                logger.info(f"Retrying task {task_id} ({task.retry_count}/{task.max_retries})")
                task.status = TaskStatus.PENDING
                await self.pending_queue.put((task.priority.value, task_id))
            else:
                if self.on_task_failed:
                    await self.on_task_failed(task)
            
            raise
        finally:
            self._persist_state()
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """Check and queue tasks that were waiting for this task."""
        if completed_task_id in self.dependents:
            for dependent_id in self.dependents[completed_task_id]:
                if dependent_id in self.tasks:
                    task = self.tasks[dependent_id]
                    if task.status == TaskStatus.PENDING and self._can_execute(task):
                        await self.pending_queue.put((task.priority.value, task.id))
                        logger.info(f"Task {dependent_id} now ready to execute")
    
    async def process_queue(self, executor: Callable):
        """
        Process tasks from the queue with concurrency limit.
        
        Args:
            executor: Async function to execute tasks
        """
        logger.info("Starting queue processor")
        
        while True:
            try:
                # Wait if we're at max concurrency
                while len(self.running_tasks) >= self.max_concurrent:
                    await asyncio.sleep(0.1)
                
                # Get next task (with timeout to allow checking for new tasks)
                try:
                    priority, task_id = await asyncio.wait_for(
                        self.pending_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    # Check if queue is truly empty and no tasks are running
                    if self.pending_queue.empty() and len(self.running_tasks) == 0:
                        logger.info("Queue empty and no running tasks")
                        break
                    continue
                
                # Skip if task was already completed or cancelled
                if task_id in self.completed_tasks:
                    continue
                
                task = self.tasks.get(task_id)
                if not task or task.status == TaskStatus.CANCELLED:
                    continue
                
                # Execute task in background
                future = asyncio.create_task(self.execute_task(task_id, executor))
                self.task_futures[task_id] = future
                
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(1)
        
        logger.info("Queue processor finished")
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if cancelled successfully
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Cancel if pending
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            logger.info(f"Task {task_id} cancelled")
            return True
        
        # Cancel if running
        if task_id in self.task_futures:
            self.task_futures[task_id].cancel()
            task.status = TaskStatus.CANCELLED
            self.running_tasks.discard(task_id)
            logger.info(f"Running task {task_id} cancelled")
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task."""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        pending_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        running_count = len(self.running_tasks)
        completed_count = len(self.completed_tasks)
        failed_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            'total_tasks': len(self.tasks),
            'pending': pending_count,
            'running': running_count,
            'completed': completed_count,
            'failed': failed_count,
            'queue_size': self.pending_queue.qsize(),
            'max_concurrent': self.max_concurrent
        }
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get all tasks with a specific tag."""
        return [t for t in self.tasks.values() if tag in t.tags]
    
    def clear_completed(self):
        """Clear all completed tasks."""
        to_remove = [tid for tid, t in self.tasks.items() if t.status == TaskStatus.COMPLETED]
        for tid in to_remove:
            del self.tasks[tid]
            self.completed_tasks.discard(tid)
        logger.info(f"Cleared {len(to_remove)} completed tasks")
    
    def _persist_state(self):
        """Persist queue state to disk."""
        if not self.persist_path:
            return
        
        try:
            state = {
                'tasks': {tid: t.to_dict() for tid, t in self.tasks.items()},
                'completed_tasks': list(self.completed_tasks),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.persist_path, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to persist queue state: {e}")
    
    def _load_state(self):
        """Load persisted queue state from disk."""
        if not self.persist_path:
            return
        
        try:
            with open(self.persist_path, 'r') as f:
                state = json.load(f)
            
            # Restore tasks
            for tid, task_data in state.get('tasks', {}).items():
                self.tasks[tid] = Task.from_dict(task_data)
            
            # Restore completed set
            self.completed_tasks = set(state.get('completed_tasks', []))
            
            logger.info(f"Loaded {len(self.tasks)} tasks from persisted state")
            
        except FileNotFoundError:
            logger.info("No persisted state found")
        except Exception as e:
            logger.error(f"Failed to load queue state: {e}")
