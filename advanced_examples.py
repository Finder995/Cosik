"""
Advanced Examples for Cosik AI Agent
Demonstrates new features: clipboard, file watcher, process monitor, smart retry
"""

import asyncio
from main import CosikAgent


async def example_clipboard_usage():
    """Example: Using clipboard plugin."""
    print("\n=== Clipboard Plugin Example ===")
    
    agent = CosikAgent()
    
    # Copy text to clipboard
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'copy',
        text='Hello from Cosik AI Agent!'
    )
    print(f"Copy result: {result}")
    
    # Paste from clipboard
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'paste'
    )
    print(f"Clipboard content: {result['content']}")
    
    # Start monitoring clipboard
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'monitor_start',
        interval=2.0
    )
    print(f"Monitoring started: {result}")
    
    # Wait a bit
    print("Monitoring clipboard for 10 seconds...")
    await asyncio.sleep(10)
    
    # Stop monitoring
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'monitor_stop'
    )
    print(f"Monitoring stopped: {result}")
    
    # Get history
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'history',
        limit=5
    )
    print(f"Clipboard history: {result['history']}")
    
    await agent.stop()


async def example_file_watcher():
    """Example: Using file watcher plugin."""
    print("\n=== File Watcher Plugin Example ===")
    
    agent = CosikAgent()
    
    # Watch current directory
    result = await agent.plugin_manager.execute_plugin(
        'file_watcher',
        'watch',
        path='.',
        recursive=False
    )
    print(f"Watching directory: {result}")
    
    # List watched paths
    result = await agent.plugin_manager.execute_plugin(
        'file_watcher',
        'list'
    )
    print(f"Watched paths: {result}")
    
    # Create a test file to trigger events
    print("Creating test file...")
    with open('test_file_watch.txt', 'w') as f:
        f.write('Test content')
    
    # Wait for events to be captured
    await asyncio.sleep(2)
    
    # Get event history
    result = await agent.plugin_manager.execute_plugin(
        'file_watcher',
        'history',
        limit=10
    )
    print(f"File events: {result['events']}")
    
    # Stop watching
    result = await agent.plugin_manager.execute_plugin(
        'file_watcher',
        'unwatch',
        path='.'
    )
    print(f"Stopped watching: {result}")
    
    await agent.stop()


async def example_process_monitor():
    """Example: Using process monitor plugin."""
    print("\n=== Process Monitor Plugin Example ===")
    
    agent = CosikAgent()
    
    # Get system stats
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'system'
    )
    print(f"System stats: {result['stats']}")
    
    # Get top processes by CPU
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'top',
        limit=5,
        sort_by='cpu'
    )
    print(f"\nTop 5 processes by CPU:")
    for proc in result['processes']:
        print(f"  {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
    
    # Get top processes by memory
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'top',
        limit=5,
        sort_by='memory'
    )
    print(f"\nTop 5 processes by Memory:")
    for proc in result['processes']:
        print(f"  {proc['name']} (PID: {proc['pid']}) - Memory: {proc['memory_percent']}%")
    
    # Start monitoring
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'monitor_start',
        interval=3.0
    )
    print(f"\nMonitoring started: {result}")
    
    # Monitor for 15 seconds
    print("Monitoring system for 15 seconds...")
    await asyncio.sleep(15)
    
    # Stop monitoring
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'monitor_stop'
    )
    print(f"Monitoring stopped: {result}")
    
    # Get monitoring history
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'history',
        limit=5
    )
    print(f"\nMonitoring history:")
    for entry in result['history']:
        print(f"  {entry['timestamp']}: CPU: {entry['cpu_percent']}%, Memory: {entry['memory_percent']}%")
        if 'alerts' in entry:
            print(f"    ALERTS: {entry['alerts']}")
    
    await agent.stop()


async def example_smart_retry():
    """Example: Using smart retry mechanism."""
    print("\n=== Smart Retry Example ===")
    
    from src.utils.smart_retry import SmartRetry
    
    retry = SmartRetry()
    
    # Simulate a task that fails a few times then succeeds
    attempt_count = 0
    
    async def unreliable_task(task):
        """Simulated unreliable task."""
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 3:
            print(f"Task failed on attempt {attempt_count}")
            return {
                'success': False,
                'error': 'Temporary network error'
            }
        else:
            print(f"Task succeeded on attempt {attempt_count}")
            return {
                'success': True,
                'data': 'Task completed successfully'
            }
    
    task = {'task_id': 'test_task', 'intent': 'test'}
    
    result = await retry.execute_with_retry(
        task=task,
        executor=unreliable_task,
        max_attempts=5,
        backoff_base=1.0,
        backoff_multiplier=2.0
    )
    
    print(f"Final result: {result}")
    print(f"Total attempts: {attempt_count}")


async def example_integrated_automation():
    """Example: Integrated automation workflow."""
    print("\n=== Integrated Automation Example ===")
    
    agent = CosikAgent()
    
    # 1. Monitor processes
    print("Step 1: Starting process monitoring...")
    await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'monitor_start',
        interval=5.0
    )
    
    # 2. Watch a directory
    print("Step 2: Watching directory for changes...")
    await agent.plugin_manager.execute_plugin(
        'file_watcher',
        'watch',
        path='.',
        recursive=False
    )
    
    # 3. Use AI to process natural language commands
    print("Step 3: Processing natural language commands...")
    
    # Parse and execute commands
    commands = [
        "zrób screenshot",
        "czekaj 2 sekundy"
    ]
    
    for cmd in commands:
        parsed = await agent.process_natural_language(cmd)
        print(f"Parsed: {parsed}")
        success = await agent.execute_task(parsed)
        print(f"Executed: {success}")
    
    # 4. Get clipboard content
    print("Step 4: Checking clipboard...")
    result = await agent.plugin_manager.execute_plugin(
        'clipboard',
        'paste'
    )
    if result.get('success'):
        print(f"Clipboard: {result['content'][:50]}...")
    
    # 5. Check system stats
    print("Step 5: Getting system stats...")
    result = await agent.plugin_manager.execute_plugin(
        'process_monitor',
        'system'
    )
    print(f"CPU: {result['stats']['cpu']['percent']}%")
    print(f"Memory: {result['stats']['memory']['percent']}%")
    
    # Cleanup
    print("Cleanup...")
    await agent.plugin_manager.execute_plugin('process_monitor', 'monitor_stop')
    await agent.plugin_manager.execute_plugin('file_watcher', 'unwatch', path='.')
    
    await agent.stop()
    print("Done!")


async def main():
    """Run all examples."""
    print("Cosik AI Agent - Advanced Examples")
    print("=" * 60)
    
    examples = [
        ("Clipboard Usage", example_clipboard_usage),
        ("File Watcher", example_file_watcher),
        ("Process Monitor", example_process_monitor),
        ("Smart Retry", example_smart_retry),
        ("Integrated Automation", example_integrated_automation)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")
    
    choice = input("\nSelect example to run (0-5): ")
    
    if choice == '0':
        for name, example_func in examples:
            print(f"\n{'=' * 60}")
            print(f"Running: {name}")
            print('=' * 60)
            try:
                await example_func()
            except Exception as e:
                print(f"Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, example_func = examples[int(choice) - 1]
        print(f"\nRunning: {name}")
        try:
            await example_func()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
