"""
Smart Retry Mechanism with exponential backoff and context awareness.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass, field


@dataclass
class RetryContext:
    """Context for retry operations."""
    task: Dict[str, Any]
    attempt: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    error_history: List[str] = field(default_factory=list)
    backoff_base: float = 1.0
    backoff_multiplier: float = 2.0
    max_backoff: float = 60.0
    first_attempt_time: Optional[datetime] = None
    last_attempt_time: Optional[datetime] = None
    
    def record_attempt(self, error: Optional[str] = None):
        """Record an attempt."""
        now = datetime.now()
        if self.first_attempt_time is None:
            self.first_attempt_time = now
        self.last_attempt_time = now
        self.attempt += 1
        
        if error:
            self.last_error = error
            self.error_history.append(f"Attempt {self.attempt}: {error}")
    
    def calculate_backoff(self) -> float:
        """Calculate backoff time for next retry."""
        if self.attempt == 0:
            return 0.0
        
        backoff = self.backoff_base * (self.backoff_multiplier ** (self.attempt - 1))
        return min(backoff, self.max_backoff)
    
    def should_retry(self) -> bool:
        """Check if should retry."""
        return self.attempt < self.max_attempts
    
    def get_summary(self) -> Dict[str, Any]:
        """Get retry summary."""
        duration = None
        if self.first_attempt_time and self.last_attempt_time:
            duration = (self.last_attempt_time - self.first_attempt_time).total_seconds()
        
        return {
            'attempts': self.attempt,
            'max_attempts': self.max_attempts,
            'last_error': self.last_error,
            'error_history': self.error_history,
            'duration_seconds': duration,
            'success': self.last_error is None
        }


class SmartRetry:
    """Smart retry mechanism with context awareness."""
    
    def __init__(self, config=None):
        """Initialize smart retry."""
        self.config = config or {}
        self.retry_contexts = {}
        self.error_patterns = {
            'network': ['connection', 'timeout', 'network', 'unreachable'],
            'permission': ['permission', 'access denied', 'forbidden'],
            'not_found': ['not found', 'does not exist', 'missing'],
            'resource': ['resource', 'memory', 'disk space'],
            'temporary': ['busy', 'locked', 'in use', 'try again']
        }
    
    async def execute_with_retry(
        self,
        task: Dict[str, Any],
        executor: Callable,
        max_attempts: int = 3,
        backoff_base: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_backoff: float = 60.0,
        error_handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with smart retry logic.
        
        Args:
            task: Task to execute
            executor: Async function to execute the task
            max_attempts: Maximum retry attempts
            backoff_base: Base backoff time in seconds
            backoff_multiplier: Backoff multiplier for exponential backoff
            max_backoff: Maximum backoff time
            error_handler: Optional custom error handler
            
        Returns:
            Result dictionary
        """
        task_id = task.get('task_id', id(task))
        
        # Create or get retry context
        if task_id not in self.retry_contexts:
            self.retry_contexts[task_id] = RetryContext(
                task=task,
                max_attempts=max_attempts,
                backoff_base=backoff_base,
                backoff_multiplier=backoff_multiplier,
                max_backoff=max_backoff
            )
        
        context = self.retry_contexts[task_id]
        
        while context.should_retry():
            try:
                # Wait before retry (except first attempt)
                if context.attempt > 0:
                    backoff = context.calculate_backoff()
                    logger.info(f"Retrying task after {backoff:.2f}s (attempt {context.attempt + 1}/{max_attempts})")
                    await asyncio.sleep(backoff)
                
                # Execute task
                result = await executor(task)
                
                # Check if successful
                if result.get('success', False):
                    context.record_attempt()
                    logger.info(f"Task succeeded on attempt {context.attempt}")
                    
                    # Clean up context
                    if task_id in self.retry_contexts:
                        del self.retry_contexts[task_id]
                    
                    return result
                
                # Task failed
                error = result.get('error', 'Unknown error')
                context.record_attempt(error)
                
                # Analyze error
                error_type = self._classify_error(error)
                logger.warning(f"Task failed (attempt {context.attempt}/{max_attempts}): {error} [type: {error_type}]")
                
                # Call custom error handler if provided
                if error_handler:
                    should_continue = await error_handler(context, error_type)
                    if not should_continue:
                        break
                
                # Check if error is retryable
                if not self._is_retryable_error(error_type):
                    logger.info(f"Error type '{error_type}' is not retryable, stopping")
                    break
                
            except Exception as e:
                error = str(e)
                context.record_attempt(error)
                logger.error(f"Exception during task execution (attempt {context.attempt}/{max_attempts}): {e}")
                
                if context.attempt >= max_attempts:
                    break
        
        # All retries exhausted or non-retryable error
        summary = context.get_summary()
        logger.error(f"Task failed after {context.attempt} attempts: {context.last_error}")
        
        # Clean up context
        if task_id in self.retry_contexts:
            del self.retry_contexts[task_id]
        
        return {
            'success': False,
            'error': context.last_error,
            'retry_summary': summary
        }
    
    def _classify_error(self, error: str) -> str:
        """Classify error type based on error message."""
        error_lower = error.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in error_lower:
                    return error_type
        
        return 'unknown'
    
    def _is_retryable_error(self, error_type: str) -> bool:
        """Check if error type is retryable."""
        retryable_types = {'network', 'temporary', 'resource', 'unknown'}
        return error_type in retryable_types
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        max_attempts: int = 3,
        backoff: float = 1.0,
        **kwargs
    ) -> Any:
        """
        Simple retry with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            max_attempts: Maximum attempts
            backoff: Initial backoff time
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                if attempt > 0:
                    wait_time = backoff * (2 ** (attempt - 1))
                    logger.info(f"Retrying after {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
                
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
                
                if attempt == max_attempts - 1:
                    raise
        
        raise last_error
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """Get statistics about current retry operations."""
        return {
            'active_retries': len(self.retry_contexts),
            'contexts': [
                {
                    'task_id': task_id,
                    'attempt': ctx.attempt,
                    'max_attempts': ctx.max_attempts,
                    'last_error': ctx.last_error
                }
                for task_id, ctx in self.retry_contexts.items()
            ]
        }
