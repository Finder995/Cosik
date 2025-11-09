"""Scheduler plugin for scheduled task execution."""

import asyncio
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger


class SchedulerPlugin:
    """Plugin for scheduling tasks to run at specific times or intervals."""
    
    def __init__(self, config):
        """Initialize scheduler plugin."""
        self.config = config
        self.scheduled_jobs = []
        self.running = False
        logger.info("Scheduler plugin initialized")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute scheduler commands.
        
        Supported commands:
        - schedule: Schedule a new task
        - list: List scheduled tasks
        - cancel: Cancel a scheduled task
        - start: Start the scheduler
        - stop: Stop the scheduler
        """
        command_lower = command.lower()
        
        if command_lower == 'schedule':
            return await self._schedule_task(**kwargs)
        elif command_lower == 'list':
            return self._list_scheduled()
        elif command_lower == 'cancel':
            return self._cancel_task(kwargs.get('job_id'))
        elif command_lower == 'start':
            return await self._start_scheduler()
        elif command_lower == 'stop':
            return self._stop_scheduler()
        else:
            return {
                'success': False,
                'error': f'Unknown command: {command}'
            }
    
    async def _schedule_task(self, task: Dict[str, Any], 
                           schedule_time: Optional[str] = None,
                           interval: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule a task for execution.
        
        Args:
            task: Task to schedule
            schedule_time: Time to run (e.g., "10:30", "2024-01-01 10:30")
            interval: Interval to run (e.g., "every 10 minutes", "daily")
            
        Returns:
            Result with job ID
        """
        try:
            job_id = len(self.scheduled_jobs) + 1
            
            if schedule_time:
                # Parse and schedule for specific time
                if ':' in schedule_time and len(schedule_time.split(':')) == 2:
                    # Daily time like "10:30"
                    schedule.every().day.at(schedule_time).do(
                        self._execute_scheduled_task, task
                    )
                else:
                    # Full datetime - parse and calculate delay
                    target_time = datetime.fromisoformat(schedule_time)
                    delay = (target_time - datetime.now()).total_seconds()
                    
                    if delay > 0:
                        asyncio.create_task(self._delayed_execute(delay, task))
                    else:
                        return {
                            'success': False,
                            'error': 'Scheduled time is in the past'
                        }
            
            elif interval:
                # Parse interval and schedule
                interval_lower = interval.lower()
                
                if 'minute' in interval_lower:
                    # Extract number
                    minutes = int(''.join(filter(str.isdigit, interval_lower)) or '1')
                    schedule.every(minutes).minutes.do(
                        self._execute_scheduled_task, task
                    )
                elif 'hour' in interval_lower:
                    hours = int(''.join(filter(str.isdigit, interval_lower)) or '1')
                    schedule.every(hours).hours.do(
                        self._execute_scheduled_task, task
                    )
                elif 'day' in interval_lower or 'daily' in interval_lower:
                    schedule.every().day.do(
                        self._execute_scheduled_task, task
                    )
                elif 'week' in interval_lower:
                    schedule.every().week.do(
                        self._execute_scheduled_task, task
                    )
                else:
                    return {
                        'success': False,
                        'error': f'Unsupported interval: {interval}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Either schedule_time or interval must be provided'
                }
            
            # Store job info
            self.scheduled_jobs.append({
                'id': job_id,
                'task': task,
                'schedule_time': schedule_time,
                'interval': interval,
                'created_at': datetime.now().isoformat()
            })
            
            logger.info(f"Scheduled task {job_id}: {task.get('description', 'unknown')}")
            
            return {
                'success': True,
                'job_id': job_id,
                'message': f'Task scheduled with ID {job_id}'
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule task: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _delayed_execute(self, delay: float, task: Dict[str, Any]):
        """Execute task after delay."""
        await asyncio.sleep(delay)
        self._execute_scheduled_task(task)
    
    def _execute_scheduled_task(self, task: Dict[str, Any]):
        """Execute a scheduled task."""
        logger.info(f"Executing scheduled task: {task.get('description', 'unknown')}")
        
        # Integrate with the main agent's task executor if available
        if hasattr(self.agent, 'task_queue') and self.agent.task_queue is not None:
            # Add task to agent's queue for execution
            self.agent.task_queue.append({
                'intent': 'scheduled_task',
                'parameters': task.get('parameters', {}),
                'description': task.get('description', 'Scheduled task'),
                'scheduled_at': task.get('scheduled_at')
            })
            logger.info(f"Added scheduled task to agent queue: {task.get('description')}")
        else:
            logger.warning("Agent task queue not available, task not executed")
    
    def _list_scheduled(self) -> Dict[str, Any]:
        """List all scheduled tasks."""
        return {
            'success': True,
            'jobs': self.scheduled_jobs,
            'count': len(self.scheduled_jobs)
        }
    
    def _cancel_task(self, job_id: Optional[int]) -> Dict[str, Any]:
        """Cancel a scheduled task."""
        if job_id is None:
            return {
                'success': False,
                'error': 'job_id required'
            }
        
        # Find and remove job
        for i, job in enumerate(self.scheduled_jobs):
            if job['id'] == job_id:
                self.scheduled_jobs.pop(i)
                # Cancel from schedule library
                schedule.clear(job_id)
                
                logger.info(f"Cancelled scheduled task {job_id}")
                return {
                    'success': True,
                    'message': f'Cancelled task {job_id}'
                }
        
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
    
    async def _start_scheduler(self) -> Dict[str, Any]:
        """Start the scheduler loop."""
        if self.running:
            return {
                'success': False,
                'message': 'Scheduler already running'
            }
        
        self.running = True
        asyncio.create_task(self._run_scheduler())
        
        logger.info("Scheduler started")
        return {
            'success': True,
            'message': 'Scheduler started'
        }
    
    def _stop_scheduler(self) -> Dict[str, Any]:
        """Stop the scheduler loop."""
        self.running = False
        logger.info("Scheduler stopped")
        
        return {
            'success': True,
            'message': 'Scheduler stopped'
        }
    
    async def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities."""
        return [
            'schedule',
            'list',
            'cancel',
            'start',
            'stop'
        ]
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        self.running = False
        schedule.clear()
        logger.info("Scheduler plugin cleaned up")


# Plugin metadata
PLUGIN_INFO = {
    'name': 'scheduler',
    'version': '1.0.0',
    'class': SchedulerPlugin,
    'description': 'Schedule tasks for execution at specific times or intervals',
    'author': 'Cosik Team'
}
