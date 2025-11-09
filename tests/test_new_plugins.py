"""
Comprehensive Tests for New Plugins (v2.3.0).

Testing:
- Database Plugin
- Email Plugin  
- Browser Automation Plugin
- Notification Plugin
- Voice Recognition Module
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.plugins.database_plugin import DatabasePlugin
from src.plugins.email_plugin import EmailPlugin
from src.plugins.browser_automation_plugin import BrowserAutomationPlugin
from src.plugins.notification_plugin import NotificationPlugin
from src.voice.voice_recognition import VoiceRecognitionModule


class TestDatabasePlugin:
    """Tests for Database Plugin."""
    
    @pytest.fixture
    def config(self):
        return {
            'plugins': {
                'database': {
                    'default_db': './data/test.db'
                }
            }
        }
    
    @pytest.fixture
    def plugin(self, config):
        return DatabasePlugin(config)
    
    @pytest.mark.asyncio
    async def test_sqlite_connect(self, plugin):
        """Test SQLite connection."""
        result = await plugin.execute('', action='connect', database='test_db', path='./data/test.db')
        
        assert result['success'] == True
        assert result['type'] == 'sqlite'
        assert 'test_db' in plugin.connections
    
    @pytest.mark.asyncio
    async def test_create_table(self, plugin):
        """Test table creation."""
        await plugin.execute('', action='connect', database='test_db', path='./data/test.db')
        
        schema = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'email': 'TEXT'
        }
        
        result = await plugin.execute('', action='create_table', table_name='users', schema=schema, database='test_db')
        
        assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_insert_data(self, plugin):
        """Test data insertion."""
        await plugin.execute('', action='connect', database='test_db', path='./data/test.db')
        
        schema = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT',
            'value': 'INTEGER'
        }
        await plugin.execute('', action='create_table', table_name='test_data', schema=schema, database='test_db')
        
        data = {'name': 'test', 'value': 123}
        result = await plugin.execute('', action='insert', table='test_data', data=data, database='test_db')
        
        assert result['success'] == True
        assert result['affected_rows'] >= 1
    
    @pytest.mark.asyncio
    async def test_query_data(self, plugin):
        """Test data querying."""
        await plugin.execute('', action='connect', database='test_db', path='./data/test.db')
        
        result = await plugin.execute('', action='query', sql='SELECT 1 as test', database='test_db')
        
        assert result['success'] == True
        assert 'rows' in result
    
    @pytest.mark.asyncio
    async def test_list_tables(self, plugin):
        """Test listing tables."""
        await plugin.execute('', action='connect', database='test_db', path='./data/test.db')
        
        result = await plugin.execute('', action='list_tables', database='test_db')
        
        assert result['success'] == True
        assert 'tables' in result
    
    def test_capabilities(self, plugin):
        """Test plugin capabilities."""
        caps = plugin.get_capabilities()
        
        assert caps['name'] == 'database'
        assert 'sqlite' in caps['supported_databases']
        assert 'query' in caps['actions']


class TestEmailPlugin:
    """Tests for Email Plugin."""
    
    @pytest.fixture
    def config(self):
        return {
            'plugins': {
                'email': {}
            }
        }
    
    @pytest.fixture
    def plugin(self, config):
        return EmailPlugin(config)
    
    @pytest.mark.asyncio
    async def test_add_account(self, plugin):
        """Test adding email account."""
        result = await plugin.execute(
            '',
            action='add_account',
            name='test',
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            username='test@example.com',
            password='password'
        )
        
        assert result['success'] == True
        assert 'test' in plugin.accounts
    
    @pytest.mark.asyncio
    async def test_list_accounts(self, plugin):
        """Test listing accounts."""
        await plugin.execute(
            '',
            action='add_account',
            name='test',
            smtp_server='smtp.gmail.com',
            smtp_port=587
        )
        
        result = await plugin.execute('', action='list_accounts')
        
        assert result['success'] == True
        assert 'test' in result['accounts']
    
    @pytest.mark.asyncio
    async def test_create_template(self, plugin):
        """Test creating email template."""
        result = await plugin.execute(
            '',
            action='create_template',
            name='welcome',
            content='Hello {name}!'
        )
        
        assert result['success'] == True
        assert 'welcome' in plugin.templates
    
    def test_capabilities(self, plugin):
        """Test plugin capabilities."""
        caps = plugin.get_capabilities()
        
        assert caps['name'] == 'email'
        assert 'send' in caps['actions']
        assert 'SMTP' in caps['protocols']


class TestBrowserAutomationPlugin:
    """Tests for Browser Automation Plugin."""
    
    @pytest.fixture
    def config(self):
        return {
            'plugins': {
                'browser': {}
            }
        }
    
    @pytest.fixture
    def plugin(self, config):
        return BrowserAutomationPlugin(config)
    
    def test_capabilities(self, plugin):
        """Test plugin capabilities."""
        caps = plugin.get_capabilities()
        
        assert caps['name'] == 'browser'
        assert 'navigate' in caps['actions']
        assert 'click' in caps['actions']
    
    @pytest.mark.asyncio
    async def test_by_method_mapping(self, plugin):
        """Test CSS selector mapping."""
        try:
            from selenium.webdriver.common.by import By
            
            assert plugin._get_by_method('css') == By.CSS_SELECTOR
            assert plugin._get_by_method('id') == By.ID
            assert plugin._get_by_method('xpath') == By.XPATH
        except ImportError:
            # Selenium not available, skip this test
            pytest.skip("Selenium not installed")


class TestNotificationPlugin:
    """Tests for Notification Plugin."""
    
    @pytest.fixture
    def config(self):
        return {
            'notifications': {
                'max_history': 100
            }
        }
    
    @pytest.fixture
    def plugin(self, config):
        return NotificationPlugin(config)
    
    @pytest.mark.asyncio
    async def test_create_template(self, plugin):
        """Test creating notification template."""
        result = await plugin.execute(
            '',
            action='create_template',
            name='alert',
            title='Alert: {type}',
            message='Message: {msg}'
        )
        
        assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_history(self, plugin):
        """Test notification history."""
        # Add notification to history
        plugin.system.history.append({
            'timestamp': '2024-01-01T00:00:00',
            'title': 'Test',
            'message': 'Test message',
            'priority': 'normal'
        })
        
        result = await plugin.execute('', action='history', limit=10)
        
        assert result['success'] == True
        assert len(result['notifications']) > 0
    
    @pytest.mark.asyncio
    async def test_clear_history(self, plugin):
        """Test clearing history."""
        plugin.system.history.append({'test': 'data'})
        
        result = await plugin.execute('', action='clear_history')
        
        assert result['success'] == True
        assert len(plugin.system.history) == 0
    
    @pytest.mark.asyncio
    async def test_stats(self, plugin):
        """Test notification statistics."""
        plugin.system.history = [
            {'priority': 'high', 'type': 'desktop'},
            {'priority': 'low', 'type': 'sound'},
            {'priority': 'high', 'type': 'desktop'}
        ]
        
        result = await plugin.execute('', action='stats')
        
        assert result['success'] == True
        stats = result['stats']
        assert stats['total'] == 3
        assert stats['by_priority']['high'] == 2
    
    def test_capabilities(self, plugin):
        """Test plugin capabilities."""
        caps = plugin.get_capabilities()
        
        assert caps['name'] == 'notification'
        assert 'send' in caps['actions']
        assert 'desktop' in caps['types']


class TestVoiceRecognitionModule:
    """Tests for Voice Recognition Module."""
    
    @pytest.fixture
    def config(self):
        return {
            'voice': {
                'language': 'en-US',
                'energy_threshold': 4000
            }
        }
    
    @pytest.fixture
    def module(self, config):
        return VoiceRecognitionModule(config)
    
    @pytest.mark.asyncio
    async def test_set_language(self, module):
        """Test setting language."""
        result = await module.set_language('pl-PL')
        
        assert result['success'] == True
        assert module.language == 'pl-PL'
    
    @pytest.mark.asyncio
    async def test_history(self, module):
        """Test recognition history."""
        module.history = [
            {'text': 'test 1', 'timestamp': '2024-01-01'},
            {'text': 'test 2', 'timestamp': '2024-01-02'}
        ]
        
        result = await module.get_history(limit=10)
        
        assert result['success'] == True
        assert len(result['history']) == 2
    
    @pytest.mark.asyncio
    async def test_clear_history(self, module):
        """Test clearing history."""
        module.history = [{'test': 'data'}]
        
        result = await module.clear_history()
        
        assert result['success'] == True
        assert len(module.history) == 0
    
    def test_status(self, module):
        """Test module status."""
        status = module.get_status()
        
        assert 'available' in status
        assert 'language' in status
        assert status['language'] == 'en-US'


class TestPluginIntegration:
    """Integration tests for all plugins."""
    
    @pytest.fixture
    def config(self):
        return {
            'plugins': {
                'database': {},
                'email': {},
                'browser': {}
            },
            'notifications': {},
            'voice': {}
        }
    
    def test_all_plugins_initialize(self, config):
        """Test that all plugins can be initialized."""
        db = DatabasePlugin(config)
        email = EmailPlugin(config)
        browser = BrowserAutomationPlugin(config)
        notif = NotificationPlugin(config)
        voice = VoiceRecognitionModule(config)
        
        assert db is not None
        assert email is not None
        assert browser is not None
        assert notif is not None
        assert voice is not None
    
    def test_all_plugins_have_capabilities(self, config):
        """Test that all plugins expose capabilities."""
        plugins = [
            DatabasePlugin(config),
            EmailPlugin(config),
            BrowserAutomationPlugin(config),
            NotificationPlugin(config)
        ]
        
        for plugin in plugins:
            caps = plugin.get_capabilities()
            assert 'name' in caps
            assert 'version' in caps
            assert 'actions' in caps


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
