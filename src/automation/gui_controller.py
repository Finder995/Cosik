"""GUI automation controller for Windows applications."""

import time
from typing import Optional, Tuple, List, Dict, Any
from loguru import logger

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image
except ImportError:
    logger.warning("GUI automation libraries not available. Install pyautogui, pygetwindow, and pillow.")
    pyautogui = None
    gw = None


class GUIController:
    """Control GUI elements and automate Windows applications."""
    
    def __init__(self, config, vision=None):
        """Initialize GUI controller."""
        self.config = config
        self.vision = vision
        
        if pyautogui:
            # Configure pyautogui
            pyautogui.FAILSAFE = config.get('gui.failsafe', True)
            pyautogui.PAUSE = config.get('gui.pause_between_actions', 0.5)
        
        self.confidence = config.get('gui.confidence_threshold', 0.8)
        self.screenshot_interval = config.get('gui.screenshot_interval', 1.0)
    
    async def click(self, x: Optional[int] = None, y: Optional[int] = None, 
                   button: str = 'left', clicks: int = 1) -> bool:
        """
        Click at specified coordinates or current position.
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            True if successful
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return False
        
        try:
            if x is not None and y is not None:
                logger.info(f"Clicking at ({x}, {y}) with {button} button")
                pyautogui.click(x, y, clicks=clicks, button=button)
            else:
                logger.info(f"Clicking at current position with {button} button")
                pyautogui.click(clicks=clicks, button=button)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    async def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Move mouse to specified coordinates.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return False
        
        try:
            logger.info(f"Moving mouse to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False
    
    async def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text using keyboard.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
            
        Returns:
            True if successful
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return False
        
        try:
            logger.info(f"Typing text: {text[:30]}...")
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return False
    
    async def press_key(self, key: str, presses: int = 1) -> bool:
        """
        Press a keyboard key.
        
        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab')
            presses: Number of presses
            
        Returns:
            True if successful
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return False
        
        try:
            logger.info(f"Pressing key: {key} ({presses} times)")
            pyautogui.press(key, presses=presses)
            return True
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return False
    
    async def hotkey(self, *keys) -> bool:
        """
        Press a combination of keys (hotkey).
        
        Args:
            *keys: Keys to press simultaneously
            
        Returns:
            True if successful
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return False
        
        try:
            logger.info(f"Pressing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            return False
    
    async def take_screenshot(self, filename: Optional[str] = None, 
                            region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """
        Take a screenshot.
        
        Args:
            filename: Output filename (None for auto-generated)
            region: Region to capture (left, top, width, height)
            
        Returns:
            Path to screenshot file
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return None
        
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"
            
            logger.info(f"Taking screenshot: {filename}")
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filename)
            return filename
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def find_on_screen(self, image_path: str, confidence: Optional[float] = None) -> Optional[Tuple[int, int]]:
        """
        Find an image on screen and return its center coordinates.
        
        Args:
            image_path: Path to image to find
            confidence: Confidence threshold (0-1)
            
        Returns:
            (x, y) coordinates if found, None otherwise
        """
        if not pyautogui:
            logger.error("pyautogui not available")
            return None
        
        try:
            conf = confidence if confidence is not None else self.confidence
            logger.info(f"Searching for image: {image_path}")
            
            location = pyautogui.locateOnScreen(image_path, confidence=conf)
            if location:
                center = pyautogui.center(location)
                logger.info(f"Found at: {center}")
                return center
            else:
                logger.info("Image not found on screen")
                return None
        except Exception as e:
            logger.error(f"Find on screen failed: {e}")
            return None
    
    async def get_window_list(self) -> List[str]:
        """
        Get list of all open windows.
        
        Returns:
            List of window titles
        """
        if not gw:
            logger.error("pygetwindow not available")
            return []
        
        try:
            windows = gw.getAllTitles()
            return [w for w in windows if w.strip()]
        except Exception as e:
            logger.error(f"Get window list failed: {e}")
            return []
    
    async def focus_window(self, title: str) -> bool:
        """
        Focus a window by title.
        
        Args:
            title: Window title (can be partial match)
            
        Returns:
            True if successful
        """
        if not gw:
            logger.error("pygetwindow not available")
            return False
        
        try:
            logger.info(f"Focusing window: {title}")
            windows = gw.getWindowsWithTitle(title)
            
            if windows:
                window = windows[0]
                window.activate()
                return True
            else:
                logger.warning(f"Window not found: {title}")
                return False
        except Exception as e:
            logger.error(f"Focus window failed: {e}")
            return False
    
    async def maximize_window(self, title: str) -> bool:
        """
        Maximize a window by title.
        
        Args:
            title: Window title
            
        Returns:
            True if successful
        """
        if not gw:
            logger.error("pygetwindow not available")
            return False
        
        try:
            logger.info(f"Maximizing window: {title}")
            windows = gw.getWindowsWithTitle(title)
            
            if windows:
                window = windows[0]
                window.maximize()
                return True
            else:
                logger.warning(f"Window not found: {title}")
                return False
        except Exception as e:
            logger.error(f"Maximize window failed: {e}")
            return False
    
    async def close_window(self, title: str) -> bool:
        """
        Close a window by title.
        
        Args:
            title: Window title
            
        Returns:
            True if successful
        """
        if not gw:
            logger.error("pygetwindow not available")
            return False
        
        try:
            logger.info(f"Closing window: {title}")
            windows = gw.getWindowsWithTitle(title)
            
            if windows:
                window = windows[0]
                window.close()
                return True
            else:
                logger.warning(f"Window not found: {title}")
                return False
        except Exception as e:
            logger.error(f"Close window failed: {e}")
            return False
    
    async def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen size.
        
        Returns:
            (width, height) tuple
        """
        if not pyautogui:
            return (0, 0)
        
        return pyautogui.size()
    
    async def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            (x, y) coordinates
        """
        if not pyautogui:
            return (0, 0)
        
        return pyautogui.position()
    
    async def click_text(self, text: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Click on text found via OCR.
        
        Args:
            text: Text to search for and click
            region: Region to search in
            
        Returns:
            True if successful
        """
        if not self.vision:
            logger.error("Vision module not available for OCR")
            return False
        
        try:
            result = await self.vision.find_text_on_screen(text, region)
            
            if result['success'] and result['found'] and result['count'] > 0:
                match = result['matches'][0]
                logger.info(f"Found text '{text}' at ({match['center_x']}, {match['center_y']})")
                return await self.click(match['center_x'], match['center_y'])
            else:
                logger.warning(f"Text '{text}' not found on screen")
                return False
                
        except Exception as e:
            logger.error(f"Click text failed: {e}")
            return False
    
    async def click_image(self, image_path: str, confidence: Optional[float] = None) -> bool:
        """
        Click on image found via template matching.
        
        Args:
            image_path: Path to template image
            confidence: Match confidence (default: from config)
            
        Returns:
            True if successful
        """
        if not self.vision:
            logger.error("Vision module not available for image matching")
            return False
        
        try:
            conf = confidence if confidence is not None else self.confidence
            result = await self.vision.find_image_on_screen(image_path, conf)
            
            if result['success'] and result['found']:
                logger.info(f"Found image at ({result['x']}, {result['y']})")
                return await self.click(result['x'], result['y'])
            else:
                logger.warning(f"Image not found: {image_path}")
                return False
                
        except Exception as e:
            logger.error(f"Click image failed: {e}")
            return False
    
    async def wait_for_text(self, text: str, timeout: int = 30, 
                          region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Wait for text to appear on screen.
        
        Args:
            text: Text to wait for
            timeout: Timeout in seconds
            region: Region to search in
            
        Returns:
            True if text found within timeout
        """
        if not self.vision:
            logger.error("Vision module not available")
            return False
        
        import asyncio
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.vision.find_text_on_screen(text, region)
            
            if result['success'] and result['found']:
                logger.info(f"Text '{text}' appeared after {time.time() - start_time:.1f}s")
                return True
            
            await asyncio.sleep(1)
        
        logger.warning(f"Text '{text}' did not appear within {timeout}s")
        return False
    
    async def wait_for_image(self, image_path: str, timeout: int = 30, 
                           confidence: Optional[float] = None) -> bool:
        """
        Wait for image to appear on screen.
        
        Args:
            image_path: Path to template image
            timeout: Timeout in seconds
            confidence: Match confidence
            
        Returns:
            True if image found within timeout
        """
        if not self.vision:
            logger.error("Vision module not available")
            return False
        
        import asyncio
        start_time = time.time()
        conf = confidence if confidence is not None else self.confidence
        
        while time.time() - start_time < timeout:
            result = await self.vision.find_image_on_screen(image_path, conf)
            
            if result['success'] and result['found']:
                logger.info(f"Image appeared after {time.time() - start_time:.1f}s")
                return True
            
            await asyncio.sleep(1)
        
        logger.warning(f"Image did not appear within {timeout}s")
        return False
