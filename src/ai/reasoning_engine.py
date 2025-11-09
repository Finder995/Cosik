"""Advanced reasoning engine for intelligent task planning and decision making."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from datetime import datetime
import json


class ReasoningEngine:
    """
    Advanced reasoning engine that provides intelligent decision making,
    goal decomposition, and strategic planning for complex tasks.
    """
    
    def __init__(self, config, ai_engine=None, memory_manager=None):
        """
        Initialize reasoning engine.
        
        Args:
            config: Configuration object
            ai_engine: AI engine for LLM-based reasoning
            memory_manager: Memory manager for context and history
        """
        self.config = config
        self.ai_engine = ai_engine
        self.memory = memory_manager
        self.reasoning_mode = config.get('reasoning.mode', 'hybrid')  # pattern, ai, hybrid
        self.max_decomposition_depth = config.get('reasoning.max_depth', 5)
        
    async def analyze_goal(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a high-level goal and determine its feasibility and requirements.
        
        Args:
            goal: High-level goal description
            context: Optional context information
            
        Returns:
            Analysis with feasibility, requirements, and suggested approach
        """
        logger.info(f"Analyzing goal: {goal}")
        
        analysis = {
            'goal': goal,
            'feasible': True,
            'confidence': 0.0,
            'requirements': [],
            'risks': [],
            'estimated_steps': 0,
            'estimated_time': 0,
            'approach': 'sequential'
        }
        
        # Get historical context
        if self.memory:
            similar_goals = await self.memory.find_similar_tasks(goal, limit=5)
            if similar_goals:
                analysis['similar_history'] = similar_goals
                analysis['confidence'] += 0.3
        
        # Pattern-based analysis
        pattern_analysis = self._pattern_analyze_goal(goal)
        analysis.update(pattern_analysis)
        
        # AI-based analysis if available
        if self.ai_engine and self.reasoning_mode in ['ai', 'hybrid']:
            ai_analysis = await self._ai_analyze_goal(goal, context)
            analysis = self._merge_analysis(analysis, ai_analysis)
        
        logger.info(f"Goal analysis complete: feasible={analysis['feasible']}, "
                   f"confidence={analysis['confidence']:.2f}")
        
        return analysis
    
    def _pattern_analyze_goal(self, goal: str) -> Dict[str, Any]:
        """Pattern-based goal analysis."""
        goal_lower = goal.lower()
        
        # Complexity estimation
        complexity_indicators = {
            'simple': ['open', 'close', 'click', 'type', 'read'],
            'medium': ['find', 'search', 'modify', 'change', 'update'],
            'complex': ['automate', 'integrate', 'analyze', 'optimize', 'learn']
        }
        
        complexity = 'simple'
        for level, keywords in complexity_indicators.items():
            if any(kw in goal_lower for kw in keywords):
                complexity = level
        
        # Estimate steps and time
        step_estimates = {'simple': 3, 'medium': 8, 'complex': 20}
        time_estimates = {'simple': 10, 'medium': 60, 'complex': 300}
        
        return {
            'complexity': complexity,
            'estimated_steps': step_estimates[complexity],
            'estimated_time': time_estimates[complexity],
            'confidence': 0.5
        }
    
    async def _ai_analyze_goal(self, goal: str, context: Optional[Dict]) -> Dict[str, Any]:
        """AI-based goal analysis using LLM."""
        if not self.ai_engine or not self.ai_engine.client:
            return {}
        
        prompt = f"""Analyze this goal and provide a structured assessment:

Goal: {goal}
Context: {json.dumps(context) if context else 'None'}

Provide analysis in JSON format with:
- feasible (boolean)
- confidence (0.0-1.0)
- requirements (list of strings)
- risks (list of strings)
- estimated_steps (integer)
- estimated_time (seconds)
- approach (sequential/parallel/adaptive)
"""
        
        try:
            response = await self.ai_engine.generate_response(prompt)
            # Parse JSON response
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {}
    
    def _merge_analysis(self, pattern_analysis: Dict, ai_analysis: Dict) -> Dict[str, Any]:
        """Merge pattern and AI analysis results."""
        merged = pattern_analysis.copy()
        
        # Merge with AI analysis, giving higher weight to AI for certain fields
        if ai_analysis:
            merged['feasible'] = ai_analysis.get('feasible', merged.get('feasible', True))
            merged['confidence'] = (
                merged.get('confidence', 0.5) * 0.3 + 
                ai_analysis.get('confidence', 0.5) * 0.7
            )
            merged['requirements'] = ai_analysis.get('requirements', [])
            merged['risks'] = ai_analysis.get('risks', [])
            merged['approach'] = ai_analysis.get('approach', 'sequential')
        
        return merged
    
    async def decompose_goal(
        self, 
        goal: str, 
        context: Optional[Dict] = None,
        depth: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Decompose a high-level goal into executable sub-tasks.
        
        Args:
            goal: High-level goal to decompose
            context: Optional context information
            depth: Current decomposition depth
            
        Returns:
            List of sub-tasks with dependencies
        """
        if depth >= self.max_decomposition_depth:
            logger.warning(f"Max decomposition depth reached: {depth}")
            return [{'type': 'atomic', 'description': goal, 'executable': True}]
        
        logger.info(f"Decomposing goal (depth {depth}): {goal}")
        
        # Check if goal is already atomic
        if self._is_atomic_task(goal):
            return [{'type': 'atomic', 'description': goal, 'executable': True}]
        
        # Decompose using appropriate method
        if self.reasoning_mode == 'pattern':
            subtasks = self._pattern_decompose(goal, context)
        elif self.reasoning_mode == 'ai' and self.ai_engine:
            subtasks = await self._ai_decompose(goal, context)
        else:  # hybrid
            pattern_tasks = self._pattern_decompose(goal, context)
            if self.ai_engine:
                ai_tasks = await self._ai_decompose(goal, context)
                subtasks = self._merge_subtasks(pattern_tasks, ai_tasks)
            else:
                subtasks = pattern_tasks
        
        # Recursively decompose non-atomic subtasks
        final_tasks = []
        for task in subtasks:
            if task.get('executable', False):
                final_tasks.append(task)
            else:
                nested = await self.decompose_goal(
                    task['description'], 
                    context, 
                    depth + 1
                )
                final_tasks.extend(nested)
        
        logger.info(f"Decomposed into {len(final_tasks)} atomic tasks")
        return final_tasks
    
    def _is_atomic_task(self, task: str) -> bool:
        """Check if a task is atomic (cannot be further decomposed)."""
        task_lower = task.lower()
        
        atomic_verbs = [
            'click', 'type', 'press', 'open', 'close', 'read', 'write',
            'move', 'scroll', 'wait', 'find', 'get', 'set'
        ]
        
        # Task is atomic if it starts with an atomic verb
        return any(task_lower.startswith(verb) for verb in atomic_verbs)
    
    def _pattern_decompose(self, goal: str, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """Pattern-based goal decomposition."""
        goal_lower = goal.lower()
        subtasks = []
        
        # Common patterns
        if 'automate' in goal_lower and 'report' in goal_lower:
            subtasks = [
                {'description': 'Open reporting application', 'executable': True},
                {'description': 'Load data from source', 'executable': True},
                {'description': 'Generate report content', 'executable': False},
                {'description': 'Format and save report', 'executable': True}
            ]
        elif 'find' in goal_lower and 'file' in goal_lower:
            subtasks = [
                {'description': 'Determine search location', 'executable': True},
                {'description': 'Execute file search', 'executable': True},
                {'description': 'Filter and sort results', 'executable': True}
            ]
        elif 'install' in goal_lower or 'setup' in goal_lower:
            subtasks = [
                {'description': 'Download installation package', 'executable': True},
                {'description': 'Run installer', 'executable': True},
                {'description': 'Configure settings', 'executable': False},
                {'description': 'Verify installation', 'executable': True}
            ]
        else:
            # Generic decomposition
            subtasks = [{'description': goal, 'executable': True}]
        
        return subtasks
    
    async def _ai_decompose(self, goal: str, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """AI-based goal decomposition using LLM."""
        if not self.ai_engine or not self.ai_engine.client:
            return [{'description': goal, 'executable': True}]
        
        prompt = f"""Decompose this goal into concrete sub-tasks:

Goal: {goal}
Context: {json.dumps(context) if context else 'None'}

Provide a JSON array of subtasks, each with:
- description (string): clear description of the subtask
- executable (boolean): true if this is an atomic action that can be directly executed
- dependencies (array): indices of tasks that must complete first

Example:
[
  {{"description": "Open notepad", "executable": true, "dependencies": []}},
  {{"description": "Type content", "executable": true, "dependencies": [0]}}
]
"""
        
        try:
            response = await self.ai_engine.generate_response(prompt)
            subtasks = json.loads(response)
            return subtasks
        except Exception as e:
            logger.warning(f"AI decomposition failed: {e}")
            return [{'description': goal, 'executable': True}]
    
    def _merge_subtasks(
        self, 
        pattern_tasks: List[Dict], 
        ai_tasks: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Merge pattern and AI subtasks intelligently."""
        # If AI provides more detailed breakdown, use it
        if len(ai_tasks) > len(pattern_tasks) and ai_tasks[0].get('description'):
            return ai_tasks
        # Otherwise use pattern-based
        return pattern_tasks
    
    async def make_decision(
        self,
        situation: str,
        options: List[str],
        criteria: Optional[Dict[str, float]] = None
    ) -> Tuple[str, float]:
        """
        Make an intelligent decision given a situation and options.
        
        Args:
            situation: Current situation description
            options: List of possible actions/choices
            criteria: Optional scoring criteria with weights
            
        Returns:
            Tuple of (chosen_option, confidence_score)
        """
        logger.info(f"Making decision for situation: {situation}")
        
        if not options:
            return ("no_action", 0.0)
        
        if len(options) == 1:
            return (options[0], 1.0)
        
        # Default criteria
        if criteria is None:
            criteria = {
                'success_probability': 0.4,
                'efficiency': 0.3,
                'safety': 0.2,
                'reversibility': 0.1
            }
        
        # Score each option
        scores = {}
        for option in options:
            score = await self._score_option(situation, option, criteria)
            scores[option] = score
        
        # Choose best option
        best_option = max(scores, key=scores.get)
        confidence = scores[best_option]
        
        logger.info(f"Decision made: {best_option} (confidence: {confidence:.2f})")
        return (best_option, confidence)
    
    async def _score_option(
        self,
        situation: str,
        option: str,
        criteria: Dict[str, float]
    ) -> float:
        """Score an option based on criteria."""
        # Pattern-based scoring
        pattern_score = self._pattern_score_option(situation, option)
        
        # AI-based scoring if available
        if self.ai_engine and self.reasoning_mode in ['ai', 'hybrid']:
            ai_score = await self._ai_score_option(situation, option, criteria)
            # Weighted combination
            return pattern_score * 0.3 + ai_score * 0.7
        
        return pattern_score
    
    def _pattern_score_option(self, situation: str, option: str) -> float:
        """Simple pattern-based scoring."""
        # Basic heuristics
        score = 0.5  # baseline
        
        option_lower = option.lower()
        
        # Prefer simpler actions
        if len(option.split()) <= 3:
            score += 0.1
        
        # Prefer safer actions
        safe_keywords = ['read', 'check', 'verify', 'view', 'list']
        if any(kw in option_lower for kw in safe_keywords):
            score += 0.15
        
        # Penalize risky actions
        risky_keywords = ['delete', 'remove', 'terminate', 'kill', 'force']
        if any(kw in option_lower for kw in risky_keywords):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _ai_score_option(
        self,
        situation: str,
        option: str,
        criteria: Dict[str, float]
    ) -> float:
        """AI-based option scoring."""
        if not self.ai_engine or not self.ai_engine.client:
            return 0.5
        
        prompt = f"""Score this option for the given situation:

Situation: {situation}
Option: {option}
Criteria: {json.dumps(criteria)}

Provide a score between 0.0 and 1.0 based on the criteria.
Return only a JSON object: {{"score": 0.75, "reasoning": "..."}}
"""
        
        try:
            response = await self.ai_engine.generate_response(prompt)
            result = json.loads(response)
            return result.get('score', 0.5)
        except Exception as e:
            logger.warning(f"AI scoring failed: {e}")
            return 0.5
    
    async def learn_from_outcome(
        self,
        goal: str,
        subtasks: List[Dict],
        outcome: Dict[str, Any]
    ) -> None:
        """
        Learn from task execution outcome to improve future reasoning.
        
        Args:
            goal: Original goal
            subtasks: Decomposed subtasks that were executed
            outcome: Execution outcome with success status and details
        """
        if not self.memory:
            return
        
        logger.info(f"Learning from outcome: {outcome.get('success', False)}")
        
        # Store execution pattern
        learning_record = {
            'timestamp': datetime.now().isoformat(),
            'goal': goal,
            'subtasks': subtasks,
            'outcome': outcome,
            'success': outcome.get('success', False),
            'execution_time': outcome.get('execution_time', 0)
        }
        
        await self.memory.store_learning(learning_record)
        
        # Update internal reasoning patterns if successful
        if outcome.get('success', False):
            logger.info("Successful outcome - reinforcing strategy")
            # Could implement reinforcement learning here
        else:
            logger.info("Failed outcome - adjusting strategy")
            # Could implement strategy adjustment here
