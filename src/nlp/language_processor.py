"""Natural Language Processing module for understanding user commands."""

import re
from typing import Dict, Any, List, Optional
from loguru import logger


class LanguageProcessor:
    """Process natural language to extract intents and parameters."""
    
    def __init__(self, config, ai_engine=None):
        """Initialize the language processor."""
        self.config = config
        self.ai_engine = ai_engine
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent patterns for command recognition."""
        return {
            'open_application': [
                r'otwórz\s+(.+)',
                r'uruchom\s+(.+)',
                r'open\s+(.+)',
                r'start\s+(.+)',
                r'włącz\s+(.+)'
            ],
            'close_application': [
                r'zamknij\s+(.+)',
                r'close\s+(.+)',
                r'wyłącz\s+(.+)',
                r'zakończ\s+(.+)'
            ],
            'click': [
                r'kliknij\s+(.+)',
                r'click\s+(.+)',
                r'naciśnij\s+(.+)',
                r'press\s+(.+)'
            ],
            'type_text': [
                r'wpisz\s+["\'](.+)["\']',
                r'type\s+["\'](.+)["\']',
                r'napisz\s+["\'](.+)["\']'
            ],
            'read_file': [
                r'przeczytaj\s+(?:plik\s+)?(.+)',
                r'read\s+(?:file\s+)?(.+)',
                r'odczytaj\s+(.+)'
            ],
            'write_file': [
                r'zapisz\s+(?:do\s+)?(?:pliku\s+)?(.+)',
                r'write\s+(?:to\s+)?(?:file\s+)?(.+)',
                r'utwórz\s+plik\s+(.+)'
            ],
            'modify_file': [
                r'modyfikuj\s+(?:plik\s+)?(.+)',
                r'modify\s+(?:file\s+)?(.+)',
                r'zmień\s+(?:plik\s+)?(.+)',
                r'edytuj\s+(.+)'
            ],
            'system_command': [
                r'wykonaj\s+polecenie\s+(.+)',
                r'execute\s+command\s+(.+)',
                r'uruchom\s+komendę\s+(.+)'
            ],
            'change_setting': [
                r'zmień\s+ustawienie\s+(.+)',
                r'change\s+setting\s+(.+)',
                r'ustaw\s+(.+)'
            ],
            'search': [
                r'znajdź\s+(.+)',
                r'search\s+(?:for\s+)?(.+)',
                r'szukaj\s+(.+)'
            ],
            'move_mouse': [
                r'przesuń\s+(?:mysz|kursor)\s+(?:do\s+)?(.+)',
                r'move\s+(?:mouse|cursor)\s+(?:to\s+)?(.+)'
            ],
            'take_screenshot': [
                r'zrób\s+(?:screenshot|zrzut\s+ekranu)',
                r'take\s+screenshot',
                r'capture\s+screen'
            ],
            'wait': [
                r'czekaj\s+(\d+)\s+(?:sekund|seconds?)',
                r'wait\s+(\d+)\s+(?:sekund|seconds?)',
                r'poczekaj\s+(\d+)'
            ]
        }
    
    async def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text to extract intent and parameters.
        
        Args:
            text: Natural language input
            
        Returns:
            Dictionary with intent, parameters, and metadata
        """
        logger.debug(f"Parsing: {text}")
        
        # Normalize text
        normalized = text.strip().lower()
        
        # Try to match intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, normalized, re.IGNORECASE)
                if match:
                    logger.info(f"Matched intent: {intent}")
                    return {
                        'intent': intent,
                        'parameters': self._extract_parameters(intent, match),
                        'original_text': text,
                        'confidence': 0.9
                    }
        
        # If no pattern matched, try to use AI for complex parsing
        logger.info("No pattern matched, using AI-based parsing")
        return await self._ai_parse(text)
    
    def _extract_parameters(self, intent: str, match: re.Match) -> Dict[str, Any]:
        """Extract parameters from regex match based on intent."""
        params = {}
        
        if match.groups():
            if intent in ['open_application', 'close_application']:
                params['application'] = match.group(1).strip()
            elif intent in ['click', 'move_mouse']:
                params['target'] = match.group(1).strip()
            elif intent == 'type_text':
                params['text'] = match.group(1).strip()
            elif intent in ['read_file', 'write_file', 'modify_file']:
                params['file_path'] = match.group(1).strip()
            elif intent == 'system_command':
                params['command'] = match.group(1).strip()
            elif intent == 'change_setting':
                params['setting'] = match.group(1).strip()
            elif intent == 'search':
                params['query'] = match.group(1).strip()
            elif intent == 'wait':
                params['duration'] = int(match.group(1))
        
        return params
    
    async def _ai_parse(self, text: str) -> Dict[str, Any]:
        """
        Use AI model to parse complex natural language.
        
        Args:
            text: Natural language input
            
        Returns:
            Parsed intent and parameters
        """
        # Use AI engine if available
        if self.ai_engine:
            logger.info("Using AI engine for complex parsing")
            try:
                # Get recent context from memory if available
                context = None
                result = await self.ai_engine.parse_complex_command(text, context)
                result['original_text'] = text
                return result
            except Exception as e:
                logger.error(f"AI parsing failed: {e}")
        
        # Fallback to generic task
        logger.info("AI parsing not available, returning generic task")
        
        return {
            'intent': 'complex_task',
            'parameters': {
                'description': text,
                'needs_ai_planning': True
            },
            'original_text': text,
            'confidence': 0.5
        }
    
    def extract_tasks_from_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        """
        Extract individual tasks from a complex plan.
        
        Args:
            plan_text: Text describing a multi-step plan
            
        Returns:
            List of individual tasks
        """
        tasks = []
        
        # Split by common task separators
        lines = plan_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Remove list markers
            line = re.sub(r'^[\d\.\-\*\+]\s*', '', line)
            
            if line:
                # Parse each line as a task
                # This could be enhanced with more sophisticated parsing
                tasks.append({
                    'description': line,
                    'status': 'pending'
                })
        
        return tasks
