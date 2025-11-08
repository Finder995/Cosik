"""AI Engine for advanced natural language understanding and task planning."""

import os
import json
from typing import Dict, Any, List, Optional
from loguru import logger


class AIEngine:
    """
    Advanced AI engine using OpenAI GPT for intelligent task planning.
    Handles complex commands that pattern matching cannot solve.
    """
    
    def __init__(self, config):
        """Initialize AI engine with configuration."""
        self.config = config
        self.provider = config.get('ai.provider', 'openai')
        self.model = config.get('ai.model', 'gpt-4')
        self.temperature = config.get('ai.temperature', 0.7)
        self.max_tokens = config.get('ai.max_tokens', 2000)
        
        # Initialize AI client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AI provider client."""
        try:
            if self.provider == 'openai':
                self._init_openai()
            elif self.provider == 'anthropic':
                self._init_anthropic()
            else:
                logger.warning(f"Unknown AI provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            logger.info("AI features will be limited to pattern matching")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment")
                return
            
            openai.api_key = api_key
            self.client = openai
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.warning("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude client."""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment")
                return
            
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info("Anthropic client initialized successfully")
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.error(f"Anthropic initialization failed: {e}")
    
    async def parse_complex_command(self, text: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Parse complex commands using AI when pattern matching fails.
        
        Args:
            text: Natural language command
            context: Previous interactions for context
            
        Returns:
            Parsed command with intent and parameters
        """
        if not self.client:
            logger.warning("AI client not available, using fallback parsing")
            return self._fallback_parse(text)
        
        try:
            if self.provider == 'openai':
                return await self._parse_with_openai(text, context)
            elif self.provider == 'anthropic':
                return await self._parse_with_anthropic(text, context)
            else:
                return self._fallback_parse(text)
        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            return self._fallback_parse(text)
    
    async def _parse_with_openai(self, text: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Parse command using OpenAI GPT."""
        system_prompt = """You are an AI assistant that parses natural language commands for a Windows automation agent.
        
Available intents:
- open_application: Open an application
- close_application: Close an application
- click: Click on screen element
- type_text: Type text
- read_file: Read file content
- write_file: Write to file
- modify_file: Modify file
- system_command: Execute system command
- change_setting: Change system setting
- search: Search for something
- move_mouse: Move mouse cursor
- take_screenshot: Take screenshot
- wait: Wait for duration
- complex_task: Multi-step task requiring planning

Return JSON with:
{
  "intent": "intent_name",
  "parameters": {...},
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}"""
        
        user_message = f"Parse this command: {text}"
        
        if context:
            context_str = "\n".join([f"- {c['input_text']}" for c in context[-3:]])
            user_message += f"\n\nRecent context:\n{context_str}"
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            logger.info(f"OpenAI parsed command: {result.get('intent')} (confidence: {result.get('confidence')})")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return self._fallback_parse(text)
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._fallback_parse(text)
    
    async def _parse_with_anthropic(self, text: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Parse command using Anthropic Claude."""
        system_prompt = """You are an AI assistant that parses natural language commands for a Windows automation agent.
Parse the command and return JSON with intent, parameters, confidence, and reasoning."""
        
        user_message = f"Parse this command: {text}"
        
        if context:
            context_str = "\n".join([f"- {c['input_text']}" for c in context[-3:]])
            user_message += f"\n\nRecent context:\n{context_str}"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result_text = message.content[0].text
            result = json.loads(result_text)
            
            logger.info(f"Anthropic parsed command: {result.get('intent')} (confidence: {result.get('confidence')})")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Anthropic response as JSON: {e}")
            return self._fallback_parse(text)
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when AI is not available."""
        return {
            'intent': 'complex_task',
            'parameters': {
                'description': text,
                'needs_ai_planning': True
            },
            'original_text': text,
            'confidence': 0.3,
            'reasoning': 'AI not available, using fallback'
        }
    
    async def create_task_plan(self, goal: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Create a detailed plan to achieve a complex goal.
        
        Args:
            goal: High-level goal description
            context: Current context (files, windows, etc.)
            
        Returns:
            List of individual tasks to execute
        """
        if not self.client:
            logger.warning("AI client not available for task planning")
            return []
        
        try:
            if self.provider == 'openai':
                return await self._plan_with_openai(goal, context)
            elif self.provider == 'anthropic':
                return await self._plan_with_anthropic(goal, context)
            else:
                return []
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            return []
    
    async def _plan_with_openai(self, goal: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Create task plan using OpenAI."""
        system_prompt = """You are an AI task planner for a Windows automation agent.
Given a high-level goal, break it down into specific, executable steps.

Each step should be a JSON object with:
{
  "step": 1,
  "intent": "intent_name",
  "parameters": {...},
  "description": "what this step does"
}

Return a JSON array of steps."""
        
        user_message = f"Goal: {goal}"
        if context:
            user_message += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            plan = json.loads(result_text)
            
            logger.info(f"Created task plan with {len(plan)} steps")
            return plan
            
        except Exception as e:
            logger.error(f"OpenAI task planning failed: {e}")
            return []
    
    async def _plan_with_anthropic(self, goal: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Create task plan using Anthropic."""
        system_prompt = """You are an AI task planner. Break down goals into executable steps."""
        
        user_message = f"Goal: {goal}"
        if context:
            user_message += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            result_text = message.content[0].text
            plan = json.loads(result_text)
            
            logger.info(f"Created task plan with {len(plan)} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Anthropic task planning failed: {e}")
            return []
    
    async def analyze_error(self, task: Dict[str, Any], error: str, 
                          history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze task failure and suggest fixes.
        
        Args:
            task: Failed task
            error: Error message
            history: Recent task history
            
        Returns:
            Analysis with suggested fixes
        """
        if not self.client:
            return {
                'analysis': 'AI not available for error analysis',
                'suggestions': []
            }
        
        system_prompt = """You are an AI assistant analyzing task failures.
Provide analysis and actionable suggestions to fix the issue.

Return JSON with:
{
  "analysis": "what went wrong",
  "suggestions": ["suggestion 1", "suggestion 2"],
  "retry_recommended": true/false,
  "modified_parameters": {...}
}"""
        
        user_message = f"""Task failed:
Intent: {task.get('intent')}
Parameters: {json.dumps(task.get('parameters', {}))}
Error: {error}
"""
        
        if history:
            history_str = "\n".join([f"- {h['intent']}: {h.get('status')}" for h in history[-5:]])
            user_message += f"\n\nRecent history:\n{history_str}"
        
        try:
            if self.provider == 'openai':
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                result_text = response.choices[0].message.content
            elif self.provider == 'anthropic':
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                result_text = message.content[0].text
            else:
                return {'analysis': 'Unknown provider', 'suggestions': []}
            
            result = json.loads(result_text)
            logger.info("Error analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"Error analysis failed: {e}")
            return {
                'analysis': f'Analysis failed: {str(e)}',
                'suggestions': ['Check error logs', 'Retry with modified parameters']
            }
