"""Advanced GUI pattern recognition for intelligent UI element detection."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import json


class PatternRecognizer:
    """
    Advanced pattern recognition for GUI elements using heuristics,
    templates, and learning from successful interactions.
    """
    
    def __init__(self, config, vision_system=None):
        """
        Initialize pattern recognizer.
        
        Args:
            config: Configuration object
            vision_system: Computer vision system for image analysis
        """
        self.config = config
        self.vision = vision_system
        
        # Known patterns
        self.element_patterns = self._load_element_patterns()
        self.learned_patterns = []
        
        # Recognition cache
        self.recognition_cache = {}
        
    def _load_element_patterns(self) -> Dict[str, List[Dict]]:
        """Load predefined UI element patterns."""
        return {
            'button': [
                {
                    'type': 'text_based',
                    'keywords': ['ok', 'cancel', 'submit', 'yes', 'no', 'close', 'apply'],
                    'confidence': 0.8
                },
                {
                    'type': 'shape_based',
                    'characteristics': ['rounded_rectangle', 'raised_border'],
                    'confidence': 0.6
                }
            ],
            'textfield': [
                {
                    'type': 'shape_based',
                    'characteristics': ['rectangle', 'white_background', 'border'],
                    'confidence': 0.7
                }
            ],
            'menu': [
                {
                    'type': 'position_based',
                    'location': 'top_of_window',
                    'characteristics': ['horizontal_list', 'text_items'],
                    'confidence': 0.8
                }
            ],
            'icon': [
                {
                    'type': 'size_based',
                    'dimensions': {'min': 16, 'max': 64},
                    'characteristics': ['square', 'colorful'],
                    'confidence': 0.6
                }
            ],
            'checkbox': [
                {
                    'type': 'shape_based',
                    'characteristics': ['small_square', 'optional_checkmark'],
                    'confidence': 0.7
                }
            ],
            'dropdown': [
                {
                    'type': 'shape_based',
                    'characteristics': ['rectangle', 'down_arrow'],
                    'confidence': 0.75
                }
            ]
        }
    
    async def recognize_element(
        self,
        description: str,
        screenshot: Optional[Any] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Recognize a GUI element from description and/or screenshot.
        
        Args:
            description: Text description of element (e.g., "OK button")
            screenshot: Optional screenshot to analyze
            context: Optional context information
            
        Returns:
            Recognition result with element type, location, and confidence
        """
        logger.info(f"Recognizing element: {description}")
        
        # Check cache first
        cache_key = f"{description}_{hash(str(screenshot))}"
        if cache_key in self.recognition_cache:
            logger.debug("Using cached recognition result")
            return self.recognition_cache[cache_key]
        
        # Parse description
        parsed = self._parse_description(description)
        
        # Combine multiple recognition methods
        results = []
        
        # Text-based recognition
        text_result = self._text_based_recognition(parsed)
        if text_result['confidence'] > 0.5:
            results.append(text_result)
        
        # Visual recognition if screenshot available
        if screenshot and self.vision:
            visual_result = await self._visual_recognition(screenshot, parsed)
            if visual_result['confidence'] > 0.5:
                results.append(visual_result)
        
        # Context-based recognition
        if context:
            context_result = self._context_based_recognition(parsed, context)
            if context_result['confidence'] > 0.5:
                results.append(context_result)
        
        # Learned pattern recognition
        learned_result = self._learned_pattern_recognition(parsed)
        if learned_result['confidence'] > 0.5:
            results.append(learned_result)
        
        # Combine results
        final_result = self._combine_results(results)
        
        # Cache result
        self.recognition_cache[cache_key] = final_result
        
        logger.info(f"Recognition complete: {final_result['element_type']} "
                   f"(confidence: {final_result['confidence']:.2f})")
        
        return final_result
    
    def _parse_description(self, description: str) -> Dict[str, Any]:
        """Parse element description to extract key information."""
        desc_lower = description.lower()
        
        # Extract element type
        element_type = 'unknown'
        for etype in self.element_patterns.keys():
            if etype in desc_lower:
                element_type = etype
                break
        
        # Extract text/label
        label = None
        for pattern_list in self.element_patterns.get(element_type, []):
            if pattern_list['type'] == 'text_based':
                for keyword in pattern_list['keywords']:
                    if keyword in desc_lower:
                        label = keyword
                        break
        
        # Extract position hints
        position_hints = []
        position_keywords = {
            'top': ['top', 'upper'],
            'bottom': ['bottom', 'lower'],
            'left': ['left'],
            'right': ['right'],
            'center': ['center', 'middle']
        }
        
        for position, keywords in position_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                position_hints.append(position)
        
        return {
            'element_type': element_type,
            'label': label,
            'position_hints': position_hints,
            'original_description': description
        }
    
    def _text_based_recognition(self, parsed: Dict) -> Dict[str, Any]:
        """Recognize element based on text patterns."""
        element_type = parsed['element_type']
        label = parsed['label']
        
        if element_type == 'unknown':
            confidence = 0.2
        else:
            confidence = 0.7
        
        if label:
            confidence += 0.2
        
        return {
            'method': 'text_based',
            'element_type': element_type,
            'label': label,
            'confidence': min(confidence, 1.0),
            'location': None
        }
    
    async def _visual_recognition(
        self,
        screenshot: Any,
        parsed: Dict
    ) -> Dict[str, Any]:
        """Recognize element using computer vision."""
        if not self.vision:
            return {'method': 'visual', 'confidence': 0.0}
        
        try:
            # Use vision system to detect UI elements
            detected_elements = await self.vision.detect_ui_elements(screenshot)
            
            # Match with parsed description
            element_type = parsed['element_type']
            label = parsed['label']
            
            best_match = None
            best_score = 0.0
            
            for element in detected_elements:
                score = 0.0
                
                # Type match
                if element.get('type') == element_type:
                    score += 0.5
                
                # Label match
                if label and label.lower() in element.get('text', '').lower():
                    score += 0.4
                
                # Position match
                for hint in parsed['position_hints']:
                    if self._position_matches(element.get('location'), hint):
                        score += 0.1
                
                if score > best_score:
                    best_score = score
                    best_match = element
            
            if best_match:
                return {
                    'method': 'visual',
                    'element_type': best_match.get('type', element_type),
                    'label': best_match.get('text'),
                    'location': best_match.get('location'),
                    'confidence': best_score
                }
            else:
                return {'method': 'visual', 'confidence': 0.3}
                
        except Exception as e:
            logger.warning(f"Visual recognition failed: {e}")
            return {'method': 'visual', 'confidence': 0.0}
    
    def _context_based_recognition(
        self,
        parsed: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Recognize element using context information."""
        confidence = 0.5
        
        # Check if element type matches recent interactions
        recent_elements = context.get('recent_elements', [])
        if parsed['element_type'] in [e.get('type') for e in recent_elements]:
            confidence += 0.2
        
        # Check if in expected application
        active_app = context.get('active_application')
        if active_app:
            confidence += 0.1
        
        return {
            'method': 'context_based',
            'element_type': parsed['element_type'],
            'confidence': min(confidence, 1.0)
        }
    
    def _learned_pattern_recognition(self, parsed: Dict) -> Dict[str, Any]:
        """Recognize using learned patterns from past successes."""
        element_type = parsed['element_type']
        label = parsed['label']
        
        # Find matching learned patterns
        matches = [
            p for p in self.learned_patterns
            if p.get('element_type') == element_type and
               (not label or p.get('label') == label)
        ]
        
        if matches:
            # Use most successful pattern
            best = max(matches, key=lambda x: x.get('success_rate', 0))
            
            return {
                'method': 'learned',
                'element_type': element_type,
                'label': label,
                'location': best.get('typical_location'),
                'confidence': best.get('success_rate', 0.5)
            }
        
        return {'method': 'learned', 'confidence': 0.0}
    
    def _position_matches(
        self,
        location: Optional[Dict],
        hint: str
    ) -> bool:
        """Check if location matches position hint."""
        if not location:
            return False
        
        x, y = location.get('x', 0), location.get('y', 0)
        screen_width = location.get('screen_width', 1920)
        screen_height = location.get('screen_height', 1080)
        
        if hint == 'top' and y < screen_height * 0.2:
            return True
        elif hint == 'bottom' and y > screen_height * 0.8:
            return True
        elif hint == 'left' and x < screen_width * 0.2:
            return True
        elif hint == 'right' and x > screen_width * 0.8:
            return True
        elif hint == 'center' and (
            screen_width * 0.3 < x < screen_width * 0.7 and
            screen_height * 0.3 < y < screen_height * 0.7
        ):
            return True
        
        return False
    
    def _combine_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine multiple recognition results into final result."""
        if not results:
            return {
                'element_type': 'unknown',
                'confidence': 0.0,
                'location': None,
                'methods_used': []
            }
        
        # Weight results by confidence
        total_confidence = sum(r['confidence'] for r in results)
        
        # Aggregate element type (most confident)
        element_type = max(
            results,
            key=lambda x: x['confidence']
        ).get('element_type', 'unknown')
        
        # Aggregate location (from visual or learned)
        location = None
        for r in sorted(results, key=lambda x: x['confidence'], reverse=True):
            if r.get('location'):
                location = r['location']
                break
        
        # Aggregate label
        label = None
        for r in results:
            if r.get('label'):
                label = r['label']
                break
        
        # Combined confidence (weighted average)
        combined_confidence = total_confidence / len(results) if results else 0.0
        
        return {
            'element_type': element_type,
            'label': label,
            'location': location,
            'confidence': combined_confidence,
            'methods_used': [r['method'] for r in results]
        }
    
    async def learn_from_interaction(
        self,
        description: str,
        element_info: Dict[str, Any],
        success: bool
    ) -> None:
        """
        Learn from a GUI interaction to improve future recognition.
        
        Args:
            description: Element description that was used
            element_info: Information about the actual element
            success: Whether the interaction was successful
        """
        logger.info(f"Learning from {'successful' if success else 'failed'} interaction")
        
        # Find or create pattern
        pattern = None
        for p in self.learned_patterns:
            if (p.get('description') == description and
                p.get('element_type') == element_info.get('type')):
                pattern = p
                break
        
        if not pattern:
            pattern = {
                'description': description,
                'element_type': element_info.get('type'),
                'label': element_info.get('label'),
                'typical_location': element_info.get('location'),
                'successes': 0,
                'failures': 0,
                'success_rate': 0.0
            }
            self.learned_patterns.append(pattern)
        
        # Update pattern
        if success:
            pattern['successes'] += 1
        else:
            pattern['failures'] += 1
        
        total = pattern['successes'] + pattern['failures']
        pattern['success_rate'] = pattern['successes'] / total if total > 0 else 0.0
        
        # Update typical location
        if success and element_info.get('location'):
            pattern['typical_location'] = element_info['location']
        
        logger.debug(f"Pattern updated: {pattern['description']} "
                    f"(success rate: {pattern['success_rate']:.2%})")
    
    def get_learned_patterns(self) -> List[Dict[str, Any]]:
        """Get all learned patterns."""
        return self.learned_patterns.copy()
    
    def clear_cache(self) -> None:
        """Clear recognition cache."""
        self.recognition_cache.clear()
        logger.info("Recognition cache cleared")
