"""
Enhanced AI prompting utilities for better task understanding and execution.
"""

from typing import Dict, Any, List, Optional
from loguru import logger


class PromptTemplates:
    """Collection of optimized prompt templates for various AI tasks."""
    
    COMMAND_PARSER = """You are an expert AI assistant specialized in parsing natural language commands for a Windows automation system.

Your task is to analyze commands and extract:
1. The primary intent (what the user wants to do)
2. All relevant parameters
3. Any implicit requirements or context

Available intents:
- open_application: Launch a Windows application
- close_application: Close an application
- click: Click on UI element (by text, image, or coordinates)
- type_text: Type text using keyboard
- read_file: Read and retrieve file contents
- write_file: Write data to a file
- modify_file: Modify existing file
- system_command: Execute Windows command/PowerShell
- change_setting: Modify system settings
- search: Search for files, text, or information
- move_mouse: Move mouse cursor to position
- take_screenshot: Capture screen or region
- wait: Pause execution for duration
- complex_task: Multi-step task requiring breakdown
- plugin_command: Execute plugin-specific command

Guidelines:
- Be precise with parameters
- Include confidence score (0.0-1.0)
- Provide reasoning for your interpretation
- Consider Polish and English language
- Handle ambiguity gracefully

Return JSON format:
{
  "intent": "intent_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "confidence": 0.95,
  "reasoning": "why you chose this interpretation",
  "alternatives": ["other possible interpretations"]
}"""

    TASK_PLANNER = """You are an expert AI task planner for Windows automation.

Given a high-level goal, create a detailed, executable plan broken down into atomic steps.

Considerations:
- Each step must be specific and actionable
- Steps should be ordered logically
- Include error handling checkpoints
- Consider dependencies between steps
- Add verification steps when appropriate
- Think about edge cases

Each step should include:
{
  "step": 1,
  "intent": "specific_intent",
  "parameters": {...},
  "description": "human-readable explanation",
  "depends_on": [previous_step_numbers],
  "expected_outcome": "what should happen",
  "verification": "how to verify success"
}

Return a JSON array of steps that will accomplish the goal efficiently and reliably."""

    ERROR_ANALYZER = """You are an expert AI debugger for Windows automation systems.

Analyze the failed task and error to provide:
1. Root cause analysis
2. Suggested fixes
3. Alternative approaches
4. Prevention strategies

Consider:
- Error type and context
- Task that was being executed
- Historical failures (if provided)
- System state
- Common Windows automation pitfalls

Return JSON format:
{
  "root_cause": "detailed explanation",
  "error_type": "classification",
  "suggested_fixes": [
    {
      "approach": "description",
      "steps": ["step1", "step2"],
      "confidence": 0.8
    }
  ],
  "alternative_approaches": ["approach1", "approach2"],
  "prevention": "how to avoid this in future"
}"""

    CODE_GENERATOR = """You are an expert Python programmer specializing in Windows automation.

Generate clean, efficient, well-documented code that:
- Follows best practices
- Includes error handling
- Has clear variable names
- Includes type hints
- Is modular and reusable

Requirements:
- Python 3.8+ syntax
- Async/await when appropriate
- Comprehensive error handling
- Logging with loguru
- Type hints

Return the code with explanation."""

    CONTEXT_BUILDER = """You are an AI context analyzer.

Given the current state and history, build a comprehensive context summary that includes:
- Current active applications
- Recent user actions
- Relevant file system state
- System resources
- User's likely intent

This context will be used to make better decisions about task execution.

Return JSON with contextual information organized by category."""


class AIPromptBuilder:
    """Build optimized prompts for AI queries."""
    
    def __init__(self):
        """Initialize prompt builder."""
        self.templates = PromptTemplates()
    
    def build_command_prompt(
        self,
        command: str,
        context: Optional[List[Dict]] = None,
        language: str = 'auto'
    ) -> Dict[str, str]:
        """
        Build prompt for command parsing.
        
        Args:
            command: User command to parse
            context: Recent interaction history
            language: Language hint (auto, pl, en)
            
        Returns:
            Dict with system and user prompts
        """
        system_prompt = self.templates.COMMAND_PARSER
        
        user_prompt = f"Command to parse: \"{command}\""
        
        if language != 'auto':
            user_prompt += f"\nLanguage: {language}"
        
        if context:
            recent = context[-3:]
            context_str = "\n".join([
                f"- User: {c.get('input_text', '')}"
                f"\n  Result: {c.get('parsed_result', {}).get('intent', 'unknown')}"
                for c in recent
            ])
            user_prompt += f"\n\nRecent context:\n{context_str}"
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def build_planning_prompt(
        self,
        goal: str,
        context: Optional[Dict] = None,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Build prompt for task planning.
        
        Args:
            goal: High-level goal
            context: Current system context
            constraints: Any constraints or limitations
            
        Returns:
            Dict with system and user prompts
        """
        system_prompt = self.templates.TASK_PLANNER
        
        user_prompt = f"Goal: {goal}"
        
        if context:
            user_prompt += f"\n\nCurrent context:\n"
            if 'active_windows' in context:
                user_prompt += f"Active windows: {context['active_windows']}\n"
            if 'current_dir' in context:
                user_prompt += f"Current directory: {context['current_dir']}\n"
            if 'clipboard' in context:
                user_prompt += f"Clipboard: {context['clipboard'][:100]}...\n"
        
        if constraints:
            user_prompt += f"\n\nConstraints:\n"
            for constraint in constraints:
                user_prompt += f"- {constraint}\n"
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def build_error_analysis_prompt(
        self,
        task: Dict[str, Any],
        error: str,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Build prompt for error analysis.
        
        Args:
            task: Failed task details
            error: Error message
            history: Historical failures
            
        Returns:
            Dict with system and user prompts
        """
        system_prompt = self.templates.ERROR_ANALYZER
        
        user_prompt = f"Failed Task:\n"
        user_prompt += f"Intent: {task.get('intent')}\n"
        user_prompt += f"Parameters: {task.get('parameters')}\n"
        user_prompt += f"\nError: {error}\n"
        
        if history:
            user_prompt += f"\nPrevious failures:\n"
            for h in history[-3:]:
                user_prompt += f"- {h.get('error', 'unknown')}\n"
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def build_code_generation_prompt(
        self,
        description: str,
        requirements: Optional[List[str]] = None,
        examples: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Build prompt for code generation.
        
        Args:
            description: What the code should do
            requirements: Specific requirements
            examples: Example code or patterns
            
        Returns:
            Dict with system and user prompts
        """
        system_prompt = self.templates.CODE_GENERATOR
        
        user_prompt = f"Generate code for: {description}\n"
        
        if requirements:
            user_prompt += f"\nRequirements:\n"
            for req in requirements:
                user_prompt += f"- {req}\n"
        
        if examples:
            user_prompt += f"\nExample patterns:\n{examples}\n"
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def build_context_summary_prompt(
        self,
        system_state: Dict[str, Any],
        recent_actions: List[Dict],
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Build prompt for context summarization.
        
        Args:
            system_state: Current system state
            recent_actions: Recent user actions
            user_preferences: User preferences if known
            
        Returns:
            Dict with system and user prompts
        """
        system_prompt = self.templates.CONTEXT_BUILDER
        
        user_prompt = "Current System State:\n"
        user_prompt += f"{system_state}\n\n"
        
        user_prompt += "Recent Actions:\n"
        for action in recent_actions[-5:]:
            user_prompt += f"- {action}\n"
        
        if user_preferences:
            user_prompt += f"\nUser Preferences:\n{user_preferences}\n"
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }


class ConversationManager:
    """Manage conversation history for better context awareness."""
    
    def __init__(self, max_history: int = 10):
        """Initialize conversation manager."""
        self.max_history = max_history
        self.history = []
    
    def add_interaction(
        self,
        user_input: str,
        agent_response: Dict[str, Any],
        success: bool
    ):
        """Add interaction to history."""
        self.history.append({
            'user': user_input,
            'agent': agent_response,
            'success': success,
            'timestamp': logger.info
        })
        
        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context(self, limit: int = 5) -> List[Dict]:
        """Get recent context."""
        return self.history[-limit:]
    
    def get_summary(self) -> str:
        """Get conversation summary."""
        if not self.history:
            return "No previous interactions"
        
        successful = sum(1 for h in self.history if h['success'])
        total = len(self.history)
        
        summary = f"Total interactions: {total}\n"
        summary += f"Successful: {successful} ({successful/total*100:.1f}%)\n"
        
        # Recent commands
        summary += "\nRecent commands:\n"
        for h in self.history[-3:]:
            summary += f"- {h['user'][:50]}... ({'✓' if h['success'] else '✗'})\n"
        
        return summary
