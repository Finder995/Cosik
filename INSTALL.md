# Cosik AI Agent - Installation Guide

## Quick Start (Windows 10)

### Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/downloads/

### Step-by-Step Installation

#### 1. Clone or Download Repository

**Option A: Using Git**
```bash
git clone https://github.com/Finder995/Cosik.git
cd Cosik
```

**Option B: Download ZIP**
- Download ZIP from GitHub
- Extract to a folder
- Open Command Prompt in that folder

#### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# You should see (venv) in your prompt
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Some dependencies like `pywin32` may require additional setup. If you encounter issues:

```bash
# Install pywin32 separately
pip install pywin32

# Run post-install script
python venv\Scripts\pywin32_postinstall.py -install
```

#### 4. Configure API Keys (Optional)

If you want to use AI features (GPT-4, Claude):

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-your-key-here
```

#### 5. Test Installation

```bash
# Run basic test
python -c "import sys; print(f'Python {sys.version}')"

# Run unit tests
pytest tests/ -v

# Try running the agent
python main.py --help
```

### First Run

#### Interactive Mode

```bash
python main.py --interactive
```

You should see:
```
Cosik AI Agent - Interactive Mode
Type 'exit' to quit

Cosik>
```

Try some commands:
```
Cosik> otwórz notatnik
Cosik> zrób screenshot
Cosik> exit
```

#### Single Command Mode

```bash
python main.py --command "otwórz calculator"
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pyautogui'`

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Permission Errors

**Problem:** Access denied when accessing system resources

**Solution:**
- Run Command Prompt as Administrator
- Check antivirus settings
- Disable safe mode in `config.yaml`

#### 3. pywin32 Issues

**Problem:** `ImportError: DLL load failed`

**Solution:**
```bash
pip uninstall pywin32
pip install pywin32
python venv\Scripts\pywin32_postinstall.py -install
```

#### 4. GUI Automation Not Working

**Problem:** Mouse/keyboard control doesn't work

**Solution:**
- Ensure you're running Windows 10
- Check that pyautogui is installed: `pip show pyautogui`
- Disable failsafe temporarily in config.yaml for testing
- Try running a simple test:
```python
python -c "import pyautogui; print(pyautogui.position())"
```

### Platform-Specific Notes

#### Windows 10/11
- Fully supported
- All features should work
- May need to disable UAC for some system operations

#### Windows 7/8
- Partially supported
- Some modern Windows features may not work
- Update to Windows 10 recommended

#### Linux/macOS
- Not officially supported
- GUI automation may work with modifications
- System management features are Windows-specific

## Configuration

### Basic Configuration

Edit `config.yaml`:

```yaml
agent:
  auto_continuation: true  # Enable auto-continuation
  max_retries: 3          # Retry failed tasks 3 times

memory:
  enabled: true           # Enable memory system

logging:
  level: "INFO"          # Change to "DEBUG" for more details
```

### Advanced Configuration

See `config.yaml` for all available options:
- AI model selection
- GUI automation settings
- Memory configuration
- System access permissions
- Self-modification options

## Verification

To verify everything is working:

```bash
# Run all tests
pytest tests/ -v --cov=src

# Run examples
python examples.py

# Check logs
type logs\agent.log
```

## Next Steps

1. Read the [README.md](README.md) for usage examples
2. Review [examples.py](examples.py) for code samples
3. Try creating your own commands
4. Explore the plugin system
5. Configure for your specific needs

## Getting Help

If you're still having issues:

1. Check the logs in `logs/agent.log`
2. Enable DEBUG logging in `config.yaml`
3. Review error messages carefully
4. Open an issue on GitHub with:
   - Your Python version
   - Your Windows version
   - Error messages
   - Steps to reproduce

## Uninstallation

To completely remove Cosik:

1. Deactivate virtual environment:
```bash
deactivate
```

2. Delete the Cosik folder:
```bash
cd ..
rmdir /s Cosik
```

3. (Optional) Remove Python packages:
```bash
pip uninstall -r requirements.txt -y
```
