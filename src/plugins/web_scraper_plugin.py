"""Web scraping plugin for extracting data from websites."""

import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger


class WebScraperPlugin:
    """Plugin for web scraping and data extraction."""
    
    def __init__(self, config):
        """Initialize web scraper plugin."""
        self.config = config
        self.session = None
        self._init_session()
        logger.info("Web scraper plugin initialized")
    
    def _init_session(self):
        """Initialize HTTP session."""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        except ImportError:
            logger.warning("requests library not installed. Web scraping features limited.")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute web scraping commands.
        
        Supported commands:
        - fetch: Fetch page content
        - extract: Extract data from page
        - download: Download file
        - search: Search for elements
        """
        command_lower = command.lower()
        
        if command_lower == 'fetch':
            return await self._fetch_page(kwargs.get('url'))
        elif command_lower == 'extract':
            return await self._extract_data(**kwargs)
        elif command_lower == 'download':
            return await self._download_file(**kwargs)
        elif command_lower == 'search':
            return await self._search_elements(**kwargs)
        else:
            return {
                'success': False,
                'error': f'Unknown command: {command}'
            }
    
    async def _fetch_page(self, url: str) -> Dict[str, Any]:
        """
        Fetch page content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content and metadata
        """
        if not self.session:
            return {
                'success': False,
                'error': 'HTTP session not available'
            }
        
        try:
            logger.info(f"Fetching page: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'url': url,
                'status_code': response.status_code,
                'content': response.text,
                'headers': dict(response.headers),
                'encoding': response.encoding
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch page: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _extract_data(self, url: Optional[str] = None, 
                          html: Optional[str] = None,
                          selector: Optional[str] = None,
                          xpath: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from HTML using CSS selectors or XPath.
        
        Args:
            url: URL to fetch (if html not provided)
            html: HTML content to parse
            selector: CSS selector
            xpath: XPath expression
            
        Returns:
            Extracted data
        """
        try:
            from bs4 import BeautifulSoup
            
            # Get HTML content
            if html is None:
                if url is None:
                    return {
                        'success': False,
                        'error': 'Either url or html must be provided'
                    }
                
                fetch_result = await self._fetch_page(url)
                if not fetch_result['success']:
                    return fetch_result
                
                html = fetch_result['content']
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract data
            if selector:
                elements = soup.select(selector)
                data = [{'text': el.get_text(strip=True), 'html': str(el)} for el in elements]
            elif xpath:
                # BeautifulSoup doesn't support XPath, need lxml
                try:
                    from lxml import html as lxml_html
                    tree = lxml_html.fromstring(html)
                    elements = tree.xpath(xpath)
                    data = [{'text': el.text_content() if hasattr(el, 'text_content') else str(el)} for el in elements]
                except ImportError:
                    return {
                        'success': False,
                        'error': 'lxml library required for XPath support'
                    }
            else:
                # Extract common elements
                data = {
                    'title': soup.title.string if soup.title else None,
                    'headings': [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
                    'links': [{'text': a.get_text(strip=True), 'href': a.get('href')} for a in soup.find_all('a')],
                    'images': [{'alt': img.get('alt'), 'src': img.get('src')} for img in soup.find_all('img')]
                }
            
            return {
                'success': True,
                'data': data,
                'count': len(data) if isinstance(data, list) else len(data.get('links', []))
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'beautifulsoup4 library not installed'
            }
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _download_file(self, url: str, save_path: str) -> Dict[str, Any]:
        """
        Download file from URL.
        
        Args:
            url: URL to download
            save_path: Path to save file
            
        Returns:
            Download result
        """
        if not self.session:
            return {
                'success': False,
                'error': 'HTTP session not available'
            }
        
        try:
            logger.info(f"Downloading file from {url} to {save_path}")
            
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                'success': True,
                'url': url,
                'save_path': save_path,
                'size': response.headers.get('Content-Length'),
                'content_type': response.headers.get('Content-Type')
            }
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _search_elements(self, url: Optional[str] = None,
                              html: Optional[str] = None,
                              tag: Optional[str] = None,
                              class_name: Optional[str] = None,
                              id: Optional[str] = None,
                              text_contains: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for elements matching criteria.
        
        Args:
            url: URL to fetch
            html: HTML content
            tag: HTML tag name
            class_name: CSS class name
            id: Element ID
            text_contains: Text to search for
            
        Returns:
            Found elements
        """
        try:
            from bs4 import BeautifulSoup
            
            # Get HTML
            if html is None:
                if url is None:
                    return {
                        'success': False,
                        'error': 'Either url or html must be provided'
                    }
                
                fetch_result = await self._fetch_page(url)
                if not fetch_result['success']:
                    return fetch_result
                
                html = fetch_result['content']
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Build search criteria
            attrs = {}
            if class_name:
                attrs['class'] = class_name
            if id:
                attrs['id'] = id
            
            # Search
            if tag:
                elements = soup.find_all(tag, attrs=attrs)
            else:
                elements = soup.find_all(attrs=attrs)
            
            # Filter by text
            if text_contains:
                elements = [el for el in elements if text_contains.lower() in el.get_text().lower()]
            
            results = []
            for el in elements:
                results.append({
                    'tag': el.name,
                    'text': el.get_text(strip=True),
                    'attrs': dict(el.attrs),
                    'html': str(el)[:200]  # Limit HTML length
                })
            
            return {
                'success': True,
                'elements': results,
                'count': len(results)
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'beautifulsoup4 library not installed'
            }
        except Exception as e:
            logger.error(f"Element search failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities."""
        return ['fetch', 'extract', 'download', 'search']
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        if self.session:
            self.session.close()
        logger.info("Web scraper plugin cleaned up")


# Plugin metadata
PLUGIN_INFO = {
    'name': 'web_scraper',
    'version': '1.0.0',
    'class': WebScraperPlugin,
    'description': 'Web scraping and data extraction from websites',
    'author': 'Cosik Team'
}
