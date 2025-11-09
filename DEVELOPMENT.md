# Cosik AI Agent - Complete Development Documentation

**Status:** ✅ Active Development  
**Version:** 2.1.0  
**Last Update:** 2024  
**Author:** Finder995

---

## Overview

Cosik to zaawansowany AI agent dla Windows 10/11 z pełną automatyzacją GUI, rozumieniem języka naturalnego, i systemem pluginów. Agent posiada pamięć, auto-kontynuację zadań i możliwość samo-modyfikacji.

---

## Quick Start

```bash
# Instalacja
git clone https://github.com/Finder995/Cosik.git
cd Cosik
pip install -r requirements.txt

# Konfiguracja (opcjonalnie)
cp .env.example .env
# Edytuj .env i dodaj klucze API

# Uruchomienie
python main.py --interactive
```

---

## Core Features (Istniejące)

### 1. Natural Language Processing (NLP)
- **Lokalizacja:** `src/nlp/language_processor.py`
- Polski i angielski język
- Pattern matching dla standardowych komend
- Integracja z AI (GPT-4/Claude) dla złożonych poleceń
- 12+ zdefiniowanych intencji

### 2. GUI Automation
- **Lokalizacja:** `src/automation/gui_controller.py`
- Kontrola myszy i klawiatury (pyautogui)
- Zarządzanie oknami Windows (pywinauto)
- Screenshoty
- Computer Vision (OCR, template matching)

### 3. AI Engine
- **Lokalizacja:** `src/ai/ai_engine.py`
- Integracja z OpenAI GPT-4
- Integracja z Anthropic Claude
- Zaawansowane planowanie zadań
- Analiza błędów i sugestie napraw

### 4. Computer Vision
- **Lokalizacja:** `src/vision/computer_vision.py`
- OCR (Tesseract)
- Template matching (OpenCV)
- Znajdowanie tekstu na ekranie
- Wykrywanie elementów UI

### 5. Memory System
- **Lokalizacja:** `src/memory/memory_manager.py`
- SQLite database
- Pamięć interakcji
- Historia zadań
- Vector storage (ChromaDB)

### 6. Task Execution
- **Lokalizacja:** `src/tasks/task_executor.py`
- Routing zadań
- Wykonywanie akcji
- Auto-continuation
- Retry mechanism

### 7. System Operations
- **Lokalizacja:** `src/system/system_manager.py`
- Registry access
- PowerShell execution
- File operations z backupami
- Process management

---

## New Features (v2.1.0)

### 1. Clipboard Plugin 📋
- **Lokalizacja:** `src/plugins/clipboard_plugin.py`
- **Funkcje:**
  - Copy/paste tekstu
  - Historia schowka
  - Monitoring zmian w czasie rzeczywistym
  - Auto-tracking operacji
  
- **Użycie:**
```python
# Kopiowanie
await plugin_manager.execute_plugin('clipboard', 'copy', text='Hello')

# Wklejanie
result = await plugin_manager.execute_plugin('clipboard', 'paste')

# Monitoring
await plugin_manager.execute_plugin('clipboard', 'monitor_start', interval=1.0)

# Historia
result = await plugin_manager.execute_plugin('clipboard', 'history', limit=10)
```

### 2. File Watcher Plugin 📁
- **Lokalizacja:** `src/plugins/file_watcher_plugin.py`
- **Funkcje:**
  - Monitorowanie katalogów
  - Wykrywanie zmian (create, modify, delete, move)
  - Rekursywne watched paths
  - Event history
  
- **Użycie:**
```python
# Rozpocznij watching
await plugin_manager.execute_plugin('file_watcher', 'watch', 
    path='/path/to/watch', recursive=True)

# Historia zdarzeń
result = await plugin_manager.execute_plugin('file_watcher', 'history', limit=50)

# Stop watching
await plugin_manager.execute_plugin('file_watcher', 'unwatch', path='/path')
```

### 3. Process Monitor Plugin 🖥️
- **Lokalizacja:** `src/plugins/process_monitor_plugin.py`
- **Funkcje:**
  - Lista procesów
  - CPU/Memory monitoring
  - Kill procesów
  - Top processes
  - System statistics
  - Real-time alerting
  
- **Użycie:**
```python
# System stats
result = await plugin_manager.execute_plugin('process_monitor', 'system')

# Top processes
result = await plugin_manager.execute_plugin('process_monitor', 'top', 
    limit=10, sort_by='cpu')

# Monitoring
await plugin_manager.execute_plugin('process_monitor', 'monitor_start', interval=5.0)

# Kill process
await plugin_manager.execute_plugin('process_monitor', 'kill', pid=1234)
```

### 4. Smart Retry Mechanism 🔄
- **Lokalizacja:** `src/utils/smart_retry.py`
- **Funkcje:**
  - Exponential backoff
  - Error classification
  - Retry context tracking
  - Configurable retry logic
  - Error pattern matching
  
- **Użycie:**
```python
from src.utils.smart_retry import SmartRetry

retry = SmartRetry()
result = await retry.execute_with_retry(
    task=task,
    executor=my_executor,
    max_attempts=5,
    backoff_base=1.0
)
```

---

## Architecture

```
Cosik/
├── main.py                    # Main agent orchestrator
├── config.yaml               # Configuration
├── requirements.txt          # Dependencies
├── examples.py              # Basic examples
├── advanced_examples.py     # Advanced examples (NEW)
│
├── src/
│   ├── ai/                  # AI Engine
│   │   ├── __init__.py
│   │   └── ai_engine.py
│   │
│   ├── nlp/                 # Natural Language Processing
│   │   ├── __init__.py
│   │   └── language_processor.py
│   │
│   ├── automation/          # GUI Automation
│   │   ├── __init__.py
│   │   └── gui_controller.py
│   │
│   ├── vision/              # Computer Vision
│   │   ├── __init__.py
│   │   └── computer_vision.py
│   │
│   ├── memory/              # Memory System
│   │   ├── __init__.py
│   │   └── memory_manager.py
│   │
│   ├── tasks/               # Task Execution
│   │   ├── __init__.py
│   │   └── task_executor.py
│   │
│   ├── system/              # System Operations
│   │   ├── __init__.py
│   │   └── system_manager.py
│   │
│   ├── config/              # Configuration
│   │   ├── __init__.py
│   │   └── config_loader.py
│   │
│   ├── plugins/             # Plugin System
│   │   ├── __init__.py
│   │   ├── plugin_manager.py
│   │   ├── example_plugin.py
│   │   ├── scheduler_plugin.py
│   │   ├── web_scraper_plugin.py
│   │   ├── clipboard_plugin.py      # NEW
│   │   ├── file_watcher_plugin.py   # NEW
│   │   └── process_monitor_plugin.py # NEW
│   │
│   └── utils/                        # NEW
│       ├── __init__.py
│       └── smart_retry.py
│
├── tests/
│   ├── __init__.py
│   └── test_agent.py
│
├── data/                    # Created at runtime
│   ├── memory/
│   ├── vector_store/
│   └── backups/
│
└── logs/                    # Created at runtime
    └── agent.log
```

---

## Code Statistics

### New in v2.1.0
- **3 nowe pluginy:** clipboard, file_watcher, process_monitor
- **1 nowy moduł:** smart_retry utility
- **1 nowy plik przykładów:** advanced_examples.py
- **~600 linii nowego kodu**

### Total Project
- **24 pliki Python** (~3,000+ linii)
- **9 pluginów**
- **7 głównych modułów**
- **1 plik dokumentacji** (ten plik)

---

## Configuration

### config.yaml
```yaml
agent:
  name: "Cosik"
  auto_continuation: true
  max_retries: 3

ai:
  provider: "openai"  # or "anthropic"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

memory:
  enabled: true
  max_history: 1000
  storage_path: "./data/memory"

gui:
  confidence_threshold: 0.8
  failsafe: true
  pause_between_actions: 0.5

plugins:
  auto_load: true
  plugins_dir: "./src/plugins"
  enabled:
    - scheduler
    - web_scraper
    - clipboard
    - file_watcher
    - process_monitor
  
  clipboard:
    max_history: 100
  
  file_watcher:
    max_history: 500
  
  process_monitor:
    max_history: 100
    cpu_threshold: 80.0
    memory_threshold: 80.0

system:
  safe_mode: true
  allow_registry_access: false
  allow_powershell: true

logging:
  level: "INFO"
  file_path: "./logs/agent.log"
  max_size: "10 MB"
  backup_count: 5
```

### .env
```bash
# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Dependencies

### Core
- Python 3.8+
- openai >= 1.0.0
- anthropic >= 0.7.0
- langchain >= 0.1.0

### GUI Automation
- pyautogui >= 0.9.54
- pywinauto >= 0.6.8
- pygetwindow >= 0.0.9
- pillow >= 10.0.0

### Computer Vision
- opencv-python >= 4.8.0
- pytesseract >= 0.3.10
- numpy >= 1.24.0

### Plugins (NEW)
- pyperclip >= 1.8.2 (clipboard)
- watchdog >= 3.0.0 (file watcher)
- psutil >= 5.9.0 (process monitor, już było)
- schedule >= 1.2.0 (scheduler)
- requests >= 2.31.0 (web scraper)
- beautifulsoup4 >= 4.12.0 (web scraper)

### Storage
- chromadb >= 0.4.0
- sqlite-utils >= 3.35

### Utilities
- pyyaml >= 6.0
- python-dotenv >= 1.0.0
- loguru >= 0.7.0

### Testing
- pytest >= 7.4.0
- pytest-asyncio >= 0.21.0

---

## API Reference

### Plugin Manager
```python
# Load all plugins
plugin_manager.load_all_plugins()

# Execute plugin command
result = await plugin_manager.execute_plugin(
    plugin_name='clipboard',
    command='copy',
    **kwargs
)

# Get capabilities
caps = plugin_manager.get_plugin_capabilities('clipboard')

# List plugins
plugins = plugin_manager.list_plugins()
```

### Clipboard Plugin
```python
# Commands: copy, paste, history, clear, monitor_start, monitor_stop

await plugin_manager.execute_plugin('clipboard', 'copy', text='Hello')
result = await plugin_manager.execute_plugin('clipboard', 'paste')
result = await plugin_manager.execute_plugin('clipboard', 'history', limit=10)
```

### File Watcher Plugin
```python
# Commands: watch, unwatch, list, history, clear_history

await plugin_manager.execute_plugin('file_watcher', 'watch', 
    path='/path', recursive=True)
result = await plugin_manager.execute_plugin('file_watcher', 'history', limit=50)
await plugin_manager.execute_plugin('file_watcher', 'unwatch', path='/path')
```

### Process Monitor Plugin
```python
# Commands: list, info, kill, top, system, monitor_start, monitor_stop, history

result = await plugin_manager.execute_plugin('process_monitor', 'system')
result = await plugin_manager.execute_plugin('process_monitor', 'top', 
    limit=10, sort_by='cpu')
await plugin_manager.execute_plugin('process_monitor', 'kill', pid=1234)
```

### Smart Retry
```python
from src.utils.smart_retry import SmartRetry

retry = SmartRetry()

# Execute with retry
result = await retry.execute_with_retry(
    task={'intent': 'test'},
    executor=my_async_function,
    max_attempts=5,
    backoff_base=1.0,
    backoff_multiplier=2.0,
    max_backoff=60.0
)

# Simple retry
result = await retry.retry_with_backoff(
    func=my_function,
    max_attempts=3,
    backoff=1.0
)
```

---

## Usage Examples

### Basic Usage
```python
import asyncio
from main import CosikAgent

async def main():
    agent = CosikAgent()
    
    # Natural language command
    await agent.run("otwórz notepad")
    
    await agent.stop()

asyncio.run(main())
```

### Advanced Workflow
```python
async def automation_workflow():
    agent = CosikAgent()
    
    # 1. Start monitoring
    await agent.plugin_manager.execute_plugin(
        'process_monitor', 'monitor_start', interval=5.0)
    
    # 2. Watch directory
    await agent.plugin_manager.execute_plugin(
        'file_watcher', 'watch', path='./data')
    
    # 3. Execute tasks
    commands = [
        "otwórz notepad",
        "wpisz 'Automated by Cosik'",
        "zrób screenshot"
    ]
    
    for cmd in commands:
        parsed = await agent.process_natural_language(cmd)
        await agent.execute_task(parsed)
    
    # 4. Get clipboard
    result = await agent.plugin_manager.execute_plugin(
        'clipboard', 'paste')
    
    # 5. Cleanup
    await agent.plugin_manager.execute_plugin(
        'process_monitor', 'monitor_stop')
    await agent.plugin_manager.execute_plugin(
        'file_watcher', 'unwatch', path='./data')
    
    await agent.stop()
```

Zobacz `advanced_examples.py` dla pełnych przykładów.

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_agent.py::TestLanguageProcessor -v
```

---

## Development

### Creating New Plugin

1. Create file in `src/plugins/my_plugin.py`:

```python
class MyPlugin:
    def __init__(self, config):
        self.config = config
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        if command == 'my_command':
            return {'success': True, 'data': 'result'}
        return {'success': False, 'error': 'Unknown command'}
    
    def get_capabilities(self) -> List[str]:
        return ['my_command']
    
    def cleanup(self):
        pass

PLUGIN_INFO = {
    'name': 'my_plugin',
    'version': '1.0.0',
    'class': MyPlugin,
    'description': 'My custom plugin'
}
```

2. Add to config.yaml:
```yaml
plugins:
  enabled:
    - my_plugin
```

3. Use:
```python
result = await plugin_manager.execute_plugin('my_plugin', 'my_command')
```

---

## Changelog v2.1.0

### ✨ Nowe Funkcje

1. **Clipboard Plugin**
   - Zarządzanie schowkiem
   - Historia operacji
   - Real-time monitoring
   - Auto-tracking

2. **File Watcher Plugin**
   - Monitorowanie katalogów
   - Event tracking (create, modify, delete, move)
   - Recursive watching
   - Event history

3. **Process Monitor Plugin**
   - Listowanie procesów
   - CPU/Memory stats
   - Kill processes
   - Top processes ranking
   - System-wide statistics
   - Real-time monitoring z alertami

4. **Smart Retry Mechanism**
   - Exponential backoff
   - Error classification
   - Retry context
   - Configurable logic

5. **Advanced Examples**
   - Nowy plik `advanced_examples.py`
   - Przykłady użycia nowych pluginów
   - Integrated automation workflows

### 🔧 Ulepszenia

- Dodano nowe zależności do requirements.txt
- Rozbudowano plugin system
- Lepsze error handling
- Dokumentacja skonsolidowana w 1 plik

---

## Troubleshooting

### Problem: Plugin not loading
**Rozwiązanie:**
- Sprawdź `config.yaml` - czy plugin jest w `enabled`
- Sprawdź czy zainstalowane dependencies (patrz requirements.txt)
- Sprawdź logi: `logs/agent.log`

### Problem: OCR nie działa
**Rozwiązanie:**
- Zainstaluj Tesseract OCR
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Ustaw ścieżkę w kodzie lub PATH

### Problem: AI commands nie działają
**Rozwiązanie:**
- Sprawdź `.env` - czy ustawiony OPENAI_API_KEY lub ANTHROPIC_API_KEY
- Sprawdź `config.yaml` - provider i model
- Agent działa bez AI (fallback na pattern matching)

### Problem: High memory usage
**Rozwiązanie:**
- Zmniejsz `max_history` w config
- Użyj `clear_history` w pluginach
- Stop monitoring gdy nie potrzebne

---

## Performance Tips

1. **Memory Management**
   - Ograniczaj history w pluginach
   - Regularnie czyszcz historię
   - Używaj pagination przy pobieraniu danych

2. **Monitoring**
   - Zwiększ interwały monitoringu
   - Monitor tylko gdy potrzebne
   - Stop monitoring po zakończeniu zadań

3. **Plugins**
   - Ładuj tylko potrzebne pluginy
   - Cleanup nieużywane pluginy
   - Używaj lazy loading gdy możliwe

---

## Roadmap

### v2.2 (Planowane)
- [ ] Email plugin (send/receive)
- [ ] Database plugin (SQL operations)
- [ ] Cloud storage plugin (Google Drive, OneDrive)
- [ ] Notification system
- [ ] Task scheduler UI

### v3.0 (Future)
- [ ] REST API
- [ ] Web dashboard
- [ ] Voice commands
- [ ] Multi-agent coordination
- [ ] Linux/macOS support

---

## Security

### Best Practices
1. Używaj safe_mode w production
2. Nie commituj `.env` do repo
3. Ogranicz access do registry/PowerShell
4. Regularnie twórz backupy
5. Review logs dla suspicious activity

### Safe Mode
```yaml
system:
  safe_mode: true
  allow_registry_access: false
  allow_powershell: false
```

---

## License

MIT License - szczegóły w pliku LICENSE

---

## Support

- **GitHub Issues:** https://github.com/Finder995/Cosik/issues
- **Documentation:** Ten plik (DEVELOPMENT.md)
- **Examples:** `examples.py`, `advanced_examples.py`
- **Logs:** `logs/agent.log`

---

## Credits

**Author:** Finder995  
**Contributors:** Cosik Team  
**Repository:** https://github.com/Finder995/Cosik

---

**End of Documentation**
