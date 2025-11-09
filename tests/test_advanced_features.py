"""
Tests for new advanced features: reasoning, workflow, context, autonomous agent, and session management.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime


class TestReasoningEngine:
    """Tests for ReasoningEngine."""
    
    @pytest.fixture
    def config(self):
        return Mock(get=lambda x, default=None: default)
    
    @pytest.fixture
    def reasoning_engine(self, config):
        from src.ai.reasoning_engine import ReasoningEngine
        return ReasoningEngine(config)
    
    @pytest.mark.asyncio
    async def test_analyze_goal_simple(self, reasoning_engine):
        """Test goal analysis for simple task."""
        result = await reasoning_engine.analyze_goal("open notepad")
        
        assert result['feasible'] is True
        assert result['complexity'] == 'simple'
        assert result['estimated_steps'] > 0
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_goal_complex(self, reasoning_engine):
        """Test goal analysis for complex task."""
        result = await reasoning_engine.analyze_goal("automate daily report generation")
        
        assert result['feasible'] is True
        assert result['complexity'] in ['medium', 'complex']
        assert result['estimated_steps'] > 5
    
    @pytest.mark.asyncio
    async def test_decompose_goal(self, reasoning_engine):
        """Test goal decomposition."""
        goal = "create and save a text file"
        subtasks = await reasoning_engine.decompose_goal(goal)
        
        assert len(subtasks) > 0
        assert all(task.get('type') == 'atomic' for task in subtasks)
    
    @pytest.mark.asyncio
    async def test_make_decision(self, reasoning_engine):
        """Test decision making."""
        situation = "Multiple files to process"
        options = ["process sequentially", "process in parallel"]
        
        decision, confidence = await reasoning_engine.make_decision(
            situation, options
        )
        
        assert decision in options
        assert 0 <= confidence <= 1.0


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator."""
    
    @pytest.fixture
    def config(self):
        return Mock(get=lambda x, default=None: {
            'workflow.max_parallel': 3,
            'workflow.retry_failed': True,
            'workflow.max_retries': 2
        }.get(x, default))
    
    @pytest.fixture
    def task_executor(self):
        executor = Mock()
        executor.execute = AsyncMock(return_value={'success': True})
        return executor
    
    @pytest.fixture
    def orchestrator(self, config, task_executor):
        from src.tasks.workflow_orchestrator import WorkflowOrchestrator
        return WorkflowOrchestrator(config, task_executor)
    
    @pytest.mark.asyncio
    async def test_execute_sequential_workflow(self, orchestrator):
        """Test sequential workflow execution."""
        tasks = [
            {'index': 0, 'description': 'Task 1', 'dependencies': []},
            {'index': 1, 'description': 'Task 2', 'dependencies': [0]},
            {'index': 2, 'description': 'Task 3', 'dependencies': [1]}
        ]
        
        result = await orchestrator.execute_workflow(
            'test_workflow',
            tasks,
            strategy='sequential'
        )
        
        assert result['success'] is True
        assert result['completed'] == 3
        assert result['failed'] == 0
    
    @pytest.mark.asyncio
    async def test_dependency_levels(self, orchestrator):
        """Test dependency level computation."""
        tasks = [
            {'index': 0, 'dependencies': []},
            {'index': 1, 'dependencies': []},
            {'index': 2, 'dependencies': [0, 1]},
            {'index': 3, 'dependencies': [2]}
        ]
        
        levels = orchestrator._compute_dependency_levels(tasks)
        
        assert len(levels) == 3
        assert set(levels[0]) == {0, 1}
        assert levels[1] == [2]
        assert levels[2] == [3]


class TestContextManager:
    """Tests for ContextManager."""
    
    @pytest.fixture
    def config(self):
        return Mock(get=lambda x, default=None: {
            'context.working_memory_size': 20,
            'context.interaction_history_size': 50
        }.get(x, default))
    
    @pytest.fixture
    def context_manager(self, config):
        from src.context.context_manager import ContextManager
        return ContextManager(config)
    
    @pytest.mark.asyncio
    async def test_start_session(self, context_manager):
        """Test session start."""
        await context_manager.start_session('test_session')
        
        assert context_manager.current_context['session_id'] == 'test_session'
        assert context_manager.current_context['start_time'] is not None
    
    @pytest.mark.asyncio
    async def test_update_goal(self, context_manager):
        """Test goal update."""
        await context_manager.start_session('test_session')
        await context_manager.update_goal('Test goal')
        
        assert context_manager.current_context['current_goal'] is not None
        assert context_manager.current_context['current_goal']['description'] == 'Test goal'
    
    @pytest.mark.asyncio
    async def test_add_task(self, context_manager):
        """Test adding tasks."""
        await context_manager.start_session('test_session')
        
        task = {'id': 'task1', 'description': 'Test task'}
        await context_manager.add_task(task)
        
        assert len(context_manager.current_context['active_tasks']) == 1
    
    @pytest.mark.asyncio
    async def test_suggest_next_action(self, context_manager):
        """Test next action suggestion."""
        await context_manager.start_session('test_session')
        await context_manager.update_goal('Complete project')
        
        suggestion = await context_manager.suggest_next_action()
        
        assert suggestion is not None
        assert 'action' in suggestion


class TestAutonomousAgent:
    """Tests for AutonomousAgent."""
    
    @pytest.fixture
    def config(self):
        return Mock(get=lambda x, default=None: {
            'agent.autonomous_mode': True,
            'agent.autonomy_level': 'supervised',
            'agent.autonomous_delay': 0.1
        }.get(x, default))
    
    @pytest.fixture
    def autonomous_agent(self, config):
        from src.ai.autonomous_agent import AutonomousAgent
        
        reasoning = Mock()
        reasoning.decompose_goal = AsyncMock(return_value=[
            {'description': 'task1', 'executable': True}
        ])
        
        context = Mock()
        context.update_goal = AsyncMock()
        context.add_task = AsyncMock()
        context.get_relevant_context = AsyncMock(return_value={
            'active_tasks': [],
            'constraints': []
        })
        
        workflow = Mock()
        executor = Mock()
        executor.execute = AsyncMock(return_value={'success': True})
        
        return AutonomousAgent(config, reasoning, context, workflow, executor)
    
    def test_autonomy_status(self, autonomous_agent):
        """Test getting autonomy status."""
        status = autonomous_agent.get_autonomy_status()
        
        assert 'active' in status
        assert 'autonomy_level' in status
        assert status['autonomy_level'] == 'supervised'
    
    def test_analyze_progress(self, autonomous_agent):
        """Test progress analysis."""
        context = {
            'active_tasks': [
                {'status': 'completed'},
                {'status': 'completed'},
                {'status': 'pending'},
                {'status': 'failed'}
            ]
        }
        
        progress = autonomous_agent._analyze_progress(context)
        
        assert progress['total_tasks'] == 4
        assert progress['completed'] == 2
        assert progress['failed'] == 1
        assert progress['pending'] == 1
        assert progress['percentage'] == 50.0


class TestSessionManager:
    """Tests for SessionManager."""
    
    @pytest.fixture
    def config(self):
        import tempfile
        temp_dir = tempfile.mkdtemp()
        return Mock(get=lambda x, default=None: {
            'session.storage_dir': temp_dir,
            'session.auto_save': False,
            'session.save_interval': 60,
            'session.max_events': 1000,
            'agent.version': '1.0'
        }.get(x, default))
    
    @pytest.fixture
    def session_manager(self, config):
        from src.session.session_manager import SessionManager
        return SessionManager(config)
    
    @pytest.mark.asyncio
    async def test_start_session(self, session_manager):
        """Test starting a new session."""
        session_id = await session_manager.start_session()
        
        assert session_id is not None
        assert session_manager.current_session is not None
        assert session_manager.session_id == session_id
    
    @pytest.mark.asyncio
    async def test_save_and_resume_session(self, session_manager):
        """Test session save and resume."""
        # Start session
        session_id = await session_manager.start_session()
        await session_manager.update_state('test_key', 'test_value')
        await session_manager.save_session()
        
        # End session
        await session_manager.end_session()
        
        # Resume session
        resumed = await session_manager.resume_session(session_id)
        assert resumed is True
        
        value = await session_manager.get_state('test_key')
        assert value == 'test_value'
    
    @pytest.mark.asyncio
    async def test_create_snapshot(self, session_manager):
        """Test creating snapshots."""
        await session_manager.start_session()
        await session_manager.update_state('key1', 'value1')
        
        snapshot_id = await session_manager.create_snapshot('Test snapshot')
        
        assert snapshot_id is not None
        assert len(session_manager.current_session['snapshots']) == 1
    
    @pytest.mark.asyncio
    async def test_add_event(self, session_manager):
        """Test adding events."""
        await session_manager.start_session()
        
        await session_manager.add_event('test_event', {'data': 'test'})
        
        events = await session_manager.get_events()
        assert len(events) > 0


class TestPatternRecognizer:
    """Tests for PatternRecognizer."""
    
    @pytest.fixture
    def config(self):
        return Mock(get=lambda x, default=None: default)
    
    @pytest.fixture
    def pattern_recognizer(self, config):
        from src.vision.pattern_recognizer import PatternRecognizer
        return PatternRecognizer(config)
    
    @pytest.mark.asyncio
    async def test_recognize_button(self, pattern_recognizer):
        """Test button recognition."""
        result = await pattern_recognizer.recognize_element("OK button")
        
        assert result['element_type'] == 'button'
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_parse_description(self, pattern_recognizer):
        """Test description parsing."""
        parsed = pattern_recognizer._parse_description("top left OK button")
        
        assert parsed['element_type'] == 'button'
        assert 'ok' in str(parsed).lower()
        assert 'top' in parsed['position_hints']
        assert 'left' in parsed['position_hints']
    
    @pytest.mark.asyncio
    async def test_learn_from_interaction(self, pattern_recognizer):
        """Test learning from interactions."""
        await pattern_recognizer.learn_from_interaction(
            "Submit button",
            {'type': 'button', 'label': 'Submit', 'location': {'x': 100, 'y': 200}},
            success=True
        )
        
        patterns = pattern_recognizer.get_learned_patterns()
        assert len(patterns) == 1
        assert patterns[0]['success_rate'] == 1.0


# Integration tests
class TestIntegration:
    """Integration tests for combined components."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_context(self):
        """Test workflow execution with context tracking."""
        from src.tasks.workflow_orchestrator import WorkflowOrchestrator
        from src.context.context_manager import ContextManager
        
        config = Mock(get=lambda x, default=None: {
            'workflow.max_parallel': 2,
            'context.working_memory_size': 20
        }.get(x, default))
        
        context = ContextManager(config)
        await context.start_session('test_integration')
        
        executor = Mock()
        executor.execute = AsyncMock(return_value={'success': True})
        
        orchestrator = WorkflowOrchestrator(config, executor)
        
        tasks = [
            {'index': 0, 'description': 'Task 1', 'dependencies': []},
            {'index': 1, 'description': 'Task 2', 'dependencies': []}
        ]
        
        result = await orchestrator.execute_workflow(
            'integration_test',
            tasks,
            strategy='parallel'
        )
        
        assert result['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
