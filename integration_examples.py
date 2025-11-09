"""
Integration Example - Using All New Advanced Systems Together

This example demonstrates how to integrate and use all the new systems:
- Advanced Task Queue
- Error Recovery System
- Performance Monitor
- REST API Server
- Command Replay System
- Enhanced Interactive CLI
"""

import asyncio
from datetime import datetime
from loguru import logger

# Import main agent
from main import CosikAgent

# Import new systems
from src.tasks.task_queue import AdvancedTaskQueue, Task, TaskPriority
from src.system.error_recovery import ErrorRecoverySystem
from src.system.performance_monitor import PerformanceMonitor
from src.automation.command_replay import CommandReplaySystem
from src.api.api_server import APIServer
from src.cli.interactive_cli import run_interactive_cli


class EnhancedCosikAgent(CosikAgent):
    """
    Enhanced Cosik AI Agent with all advanced systems integrated.
    
    This extends the base CosikAgent with:
    - Advanced task queue
    - Error recovery
    - Performance monitoring
    - Command replay
    - REST API (optional)
    """
    
    def __init__(self, config_path: str = "config.yaml", enable_api: bool = False, api_port: int = 8000):
        """
        Initialize enhanced agent.
        
        Args:
            config_path: Path to config file
            enable_api: Whether to start REST API server
            api_port: Port for REST API
        """
        # Initialize base agent
        super().__init__(config_path)
        
        # Initialize advanced task queue
        max_concurrent = self.config.get('queue.max_concurrent', 5)
        persist_path = self.config.get('queue.persist_path', './data/queue_state.json')
        self.advanced_queue = AdvancedTaskQueue(
            max_concurrent=max_concurrent,
            persist_path=persist_path
        )
        logger.info(f"Advanced Task Queue initialized (max_concurrent={max_concurrent})")
        
        # Initialize error recovery system
        self.error_recovery = ErrorRecoverySystem()
        logger.info("Error Recovery System initialized")
        
        # Initialize performance monitor
        history_size = self.config.get('performance.history_size', 1000)
        self.performance_monitor = PerformanceMonitor(
            history_size=history_size,
            enable_profiling=True
        )
        logger.info("Performance Monitor initialized")
        
        # Initialize command replay system
        workflow_path = self.config.get('workflows.library_path', './data/workflows')
        self.command_replay = CommandReplaySystem(self, workflow_path)
        logger.info("Command Replay System initialized")
        
        # Initialize REST API (optional)
        self.api_server = None
        if enable_api:
            self.api_server = APIServer(self, host="0.0.0.0", port=api_port)
            logger.info(f"REST API Server initialized (port={api_port})")
        
        logger.info("Enhanced Cosik Agent fully initialized")
    
    async def start(self):
        """Start all systems."""
        # Start performance monitoring
        await self.performance_monitor.start_monitoring()
        
        # Start API server if enabled
        if self.api_server:
            asyncio.create_task(self.api_server.start())
            logger.info("REST API Server started")
        
        logger.info("All systems started")
    
    async def execute_task_enhanced(self, task: Task) -> bool:
        """
        Execute a task with performance monitoring and error recovery.
        
        Args:
            task: Task to execute
            
        Returns:
            True if successful
        """
        # Measure performance
        async with self.performance_monitor.measure(f"task_{task.intent}", metadata=task.to_dict()):
            try:
                # Execute task using base agent
                result = await self.execute_task(task.to_dict())
                return result
                
            except Exception as e:
                # Record error
                error = await self.error_recovery.record_error(
                    str(e),
                    task_info=task.to_dict(),
                    context={'timestamp': datetime.now().isoformat()}
                )
                
                # Attempt recovery
                recovered = await self.error_recovery.attempt_recovery(error)
                
                if recovered:
                    logger.info(f"Error recovered, retrying task {task.id}")
                    # Retry task
                    result = await self.execute_task(task.to_dict())
                    return result
                else:
                    raise
    
    async def run_enhanced(self, command: str = None):
        """
        Enhanced run method with all systems integrated.
        
        Args:
            command: Optional initial command
        """
        await self.start()
        
        if command:
            # Process command and add to advanced queue
            parsed = await self.process_natural_language(command)
            
            # Create task
            task = Task(
                id=f"task_{datetime.now().timestamp()}",
                intent=parsed.get('intent', 'unknown'),
                parameters=parsed.get('parameters', {}),
                priority=TaskPriority.NORMAL
            )
            
            # Add to queue
            await self.advanced_queue.add_task(task)
            
            # Process queue
            await self.advanced_queue.process_queue(self.execute_task_enhanced)
        
        # Show summary
        self._show_summary()
    
    def _show_summary(self):
        """Show summary of all systems."""
        print("\n" + "="*60)
        print("Enhanced Cosik Agent - Systems Summary")
        print("="*60)
        
        # Queue stats
        queue_stats = self.advanced_queue.get_queue_stats()
        print(f"\n📋 Task Queue:")
        print(f"   Total tasks: {queue_stats['total_tasks']}")
        print(f"   Pending: {queue_stats['pending']}")
        print(f"   Running: {queue_stats['running']}")
        print(f"   Completed: {queue_stats['completed']}")
        print(f"   Failed: {queue_stats['failed']}")
        
        # Performance stats
        perf_summary = self.performance_monitor.get_performance_summary()
        print(f"\n⚡ Performance:")
        print(f"   Total operations: {perf_summary['total_operations']}")
        print(f"   Success rate: {perf_summary['success_rate']}")
        if perf_summary.get('slowest_operation'):
            print(f"   Slowest: {perf_summary['slowest_operation']['name']}")
        
        # Error stats
        error_stats = self.error_recovery.get_error_statistics()
        print(f"\n🔧 Error Recovery:")
        print(f"   Total errors: {error_stats['total_errors']}")
        print(f"   Recovered: {error_stats['recovered_errors']}")
        print(f"   Recovery rate: {error_stats['recovery_rate']}")
        
        # Workflow stats
        workflows = self.command_replay.list_workflows()
        print(f"\n🔄 Workflows:")
        print(f"   Available workflows: {len(workflows)}")
        
        # API info
        if self.api_server:
            print(f"\n🌐 REST API:")
            print(f"   Status: Running")
            print(f"   URL: http://{self.api_server.host}:{self.api_server.port}")
            print(f"   Master Key: {self.api_server.master_key}")
        
        print("\n" + "="*60 + "\n")


async def example_basic_integration():
    """Basic integration example."""
    print("\n=== Example 1: Basic Integration ===\n")
    
    # Create enhanced agent
    agent = EnhancedCosikAgent()
    
    # Execute a simple command
    await agent.run_enhanced("otwórz notepad")
    
    await agent.stop()


async def example_task_queue():
    """Task queue with priorities and dependencies."""
    print("\n=== Example 2: Advanced Task Queue ===\n")
    
    agent = EnhancedCosikAgent()
    await agent.start()
    
    # Create tasks with priorities and dependencies
    task1 = Task(
        id="create_folder",
        intent="create_folder",
        parameters={"path": "./test_output"},
        priority=TaskPriority.HIGH
    )
    
    task2 = Task(
        id="create_file",
        intent="create_file",
        parameters={"path": "./test_output/data.txt"},
        priority=TaskPriority.NORMAL,
        dependencies=["create_folder"]  # Wait for folder to be created
    )
    
    task3 = Task(
        id="cleanup",
        intent="cleanup",
        priority=TaskPriority.LOW,
        dependencies=["create_file"]
    )
    
    # Add to queue
    await agent.advanced_queue.add_task(task1)
    await agent.advanced_queue.add_task(task2)
    await agent.advanced_queue.add_task(task3)
    
    # Process queue
    await agent.advanced_queue.process_queue(agent.execute_task_enhanced)
    
    # Show stats
    agent._show_summary()
    
    await agent.stop()


async def example_error_recovery():
    """Error recovery demonstration."""
    print("\n=== Example 3: Error Recovery ===\n")
    
    agent = EnhancedCosikAgent()
    await agent.start()
    
    # Simulate errors
    errors = [
        ("Connection timeout", {"intent": "fetch_url"}),
        ("Permission denied", {"intent": "write_file"}),
        ("File not found", {"intent": "read_file"}),
    ]
    
    for error_msg, task_info in errors:
        error = await agent.error_recovery.record_error(error_msg, task_info)
        recovered = await agent.error_recovery.attempt_recovery(error)
        print(f"Error: {error_msg} - Recovered: {recovered}")
    
    # Show error insights
    insights = agent.error_recovery.get_pattern_insights()
    print(f"\nError patterns detected: {len(insights)}")
    
    suggestions = agent.error_recovery.suggest_preventive_actions()
    print(f"\nPreventive suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    await agent.stop()


async def example_workflow_recording():
    """Workflow recording and replay."""
    print("\n=== Example 4: Workflow Recording & Replay ===\n")
    
    agent = EnhancedCosikAgent()
    await agent.start()
    
    # Start recording
    agent.command_replay.start_recording("example_workflow", "Example automation workflow")
    
    # Record commands
    agent.command_replay.record("otwórz notepad")
    agent.command_replay.record("wpisz 'Hello from workflow'")
    agent.command_replay.record("zapisz jako ${output_file}")
    
    # Stop recording (auto-saves)
    workflow_name = agent.command_replay.stop_recording()
    print(f"Workflow saved: {workflow_name}")
    
    # List workflows
    workflows = agent.command_replay.list_workflows()
    print(f"\nAvailable workflows: {len(workflows)}")
    for wf in workflows:
        print(f"  - {wf['name']}: {wf['commands_count']} commands")
    
    # Replay with variables
    print("\nReplaying workflow...")
    result = await agent.command_replay.replay(
        "example_workflow",
        variables={"output_file": "output.txt"}
    )
    print(f"Replay result: {result['success_rate']}")
    
    await agent.stop()


async def example_interactive_cli():
    """Interactive CLI mode."""
    print("\n=== Example 5: Interactive CLI ===\n")
    
    agent = EnhancedCosikAgent()
    await agent.start()
    
    # Run interactive CLI
    await run_interactive_cli(agent)
    
    await agent.stop()


async def example_rest_api():
    """REST API server."""
    print("\n=== Example 6: REST API Server ===\n")
    
    # Create agent with API enabled
    agent = EnhancedCosikAgent(enable_api=True, api_port=8000)
    await agent.start()
    
    print("REST API Server started!")
    print(f"Master API Key: {agent.api_server.master_key}")
    print("\nAvailable endpoints:")
    print("  GET  /health")
    print("  GET  /api/status")
    print("  POST /api/tasks")
    print("  WS   /ws")
    print("\nExample curl command:")
    print(f"  curl -H 'Authorization: Bearer {agent.api_server.master_key}' \\")
    print("       http://localhost:8000/api/status")
    
    # Keep server running
    print("\nPress Ctrl+C to stop...")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    
    await agent.stop()


async def example_full_integration():
    """Full integration of all systems."""
    print("\n=== Example 7: Full Integration ===\n")
    
    # Create enhanced agent with all features
    agent = EnhancedCosikAgent(enable_api=True, api_port=8000)
    await agent.start()
    
    # 1. Add some tasks to queue
    print("1. Adding tasks to queue...")
    for i in range(3):
        task = Task(
            id=f"task_{i}",
            intent="test_operation",
            priority=TaskPriority.NORMAL
        )
        await agent.advanced_queue.add_task(task)
    
    # 2. Create a workflow
    print("2. Creating workflow...")
    agent.command_replay.start_recording("test_workflow")
    agent.command_replay.record("status")
    agent.command_replay.record("queue")
    workflow_name = agent.command_replay.stop_recording()
    
    # 3. Monitor performance
    print("3. Monitoring performance...")
    async with agent.performance_monitor.measure('full_integration_test'):
        await asyncio.sleep(1)  # Simulate work
    
    # 4. Simulate an error and recovery
    print("4. Testing error recovery...")
    error = await agent.error_recovery.record_error(
        "Test error",
        task_info={'test': True}
    )
    await agent.error_recovery.attempt_recovery(error)
    
    # 5. Show complete summary
    print("\n5. Complete System Summary:")
    agent._show_summary()
    
    # 6. Export reports
    print("6. Exporting reports...")
    agent.performance_monitor.export_report('./reports/performance.json')
    error_report = agent.error_recovery.export_error_report()
    
    print("\nAll systems working together successfully!")
    
    await agent.stop()


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Enhanced Cosik Agent - Integration Examples")
    print("="*60)
    
    # Choose which example to run
    examples = {
        '1': ('Basic Integration', example_basic_integration),
        '2': ('Task Queue', example_task_queue),
        '3': ('Error Recovery', example_error_recovery),
        '4': ('Workflow Recording', example_workflow_recording),
        '5': ('Interactive CLI', example_interactive_cli),
        '6': ('REST API Server', example_rest_api),
        '7': ('Full Integration', example_full_integration),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-7, or 'all'): ").strip()
    
    if choice == 'all':
        for key in ['1', '2', '3', '4']:  # Skip interactive ones
            name, func = examples[key]
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            await func()
    elif choice in examples:
        name, func = examples[choice]
        await func()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
