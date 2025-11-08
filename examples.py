"""
Example usage of Cosik AI Agent
"""

import asyncio
from main import CosikAgent


async def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===\n")
    
    # Create agent
    agent = CosikAgent()
    
    # Execute single command
    await agent.run("otwórz notatnik")
    
    await agent.stop()


async def example_multiple_tasks():
    """Execute multiple tasks in sequence."""
    print("\n=== Multiple Tasks Example ===\n")
    
    agent = CosikAgent()
    
    # Queue multiple tasks
    tasks = [
        "otwórz notepad",
        "wpisz 'Hello from Cosik AI Agent'",
        "zrób screenshot"
    ]
    
    for task in tasks:
        await agent.run(task)
        await asyncio.sleep(1)
    
    await agent.stop()


async def example_file_operations():
    """File operations example."""
    print("\n=== File Operations Example ===\n")
    
    agent = CosikAgent()
    
    # Read, modify, and write files
    await agent.run("przeczytaj plik config.yaml")
    await agent.run("zapisz do pliku test_output.txt")
    
    await agent.stop()


async def example_with_memory():
    """Demonstrate memory and auto-continuation."""
    print("\n=== Memory and Auto-Continuation Example ===\n")
    
    agent = CosikAgent()
    
    # First session
    await agent.run("otwórz calculator")
    
    # Check incomplete tasks
    incomplete = await agent.memory.get_incomplete_tasks()
    print(f"Incomplete tasks: {len(incomplete)}")
    
    # Recent interactions
    recent = await agent.memory.get_recent_interactions(5)
    print(f"Recent interactions: {len(recent)}")
    
    await agent.stop()


async def example_self_modification():
    """Demonstrate self-modification capability."""
    print("\n=== Self-Modification Example ===\n")
    
    agent = CosikAgent()
    
    # Create a modification request
    modification = {
        'type': 'config',
        'changes': {
            'agent': {
                'max_retries': 5  # Change max retries
            }
        }
    }
    
    success = await agent.self_modify(modification)
    print(f"Self-modification successful: {success}")
    
    await agent.stop()


async def main():
    """Run all examples."""
    print("Cosik AI Agent - Examples\n")
    print("=" * 50)
    
    # Run examples
    await example_basic_usage()
    # await example_multiple_tasks()
    # await example_file_operations()
    # await example_with_memory()
    # await example_self_modification()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
