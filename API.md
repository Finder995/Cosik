# Cosik AI Agent - API Documentation

## Table of Contents

1. [Core Agent](#core-agent)
2. [NLP Module](#nlp-module)
3. [GUI Controller](#gui-controller)
4. [Memory Manager](#memory-manager)
5. [Task Executor](#task-executor)
6. [System Manager](#system-manager)
7. [Configuration](#configuration)
8. [Plugin System](#plugin-system)

---

## Core Agent

### CosikAgent

Main agent class that orchestrates all components.

#### Initialization

```python
from main import CosikAgent

agent = CosikAgent(config_path="config.yaml")
```

#### Methods

##### `async run(command: Optional[str] = None)`

Run the agent with an optional initial command.

```python
await agent.run("otwórz notepad")
```

##### `async process_natural_language(text: str) -> Dict[str, Any]`

Process natural language input.

```python
result = await agent.process_natural_language("otwórz Chrome")
# Returns: {'intent': 'open_application', 'parameters': {'application': 'chrome'}}
```

##### `async execute_task(task: Dict[str, Any]) -> bool`

Execute a single task.

```python
task = {
    'intent': 'type_text',
    'parameters': {'text': 'Hello World'}
}
success = await agent.execute_task(task)
```

##### `async self_modify(modification_request: Dict[str, Any]) -> bool`

Perform self-modification.

```python
modification = {
    'type': 'config',
    'changes': {'agent': {'max_retries': 5}}
}
success = await agent.self_modify(modification)
```

##### `async stop()`

Stop the agent gracefully.

```python
await agent.stop()
```

---

## NLP Module

### LanguageProcessor

Natural language processing for command understanding.

#### Supported Intents

| Intent | Polish Examples | English Examples |
|--------|----------------|------------------|
| `open_application` | "otwórz notepad" | "open chrome" |
| `close_application` | "zamknij chrome" | "close firefox" |
| `click` | "kliknij przycisk" | "click button" |
| `type_text` | "wpisz 'tekst'" | "type 'text'" |
| `read_file` | "przeczytaj plik.txt" | "read file.txt" |
| `write_file` | "zapisz do pliku" | "write to file" |
| `modify_file` | "modyfikuj plik" | "modify file" |
| `system_command` | "wykonaj polecenie" | "execute command" |
| `search` | "znajdź dokument" | "search document" |
| `take_screenshot` | "zrób screenshot" | "take screenshot" |
| `wait` | "czekaj 5 sekund" | "wait 5 seconds" |

#### Methods

##### `async parse(text: str) -> Dict[str, Any]`

Parse natural language to extract intent and parameters.

```python
nlp = LanguageProcessor(config)
result = await nlp.parse("otwórz calculator")
# Returns: {
#     'intent': 'open_application',
#     'parameters': {'application': 'calculator'},
#     'original_text': 'otwórz calculator',
#     'confidence': 0.9
# }
```

##### `extract_tasks_from_plan(plan_text: str) -> List[Dict[str, Any]]`

Extract individual tasks from a multi-step plan.

```python
plan = """
1. Open notepad
2. Type "Hello"
3. Save file
"""
tasks = nlp.extract_tasks_from_plan(plan)
```

---

## GUI Controller

### GUIController

Windows GUI automation controller.

#### Methods

##### `async click(x: int, y: int, button: str = 'left', clicks: int = 1) -> bool`

Click at specific coordinates.

```python
gui = GUIController(config)
await gui.click(100, 200)  # Left click at (100, 200)
await gui.click(100, 200, button='right')  # Right click
```

##### `async move_mouse(x: int, y: int, duration: float = 0.5) -> bool`

Move mouse to coordinates.

```python
await gui.move_mouse(500, 300, duration=1.0)
```

##### `async type_text(text: str, interval: float = 0.05) -> bool`

Type text using keyboard.

```python
await gui.type_text("Hello World", interval=0.1)
```

##### `async press_key(key: str, presses: int = 1) -> bool`

Press a keyboard key.

```python
await gui.press_key('enter')
await gui.press_key('a', presses=3)
```

##### `async hotkey(*keys) -> bool`

Press key combination.

```python
await gui.hotkey('ctrl', 'c')  # Copy
await gui.hotkey('win', 'r')   # Open Run dialog
```

##### `async take_screenshot(filename: str = None, region: Tuple = None) -> str`

Take a screenshot.

```python
# Full screenshot
filename = await gui.take_screenshot()

# Region screenshot
filename = await gui.take_screenshot(region=(0, 0, 800, 600))
```

##### `async find_on_screen(image_path: str, confidence: float = None) -> Tuple[int, int]`

Find image on screen.

```python
coords = await gui.find_on_screen("button.png", confidence=0.9)
if coords:
    x, y = coords
    await gui.click(x, y)
```

##### `async get_window_list() -> List[str]`

Get list of open windows.

```python
windows = await gui.get_window_list()
print(windows)  # ['Chrome', 'Notepad', 'Calculator', ...]
```

##### `async focus_window(title: str) -> bool`

Focus a window by title.

```python
await gui.focus_window("Notepad")
```

##### `async close_window(title: str) -> bool`

Close a window.

```python
await gui.close_window("Calculator")
```

---

## Memory Manager

### MemoryManager

Persistent memory and state management.

#### Methods

##### `async add_interaction(input_text: str, parsed_result: Dict) -> int`

Store an interaction.

```python
memory = MemoryManager(config)
interaction_id = await memory.add_interaction(
    input_text="open notepad",
    parsed_result={'intent': 'open_application', 'parameters': {...}}
)
```

##### `async add_task_result(task: Dict, result: Dict) -> int`

Store task execution result.

```python
task_id = await memory.add_task_result(
    task={'intent': 'click', 'parameters': {}},
    result={'success': True, 'message': 'Clicked successfully'}
)
```

##### `async get_incomplete_tasks() -> List[Dict]`

Get incomplete tasks for auto-continuation.

```python
tasks = await memory.get_incomplete_tasks()
for task in tasks:
    await agent.execute_task(task)
```

##### `async get_recent_interactions(limit: int = 10) -> List[Dict]`

Get recent interactions.

```python
recent = await memory.get_recent_interactions(limit=5)
```

##### `async save_state()` / `async load_state() -> Dict`

Save and load agent state.

```python
# Save
await memory.save_state()

# Load
state = await memory.load_state()
```

---

## Task Executor

### TaskExecutor

Execute tasks based on intents.

#### Methods

##### `async execute(task: Dict[str, Any]) -> Dict[str, Any]`

Execute a task.

```python
executor = TaskExecutor(config, gui, memory)

task = {
    'intent': 'open_application',
    'parameters': {'application': 'notepad'}
}

result = await executor.execute(task)
# Returns: {'success': True, 'message': 'Opened notepad'}
```

---

## System Manager

### SystemManager

System-level operations.

#### File Operations

##### `async read_file(file_path: str) -> str`

Read file content.

```python
system = SystemManager(config)
content = await system.read_file("config.yaml")
```

##### `async write_file(file_path: str, content: str, backup: bool = True) -> bool`

Write to file.

```python
success = await system.write_file(
    "output.txt",
    "Hello World",
    backup=True
)
```

##### `async modify_file(file_path: str, changes: Dict) -> bool`

Modify file content.

```python
changes = {
    'replacements': {
        'old_text': 'new_text'
    },
    'insertions': {
        5: 'New line at position 5'
    }
}
success = await system.modify_file("file.txt", changes)
```

##### `async backup_file(file_path: str) -> str`

Create file backup.

```python
backup_path = await system.backup_file("important.txt")
```

#### Directory Operations

##### `async list_directory(dir_path: str, pattern: str = "*") -> List[str]`

List files in directory.

```python
files = await system.list_directory("C:\\Users\\Documents", "*.txt")
```

##### `async create_directory(dir_path: str) -> bool`

Create directory.

```python
success = await system.create_directory("C:\\MyFolder")
```

#### Registry Operations

##### `async get_registry_value(key_path: str, value_name: str) -> Any`

Read Windows registry value.

```python
value = await system.get_registry_value(
    "HKEY_CURRENT_USER\\Software\\MyApp",
    "SettingName"
)
```

##### `async set_registry_value(key_path: str, value_name: str, value: Any) -> bool`

Write to Windows registry.

```python
success = await system.set_registry_value(
    "HKEY_CURRENT_USER\\Software\\MyApp",
    "SettingName",
    "NewValue"
)
```

#### PowerShell Execution

##### `async execute_powershell(script: str) -> Dict`

Execute PowerShell script.

```python
result = await system.execute_powershell("Get-Process | Select-Object -First 5")
print(result['stdout'])
```

---

## Configuration

### ConfigLoader

Configuration management.

#### Methods

##### `get(key: str, default: Any = None) -> Any`

Get configuration value using dot notation.

```python
config = ConfigLoader("config.yaml")

# Get nested value
max_retries = config.get('agent.max_retries', 3)

# Get top-level value
agent_config = config.get('agent')
```

##### `async update(changes: Dict) -> bool`

Update configuration.

```python
changes = {
    'agent': {
        'max_retries': 5,
        'auto_continuation': True
    }
}
success = await config.update(changes)
```

---

## Plugin System

### Creating a Plugin

Create a file in `src/plugins/`:

```python
from loguru import logger

class MyPlugin:
    """Custom plugin."""
    
    def __init__(self, agent):
        self.agent = agent
        self.name = "my_plugin"
    
    async def execute(self, command: str, **kwargs):
        """Execute plugin command."""
        logger.info(f"Plugin executing: {command}")
        
        if command == "my_action":
            # Your custom logic
            return {
                'success': True,
                'message': 'Action completed'
            }
        
        return {
            'success': False,
            'error': 'Unknown command'
        }
    
    async def on_task_complete(self, task, result):
        """Hook called after task completion."""
        pass

# Plugin metadata
PLUGIN_INFO = {
    'name': 'my_plugin',
    'version': '1.0.0',
    'description': 'My custom plugin',
    'author': 'Your Name',
    'class': MyPlugin
}
```

### Using Plugins

Plugins are automatically loaded at startup. Access them through the agent:

```python
# Plugins will be loaded automatically
agent = CosikAgent()
```

---

## Examples

### Complete Workflow

```python
import asyncio
from main import CosikAgent

async def main():
    # Initialize agent
    agent = CosikAgent()
    
    # Execute commands
    await agent.run("otwórz notepad")
    await asyncio.sleep(1)
    
    await agent.run("wpisz 'Hello from Cosik'")
    await asyncio.sleep(0.5)
    
    await agent.run("zrób screenshot")
    
    # Stop agent
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling

```python
try:
    result = await agent.execute_task(task)
    if not result['success']:
        print(f"Task failed: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception occurred: {e}")
```

### Custom Task

```python
# Define custom task
custom_task = {
    'intent': 'complex_task',
    'parameters': {
        'description': 'My complex multi-step task',
        'needs_ai_planning': True
    }
}

# Execute
result = await agent.execute_task(custom_task)
```
