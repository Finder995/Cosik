"""
Basic tests for new advanced systems.

Tests:
- Advanced Task Queue
- Error Recovery System
- Performance Monitor
- Command Replay System
"""

import asyncio
import pytest
from datetime import datetime

from src.tasks.task_queue import AdvancedTaskQueue, Task, TaskPriority, TaskStatus
from src.system.error_recovery import ErrorRecoverySystem, ErrorCategory
from src.system.performance_monitor import PerformanceMonitor
from src.automation.command_replay import CommandReplaySystem, Workflow, Command


class TestAdvancedTaskQueue:
    """Tests for Advanced Task Queue."""
    
    @pytest.mark.asyncio
    async def test_task_creation(self):
        """Test task creation."""
        task = Task(
            id="test1",
            intent="test",
            priority=TaskPriority.HIGH
        )
        assert task.id == "test1"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_queue_add_task(self):
        """Test adding tasks to queue."""
        queue = AdvancedTaskQueue(max_concurrent=2)
        
        task = Task(id="test1", intent="test")
        task_id = await queue.add_task(task)
        
        assert task_id == "test1"
        assert "test1" in queue.tasks
        assert queue.tasks["test1"].status == TaskStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_queue_with_dependencies(self):
        """Test task dependencies."""
        queue = AdvancedTaskQueue(max_concurrent=2)
        
        # Create tasks with dependencies
        task1 = Task(id="task1", intent="first")
        task2 = Task(id="task2", intent="second", dependencies=["task1"])
        
        await queue.add_task(task1)
        await queue.add_task(task2)
        
        # Task2 should wait for task1
        assert not queue._can_execute(task2)
        
        # Complete task1
        queue.completed_tasks.add("task1")
        
        # Now task2 can execute
        assert queue._can_execute(task2)
    
    @pytest.mark.asyncio
    async def test_queue_stats(self):
        """Test queue statistics."""
        queue = AdvancedTaskQueue(max_concurrent=2)
        
        task = Task(id="test1", intent="test")
        await queue.add_task(task)
        
        stats = queue.get_queue_stats()
        assert stats['total_tasks'] == 1
        assert stats['pending'] >= 0
        assert stats['max_concurrent'] == 2


class TestErrorRecoverySystem:
    """Tests for Error Recovery System."""
    
    @pytest.mark.asyncio
    async def test_error_classification(self):
        """Test error classification."""
        recovery = ErrorRecoverySystem()
        
        # Test different error types
        assert recovery.classify_error("connection timeout") == ErrorCategory.NETWORK
        assert recovery.classify_error("permission denied") == ErrorCategory.PERMISSION
        assert recovery.classify_error("file not found") == ErrorCategory.NOT_FOUND
        assert recovery.classify_error("memory limit exceeded") == ErrorCategory.RESOURCE
    
    @pytest.mark.asyncio
    async def test_record_error(self):
        """Test recording errors."""
        recovery = ErrorRecoverySystem()
        
        error = await recovery.record_error(
            "Test error",
            task_info={'intent': 'test'},
            context={'attempt': 1}
        )
        
        assert error.error_message == "Test error"
        assert error.category == ErrorCategory.UNKNOWN
        assert len(recovery.error_history) == 1
        assert recovery.total_errors == 1
    
    @pytest.mark.asyncio
    async def test_error_statistics(self):
        """Test error statistics."""
        recovery = ErrorRecoverySystem()
        
        # Record some errors
        await recovery.record_error("network timeout", {'test': 1})
        await recovery.record_error("permission denied", {'test': 2})
        await recovery.record_error("file not found", {'test': 3})
        
        stats = recovery.get_error_statistics()
        assert stats['total_errors'] == 3
        assert 'network' in stats['errors_by_category']
        assert 'permission' in stats['errors_by_category']


class TestPerformanceMonitor:
    """Tests for Performance Monitor."""
    
    @pytest.mark.asyncio
    async def test_performance_metric(self):
        """Test performance measurement."""
        monitor = PerformanceMonitor(history_size=100)
        
        async with monitor.measure('test_operation'):
            await asyncio.sleep(0.1)
        
        assert len(monitor.metrics) == 1
        metric = list(monitor.metrics)[0]
        assert metric.operation == 'test_operation'
        assert metric.duration_ms >= 100
        assert metric.success is True
    
    @pytest.mark.asyncio
    async def test_operation_stats(self):
        """Test operation statistics."""
        monitor = PerformanceMonitor(history_size=100)
        
        # Perform same operation multiple times
        for _ in range(3):
            async with monitor.measure('test_op'):
                await asyncio.sleep(0.01)
        
        stats = monitor.get_operation_stats('test_op')
        assert stats['count'] == 3
        assert stats['avg_duration'] > 0
        assert stats['min_duration'] > 0
        assert stats['max_duration'] > 0
    
    def test_performance_summary(self):
        """Test performance summary."""
        monitor = PerformanceMonitor(history_size=100)
        
        summary = monitor.get_performance_summary()
        assert 'total_operations' in summary
        assert 'success_rate' in summary
        assert 'unique_operations' in summary


class TestCommandReplaySystem:
    """Tests for Command Replay System."""
    
    def test_workflow_creation(self):
        """Test workflow creation."""
        workflow = Workflow(
            name="test_workflow",
            description="Test workflow"
        )
        
        assert workflow.name == "test_workflow"
        assert len(workflow.commands) == 0
        assert len(workflow.variables) == 0
    
    def test_workflow_with_commands(self):
        """Test workflow with commands."""
        workflow = Workflow(
            name="test_workflow",
            commands=[
                Command(command="open notepad"),
                Command(command="type hello"),
            ]
        )
        
        assert len(workflow.commands) == 2
        assert workflow.commands[0].command == "open notepad"
    
    def test_workflow_serialization(self):
        """Test workflow to/from dict."""
        workflow = Workflow(
            name="test_workflow",
            description="Test",
            commands=[Command(command="test")]
        )
        
        # To dict
        data = workflow.to_dict()
        assert data['name'] == "test_workflow"
        assert len(data['commands']) == 1
        
        # From dict
        loaded = Workflow.from_dict(data)
        assert loaded.name == workflow.name
        assert len(loaded.commands) == 1
    
    def test_workflow_recorder(self):
        """Test workflow recording."""
        from src.automation.command_replay import WorkflowRecorder
        
        recorder = WorkflowRecorder()
        
        # Start recording
        recorder.start_recording("test_workflow")
        assert recorder.is_recording is True
        
        # Record commands
        recorder.record_command("open file")
        recorder.record_command("save file")
        assert len(recorder.recorded_commands) == 2
        
        # Stop recording
        workflow = recorder.stop_recording()
        assert workflow is not None
        assert workflow.name == "test_workflow"
        assert len(workflow.commands) == 2
        assert recorder.is_recording is False


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_task_with_performance(self):
        """Test task execution with performance monitoring."""
        monitor = PerformanceMonitor()
        queue = AdvancedTaskQueue()
        
        async def dummy_executor(task):
            async with monitor.measure(f"execute_{task.intent}"):
                await asyncio.sleep(0.01)
                return {"success": True}
        
        task = Task(id="test1", intent="dummy")
        await queue.add_task(task)
        
        # Execute
        await queue.execute_task("test1", dummy_executor)
        
        # Check performance was measured
        assert len(monitor.metrics) == 1
        
        # Check task completed
        assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery with task execution."""
        recovery = ErrorRecoverySystem()
        queue = AdvancedTaskQueue()
        
        async def failing_executor(task):
            raise Exception("Simulated failure")
        
        task = Task(id="test1", intent="failing")
        await queue.add_task(task)
        
        # Try to execute (will fail)
        try:
            await queue.execute_task("test1", failing_executor)
        except Exception as e:
            # Record error
            error = await recovery.record_error(str(e), task.to_dict())
            assert error.category != ErrorCategory.UNKNOWN  # Should be classified
        
        # Check error was recorded
        assert recovery.total_errors == 1


def run_tests():
    """Run all tests."""
    import sys
    
    print("Running tests for advanced systems...")
    print("=" * 60)
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto'
    ])
    
    return exit_code


if __name__ == "__main__":
    exit(run_tests())
