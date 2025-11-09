"""
Demo script showcasing new advanced features of Cosik AI Agent.
"""

import asyncio
from typing import Dict, Any


class MockConfig:
    """Mock configuration for demo."""
    
    def get(self, key: str, default=None):
        config_values = {
            'reasoning.mode': 'hybrid',
            'reasoning.max_depth': 5,
            'workflow.max_parallel': 3,
            'workflow.retry_failed': True,
            'workflow.max_retries': 2,
            'context.working_memory_size': 20,
            'context.interaction_history_size': 50,
            'agent.autonomous_mode': True,
            'agent.autonomy_level': 'supervised',
            'agent.autonomous_delay': 0.5,
            'session.storage_dir': './data/sessions',
            'session.auto_save': False,
            'session.save_interval': 60,
            'agent.version': '2.4.0'
        }
        return config_values.get(key, default)


class MockTaskExecutor:
    """Mock task executor for demo."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate task execution."""
        await asyncio.sleep(0.1)  # Simulate work
        return {'success': True, 'result': f"Executed: {task.get('description', 'unknown')}"}


async def demo_reasoning_engine():
    """Demo: Reasoning Engine."""
    print("\n" + "="*60)
    print("DEMO 1: Reasoning Engine - Intelligent Planning")
    print("="*60)
    
    from src.ai.reasoning_engine import ReasoningEngine
    
    config = MockConfig()
    reasoning = ReasoningEngine(config)
    
    # Analyze a goal
    print("\n1. Analyzing goal...")
    goal = "Create a presentation and send it by email"
    analysis = await reasoning.analyze_goal(goal)
    
    print(f"   Goal: {goal}")
    print(f"   Feasible: {analysis['feasible']}")
    print(f"   Complexity: {analysis['complexity']}")
    print(f"   Estimated steps: {analysis['estimated_steps']}")
    print(f"   Confidence: {analysis['confidence']:.2f}")
    
    # Decompose goal
    print("\n2. Decomposing goal into subtasks...")
    subtasks = await reasoning.decompose_goal(goal)
    
    print(f"   Decomposed into {len(subtasks)} atomic tasks:")
    for i, task in enumerate(subtasks, 1):
        print(f"      {i}. {task['description']}")
    
    # Make a decision
    print("\n3. Making intelligent decision...")
    situation = "Multiple files need processing"
    options = ["process sequentially", "process in parallel"]
    
    decision, confidence = await reasoning.make_decision(situation, options)
    print(f"   Situation: {situation}")
    print(f"   Options: {options}")
    print(f"   Decision: {decision} (confidence: {confidence:.2f})")


async def demo_workflow_orchestrator():
    """Demo: Workflow Orchestrator."""
    print("\n" + "="*60)
    print("DEMO 2: Workflow Orchestrator - Task Execution")
    print("="*60)
    
    from src.tasks.workflow_orchestrator import WorkflowOrchestrator
    
    config = MockConfig()
    executor = MockTaskExecutor()
    orchestrator = WorkflowOrchestrator(config, executor)
    
    # Define workflow with dependencies
    print("\n1. Creating workflow with dependencies...")
    tasks = [
        {
            'index': 0,
            'description': 'Open PowerPoint',
            'dependencies': []
        },
        {
            'index': 1,
            'description': 'Load template',
            'dependencies': [0]
        },
        {
            'index': 2,
            'description': 'Add content slides',
            'dependencies': [1]
        },
        {
            'index': 3,
            'description': 'Add charts',
            'dependencies': [1]
        },
        {
            'index': 4,
            'description': 'Save presentation',
            'dependencies': [2, 3]
        }
    ]
    
    print("   Tasks:")
    for task in tasks:
        deps = task['dependencies']
        deps_str = str(deps) if deps else "none"
        print(f"      {task['index']}: {task['description']} (deps: {deps_str})")
    
    # Execute workflow
    print("\n2. Executing workflow adaptively...")
    result = await orchestrator.execute_workflow(
        'presentation_workflow',
        tasks,
        strategy='adaptive'
    )
    
    print(f"   Workflow ID: {result['workflow_id']}")
    print(f"   Success: {result['success']}")
    print(f"   Completed: {result['completed']} tasks")
    print(f"   Failed: {result['failed']} tasks")
    print(f"   Duration: {result['duration']:.2f}s")


async def demo_context_manager():
    """Demo: Context Manager."""
    print("\n" + "="*60)
    print("DEMO 3: Context Manager - Awareness & State")
    print("="*60)
    
    from src.context.context_manager import ContextManager
    
    config = MockConfig()
    context = ContextManager(config)
    
    # Start session
    print("\n1. Starting session...")
    await context.start_session('demo_session')
    print(f"   Session started: {context.current_context['session_id']}")
    
    # Set goal
    print("\n2. Setting goal...")
    goal = "Prepare quarterly report"
    await context.update_goal(goal)
    print(f"   Current goal: {goal}")
    
    # Add tasks
    print("\n3. Adding tasks...")
    tasks = [
        {'id': 't1', 'description': 'Collect data'},
        {'id': 't2', 'description': 'Analyze trends'},
        {'id': 't3', 'description': 'Create visualizations'}
    ]
    
    for task in tasks:
        await context.add_task(task)
        print(f"      Added: {task['description']}")
    
    # Get context summary
    print("\n4. Context summary...")
    summary = await context.get_context_summary()
    print(f"   {summary}")
    
    # Suggest next action
    print("\n5. Suggesting next action...")
    suggestion = await context.suggest_next_action()
    if suggestion:
        print(f"   Suggested action: {suggestion['action']}")
        print(f"   Reasoning: {suggestion['reasoning']}")


async def demo_session_manager():
    """Demo: Session Manager."""
    print("\n" + "="*60)
    print("DEMO 4: Session Manager - Persistence")
    print("="*60)
    
    from src.session.session_manager import SessionManager
    
    config = MockConfig()
    session = SessionManager(config)
    
    # Start session
    print("\n1. Starting new session...")
    session_id = await session.start_session()
    print(f"   Session ID: {session_id}")
    
    # Update state
    print("\n2. Updating session state...")
    await session.update_state('current_task', 'data_analysis')
    await session.update_state('progress', 50)
    print("   State updated: current_task, progress")
    
    # Add events
    print("\n3. Recording events...")
    await session.add_event('task_started', {'task': 'data_analysis'})
    await session.add_event('milestone_reached', {'milestone': '50%'})
    print("   Events recorded: 2")
    
    # Create snapshot
    print("\n4. Creating snapshot...")
    snapshot_id = await session.create_snapshot("Halfway point")
    print(f"   Snapshot created: {snapshot_id}")
    
    # Get session info
    print("\n5. Session info...")
    events = await session.get_events()
    state_value = await session.get_state('progress')
    print(f"   Events: {len(events)}")
    print(f"   Progress: {state_value}%")
    print(f"   Snapshots: {len(session.current_session['snapshots'])}")


async def demo_pattern_recognizer():
    """Demo: Pattern Recognizer."""
    print("\n" + "="*60)
    print("DEMO 5: Pattern Recognizer - GUI Element Detection")
    print("="*60)
    
    from src.vision.pattern_recognizer import PatternRecognizer
    
    config = MockConfig()
    recognizer = PatternRecognizer(config)
    
    # Recognize elements
    print("\n1. Recognizing GUI elements...")
    
    elements_to_recognize = [
        "OK button",
        "Cancel button in bottom right",
        "Username textfield",
        "Submit button at bottom"
    ]
    
    for elem_desc in elements_to_recognize:
        result = await recognizer.recognize_element(elem_desc)
        print(f"\n   Description: {elem_desc}")
        print(f"   Type: {result['element_type']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Methods used: {', '.join(result['methods_used'])}")
    
    # Learn from interaction
    print("\n2. Learning from successful interaction...")
    await recognizer.learn_from_interaction(
        "Submit button",
        {'type': 'button', 'label': 'Submit', 'location': {'x': 500, 'y': 600}},
        success=True
    )
    
    learned = recognizer.get_learned_patterns()
    print(f"   Learned patterns: {len(learned)}")
    if learned:
        print(f"   Last pattern: {learned[-1]['description']}")
        print(f"   Success rate: {learned[-1]['success_rate']:.1%}")


async def demo_integrated_workflow():
    """Demo: Integrated workflow using multiple components."""
    print("\n" + "="*60)
    print("DEMO 6: Integrated Workflow - All Components Working Together")
    print("="*60)
    
    from src.ai.reasoning_engine import ReasoningEngine
    from src.tasks.workflow_orchestrator import WorkflowOrchestrator
    from src.context.context_manager import ContextManager
    from src.session.session_manager import SessionManager
    
    config = MockConfig()
    
    # Initialize components
    print("\n1. Initializing components...")
    reasoning = ReasoningEngine(config)
    context = ContextManager(config)
    session = SessionManager(config)
    executor = MockTaskExecutor()
    orchestrator = WorkflowOrchestrator(config, executor, reasoning)
    
    print("   ✓ ReasoningEngine")
    print("   ✓ ContextManager")
    print("   ✓ SessionManager")
    print("   ✓ WorkflowOrchestrator")
    
    # Start session and context
    print("\n2. Starting session and context...")
    session_id = await session.start_session()
    await context.start_session('integrated_demo')
    print(f"   Session: {session_id}")
    
    # Define and analyze goal
    print("\n3. Analyzing and decomposing goal...")
    goal = "Create monthly sales report"
    await context.update_goal(goal)
    await session.update_state('goal', goal)
    
    analysis = await reasoning.analyze_goal(goal)
    subtasks = await reasoning.decompose_goal(goal)
    
    print(f"   Goal: {goal}")
    print(f"   Complexity: {analysis['complexity']}")
    print(f"   Subtasks: {len(subtasks)}")
    
    # Create workflow from subtasks
    print("\n4. Creating and executing workflow...")
    workflow_tasks = []
    for i, subtask in enumerate(subtasks[:5]):  # Limit to 5 for demo
        workflow_tasks.append({
            'index': i,
            'description': subtask['description'],
            'dependencies': []
        })
    
    result = await orchestrator.execute_workflow(
        'sales_report_workflow',
        workflow_tasks,
        strategy='adaptive'
    )
    
    print(f"   Executed: {result['completed']} tasks")
    print(f"   Duration: {result['duration']:.2f}s")
    
    # Update context and session
    print("\n5. Updating context and session...")
    await session.add_event('workflow_completed', result)
    await session.create_snapshot("After workflow completion")
    
    summary = await context.get_context_summary()
    print(f"   {summary}")
    
    # End session
    print("\n6. Ending session...")
    session_summary = await session.end_session()
    print(f"   Duration: {session_summary['duration_seconds']:.1f}s")
    print(f"   Events: {session_summary['events_count']}")


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  COSIK AI AGENT - Advanced Features Demo".center(58) + "║")
    print("║" + "  Version 2.4.0".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        await demo_reasoning_engine()
        await demo_workflow_orchestrator()
        await demo_context_manager()
        await demo_session_manager()
        await demo_pattern_recognizer()
        await demo_integrated_workflow()
        
        print("\n" + "="*60)
        print("All demos completed successfully! ✅")
        print("="*60)
        print("\nNew features demonstrated:")
        print("  ✓ Intelligent reasoning and planning")
        print("  ✓ Advanced workflow orchestration")
        print("  ✓ Context awareness and management")
        print("  ✓ Session persistence")
        print("  ✓ GUI pattern recognition")
        print("  ✓ Integrated multi-component workflow")
        print("\nFor more information, see CHANGES.md")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
