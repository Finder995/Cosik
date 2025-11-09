"""Workflow orchestrator for managing complex multi-step task execution."""

import asyncio
from typing import Dict, Any, List, Optional, Set
from loguru import logger
from datetime import datetime
from enum import Enum
import json


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class WorkflowOrchestrator:
    """
    Orchestrates complex workflows with dependencies, parallel execution,
    error recovery, and adaptive execution strategies.
    """
    
    def __init__(self, config, task_executor, reasoning_engine=None):
        """
        Initialize workflow orchestrator.
        
        Args:
            config: Configuration object
            task_executor: Task executor instance
            reasoning_engine: Optional reasoning engine for intelligent decisions
        """
        self.config = config
        self.executor = task_executor
        self.reasoning = reasoning_engine
        
        # Workflow state
        self.workflows = {}
        self.active_tasks = {}
        self.max_parallel = config.get('workflow.max_parallel', 3)
        self.retry_failed = config.get('workflow.retry_failed', True)
        self.max_retries = config.get('workflow.max_retries', 2)
        
    async def execute_workflow(
        self,
        workflow_id: str,
        tasks: List[Dict[str, Any]],
        strategy: str = 'adaptive'
    ) -> Dict[str, Any]:
        """
        Execute a workflow of tasks with dependencies.
        
        Args:
            workflow_id: Unique workflow identifier
            tasks: List of task definitions with dependencies
            strategy: Execution strategy (sequential, parallel, adaptive)
            
        Returns:
            Workflow execution result
        """
        logger.info(f"Starting workflow {workflow_id} with {len(tasks)} tasks")
        
        start_time = datetime.now()
        
        # Initialize workflow state
        workflow = {
            'id': workflow_id,
            'tasks': self._prepare_tasks(tasks),
            'strategy': strategy,
            'status': {},
            'results': {},
            'start_time': start_time,
            'completed': 0,
            'failed': 0
        }
        self.workflows[workflow_id] = workflow
        
        try:
            # Execute based on strategy
            if strategy == 'sequential':
                result = await self._execute_sequential(workflow)
            elif strategy == 'parallel':
                result = await self._execute_parallel(workflow)
            else:  # adaptive
                result = await self._execute_adaptive(workflow)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'workflow_id': workflow_id,
                'success': result['completed'] > 0 and result['failed'] == 0,
                'completed': result['completed'],
                'failed': result['failed'],
                'duration': duration,
                'results': result['results']
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e)
            }
        finally:
            # Cleanup
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
    
    def _prepare_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare tasks with indices and status."""
        prepared = []
        for i, task in enumerate(tasks):
            task_copy = task.copy()
            task_copy['index'] = i
            task_copy['status'] = TaskStatus.PENDING
            task_copy['dependencies'] = task.get('dependencies', [])
            task_copy['retry_count'] = 0
            prepared.append(task_copy)
        return prepared
    
    async def _execute_sequential(self, workflow: Dict) -> Dict[str, Any]:
        """Execute tasks sequentially in order."""
        logger.info(f"Executing workflow {workflow['id']} sequentially")
        
        results = {}
        completed = 0
        failed = 0
        
        for task in workflow['tasks']:
            task_id = task['index']
            
            # Check dependencies
            if not self._dependencies_met(task, workflow['status']):
                logger.warning(f"Task {task_id} dependencies not met, skipping")
                workflow['status'][task_id] = TaskStatus.SKIPPED
                continue
            
            # Execute task
            workflow['status'][task_id] = TaskStatus.RUNNING
            result = await self._execute_single_task(task, workflow)
            
            if result['success']:
                workflow['status'][task_id] = TaskStatus.COMPLETED
                completed += 1
            else:
                workflow['status'][task_id] = TaskStatus.FAILED
                failed += 1
                
                # Stop on failure unless configured otherwise
                if not self.config.get('workflow.continue_on_failure', False):
                    logger.warning("Stopping workflow due to task failure")
                    break
            
            results[task_id] = result
        
        return {
            'completed': completed,
            'failed': failed,
            'results': results
        }
    
    async def _execute_parallel(self, workflow: Dict) -> Dict[str, Any]:
        """Execute independent tasks in parallel."""
        logger.info(f"Executing workflow {workflow['id']} in parallel")
        
        results = {}
        completed = 0
        failed = 0
        
        # Group tasks by dependency level
        levels = self._compute_dependency_levels(workflow['tasks'])
        
        # Execute each level
        for level, task_indices in enumerate(levels):
            logger.info(f"Executing level {level} with {len(task_indices)} tasks")
            
            # Get tasks for this level
            level_tasks = [workflow['tasks'][i] for i in task_indices]
            
            # Execute in batches respecting max_parallel
            for i in range(0, len(level_tasks), self.max_parallel):
                batch = level_tasks[i:i + self.max_parallel]
                
                # Execute batch in parallel
                batch_results = await asyncio.gather(
                    *[self._execute_single_task(task, workflow) for task in batch],
                    return_exceptions=True
                )
                
                # Process results
                for task, result in zip(batch, batch_results):
                    task_id = task['index']
                    
                    if isinstance(result, Exception):
                        logger.error(f"Task {task_id} raised exception: {result}")
                        workflow['status'][task_id] = TaskStatus.FAILED
                        results[task_id] = {'success': False, 'error': str(result)}
                        failed += 1
                    elif result.get('success', False):
                        workflow['status'][task_id] = TaskStatus.COMPLETED
                        results[task_id] = result
                        completed += 1
                    else:
                        workflow['status'][task_id] = TaskStatus.FAILED
                        results[task_id] = result
                        failed += 1
        
        return {
            'completed': completed,
            'failed': failed,
            'results': results
        }
    
    async def _execute_adaptive(self, workflow: Dict) -> Dict[str, Any]:
        """
        Adaptive execution that dynamically chooses between sequential
        and parallel based on task characteristics and system state.
        """
        logger.info(f"Executing workflow {workflow['id']} adaptively")
        
        results = {}
        completed = 0
        failed = 0
        
        # Analyze workflow
        analysis = self._analyze_workflow(workflow['tasks'])
        
        # Decide strategy based on analysis
        if analysis['has_dependencies'] and analysis['avg_task_complexity'] > 0.7:
            # Complex with dependencies - use parallel by levels
            logger.info("Using parallel-by-level strategy")
            return await self._execute_parallel(workflow)
        elif not analysis['has_dependencies'] and len(workflow['tasks']) > 5:
            # Many independent tasks - use full parallel
            logger.info("Using full parallel strategy")
            return await self._execute_parallel(workflow)
        else:
            # Simple or few tasks - use sequential
            logger.info("Using sequential strategy")
            return await self._execute_sequential(workflow)
    
    async def _execute_single_task(
        self,
        task: Dict[str, Any],
        workflow: Dict
    ) -> Dict[str, Any]:
        """Execute a single task with retry logic."""
        task_id = task['index']
        logger.info(f"Executing task {task_id}: {task.get('description', 'unknown')}")
        
        max_retries = self.max_retries if self.retry_failed else 0
        
        for attempt in range(max_retries + 1):
            try:
                # Execute task
                result = await self.executor.execute(task)
                
                if result.get('success', False):
                    logger.info(f"Task {task_id} completed successfully")
                    return result
                else:
                    logger.warning(f"Task {task_id} failed: {result.get('error', 'unknown')}")
                    
                    if attempt < max_retries:
                        # Retry with backoff
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying task {task_id} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        # Max retries reached
                        return result
                        
            except Exception as e:
                logger.error(f"Task {task_id} raised exception: {e}")
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying task {task_id} after exception in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    def _dependencies_met(
        self,
        task: Dict[str, Any],
        status_map: Dict[int, TaskStatus]
    ) -> bool:
        """Check if all task dependencies are met."""
        dependencies = task.get('dependencies', [])
        
        for dep_id in dependencies:
            dep_status = status_map.get(dep_id, TaskStatus.PENDING)
            if dep_status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _compute_dependency_levels(self, tasks: List[Dict]) -> List[List[int]]:
        """Compute dependency levels for parallel execution."""
        levels = []
        processed = set()
        task_map = {task['index']: task for task in tasks}
        
        while len(processed) < len(tasks):
            level = []
            
            for task in tasks:
                task_id = task['index']
                
                if task_id in processed:
                    continue
                
                # Check if all dependencies are processed
                deps = task.get('dependencies', [])
                if all(dep in processed for dep in deps):
                    level.append(task_id)
            
            if not level:
                # Circular dependency or error
                logger.warning("Circular dependency detected or no tasks ready")
                # Add remaining tasks to avoid infinite loop
                level = [t['index'] for t in tasks if t['index'] not in processed]
            
            levels.append(level)
            processed.update(level)
        
        return levels
    
    def _analyze_workflow(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze workflow characteristics."""
        has_deps = any(task.get('dependencies') for task in tasks)
        
        # Estimate complexity based on task descriptions
        complexities = []
        for task in tasks:
            desc = task.get('description', '').lower()
            # Simple heuristic
            complexity = 0.3 if len(desc.split()) <= 3 else 0.7
            complexities.append(complexity)
        
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0.5
        
        return {
            'has_dependencies': has_deps,
            'task_count': len(tasks),
            'avg_task_complexity': avg_complexity
        }
    
    async def optimize_workflow(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Optimize task order and dependencies for better execution.
        
        Args:
            tasks: List of tasks to optimize
            
        Returns:
            Optimized task list
        """
        logger.info("Optimizing workflow")
        
        # Topological sort for dependency ordering
        optimized = self._topological_sort(tasks)
        
        # Identify parallelizable tasks
        optimized = self._identify_parallel_groups(optimized)
        
        return optimized
    
    def _topological_sort(self, tasks: List[Dict]) -> List[Dict]:
        """Topological sort of tasks based on dependencies."""
        sorted_tasks = []
        visited = set()
        temp_mark = set()
        
        def visit(task_idx):
            if task_idx in temp_mark:
                logger.warning("Circular dependency detected")
                return
            if task_idx in visited:
                return
            
            temp_mark.add(task_idx)
            
            task = tasks[task_idx]
            for dep in task.get('dependencies', []):
                if dep < len(tasks):
                    visit(dep)
            
            temp_mark.remove(task_idx)
            visited.add(task_idx)
            sorted_tasks.append(task)
        
        for i in range(len(tasks)):
            if i not in visited:
                visit(i)
        
        return sorted_tasks
    
    def _identify_parallel_groups(self, tasks: List[Dict]) -> List[Dict]:
        """Identify groups of tasks that can run in parallel."""
        # Add metadata about parallelization potential
        for i, task in enumerate(tasks):
            # Tasks with no dependencies or same dependency set can be parallel
            deps = set(task.get('dependencies', []))
            
            parallel_group = 0
            for j in range(i):
                other_deps = set(tasks[j].get('dependencies', []))
                if deps == other_deps:
                    parallel_group = tasks[j].get('parallel_group', 0)
                    break
            
            task['parallel_group'] = parallel_group if parallel_group else i
        
        return tasks
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        if workflow_id not in self.workflows:
            return False
        
        logger.info(f"Pausing workflow {workflow_id}")
        self.workflows[workflow_id]['paused'] = True
        return True
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id not in self.workflows:
            return False
        
        logger.info(f"Resuming workflow {workflow_id}")
        self.workflows[workflow_id]['paused'] = False
        return True
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id not in self.workflows:
            return False
        
        logger.info(f"Canceling workflow {workflow_id}")
        self.workflows[workflow_id]['cancelled'] = True
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow."""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            'id': workflow_id,
            'total_tasks': len(workflow['tasks']),
            'completed': workflow['completed'],
            'failed': workflow['failed'],
            'status': {
                task['index']: task['status'].value 
                for task in workflow['tasks']
            }
        }
