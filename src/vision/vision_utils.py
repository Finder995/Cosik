"""
Enhanced computer vision utilities for advanced screen analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from loguru import logger
import time

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None


class ColorAnalyzer:
    """Analyze colors in screen regions."""
    
    @staticmethod
    def get_dominant_color(image_array) -> Tuple[int, int, int]:
        """
        Get dominant color in image.
        
        Args:
            image_array: Numpy array of image
            
        Returns:
            RGB tuple of dominant color
        """
        if not CV2_AVAILABLE or np is None:
            return (0, 0, 0)
        
        # Reshape image to list of pixels
        pixels = image_array.reshape(-1, 3)
        
        # Use K-means clustering to find dominant color
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=1, random_state=0)
        kmeans.fit(pixels)
        
        dominant = kmeans.cluster_centers_[0]
        return tuple(map(int, dominant))
    
    @staticmethod
    def detect_color_region(
        image_array,
        color_rgb: Tuple[int, int, int],
        tolerance: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Find regions of specific color.
        
        Args:
            image_array: Image array
            color_rgb: Target color in RGB
            tolerance: Color matching tolerance
            
        Returns:
            List of regions matching the color
        """
        if not CV2_AVAILABLE or np is None:
            return []
        
        # Convert to BGR (OpenCV format)
        color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])
        
        # Create color range
        lower = np.array([max(0, c - tolerance) for c in color_bgr])
        upper = np.array([min(255, c + tolerance) for c in color_bgr])
        
        # Create mask
        mask = cv2.inRange(image_array, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 5 and h > 5:  # Filter tiny regions
                regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center': (int(x + w // 2), int(y + h // 2))
                })
        
        return regions


class UIElementDetector:
    """Advanced UI element detection."""
    
    def __init__(self):
        """Initialize detector."""
        self.element_patterns = {
            'button': {
                'min_width': 60,
                'max_width': 200,
                'min_height': 20,
                'max_height': 50,
                'aspect_ratio_range': (1.5, 5.0)
            },
            'textfield': {
                'min_width': 100,
                'max_width': 400,
                'min_height': 20,
                'max_height': 40,
                'aspect_ratio_range': (3.0, 15.0)
            },
            'checkbox': {
                'min_width': 15,
                'max_width': 25,
                'min_height': 15,
                'max_height': 25,
                'aspect_ratio_range': (0.8, 1.2)
            }
        }
    
    def classify_element(
        self,
        region: Tuple[int, int, int, int],
        image_array: Optional[Any] = None
    ) -> str:
        """
        Classify UI element type based on characteristics.
        
        Args:
            region: (x, y, width, height) tuple
            image_array: Optional image for analysis
            
        Returns:
            Element type string
        """
        x, y, w, h = region
        aspect_ratio = w / h if h > 0 else 0
        
        # Check against patterns
        for element_type, pattern in self.element_patterns.items():
            if (pattern['min_width'] <= w <= pattern['max_width'] and
                pattern['min_height'] <= h <= pattern['max_height'] and
                pattern['aspect_ratio_range'][0] <= aspect_ratio <= pattern['aspect_ratio_range'][1]):
                return element_type
        
        # Fallback classification
        if aspect_ratio > 5:
            return 'textfield'
        elif 0.8 < aspect_ratio < 1.2:
            return 'icon'
        elif aspect_ratio > 1.5:
            return 'button'
        else:
            return 'unknown'
    
    def detect_buttons(self, image_array) -> List[Dict[str, Any]]:
        """Detect button-like elements."""
        if not CV2_AVAILABLE or cv2 is None:
            return []
        
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        pattern = self.element_patterns['button']
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if (pattern['min_width'] <= w <= pattern['max_width'] and
                pattern['min_height'] <= h <= pattern['max_height'] and
                pattern['aspect_ratio_range'][0] <= aspect_ratio <= pattern['aspect_ratio_range'][1]):
                
                buttons.append({
                    'region': (x, y, w, h),
                    'center': (x + w // 2, y + h // 2),
                    'type': 'button',
                    'confidence': 0.7
                })
        
        return buttons


class ScreenRecorder:
    """Record screen activity for analysis."""
    
    def __init__(self):
        """Initialize screen recorder."""
        self.recording = False
        self.frames = []
        self.fps = 10
    
    def start_recording(self, fps: int = 10):
        """Start recording screen."""
        self.recording = True
        self.frames = []
        self.fps = fps
        logger.info(f"Started screen recording at {fps} FPS")
    
    def capture_frame(self) -> bool:
        """Capture a single frame."""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            self.frames.append(np.array(screenshot))
            return True
        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            return False
    
    def stop_recording(self) -> List[Any]:
        """Stop recording and return frames."""
        self.recording = False
        logger.info(f"Stopped recording. Captured {len(self.frames)} frames")
        return self.frames
    
    def save_video(self, output_path: str, fps: Optional[int] = None):
        """Save recorded frames as video."""
        if not CV2_AVAILABLE or not self.frames:
            logger.error("Cannot save video: no frames or OpenCV not available")
            return False
        
        fps = fps or self.fps
        height, width = self.frames[0].shape[:2]
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in self.frames:
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        logger.info(f"Saved video to {output_path}")
        return True


class ImageComparison:
    """Compare images for changes or similarity."""
    
    @staticmethod
    def calculate_similarity(img1, img2) -> float:
        """
        Calculate similarity between two images.
        
        Args:
            img1: First image array
            img2: Second image array
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not CV2_AVAILABLE or cv2 is None or np is None:
            return 0.0
        
        # Resize to same dimensions if needed
        if img1.shape != img2.shape:
            h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (w, h))
            img2 = cv2.resize(img2, (w, h))
        
        # Calculate mean squared error
        mse = np.mean((img1 - img2) ** 2)
        
        # Convert to similarity score (0 = identical, higher = more different)
        # Normalize to 0-1 range
        max_mse = 255 ** 2  # Maximum possible MSE for 8-bit images
        similarity = 1.0 - (mse / max_mse)
        
        return float(similarity)
    
    @staticmethod
    def detect_changes(
        img1,
        img2,
        threshold: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect regions that changed between images.
        
        Args:
            img1: First image
            img2: Second image
            threshold: Change detection threshold
            
        Returns:
            List of changed regions
        """
        if not CV2_AVAILABLE or cv2 is None:
            return []
        
        # Ensure same dimensions
        if img1.shape != img2.shape:
            h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (w, h))
            img2 = cv2.resize(img2, (w, h))
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Threshold
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours of changed regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        changes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:  # Filter small changes
                changes.append({
                    'region': (x, y, w, h),
                    'center': (x + w // 2, y + h // 2),
                    'area': int(cv2.contourArea(contour))
                })
        
        return changes


class OCREnhancer:
    """Enhanced OCR with preprocessing."""
    
    @staticmethod
    def preprocess_for_ocr(image_array) -> Any:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_array: Input image
            
        Returns:
            Preprocessed image
        """
        if not CV2_AVAILABLE or cv2 is None:
            return image_array
        
        # Convert to grayscale
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    @staticmethod
    def extract_text_enhanced(
        image_array,
        language: str = 'eng+pol'
    ) -> Dict[str, Any]:
        """
        Extract text with enhanced preprocessing.
        
        Args:
            image_array: Image to process
            language: OCR language
            
        Returns:
            Extracted text and metadata
        """
        if not OCR_AVAILABLE or pytesseract is None or Image is None:
            return {
                'success': False,
                'error': 'OCR not available'
            }
        
        try:
            # Preprocess
            processed = OCREnhancer.preprocess_for_ocr(image_array)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed)
            
            # Extract text
            text = pytesseract.image_to_string(pil_image, lang=language)
            
            # Get detailed data
            data = pytesseract.image_to_data(pil_image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Filter confident words
            words = []
            for i, word in enumerate(data['text']):
                if word.strip() and data['conf'][i] > 60:
                    words.append({
                        'text': word,
                        'confidence': data['conf'][i],
                        'position': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    })
            
            return {
                'success': True,
                'text': text.strip(),
                'words': words,
                'word_count': len(words)
            }
            
        except Exception as e:
            logger.error(f"Enhanced OCR failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
