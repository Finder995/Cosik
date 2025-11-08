# Cosik AI Agent - Project Overview

## Quick Links
- [Installation Guide](INSTALL.md)
- [API Documentation](API.md)
- [FAQ & Troubleshooting](FAQ.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Examples](examples.py)

---

## Project Summary

**Cosik** is an intelligent AI agent for Windows 10/11 that understands natural language commands and can automate GUI applications, manage files, access system settings, and modify itself. It features auto-continuation, persistent memory, and extensibility through plugins.

### Key Features

✨ **Natural Language Understanding**
- Supports Polish and English commands
- Automatic intent recognition
- Context-aware parsing

🤖 **GUI Automation**
- Mouse and keyboard control
- Window management
- Screen capture and image recognition
- Application launching

🧠 **Memory & Auto-continuation**
- Persistent SQLite database
- Remembers all interactions
- Automatically continues incomplete tasks
- Learning from past actions

📁 **File Operations**
- Read, write, modify files
- Automatic backups
- Directory management
- Multiple format support

⚙️ **System Access**
- Windows Registry access
- PowerShell script execution
- Process management
- System configuration

🔧 **Self-modification**
- Code modification capabilities
- Configuration updates
- Plugin system
- Safe modification with backups

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Cosik AI Agent (main.py)        │
│  - Orchestration                        │
│  - Async execution loop                 │
│  - Task queue management                │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼────┐    ┌────▼────┐
   │  NLP   │    │   GUI   │
   │Module  │    │Controller│
   └───┬────┘    └────┬────┘
       │              │
   ┌───▼──────────────▼───┐
   │   Task Executor      │
   │  - Intent routing    │
   │  - Command execution │
   └───┬──────────────────┘
       │
   ┌───▼────┬──────┬───────┐
   │Memory  │System│Config │
   │Manager │Mgr   │Loader │
   └────────┴──────┴───────┘
```

### Components

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Core Agent** | Main orchestration, task management | `main.py` |
| **NLP Module** | Natural language understanding | `src/nlp/language_processor.py` |
| **GUI Controller** | Windows automation | `src/automation/gui_controller.py` |
| **Memory Manager** | Persistent storage, state | `src/memory/memory_manager.py` |
| **Task Executor** | Command execution | `src/tasks/task_executor.py` |
| **System Manager** | File and system ops | `src/system/system_manager.py` |
| **Config Loader** | Configuration management | `src/config/config_loader.py` |
| **Plugins** | Extensibility | `src/plugins/` |

---

## Getting Started

### Quick Start (3 steps)

1. **Install Python 3.8+**
   - Download from python.org
   - Check "Add to PATH"

2. **Run Quick Start Script**
   ```bash
   start.bat
   ```

3. **Start Using**
   ```
   Cosik> otwórz notepad
   Cosik> wpisz "Hello World"
   Cosik> zrób screenshot
   ```

### Command Examples

| Task | Polish Command | English Command |
|------|---------------|-----------------|
| Open app | `otwórz calculator` | `open calculator` |
| Type text | `wpisz "tekst"` | `type "text"` |
| Click | `kliknij przycisk` | `click button` |
| Screenshot | `zrób screenshot` | `take screenshot` |
| Read file | `przeczytaj plik.txt` | `read file.txt` |
| Wait | `czekaj 5 sekund` | `wait 5 seconds` |
| Search | `znajdź dokument` | `search document` |

---

## File Structure

```
Cosik/
├── 📄 main.py                    # Main entry point
├── 📄 config.yaml               # Configuration
├── 📄 requirements.txt          # Dependencies
├── 📄 examples.py               # Usage examples
├── 📄 start.bat                 # Quick start script
│
├── 📁 src/                      # Source code
│   ├── 📁 nlp/                  # Natural language processing
│   │   └── language_processor.py
│   ├── 📁 automation/           # GUI automation
│   │   └── gui_controller.py
│   ├── 📁 memory/               # Memory management
│   │   └── memory_manager.py
│   ├── 📁 tasks/                # Task execution
│   │   └── task_executor.py
│   ├── 📁 system/               # System operations
│   │   └── system_manager.py
│   ├── 📁 config/               # Configuration
│   │   └── config_loader.py
│   └── 📁 plugins/              # Plugin system
│       └── example_plugin.py
│
├── 📁 tests/                    # Test suite
│   └── test_agent.py
│
├── 📁 data/                     # Runtime data
│   ├── 📁 memory/               # Memory database
│   ├── 📁 vector_store/         # Vector embeddings
│   └── 📁 backups/              # File backups
│
├── 📁 logs/                     # Log files
│   └── agent.log
│
└── 📁 docs/                     # Documentation
    ├── README.md               # Main documentation
    ├── INSTALL.md              # Installation guide
    ├── API.md                  # API reference
    ├── FAQ.md                  # FAQ & troubleshooting
    └── CONTRIBUTING.md         # Contributing guide
```

---

## Configuration

### Essential Settings

```yaml
# config.yaml

agent:
  auto_continuation: true    # Continue incomplete tasks
  max_retries: 3            # Retry failed tasks

memory:
  enabled: true             # Enable memory system
  max_history: 1000        # Maximum stored interactions

gui:
  confidence_threshold: 0.8  # Image recognition confidence
  failsafe: true            # Emergency stop (move mouse to corner)

system:
  safe_mode: false          # Enable safety restrictions
  allow_registry_access: true

self_modification:
  enabled: true             # Allow self-modification
  backup_before_modify: true
```

---

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/test_agent.py::TestLanguageProcessor -v
```

### Adding Features

1. **New Intent**
   - Add pattern to `src/nlp/language_processor.py`
   - Add handler to `src/tasks/task_executor.py`
   - Add test to `tests/test_agent.py`

2. **New Plugin**
   - Create file in `src/plugins/`
   - Implement plugin class
   - Add PLUGIN_INFO metadata

3. **Documentation**
   - Update API.md for new APIs
   - Update README.md for new features
   - Add examples to examples.py

### Code Quality

```bash
# Syntax check
python -m py_compile main.py

# Style check (if installed)
flake8 src/

# Type check (if installed)
mypy src/
```

---

## Use Cases

### 1. Office Automation
```python
# Automate daily tasks
await agent.run("otwórz Excel")
await agent.run("przeczytaj plik data.csv")
await agent.run("stwórz raport")
```

### 2. Testing
```python
# GUI testing
await agent.run("otwórz aplikację")
await agent.run("kliknij przycisk Login")
await agent.run("wpisz credentials")
await agent.run("zweryfikuj wynik")
```

### 3. System Maintenance
```python
# System tasks
await agent.run("wyczyść temp files")
await agent.run("sprawdź system updates")
await agent.run("backup important files")
```

### 4. Data Processing
```python
# Batch processing
for file in files:
    await agent.run(f"przetwórz plik {file}")
```

---

## Performance

### Benchmarks

| Operation | Average Time |
|-----------|-------------|
| Parse command | ~10ms |
| Open application | ~2s |
| Type text (100 chars) | ~5s |
| Screenshot | ~500ms |
| File read/write | ~50ms |
| Database query | ~5ms |

### Optimization Tips

1. **Reduce GUI pauses**
   ```yaml
   gui:
     pause_between_actions: 0.1
   ```

2. **Limit memory history**
   ```yaml
   memory:
     max_history: 100
   ```

3. **Disable unnecessary features**
   ```yaml
   memory:
     enabled: false
   ```

---

## Security

### Safety Features

✅ **Safe Mode** - Restricts dangerous operations
✅ **Automatic Backups** - Before file modifications
✅ **Configurable Permissions** - Control access levels
✅ **Logging** - Track all actions
✅ **Local Storage** - No data sent externally

### Best Practices

1. Enable safe mode for testing
2. Review logs regularly
3. Restrict file access patterns
4. Use virtual environments
5. Keep backups enabled
6. Monitor system resources

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| GUI not working | Check pyautogui installation |
| Permission denied | Run as Administrator |
| Database locked | Close other instances |
| Command not understood | Check command format |

See [FAQ.md](FAQ.md) for detailed troubleshooting.

---

## Support

### Resources

- 📖 [Full Documentation](README.md)
- 🔧 [API Reference](API.md)
- ❓ [FAQ](FAQ.md)
- 🐛 [Report Issues](https://github.com/Finder995/Cosik/issues)
- 💬 [Discussions](https://github.com/Finder995/Cosik/discussions)

### Community

- Share your use cases
- Contribute plugins
- Help others
- Report bugs
- Suggest features

---

## Roadmap

### Current Version: 1.0.0

✅ Natural language understanding
✅ GUI automation
✅ Memory system
✅ File operations
✅ System access
✅ Self-modification
✅ Plugin system

### Planned Features

🔜 **Version 1.1**
- Computer vision (OCR, object detection)
- Voice command support
- Enhanced AI planning

🔜 **Version 1.2**
- Web dashboard
- REST API
- Remote control

🔜 **Version 2.0**
- Multi-platform support (Linux, macOS)
- Cloud synchronization
- Advanced learning algorithms

---

## Credits

**Author:** Finder995

**License:** MIT License

**Built With:**
- Python 3.8+
- PyAutoGUI - GUI automation
- SQLite - Data storage
- asyncio - Async execution
- loguru - Logging
- Many other amazing libraries

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- Report bugs
- Suggest features
- Write documentation
- Submit pull requests
- Create plugins
- Share examples

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Ready to start?** Run `start.bat` or check [INSTALL.md](INSTALL.md)!

**Need help?** See [FAQ.md](FAQ.md) or open an issue.

**Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md).
