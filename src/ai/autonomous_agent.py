"""Autonomous goal-oriented behavior system for self-directed task execution."""

import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import random


class AutonomousAgent:
    """
    Autonomous agent capable of self-directed behavior and goal pursuit.
    Works independently to achieve objectives with minimal human intervention.
    """
    
    def __init__(
        self,
        config,
        reasoning_engine,
        context_manager,
        workflow_orchestrator,
        task_executor
    ):
        """
        Initialize autonomous agent.
        
        Args:
            config: Configuration object
            reasoning_engine: For intelligent planning
            context_manager: For context awareness
            workflow_orchestrator: For task execution
            task_executor: For individual task execution
        """
        self.config = config
        self.reasoning = reasoning_engine
        self.context = context_manager
        self.workflow = workflow_orchestrator
        self.executor = task_executor
        
        # Agent state
        self.is_autonomous = config.get('agent.autonomous_mode', False)
        self.autonomy_level = config.get('agent.autonomy_level', 'supervised')  # supervised, semi, full
        self.active = False
        self.current_objective = None
        
        # Learning and adaptation
        self.success_patterns = []
        self.failure_patterns = []
        
    async def start_autonomous_mode(self, objective: str) -> None:
        """
        Start autonomous mode with a high-level objective.
        
        Args:
            objective: High-level objective to achieve
        """
        logger.info(f"Starting autonomous mode with objective: {objective}")
        
        self.active = True
        self.current_objective = objective
        
        await self.context.update_goal(objective, {'autonomous': True})
        
        # Main autonomous loop
        while self.active:
            try:
                # Assess current situation
                situation = await self._assess_situation()
                
                # Make decision on next action
                decision = await self._make_autonomous_decision(situation)
                
                if decision['action'] == 'stop':
                    logger.info("Autonomous agent stopping: objective complete or impossible")
                    break
                
                # Execute decision
                result = await self._execute_decision(decision)
                
                # Learn from outcome
                await self._learn_from_result(decision, result)
                
                # Wait before next iteration
                await asyncio.sleep(self.config.get('agent.autonomous_delay', 1.0))
                
            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")
                
                if self.autonomy_level == 'supervised':
                    # Stop and ask for help in supervised mode
                    logger.info("Stopping autonomous mode due to error in supervised mode")
                    break
                else:
                    # Try to recover in other modes
                    await self._attempt_recovery(e)
        
        self.active = False
        logger.info("Autonomous mode ended")
    
    async def _assess_situation(self) -> Dict[str, Any]:
        """Assess current situation and progress."""
        # Get current context
        context = await self.context.get_relevant_context(
            self.current_objective
        )
        
        # Analyze progress
        progress = self._analyze_progress(context)
        
        # Identify obstacles
        obstacles = self._identify_obstacles(context)
        
        # Gather available resources
        resources = await self._gather_resources()
        
        return {
            'context': context,
            'progress': progress,
            'obstacles': obstacles,
            'resources': resources,
            'objective': self.current_objective
        }
    
    def _analyze_progress(self, context: Dict) -> Dict[str, Any]:
        """Analyze progress towards objective."""
        active_tasks = context.get('active_tasks', [])
        
        total_tasks = len(active_tasks)
        completed = sum(1 for t in active_tasks if t.get('status') == 'completed')
        failed = sum(1 for t in active_tasks if t.get('status') == 'failed')
        pending = sum(1 for t in active_tasks if t.get('status') == 'pending')
        
        progress_percentage = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'percentage': progress_percentage,
            'is_complete': pending == 0 and failed == 0 and total_tasks > 0
        }
    
    def _identify_obstacles(self, context: Dict) -> List[Dict[str, Any]]:
        """Identify obstacles preventing progress."""
        obstacles = []
        
        # Check failed tasks
        failed_tasks = [
            t for t in context.get('active_tasks', [])
            if t.get('status') == 'failed'
        ]
        
        for task in failed_tasks:
            obstacles.append({
                'type': 'failed_task',
                'task': task,
                'severity': 'high'
            })
        
        # Check blocked tasks
        blocked_tasks = [
            t for t in context.get('active_tasks', [])
            if t.get('status') == 'blocked'
        ]
        
        for task in blocked_tasks:
            obstacles.append({
                'type': 'blocked_task',
                'task': task,
                'severity': 'medium'
            })
        
        # Check constraints
        constraints = context.get('constraints', [])
        if constraints:
            obstacles.append({
                'type': 'constraints',
                'count': len(constraints),
                'severity': 'low'
            })
        
        return obstacles
    
    async def _gather_resources(self) -> Dict[str, Any]:
        """Gather available resources for task execution."""
        return {
            'ai_engine_available': self.reasoning.ai_engine is not None,
            'memory_available': self.reasoning.memory is not None,
            'autonomy_level': self.autonomy_level,
            'max_parallel_tasks': self.workflow.max_parallel
        }
    
    async def _make_autonomous_decision(
        self,
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make an autonomous decision based on current situation.
        
        Args:
            situation: Current situation assessment
            
        Returns:
            Decision with action and parameters
        """
        logger.info("Making autonomous decision")
        
        progress = situation['progress']
        obstacles = situation['obstacles']
        
        # Check if objective is complete
        if progress['is_complete']:
            return {
                'action': 'stop',
                'reason': 'objective_complete'
            }
        
        # Handle obstacles first
        if obstacles:
            return await self._decide_obstacle_resolution(obstacles)
        
        # Check if we need to decompose the goal
        if progress['total_tasks'] == 0:
            return {
                'action': 'decompose_goal',
                'goal': self.current_objective
            }
        
        # Execute pending tasks
        if progress['pending'] > 0:
            return {
                'action': 'execute_pending_tasks'
            }
        
        # If nothing to do, explore or stop
        if progress['completed'] > 0:
            return {
                'action': 'stop',
                'reason': 'all_tasks_processed'
            }
        
        # Default: analyze and plan
        return {
            'action': 'analyze_and_plan'
        }
    
    async def _decide_obstacle_resolution(
        self,
        obstacles: List[Dict]
    ) -> Dict[str, Any]:
        """Decide how to resolve obstacles."""
        # Sort by severity
        obstacles_sorted = sorted(
            obstacles,
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['severity']],
            reverse=True
        )
        
        top_obstacle = obstacles_sorted[0]
        
        if top_obstacle['type'] == 'failed_task':
            # Try alternative approach
            return {
                'action': 'retry_with_alternative',
                'task': top_obstacle['task']
            }
        elif top_obstacle['type'] == 'blocked_task':
            # Try to unblock
            return {
                'action': 'attempt_unblock',
                'task': top_obstacle['task']
            }
        else:
            # Skip or adapt
            return {
                'action': 'adapt_strategy'
            }
    
    async def _execute_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a decision."""
        action = decision['action']
        logger.info(f"Executing decision: {action}")
        
        try:
            if action == 'stop':
                return {'success': True, 'stopped': True}
            
            elif action == 'decompose_goal':
                goal = decision.get('goal', self.current_objective)
                subtasks = await self.reasoning.decompose_goal(goal)
                
                # Add subtasks to context
                for task in subtasks:
                    await self.context.add_task(task)
                
                return {
                    'success': True,
                    'subtasks_created': len(subtasks)
                }
            
            elif action == 'execute_pending_tasks':
                # Get pending tasks
                context = await self.context.get_relevant_context('')
                pending = [
                    t for t in context.get('active_tasks', [])
                    if t.get('status') == 'pending'
                ]
                
                # Execute first pending task
                if pending:
                    task = pending[0]
                    result = await self.executor.execute(task)
                    
                    # Update task status
                    await self.context.update_task_status(
                        task.get('id', ''),
                        'completed' if result.get('success') else 'failed',
                        result
                    )
                    
                    return result
                
                return {'success': True, 'no_tasks': True}
            
            elif action == 'retry_with_alternative':
                task = decision.get('task', {})
                # Modify task parameters for alternative approach
                alternative_task = self._create_alternative(task)
                result = await self.executor.execute(alternative_task)
                return result
            
            elif action == 'attempt_unblock':
                # Try to resolve blocking issue
                task = decision.get('task', {})
                # This would need specific unblocking logic
                return {'success': True, 'attempted': True}
            
            elif action == 'adapt_strategy':
                # Adapt execution strategy
                return {'success': True, 'strategy_adapted': True}
            
            elif action == 'analyze_and_plan':
                # Analyze situation and create new plan
                analysis = await self.reasoning.analyze_goal(self.current_objective)
                return {'success': True, 'analysis': analysis}
            
            else:
                logger.warning(f"Unknown action: {action}")
                return {'success': False, 'error': 'unknown_action'}
                
        except Exception as e:
            logger.error(f"Decision execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_alternative(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alternative version of a failed task."""
        alternative = task.copy()
        
        # Modify parameters slightly
        if 'parameters' in alternative:
            params = alternative['parameters'].copy()
            
            # Example: try different timeout, different approach
            params['timeout'] = params.get('timeout', 30) * 2
            params['alternative_method'] = True
            
            alternative['parameters'] = params
        
        return alternative
    
    async def _learn_from_result(
        self,
        decision: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Learn from decision result to improve future decisions."""
        pattern = {
            'decision': decision,
            'result': result,
            'timestamp': datetime.now(),
            'objective': self.current_objective
        }
        
        if result.get('success', False):
            self.success_patterns.append(pattern)
            logger.debug(f"Recorded successful pattern: {decision['action']}")
        else:
            self.failure_patterns.append(pattern)
            logger.debug(f"Recorded failed pattern: {decision['action']}")
        
        # Limit pattern memory
        max_patterns = 100
        if len(self.success_patterns) > max_patterns:
            self.success_patterns = self.success_patterns[-max_patterns:]
        if len(self.failure_patterns) > max_patterns:
            self.failure_patterns = self.failure_patterns[-max_patterns:]
        
        # Update reasoning engine if available
        if self.reasoning and self.reasoning.memory:
            await self.reasoning.learn_from_outcome(
                self.current_objective,
                [decision],
                result
            )
    
    async def _attempt_recovery(self, error: Exception) -> None:
        """Attempt to recover from an error."""
        logger.warning(f"Attempting recovery from error: {error}")
        
        # Simple recovery strategies
        recovery_strategies = [
            'wait_and_retry',
            'reset_context',
            'reduce_complexity',
            'ask_for_help'
        ]
        
        # Choose strategy based on autonomy level
        if self.autonomy_level == 'full':
            strategy = random.choice(recovery_strategies[:3])
        else:
            strategy = 'ask_for_help'
        
        if strategy == 'wait_and_retry':
            await asyncio.sleep(5)
        elif strategy == 'reset_context':
            # Clear some context
            pass
        elif strategy == 'reduce_complexity':
            # Simplify current goal
            pass
        elif strategy == 'ask_for_help':
            logger.info("Requesting human intervention")
            self.active = False
    
    async def stop_autonomous_mode(self) -> None:
        """Stop autonomous mode."""
        logger.info("Stopping autonomous mode")
        self.active = False
    
    def get_autonomy_status(self) -> Dict[str, Any]:
        """Get current autonomy status."""
        return {
            'active': self.active,
            'autonomy_level': self.autonomy_level,
            'current_objective': self.current_objective,
            'success_patterns_learned': len(self.success_patterns),
            'failure_patterns_learned': len(self.failure_patterns)
        }
