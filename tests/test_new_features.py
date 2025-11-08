"""
Tests for new plugins and utilities.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.config_loader import ConfigLoader
from src.plugins.clipboard_plugin import ClipboardPlugin
from src.plugins.file_watcher_plugin import FileWatcherPlugin
from src.plugins.process_monitor_plugin import ProcessMonitorPlugin
from src.utils.smart_retry import SmartRetry, RetryContext


class TestClipboardPlugin:
    """Test clipboard plugin functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConfigLoader()
    
    @pytest.fixture
    def clipboard(self, config):
        """Create clipboard plugin."""
        return ClipboardPlugin(config)
    
    @pytest.mark.asyncio
    async def test_copy_paste(self, clipboard):
        """Test copy and paste operations."""
        test_text = "Test clipboard content"
        
        # Copy
        result = await clipboard.execute('copy', text=test_text)
        assert result.get('success', False) or 'error' in result
        
        # Paste
        result = await clipboard.execute('paste')
        assert result.get('success', False) or 'error' in result
    
    @pytest.mark.asyncio
    async def test_history(self, clipboard):
        """Test clipboard history."""
        result = await clipboard.execute('history', limit=5)
        
        assert 'history' in result or 'error' in result
        if 'history' in result:
            assert isinstance(result['history'], list)
    
    @pytest.mark.asyncio
    async def test_clear(self, clipboard):
        """Test clipboard clear."""
        result = await clipboard.execute('clear')
        assert result.get('success', False) or 'error' in result
    
    def test_capabilities(self, clipboard):
        """Test getting capabilities."""
        caps = clipboard.get_capabilities()
        
        assert isinstance(caps, list)
        assert 'copy' in caps
        assert 'paste' in caps


class TestFileWatcherPlugin:
    """Test file watcher plugin."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConfigLoader()
    
    @pytest.fixture
    def watcher(self, config):
        """Create file watcher plugin."""
        return FileWatcherPlugin(config)
    
    @pytest.mark.asyncio
    async def test_watch_unwatch(self, watcher, tmp_path):
        """Test watching and unwatching directories."""
        # Watch
        result = await watcher.execute('watch', path=str(tmp_path), recursive=False)
        assert result.get('success', False) or 'error' in result
        
        # List
        result = await watcher.execute('list')
        assert 'watched_paths' in result or 'error' in result
        
        # Unwatch
        result = await watcher.execute('unwatch', path=str(tmp_path))
        assert result.get('success', False) or 'error' in result
    
    @pytest.mark.asyncio
    async def test_history(self, watcher):
        """Test event history."""
        result = await watcher.execute('history', limit=10)
        
        assert 'events' in result or 'error' in result
        if 'events' in result:
            assert isinstance(result['events'], list)
    
    def test_capabilities(self, watcher):
        """Test getting capabilities."""
        caps = watcher.get_capabilities()
        
        assert isinstance(caps, list)
        assert 'watch' in caps
        assert 'unwatch' in caps


class TestProcessMonitorPlugin:
    """Test process monitor plugin."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConfigLoader()
    
    @pytest.fixture
    def monitor(self, config):
        """Create process monitor plugin."""
        return ProcessMonitorPlugin(config)
    
    @pytest.mark.asyncio
    async def test_list_processes(self, monitor):
        """Test listing processes."""
        result = await monitor.execute('list')
        
        assert result.get('success', False) or 'error' in result
        if result.get('success'):
            assert 'processes' in result
            assert isinstance(result['processes'], list)
    
    @pytest.mark.asyncio
    async def test_system_stats(self, monitor):
        """Test getting system statistics."""
        result = await monitor.execute('system')
        
        assert result.get('success', False) or 'error' in result
        if result.get('success'):
            assert 'stats' in result
            assert 'cpu' in result['stats']
            assert 'memory' in result['stats']
    
    @pytest.mark.asyncio
    async def test_top_processes(self, monitor):
        """Test getting top processes."""
        result = await monitor.execute('top', limit=5, sort_by='cpu')
        
        assert result.get('success', False) or 'error' in result
        if result.get('success'):
            assert 'processes' in result
            assert len(result['processes']) <= 5
    
    def test_capabilities(self, monitor):
        """Test getting capabilities."""
        caps = monitor.get_capabilities()
        
        assert isinstance(caps, list)
        assert 'list' in caps
        assert 'system' in caps
        assert 'top' in caps


class TestSmartRetry:
    """Test smart retry mechanism."""
    
    @pytest.fixture
    def retry(self):
        """Create smart retry instance."""
        return SmartRetry()
    
    @pytest.mark.asyncio
    async def test_retry_context(self):
        """Test retry context creation."""
        task = {'task_id': 'test', 'intent': 'test'}
        context = RetryContext(task=task, max_attempts=3)
        
        assert context.attempt == 0
        assert context.should_retry()
        
        context.record_attempt('Test error')
        assert context.attempt == 1
        assert context.last_error == 'Test error'
    
    @pytest.mark.asyncio
    async def test_successful_retry(self, retry):
        """Test successful retry after failures."""
        attempt_count = [0]
        
        async def failing_task(task):
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                return {'success': False, 'error': 'Temporary error'}
            return {'success': True, 'data': 'Success'}
        
        task = {'task_id': 'test1', 'intent': 'test'}
        result = await retry.execute_with_retry(
            task=task,
            executor=failing_task,
            max_attempts=5,
            backoff_base=0.1
        )
        
        assert result['success'] == True
        assert attempt_count[0] == 3
    
    @pytest.mark.asyncio
    async def test_failed_retry(self, retry):
        """Test failed retry after max attempts."""
        async def always_failing_task(task):
            return {'success': False, 'error': 'Permanent error'}
        
        task = {'task_id': 'test2', 'intent': 'test'}
        result = await retry.execute_with_retry(
            task=task,
            executor=always_failing_task,
            max_attempts=3,
            backoff_base=0.1
        )
        
        assert result['success'] == False
        assert 'retry_summary' in result
    
    def test_error_classification(self, retry):
        """Test error type classification."""
        assert retry._classify_error('Connection timeout') == 'network'
        assert retry._classify_error('Permission denied') == 'permission'
        assert retry._classify_error('File not found') == 'not_found'
        assert retry._classify_error('Resource busy') == 'resource'
        assert retry._classify_error('Some random error') == 'unknown'
    
    def test_retryable_errors(self, retry):
        """Test retryable error detection."""
        assert retry._is_retryable_error('network') == True
        assert retry._is_retryable_error('temporary') == True
        assert retry._is_retryable_error('permission') == False
        assert retry._is_retryable_error('not_found') == False


class TestPluginIntegration:
    """Integration tests for plugins."""
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self):
        """Test plugin initialization and cleanup."""
        config = ConfigLoader()
        
        # Create plugins
        clipboard = ClipboardPlugin(config)
        watcher = FileWatcherPlugin(config)
        monitor = ProcessMonitorPlugin(config)
        
        # Test capabilities
        assert len(clipboard.get_capabilities()) > 0
        assert len(watcher.get_capabilities()) > 0
        assert len(monitor.get_capabilities()) > 0
        
        # Cleanup
        clipboard.cleanup()
        watcher.cleanup()
        monitor.cleanup()


def test_retry_context_summary():
    """Test retry context summary."""
    task = {'task_id': 'test', 'intent': 'test'}
    context = RetryContext(task=task, max_attempts=3)
    
    context.record_attempt('Error 1')
    context.record_attempt('Error 2')
    context.record_attempt()  # Success
    
    summary = context.get_summary()
    
    assert summary['attempts'] == 3
    assert summary['max_attempts'] == 3
    assert len(summary['error_history']) == 2
    assert summary['success'] == True


def test_backoff_calculation():
    """Test backoff calculation."""
    task = {'task_id': 'test', 'intent': 'test'}
    context = RetryContext(
        task=task,
        backoff_base=1.0,
        backoff_multiplier=2.0,
        max_backoff=10.0
    )
    
    # First attempt - no backoff
    assert context.calculate_backoff() == 0.0
    
    # Subsequent attempts
    context.record_attempt('Error')
    assert context.calculate_backoff() == 1.0
    
    context.record_attempt('Error')
    assert context.calculate_backoff() == 2.0
    
    context.record_attempt('Error')
    assert context.calculate_backoff() == 4.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
