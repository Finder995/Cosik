"""Computer Vision module for advanced screen analysis and OCR."""

import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from loguru import logger


class ComputerVision:
    """
    Computer vision capabilities for the agent.
    Includes OCR, template matching, and object detection.
    """
    
    def __init__(self, config):
        """Initialize computer vision module."""
        self.config = config
        self.ocr_engine = None
        self.cv2 = None
        self._init_libraries()
    
    def _init_libraries(self):
        """Initialize computer vision libraries."""
        try:
            import cv2
            self.cv2 = cv2
            logger.info("OpenCV initialized successfully")
        except ImportError:
            logger.warning("OpenCV not installed. Install with: pip install opencv-python")
        
        try:
            import pytesseract
            self.ocr_engine = pytesseract
            
            # Try to set tesseract path for Windows
            if os.name == 'nt':
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            
            logger.info("Tesseract OCR initialized successfully")
        except ImportError:
            logger.warning("pytesseract not installed. Install with: pip install pytesseract")
    
    async def extract_text_from_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """
        Extract text from screen using OCR.
        
        Args:
            region: (left, top, width, height) or None for full screen
            
        Returns:
            Extracted text and metadata
        """
        if not self.ocr_engine:
            return {
                'success': False,
                'error': 'OCR engine not available'
            }
        
        try:
            import pyautogui
            from PIL import Image
            
            # Take screenshot
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Extract text
            text = self.ocr_engine.image_to_string(screenshot)
            
            # Get detailed data
            data = self.ocr_engine.image_to_data(screenshot, output_type=self.ocr_engine.Output.DICT)
            
            # Filter confident results
            confident_text = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 60:  # Confidence threshold
                    confident_text.append({
                        'text': data['text'][i],
                        'confidence': conf,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            return {
                'success': True,
                'text': text.strip(),
                'detailed_results': confident_text,
                'region': region
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def extract_text_from_image(self, image_path: str, 
                                     language: str = 'eng') -> Dict[str, Any]:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file
            language: OCR language (eng, pol, etc.)
            
        Returns:
            Extracted text
        """
        if not self.ocr_engine:
            return {
                'success': False,
                'error': 'OCR engine not available'
            }
        
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            text = self.ocr_engine.image_to_string(image, lang=language)
            
            return {
                'success': True,
                'text': text.strip(),
                'image_path': image_path,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def find_text_on_screen(self, search_text: str, 
                                 region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """
        Find specific text on screen and return its location.
        
        Args:
            search_text: Text to search for
            region: Region to search in
            
        Returns:
            Location of text if found
        """
        ocr_result = await self.extract_text_from_screen(region)
        
        if not ocr_result['success']:
            return ocr_result
        
        # Search in detailed results
        matches = []
        for item in ocr_result['detailed_results']:
            if search_text.lower() in item['text'].lower():
                matches.append({
                    'text': item['text'],
                    'center_x': item['left'] + item['width'] // 2,
                    'center_y': item['top'] + item['height'] // 2,
                    'confidence': item['confidence']
                })
        
        return {
            'success': True,
            'found': len(matches) > 0,
            'matches': matches,
            'count': len(matches)
        }
    
    async def find_image_on_screen(self, template_path: str, 
                                  confidence: float = 0.8) -> Dict[str, Any]:
        """
        Find image template on screen using template matching.
        
        Args:
            template_path: Path to template image
            confidence: Match confidence threshold (0-1)
            
        Returns:
            Location of image if found
        """
        if not self.cv2:
            # Fallback to pyautogui
            try:
                import pyautogui
                location = pyautogui.locateOnScreen(template_path, confidence=confidence)
                
                if location:
                    center = pyautogui.center(location)
                    return {
                        'success': True,
                        'found': True,
                        'x': center.x,
                        'y': center.y,
                        'region': (location.left, location.top, location.width, location.height)
                    }
                else:
                    return {
                        'success': True,
                        'found': False
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        try:
            import pyautogui
            import numpy as np
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_gray = self.cv2.cvtColor(screenshot_np, self.cv2.COLOR_RGB2GRAY)
            
            # Load template
            template = self.cv2.imread(template_path, self.cv2.IMREAD_GRAYSCALE)
            
            if template is None:
                return {
                    'success': False,
                    'error': f'Could not load template: {template_path}'
                }
            
            # Template matching
            result = self.cv2.matchTemplate(screenshot_gray, template, self.cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                return {
                    'success': True,
                    'found': True,
                    'x': center_x,
                    'y': center_y,
                    'confidence': float(max_val),
                    'region': (max_loc[0], max_loc[1], w, h)
                }
            else:
                return {
                    'success': True,
                    'found': False,
                    'max_confidence': float(max_val)
                }
                
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def find_all_matches(self, template_path: str, 
                             confidence: float = 0.8) -> Dict[str, Any]:
        """
        Find all instances of template on screen.
        
        Args:
            template_path: Path to template image
            confidence: Match confidence threshold
            
        Returns:
            All matching locations
        """
        if not self.cv2:
            return {
                'success': False,
                'error': 'OpenCV not available'
            }
        
        try:
            import pyautogui
            import numpy as np
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_gray = self.cv2.cvtColor(screenshot_np, self.cv2.COLOR_RGB2GRAY)
            
            # Load template
            template = self.cv2.imread(template_path, self.cv2.IMREAD_GRAYSCALE)
            h, w = template.shape
            
            # Template matching
            result = self.cv2.matchTemplate(screenshot_gray, template, self.cv2.TM_CCOEFF_NORMED)
            
            # Find all matches above threshold
            locations = np.where(result >= confidence)
            matches = []
            
            for pt in zip(*locations[::-1]):
                matches.append({
                    'x': int(pt[0] + w // 2),
                    'y': int(pt[1] + h // 2),
                    'region': (int(pt[0]), int(pt[1]), w, h),
                    'confidence': float(result[pt[1], pt[0]])
                })
            
            return {
                'success': True,
                'matches': matches,
                'count': len(matches)
            }
            
        except Exception as e:
            logger.error(f"Multi-match failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def detect_ui_elements(self, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect UI elements on screen (buttons, text fields, etc.).
        
        Args:
            screenshot_path: Path to screenshot, or None to capture
            
        Returns:
            Detected UI elements
        """
        if not self.cv2:
            return {
                'success': False,
                'error': 'OpenCV not available'
            }
        
        try:
            import pyautogui
            import numpy as np
            
            # Get image
            if screenshot_path:
                image = self.cv2.imread(screenshot_path)
            else:
                screenshot = pyautogui.screenshot()
                image = np.array(screenshot)
                image = self.cv2.cvtColor(image, self.cv2.COLOR_RGB2BGR)
            
            gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = self.cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = self.cv2.findContours(edges, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and classify potential UI elements
            elements = []
            for contour in contours:
                x, y, w, h = self.cv2.boundingRect(contour)
                
                # Filter by size (likely UI elements)
                if 20 < w < 500 and 10 < h < 100:
                    aspect_ratio = w / h
                    
                    # Classify based on aspect ratio
                    if 1.5 < aspect_ratio < 5:
                        element_type = 'button'
                    elif aspect_ratio > 5:
                        element_type = 'textfield'
                    else:
                        element_type = 'icon'
                    
                    elements.append({
                        'type': element_type,
                        'x': int(x + w // 2),
                        'y': int(y + h // 2),
                        'region': (int(x), int(y), int(w), int(h)),
                        'aspect_ratio': float(aspect_ratio)
                    })
            
            return {
                'success': True,
                'elements': elements,
                'count': len(elements)
            }
            
        except Exception as e:
            logger.error(f"UI detection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
