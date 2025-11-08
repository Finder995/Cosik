# Cosik AI Agent - FAQ and Troubleshooting

## Frequently Asked Questions

### General Questions

#### Q: What is Cosik AI Agent?
**A:** Cosik is an intelligent AI agent for Windows 10 that can understand natural language commands, automate GUI applications, manage files, access system settings, and even modify itself. It features auto-continuation, persistent memory, and extensibility through plugins.

#### Q: What can Cosik do?
**A:** Cosik can:
- Open and control applications
- Automate mouse and keyboard actions
- Read, write, and modify files
- Execute system commands
- Access Windows registry
- Take screenshots
- Remember previous interactions
- Continue incomplete tasks automatically
- Modify its own code and configuration

#### Q: Do I need programming knowledge to use Cosik?
**A:** No! Cosik understands natural language commands in both Polish and English. You can simply type what you want to do, like "otwórz notepad" or "open calculator".

#### Q: Is Cosik free?
**A:** Yes, Cosik is open source and free to use under the MIT License.

#### Q: Does Cosik work on Windows 11?
**A:** Yes, Cosik works on both Windows 10 and Windows 11.

#### Q: Can I use Cosik on Linux or macOS?
**A:** Cosik is designed for Windows. Some features may work on other operating systems, but full functionality is not guaranteed.

### Installation Questions

#### Q: What are the system requirements?
**A:**
- Windows 10 or 11
- Python 3.8 or higher
- 500 MB free disk space
- 2 GB RAM (4 GB recommended)

#### Q: Do I need an API key?
**A:** API keys are optional. They're only needed if you want to use advanced AI features with OpenAI or Anthropic. Basic functionality works without API keys.

#### Q: How do I install Python?
**A:**
1. Download from https://www.python.org/downloads/
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Verify: Open Command Prompt and type `python --version`

#### Q: Installation fails with "pip is not recognized"
**A:** Python wasn't added to PATH. Either:
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH in Windows Environment Variables

### Usage Questions

#### Q: How do I start Cosik?
**A:**
```bash
# Option 1: Use quick start script
start.bat

# Option 2: Run manually
python main.py --interactive
```

#### Q: What commands can I use?
**A:** See the README.md for a full list. Examples:
- `otwórz notepad` / `open notepad`
- `wpisz "tekst"` / `type "text"`
- `zrób screenshot` / `take screenshot`
- `zapisz do pliku test.txt` / `write to file test.txt`
- `czekaj 5 sekund` / `wait 5 seconds`

#### Q: Can I use Cosik for automation scripts?
**A:** Yes! You can:
- Use it programmatically with Python
- Create scheduled tasks
- Write custom plugins
- Chain multiple commands

#### Q: How does auto-continuation work?
**A:** Cosik remembers incomplete tasks and automatically continues them when restarted. You can disable this in `config.yaml` by setting `auto_continuation: false`.

#### Q: How do I stop Cosik?
**A:** In interactive mode, type `exit` or `quit`. Alternatively, press Ctrl+C.

### Technical Questions

#### Q: Where are logs stored?
**A:** Logs are in the `logs/` directory. The main log file is `logs/agent.log`.

#### Q: Where is my data stored?
**A:**
- Memory database: `data/memory/memory.db`
- State: `data/memory/agent_state.json`
- Backups: `data/backups/`

#### Q: How do I enable debug mode?
**A:** Edit `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

#### Q: Can Cosik damage my system?
**A:** Cosik has safety features:
- Safe mode prevents dangerous operations
- Automatic backups before file modifications
- Configurable permissions
- You control what it can access

Enable safe mode in `config.yaml`:
```yaml
system:
  safe_mode: true
```

#### Q: How do I create a plugin?
**A:** See API.md for details. Basic structure:
```python
class MyPlugin:
    def __init__(self, agent):
        self.agent = agent
    
    async def execute(self, command, **kwargs):
        # Your code here
        pass

PLUGIN_INFO = {
    'name': 'my_plugin',
    'version': '1.0.0',
    'class': MyPlugin
}
```

### Privacy and Security Questions

#### Q: Does Cosik send my data anywhere?
**A:** No. All data is stored locally. The only external connections are:
- API calls to OpenAI/Anthropic (only if configured)
- Python package downloads during installation

#### Q: Can Cosik access my private files?
**A:** Only files you explicitly tell it to access. You can restrict access in `config.yaml`.

#### Q: Is it safe to enable self-modification?
**A:** Self-modification is controlled:
- Backups are created automatically
- Only configured files can be modified
- Can require user confirmation
- You can disable it entirely

## Troubleshooting

### Installation Issues

#### Problem: "Python is not recognized"
**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or add Python to PATH manually:
   - Search "Environment Variables" in Windows
   - Edit PATH variable
   - Add Python installation directory

#### Problem: "Failed to install pywin32"
**Solution:**
```bash
pip install --upgrade pip
pip install pywin32
python venv\Scripts\pywin32_postinstall.py -install
```

#### Problem: "Permission denied" during installation
**Solution:**
- Run Command Prompt as Administrator
- Or install in user mode: `pip install --user -r requirements.txt`

### Runtime Issues

#### Problem: "ImportError: No module named 'src'"
**Solution:**
Make sure you're running from the Cosik directory:
```bash
cd C:\path\to\Cosik
python main.py
```

#### Problem: Mouse/keyboard control doesn't work
**Solution:**
1. Check pyautogui is installed: `pip show pyautogui`
2. Disable failsafe temporarily in `config.yaml`:
   ```yaml
   gui:
     failsafe: false
   ```
3. Try a simple test:
   ```python
   python -c "import pyautogui; print(pyautogui.position())"
   ```

#### Problem: "PermissionError: Access denied"
**Solution:**
- Run as Administrator for system operations
- Or disable restricted operations in `config.yaml`:
  ```yaml
  system:
    allow_registry_access: false
    restrict_system_files: true
  ```

#### Problem: Agent doesn't understand my commands
**Solution:**
1. Check command format in README.md
2. Try both Polish and English versions
3. Enable DEBUG logging to see parsing details
4. Use quotes for text: `wpisz "my text"`

#### Problem: "Database is locked"
**Solution:**
```bash
# Close all Cosik instances
# Delete the lock file
del data\memory\memory.db-journal
# Restart Cosik
```

#### Problem: High memory usage
**Solution:**
1. Reduce history limit in `config.yaml`:
   ```yaml
   memory:
     max_history: 100
   ```
2. Clear old data:
   ```bash
   del data\memory\memory.db
   ```

#### Problem: Screenshots not working
**Solution:**
1. Install Pillow: `pip install pillow`
2. Check screenshots aren't being blocked by antivirus
3. Verify screen capture permissions in Windows Privacy settings

### Performance Issues

#### Problem: Slow command execution
**Solution:**
1. Reduce pause between actions in `config.yaml`:
   ```yaml
   gui:
     pause_between_actions: 0.1
   ```
2. Disable unnecessary features
3. Check for background processes using resources

#### Problem: Commands timeout
**Solution:**
Increase timeout in `config.yaml`:
```yaml
agent:
  task_timeout: 600  # 10 minutes
```

### Error Messages

#### "FileNotFoundError: config.yaml"
**Solution:**
Make sure `config.yaml` exists in the Cosik directory.

#### "sqlite3.OperationalError"
**Solution:**
Database is corrupted. Backup and delete:
```bash
move data\memory\memory.db data\memory\memory.db.bak
```

#### "WindowsError: [Error 5] Access denied"
**Solution:**
Run as Administrator or reduce permissions in config.

## Getting More Help

### Check Logs
Always check `logs/agent.log` for detailed error information:
```bash
type logs\agent.log
```

### Enable Debug Mode
Edit `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

### Report an Issue
If you can't solve the problem:
1. Check existing GitHub issues
2. Gather information:
   - Python version: `python --version`
   - Windows version
   - Error message
   - Steps to reproduce
   - Relevant log entries
3. Open a new issue on GitHub

### Community Support
- GitHub Discussions
- Check documentation (README.md, API.md, INSTALL.md)
- Review examples.py

## Common Use Cases

### Running Commands on Schedule

Use Windows Task Scheduler:
1. Create new task
2. Trigger: Schedule
3. Action: `python C:\path\to\Cosik\main.py --command "your command"`

### Batch Processing

Create a script:
```python
import asyncio
from main import CosikAgent

async def main():
    agent = CosikAgent()
    
    commands = [
        "command 1",
        "command 2",
        "command 3"
    ]
    
    for cmd in commands:
        await agent.run(cmd)
    
    await agent.stop()

asyncio.run(main())
```

### Integration with Other Tools

Cosik can be used as a Python library:
```python
from src.automation.gui_controller import GUIController
from src.config.config_loader import ConfigLoader

config = ConfigLoader()
gui = GUIController(config)

# Use GUI controller directly
await gui.click(100, 200)
```

## Tips and Best Practices

1. **Start Simple:** Begin with basic commands before complex automation
2. **Use Safe Mode:** Enable when learning or testing
3. **Backup Important Files:** Let Cosik create backups automatically
4. **Monitor Logs:** Watch logs when troubleshooting
5. **Version Control:** Keep config.yaml in version control
6. **Test Commands:** Test in a safe environment first
7. **Read Documentation:** Most answers are in the docs
8. **Update Regularly:** Keep Python and packages updated

## Known Limitations

- Windows-only (full features)
- Some antivirus software may block automation
- UAC prompts require manual intervention
- Screen resolution changes may affect image recognition
- Complex AI planning requires API key
- Self-modification has safety restrictions

## Roadmap

Planned improvements:
- Computer vision integration
- Voice command support
- Web dashboard
- macOS/Linux support
- Advanced scheduling
- Cloud synchronization
- Enhanced AI planning
