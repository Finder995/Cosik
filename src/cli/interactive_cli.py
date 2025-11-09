"""
Enhanced Interactive CLI for Cosik AI Agent.

Features:
- Command history with up/down arrows
- Auto-completion
- Syntax highlighting
- Multi-line input support
- Command aliases
- Help system
"""

import os
import sys
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import json
from loguru import logger

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter, Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.key_binding import KeyBindings
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    logger.warning("prompt_toolkit not available. Install with: pip install prompt-toolkit")


class CommandCompleter(Completer):
    """Custom completer for Cosik commands."""
    
    def __init__(self, commands: List[str], workflows: List[str]):
        self.commands = commands
        self.workflows = workflows
    
    def get_completions(self, document, complete_event):
        """Get completions for current input."""
        word = document.get_word_before_cursor()
        
        # Command completions
        for command in self.commands:
            if command.startswith(word.lower()):
                yield Completion(command, start_position=-len(word))
        
        # Workflow completions (if user types 'replay ')
        if 'replay' in document.text_before_cursor:
            for workflow in self.workflows:
                if workflow.startswith(word):
                    yield Completion(workflow, start_position=-len(word))


class InteractiveCLI:
    """
    Enhanced interactive CLI for Cosik AI Agent.
    
    Features:
    - Command history
    - Auto-completion
    - Syntax highlighting
    - Multi-line support
    - Aliases
    - Built-in help
    """
    
    def __init__(self, agent, history_file: str = "./data/cli_history.txt"):
        """
        Initialize interactive CLI.
        
        Args:
            agent: CosikAgent instance
            history_file: Path to history file
        """
        self.agent = agent
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Command aliases
        self.aliases = {
            'q': 'exit',
            'quit': 'exit',
            'h': 'help',
            '?': 'help',
            'ls': 'list',
            'clear': 'cls',
            'rec': 'record',
            'play': 'replay',
            'ws': 'workflows',
            'st': 'status',
            'perf': 'performance'
        }
        
        # Built-in commands
        self.builtin_commands = [
            'help', 'exit', 'status', 'history', 'clear', 'cls',
            'record', 'stop', 'replay', 'workflows', 'list',
            'performance', 'errors', 'queue', 'config'
        ]
        
        # Common agent commands
        self.agent_commands = [
            'otwórz', 'open', 'uruchom', 'run', 'kliknij', 'click',
            'wpisz', 'type', 'zapisz', 'save', 'przeczytaj', 'read',
            'znajdź', 'find', 'zamknij', 'close'
        ]
        
        # Initialize prompt toolkit if available
        self.session = None
        if PROMPT_TOOLKIT_AVAILABLE:
            self._setup_prompt_toolkit()
        
        # CLI state
        self.is_running = False
        self.command_count = 0
        
        logger.info("Interactive CLI initialized")
    
    def _setup_prompt_toolkit(self):
        """Setup prompt_toolkit session."""
        # History
        history = FileHistory(str(self.history_file))
        
        # Style
        style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'command': '#ffffff',
            'completion-menu': 'bg:#333333 #ffffff',
            'completion-menu.completion.current': 'bg:#00aa00 #000000',
        })
        
        # Get workflows for completion
        workflows = []
        if hasattr(self.agent, 'command_replay'):
            workflows = [w['name'] for w in self.agent.command_replay.list_workflows()]
        
        # Completer
        completer = CommandCompleter(
            commands=self.builtin_commands + self.agent_commands,
            workflows=workflows
        )
        
        # Create session
        self.session = PromptSession(
            history=history,
            completer=completer,
            style=style,
            complete_while_typing=True
        )
    
    def _get_prompt_text(self) -> str:
        """Get prompt text with formatting."""
        if PROMPT_TOOLKIT_AVAILABLE:
            return HTML('<prompt>Cosik> </prompt>')
        else:
            return "Cosik> "
    
    async def _execute_builtin(self, command: str, args: List[str]) -> bool:
        """
        Execute built-in CLI command.
        
        Returns:
            True if command was handled, False to pass to agent
        """
        cmd = command.lower()
        
        # Exit
        if cmd in ['exit', 'quit', 'q']:
            print("Shutting down...")
            self.is_running = False
            return True
        
        # Help
        elif cmd in ['help', 'h', '?']:
            self._show_help()
            return True
        
        # Clear screen
        elif cmd in ['clear', 'cls']:
            os.system('cls' if os.name == 'nt' else 'clear')
            return True
        
        # Show status
        elif cmd in ['status', 'st']:
            await self._show_status()
            return True
        
        # Show history
        elif cmd == 'history':
            self._show_history()
            return True
        
        # List workflows
        elif cmd in ['workflows', 'ws', 'list', 'ls']:
            self._show_workflows()
            return True
        
        # Show performance
        elif cmd in ['performance', 'perf']:
            self._show_performance()
            return True
        
        # Show errors
        elif cmd == 'errors':
            self._show_errors()
            return True
        
        # Show queue
        elif cmd == 'queue':
            self._show_queue()
            return True
        
        # Start recording
        elif cmd in ['record', 'rec']:
            if not args:
                print("Usage: record <workflow_name>")
            else:
                workflow_name = ' '.join(args)
                if hasattr(self.agent, 'command_replay'):
                    self.agent.command_replay.start_recording(workflow_name)
                    print(f"Recording workflow: {workflow_name}")
                else:
                    print("Command replay not available")
            return True
        
        # Stop recording
        elif cmd == 'stop':
            if hasattr(self.agent, 'command_replay'):
                workflow_name = self.agent.command_replay.stop_recording()
                if workflow_name:
                    print(f"Workflow saved: {workflow_name}")
                else:
                    print("No recording in progress")
            else:
                print("Command replay not available")
            return True
        
        # Replay workflow
        elif cmd in ['replay', 'play']:
            if not args:
                print("Usage: replay <workflow_name>")
            else:
                workflow_name = ' '.join(args)
                if hasattr(self.agent, 'command_replay'):
                    try:
                        print(f"Replaying workflow: {workflow_name}")
                        result = await self.agent.command_replay.replay(workflow_name)
                        print(f"Workflow completed: {result['success_rate']}")
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Command replay not available")
            return True
        
        # Show config
        elif cmd == 'config':
            self._show_config()
            return True
        
        return False
    
    def _show_help(self):
        """Display help text."""
        help_text = """
Cosik AI Agent - Interactive CLI Help

Built-in Commands:
  help, h, ?          Show this help
  exit, quit, q       Exit the CLI
  clear, cls          Clear screen
  status, st          Show agent status
  history             Show command history
  
Workflow Commands:
  workflows, ws, ls   List all workflows
  record <name>       Start recording a workflow
  stop                Stop recording
  replay <name>       Replay a workflow
  
Information Commands:
  performance, perf   Show performance metrics
  errors              Show recent errors
  queue               Show task queue status
  config              Show configuration
  
Agent Commands:
  Any natural language command will be sent to the agent.
  Examples:
    - otwórz notepad
    - click on button
    - save file as output.txt

Aliases:
  q -> exit           h -> help
  ls -> workflows     rec -> record
  play -> replay      st -> status
  perf -> performance

Tips:
  - Use arrow keys to navigate history
  - Press Tab for auto-completion
  - Commands are case-insensitive
  - Use Ctrl+C to cancel current operation
"""
        print(help_text)
    
    async def _show_status(self):
        """Show agent status."""
        print("\n=== Agent Status ===")
        print(f"Running: {self.agent.is_running}")
        print(f"Commands executed: {self.command_count}")
        
        # Queue stats
        if hasattr(self.agent, 'task_queue'):
            stats = self.agent.task_queue.get_queue_stats()
            print(f"\nTask Queue:")
            print(f"  Pending: {stats.get('pending', 0)}")
            print(f"  Running: {stats.get('running', 0)}")
            print(f"  Completed: {stats.get('completed', 0)}")
            print(f"  Failed: {stats.get('failed', 0)}")
        
        print()
    
    def _show_history(self):
        """Show command history."""
        if not self.history_file.exists():
            print("No history available")
            return
        
        try:
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
            
            print("\n=== Command History (last 20) ===")
            for i, line in enumerate(lines[-20:], 1):
                print(f"{i}. {line.strip()}")
            print()
        except Exception as e:
            print(f"Error reading history: {e}")
    
    def _show_workflows(self):
        """Show available workflows."""
        if not hasattr(self.agent, 'command_replay'):
            print("Command replay not available")
            return
        
        workflows = self.agent.command_replay.list_workflows()
        
        if not workflows:
            print("No workflows available")
            return
        
        print("\n=== Available Workflows ===")
        for wf in workflows:
            print(f"\n{wf['name']}")
            if wf.get('description'):
                print(f"  Description: {wf['description']}")
            print(f"  Commands: {wf['commands_count']}")
            if wf.get('tags'):
                print(f"  Tags: {', '.join(wf['tags'])}")
        print()
    
    def _show_performance(self):
        """Show performance metrics."""
        if not hasattr(self.agent, 'performance_monitor'):
            print("Performance monitoring not available")
            return
        
        summary = self.agent.performance_monitor.get_performance_summary()
        
        print("\n=== Performance Metrics ===")
        print(f"Total operations: {summary.get('total_operations', 0)}")
        print(f"Success rate: {summary.get('success_rate', 'N/A')}")
        
        if summary.get('slowest_operation'):
            print(f"\nSlowest operation:")
            print(f"  {summary['slowest_operation']['name']}")
            print(f"  Avg: {summary['slowest_operation']['avg_duration_ms']:.0f}ms")
        
        bottlenecks = summary.get('bottlenecks', [])
        if bottlenecks:
            print(f"\nBottlenecks detected: {len(bottlenecks)}")
            for bn in bottlenecks[:3]:
                print(f"  - {bn['operation']}: {bn['avg_duration_ms']:.0f}ms avg")
        
        print()
    
    def _show_errors(self):
        """Show recent errors."""
        if not hasattr(self.agent, 'error_recovery'):
            print("Error recovery not available")
            return
        
        stats = self.agent.error_recovery.get_error_statistics()
        
        print("\n=== Error Statistics ===")
        print(f"Total errors: {stats.get('total_errors', 0)}")
        print(f"Recovered: {stats.get('recovered_errors', 0)}")
        print(f"Recovery rate: {stats.get('recovery_rate', 'N/A')}")
        
        if stats.get('errors_by_category'):
            print("\nErrors by category:")
            for cat, count in stats['errors_by_category'].items():
                print(f"  {cat}: {count}")
        
        print()
    
    def _show_queue(self):
        """Show task queue status."""
        if not hasattr(self.agent, 'task_queue'):
            print("Task queue not available")
            return
        
        stats = self.agent.task_queue.get_queue_stats()
        
        print("\n=== Task Queue ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
        print()
    
    def _show_config(self):
        """Show current configuration."""
        print("\n=== Configuration ===")
        # This would show relevant config from agent.config
        print("Config display not yet implemented")
        print()
    
    async def run(self):
        """Run the interactive CLI."""
        self.is_running = True
        
        # Welcome message
        print("\n" + "="*50)
        print("Cosik AI Agent - Interactive Mode")
        print("="*50)
        print("Type 'help' for available commands")
        print("Type 'exit' to quit\n")
        
        while self.is_running:
            try:
                # Get input
                if self.session:
                    user_input = await self.session.prompt_async(self._get_prompt_text())
                else:
                    user_input = input("Cosik> ")
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Process input
                await self._process_input(user_input.strip())
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except EOFError:
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                print(f"Error: {e}")
        
        print("\nGoodbye!")
    
    async def _process_input(self, user_input: str):
        """Process user input."""
        # Expand aliases
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        if command in self.aliases:
            command = self.aliases[command]
        
        # Try built-in commands first
        if await self._execute_builtin(command, args):
            return
        
        # Record if recording
        if hasattr(self.agent, 'command_replay') and self.agent.command_replay.recorder.is_recording:
            self.agent.command_replay.record(user_input)
        
        # Send to agent
        try:
            self.command_count += 1
            await self.agent.run(user_input)
        except Exception as e:
            print(f"Error executing command: {e}")
            logger.error(f"Command execution error: {e}")


async def run_interactive_cli(agent):
    """
    Run interactive CLI for agent.
    
    Args:
        agent: CosikAgent instance
    """
    cli = InteractiveCLI(agent)
    await cli.run()
