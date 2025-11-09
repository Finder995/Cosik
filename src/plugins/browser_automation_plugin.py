"""
Browser Automation Plugin for Cosik AI Agent.

Features:
- Web browser automation (Selenium)
- Page navigation and interaction
- Form filling and submission
- JavaScript execution
- Screenshot capture
- Cookie management
- Multi-browser support (Chrome, Firefox, Edge)
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from loguru import logger
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available - Browser automation disabled. Install with: pip install selenium")


class BrowserAutomationPlugin:
    """
    Browser automation plugin using Selenium WebDriver.
    
    Features:
    - Multi-browser support
    - Page interaction
    - Form automation
    - JavaScript execution
    - Screenshot capture
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser automation plugin.
        
        Args:
            config: Plugin configuration
        """
        self.config = config
        self.browser_config = config.get('plugins', {}).get('browser', {})
        
        # Active browser sessions
        self.browsers = {}
        
        logger.info("Browser automation plugin initialized")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute browser automation operation.
        
        Args:
            command: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Operation result
        """
        if not SELENIUM_AVAILABLE:
            return {
                'success': False,
                'error': 'Selenium not available'
            }
        
        action = kwargs.pop('action', 'navigate')
        
        try:
            if action == 'start':
                return await self._start_browser(**kwargs)
            elif action == 'stop':
                return await self._stop_browser(**kwargs)
            elif action == 'navigate':
                return await self._navigate(**kwargs)
            elif action == 'click':
                return await self._click(**kwargs)
            elif action == 'type':
                return await self._type(**kwargs)
            elif action == 'submit':
                return await self._submit(**kwargs)
            elif action == 'get_text':
                return await self._get_text(**kwargs)
            elif action == 'screenshot':
                return await self._screenshot(**kwargs)
            elif action == 'execute_js':
                return await self._execute_js(**kwargs)
            elif action == 'wait_for':
                return await self._wait_for(**kwargs)
            elif action == 'get_cookies':
                return await self._get_cookies(**kwargs)
            elif action == 'set_cookie':
                return await self._set_cookie(**kwargs)
            elif action == 'back':
                return await self._back(**kwargs)
            elif action == 'forward':
                return await self._forward(**kwargs)
            elif action == 'refresh':
                return await self._refresh(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
        except Exception as e:
            logger.error(f"Browser automation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _start_browser(self, browser_type: str = 'chrome',
                            session_name: str = 'default',
                            headless: bool = False,
                            window_size: Optional[tuple] = None) -> Dict[str, Any]:
        """Start browser session."""
        try:
            if session_name in self.browsers:
                return {
                    'success': False,
                    'error': f'Browser session already exists: {session_name}'
                }
            
            # Create browser instance
            if browser_type.lower() == 'chrome':
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(options=options)
            
            elif browser_type.lower() == 'firefox':
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                driver = webdriver.Firefox(options=options)
            
            elif browser_type.lower() == 'edge':
                options = webdriver.EdgeOptions()
                if headless:
                    options.add_argument('--headless')
                driver = webdriver.Edge(options=options)
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported browser: {browser_type}'
                }
            
            # Set window size if specified
            if window_size:
                driver.set_window_size(window_size[0], window_size[1])
            else:
                driver.maximize_window()
            
            self.browsers[session_name] = {
                'driver': driver,
                'type': browser_type,
                'started_at': datetime.now()
            }
            
            logger.info(f"Browser started: {browser_type} ({session_name})")
            return {
                'success': True,
                'session': session_name,
                'browser': browser_type
            }
        
        except Exception as e:
            logger.error(f"Start browser failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _stop_browser(self, session_name: str = 'default') -> Dict[str, Any]:
        """Stop browser session."""
        try:
            if session_name not in self.browsers:
                return {
                    'success': False,
                    'error': f'Browser session not found: {session_name}'
                }
            
            browser = self.browsers[session_name]
            browser['driver'].quit()
            del self.browsers[session_name]
            
            logger.info(f"Browser stopped: {session_name}")
            return {
                'success': True,
                'session': session_name
            }
        
        except Exception as e:
            logger.error(f"Stop browser failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _navigate(self, url: str, session_name: str = 'default') -> Dict[str, Any]:
        """Navigate to URL."""
        try:
            if session_name not in self.browsers:
                # Auto-start browser
                await self._start_browser(session_name=session_name)
            
            driver = self.browsers[session_name]['driver']
            driver.get(url)
            
            logger.info(f"Navigated to: {url}")
            return {
                'success': True,
                'url': url,
                'title': driver.title
            }
        
        except Exception as e:
            logger.error(f"Navigate failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _click(self, selector: str, by: str = 'css',
                    session_name: str = 'default', timeout: int = 10) -> Dict[str, Any]:
        """Click element."""
        try:
            driver = self.browsers[session_name]['driver']
            
            # Map by method
            by_method = self._get_by_method(by)
            
            # Wait for element
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by_method, selector))
            )
            
            element.click()
            
            logger.info(f"Clicked element: {selector}")
            return {
                'success': True,
                'selector': selector
            }
        
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _type(self, selector: str, text: str, by: str = 'css',
                   session_name: str = 'default', timeout: int = 10,
                   clear_first: bool = True) -> Dict[str, Any]:
        """Type text into element."""
        try:
            driver = self.browsers[session_name]['driver']
            by_method = self._get_by_method(by)
            
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            
            logger.info(f"Typed text into: {selector}")
            return {
                'success': True,
                'selector': selector,
                'text_length': len(text)
            }
        
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _submit(self, selector: str, by: str = 'css',
                     session_name: str = 'default', timeout: int = 10) -> Dict[str, Any]:
        """Submit form."""
        try:
            driver = self.browsers[session_name]['driver']
            by_method = self._get_by_method(by)
            
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            
            element.submit()
            
            logger.info(f"Form submitted: {selector}")
            return {
                'success': True,
                'selector': selector
            }
        
        except Exception as e:
            logger.error(f"Submit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_text(self, selector: str, by: str = 'css',
                       session_name: str = 'default', timeout: int = 10) -> Dict[str, Any]:
        """Get element text."""
        try:
            driver = self.browsers[session_name]['driver']
            by_method = self._get_by_method(by)
            
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            
            text = element.text
            
            return {
                'success': True,
                'text': text
            }
        
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _screenshot(self, session_name: str = 'default',
                         filename: Optional[str] = None,
                         element_selector: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot."""
        try:
            driver = self.browsers[session_name]['driver']
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'./data/screenshots/browser_{timestamp}.png'
            
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            if element_selector:
                # Screenshot specific element
                element = driver.find_element(By.CSS_SELECTOR, element_selector)
                element.screenshot(filename)
            else:
                # Full page screenshot
                driver.save_screenshot(filename)
            
            logger.info(f"Screenshot saved: {filename}")
            return {
                'success': True,
                'filename': filename
            }
        
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_js(self, script: str, session_name: str = 'default',
                         *args) -> Dict[str, Any]:
        """Execute JavaScript."""
        try:
            driver = self.browsers[session_name]['driver']
            result = driver.execute_script(script, *args)
            
            logger.info("JavaScript executed")
            return {
                'success': True,
                'result': result
            }
        
        except Exception as e:
            logger.error(f"Execute JS failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _wait_for(self, selector: str, by: str = 'css',
                       session_name: str = 'default', timeout: int = 10,
                       condition: str = 'present') -> Dict[str, Any]:
        """Wait for element."""
        try:
            driver = self.browsers[session_name]['driver']
            by_method = self._get_by_method(by)
            
            if condition == 'present':
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by_method, selector))
                )
            elif condition == 'visible':
                WebDriverWait(driver, timeout).until(
                    EC.visibility_of_element_located((by_method, selector))
                )
            elif condition == 'clickable':
                WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
            
            logger.info(f"Wait completed: {selector}")
            return {
                'success': True,
                'selector': selector
            }
        
        except TimeoutException:
            return {
                'success': False,
                'error': f'Timeout waiting for element: {selector}'
            }
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_cookies(self, session_name: str = 'default') -> Dict[str, Any]:
        """Get all cookies."""
        try:
            driver = self.browsers[session_name]['driver']
            cookies = driver.get_cookies()
            
            return {
                'success': True,
                'cookies': cookies,
                'count': len(cookies)
            }
        
        except Exception as e:
            logger.error(f"Get cookies failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _set_cookie(self, cookie: Dict[str, Any],
                         session_name: str = 'default') -> Dict[str, Any]:
        """Set cookie."""
        try:
            driver = self.browsers[session_name]['driver']
            driver.add_cookie(cookie)
            
            logger.info(f"Cookie set: {cookie.get('name')}")
            return {
                'success': True,
                'cookie': cookie.get('name')
            }
        
        except Exception as e:
            logger.error(f"Set cookie failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _back(self, session_name: str = 'default') -> Dict[str, Any]:
        """Go back."""
        try:
            driver = self.browsers[session_name]['driver']
            driver.back()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _forward(self, session_name: str = 'default') -> Dict[str, Any]:
        """Go forward."""
        try:
            driver = self.browsers[session_name]['driver']
            driver.forward()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _refresh(self, session_name: str = 'default') -> Dict[str, Any]:
        """Refresh page."""
        try:
            driver = self.browsers[session_name]['driver']
            driver.refresh()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_by_method(self, by: str):
        """Map by string to Selenium By method."""
        by_map = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return by_map.get(by.lower(), By.CSS_SELECTOR)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities."""
        return {
            'name': 'browser',
            'version': '1.0.0',
            'description': 'Browser automation (Selenium)',
            'actions': [
                'start', 'stop', 'navigate', 'click', 'type',
                'submit', 'get_text', 'screenshot', 'execute_js',
                'wait_for', 'get_cookies', 'set_cookie',
                'back', 'forward', 'refresh'
            ],
            'browsers': ['chrome', 'firefox', 'edge'] if SELENIUM_AVAILABLE else []
        }


# Plugin metadata
PLUGIN_INFO = {
    'name': 'browser',
    'version': '1.0.0',
    'class': BrowserAutomationPlugin,
    'description': 'Web browser automation (Selenium)',
    'author': 'Finder995',
    'requires': ['selenium']
}
