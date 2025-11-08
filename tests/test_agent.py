"""
Unit tests for Cosik AI Agent
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp.language_processor import LanguageProcessor
from src.config.config_loader import ConfigLoader
from src.memory.memory_manager import MemoryManager


class TestLanguageProcessor:
    """Test natural language processing."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConfigLoader()
    
    @pytest.fixture
    def nlp(self, config):
        """Create language processor."""
        return LanguageProcessor(config)
    
    @pytest.mark.asyncio
    async def test_parse_open_application_polish(self, nlp):
        """Test parsing Polish 'open application' command."""
        result = await nlp.parse("otwórz notepad")
        
        assert result['intent'] == 'open_application'
        assert 'notepad' in result['parameters']['application']
    
    @pytest.mark.asyncio
    async def test_parse_open_application_english(self, nlp):
        """Test parsing English 'open application' command."""
        result = await nlp.parse("open chrome")
        
        assert result['intent'] == 'open_application'
        assert 'chrome' in result['parameters']['application']
    
    @pytest.mark.asyncio
    async def test_parse_type_text(self, nlp):
        """Test parsing type text command."""
        result = await nlp.parse('wpisz "Hello World"')
        
        assert result['intent'] == 'type_text'
        assert result['parameters']['text'] == 'Hello World'
    
    @pytest.mark.asyncio
    async def test_parse_read_file(self, nlp):
        """Test parsing read file command."""
        result = await nlp.parse("przeczytaj plik test.txt")
        
        assert result['intent'] == 'read_file'
        assert 'test.txt' in result['parameters']['file_path']
    
    @pytest.mark.asyncio
    async def test_parse_wait(self, nlp):
        """Test parsing wait command."""
        result = await nlp.parse("czekaj 5 sekund")
        
        assert result['intent'] == 'wait'
        assert result['parameters']['duration'] == 5
    
    @pytest.mark.asyncio
    async def test_parse_screenshot(self, nlp):
        """Test parsing screenshot command."""
        result = await nlp.parse("zrób screenshot")
        
        assert result['intent'] == 'take_screenshot'


class TestConfigLoader:
    """Test configuration management."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = ConfigLoader()
        
        assert config.get('agent.name') == 'Cosik'
        assert config.get('agent.auto_continuation') == True
    
    def test_get_nested_value(self):
        """Test getting nested configuration value."""
        config = ConfigLoader()
        
        value = config.get('memory.enabled', False)
        assert isinstance(value, bool)
    
    def test_get_with_default(self):
        """Test getting non-existent key with default."""
        config = ConfigLoader()
        
        value = config.get('non.existent.key', 'default')
        assert value == 'default'
    
    @pytest.mark.asyncio
    async def test_update_config(self):
        """Test updating configuration."""
        config = ConfigLoader()
        
        changes = {
            'agent': {
                'max_retries': 10
            }
        }
        
        # Note: This would need a temporary config file to test properly
        # For now, just verify the method exists and is callable
        assert hasattr(config, 'update')


class TestMemoryManager:
    """Test memory management."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConfigLoader()
    
    @pytest.fixture
    def memory(self, config, tmp_path):
        """Create memory manager with temporary storage."""
        # Override storage path to use temporary directory
        config.config['memory']['storage_path'] = str(tmp_path / 'memory')
        return MemoryManager(config)
    
    @pytest.mark.asyncio
    async def test_add_interaction(self, memory):
        """Test adding interaction to memory."""
        interaction_id = await memory.add_interaction(
            input_text="test command",
            parsed_result={'intent': 'test', 'parameters': {}}
        )
        
        assert interaction_id > 0
    
    @pytest.mark.asyncio
    async def test_add_task_result(self, memory):
        """Test adding task result."""
        task = {
            'intent': 'test_task',
            'parameters': {'param': 'value'}
        }
        result = {
            'success': True,
            'message': 'Test completed'
        }
        
        task_id = await memory.add_task_result(task, result)
        assert task_id > 0
    
    @pytest.mark.asyncio
    async def test_get_incomplete_tasks(self, memory):
        """Test retrieving incomplete tasks."""
        tasks = await memory.get_incomplete_tasks()
        
        assert isinstance(tasks, list)
    
    @pytest.mark.asyncio
    async def test_get_recent_interactions(self, memory):
        """Test retrieving recent interactions."""
        # Add some interactions first
        await memory.add_interaction("test 1", {'intent': 'test'})
        await memory.add_interaction("test 2", {'intent': 'test'})
        
        recent = await memory.get_recent_interactions(limit=5)
        
        assert isinstance(recent, list)
        assert len(recent) >= 2
    
    @pytest.mark.asyncio
    async def test_save_and_load_state(self, memory):
        """Test state persistence."""
        await memory.save_state()
        
        loaded_state = await memory.load_state()
        
        assert loaded_state is not None
        assert 'timestamp' in loaded_state


class TestTaskIntegration:
    """Integration tests for task execution."""
    
    @pytest.mark.asyncio
    async def test_full_parsing_flow(self):
        """Test full flow from parsing to task structure."""
        config = ConfigLoader()
        nlp = LanguageProcessor(config)
        
        # Parse command
        result = await nlp.parse("otwórz notatnik")
        
        # Verify structure is suitable for task execution
        assert 'intent' in result
        assert 'parameters' in result
        assert result['intent'] == 'open_application'


def test_project_structure():
    """Test that required files and directories exist."""
    base_path = Path(__file__).parent.parent
    
    # Check main files
    assert (base_path / 'main.py').exists()
    assert (base_path / 'config.yaml').exists()
    assert (base_path / 'requirements.txt').exists()
    assert (base_path / 'README.md').exists()
    
    # Check directories
    assert (base_path / 'src').exists()
    assert (base_path / 'src' / 'nlp').exists()
    assert (base_path / 'src' / 'automation').exists()
    assert (base_path / 'src' / 'memory').exists()
    assert (base_path / 'src' / 'tasks').exists()
    assert (base_path / 'src' / 'system').exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
