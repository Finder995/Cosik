# Cosik AI Agent

> An advanced desktop AI agent that leverages existing AI models (GPT, Gemini, Llama) for desktop automation, GUI control, and program/game creation.

## 🎯 Vision

Cosik is designed to be a powerful desktop AI assistant that:
- **Uses ready-made AI models** (OpenAI GPT, Google Gemini, Meta Llama, Anthropic Claude)
- **Automates desktop work** in graphical environments (Windows 10+)
- **Creates programs and games** through AI-powered code generation
- **Handles applications** with intelligent GUI automation
- **Understands natural language** (Polish and English)

## ✨ Key Features

### 🤖 Multi-Model AI Integration
- **OpenAI**: GPT-4 Turbo, GPT-4 Vision, GPT-3.5 Turbo, DALL-E 3
- **Google**: Gemini Ultra/Pro/Nano, Gemini Vision
- **Meta**: Llama 2/3, Code Llama (local or API)
- **Anthropic**: Claude 3 Opus/Sonnet/Haiku
- **Open Source**: Mistral, Phi-2, Vicuna, and more
- Auto-routing and fallback chains for reliability
- Cost optimization through intelligent model selection
- Local deployment option for privacy

### 🖥️ Desktop Automation
- AI-guided GUI navigation and control
- Self-healing UI automation that adapts to interface changes
- Multi-window and multi-application management
- Vision AI for screen understanding and element detection
- Application integration (Office, browsers, IDEs, games)
- Natural language to GUI actions

### 💻 Code Generation
- **Languages**: Python, JavaScript, C#, C++, HTML/CSS, SQL
- Complete project scaffolding from descriptions
- Code refactoring and optimization
- Automated testing and documentation
- Bug fixing through AI analysis
- Design pattern implementation

### 🎮 Game Development
- **Unity Integration**: Scene creation, GameObject manipulation, C# scripting
- **Unreal Engine**: Blueprint generation, C++ code, level design
- **Godot**: GDScript generation, scene management
- Game mechanics generation (player controller, AI, inventory, combat)
- AI-powered asset generation (sprites, textures, sounds)
- Game bot framework for automation

### 🔄 Workflow Automation
- Intelligent task decomposition and planning
- Workflow recording and playback
- Multi-step automation with dependencies
- Error recovery and retry strategies
- Pattern learning from user behavior

### 🧠 Advanced Capabilities
- Long-term memory with vector database
- Context-aware decision making
- Multi-modal reasoning (text + vision + audio)
- Voice recognition and control
- Plugin ecosystem for extensibility

## 📋 Current Status

The agent currently includes:
- ✅ Basic NLP and language processing
- ✅ GUI automation framework (PyAutoGUI, pywinauto)
- ✅ Computer vision (OpenCV, OCR)
- ✅ Basic AI integration (OpenAI, Anthropic)
- ✅ Memory system (SQLite)
- ✅ Task execution and workflow orchestration
- ✅ Plugin system with multiple plugins
- ✅ REST API server
- ✅ Voice recognition

## 🚀 Roadmap

### Phase 1: Multi-Model AI Integration (1-2 months)
- Complete integration with GPT, Gemini, Llama, Claude
- Implement model routing and fallback
- Add vision model support
- Optimize prompting strategies

### Phase 2: Desktop Automation (1-3 months)
- AI-guided GUI navigation
- Self-healing automation
- Advanced screen analysis
- Application and game integration

### Phase 3: Code & Game Creation (2-4 months)
- Code generation for multiple languages
- Unity and Unreal Engine integration
- Game mechanics generation
- AI-powered asset creation

### Phase 4: Workflow & Productivity (3-5 months)
- Intelligent task automation
- Productivity tools
- Data processing and analysis
- Communication automation

### Phase 5: Advanced Features (4-6 months)
- Performance optimization
- Advanced learning and adaptation
- Multi-step reasoning
- Team collaboration features

### Phase 6: Platform Extension (6-12 months)
- Cross-platform support (macOS, Linux)
- Plugin marketplace
- External integrations
- Developer tools and SDKs

## 🛠️ Technology Stack

**AI Models & Frameworks:**
- OpenAI GPT, Google Gemini, Meta Llama, Anthropic Claude
- LangChain, LlamaIndex, AutoGen
- Ollama, llama.cpp for local deployment
- LiteLLM for unified API

**Desktop Automation:**
- PyAutoGUI, pywinauto for Windows automation
- OpenCV, Tesseract for computer vision
- Playwright/Selenium for browser automation

**Game Engines:**
- Unity (C#), Unreal Engine (C++/Blueprints), Godot (GDScript)

**Development:**
- Python 3.8+
- FastAPI for REST API
- SQLite + Vector DB for memory
- Docker for containerization

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Finder995/Cosik.git
cd Cosik

# Install dependencies
pip install -r requirements.txt

# Configure API keys (copy and edit)
cp .env.example .env

# Run the agent
python main.py
```

## 💡 Usage Examples

```python
# Simple command
python main.py --command "otwórz notepad i napisz Hello World"

# Interactive mode
python main.py --interactive

# Generate a Python script
python main.py --command "stwórz skrypt Python do sortowania plików"

# Create a simple game
python main.py --command "stwórz prostą grę platformową w Unity"
```

## 📖 Documentation

- [AGENT_DOCUMENTATION.txt](AGENT_DOCUMENTATION.txt) - Complete feature documentation (Polish)
- [DEVELOPMENT_PLAN.txt](DEVELOPMENT_PLAN.txt) - Detailed development roadmap (Polish)
- [config.yaml](config.yaml) - Configuration reference

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub**: https://github.com/Finder995/Cosik
- **Issues**: https://github.com/Finder995/Cosik/issues

## 🙏 Acknowledgments

This project leverages amazing AI models and tools from:
- OpenAI (GPT, DALL-E, Whisper)
- Google (Gemini)
- Meta (Llama)
- Anthropic (Claude)
- And many open source contributors

---

**Note**: This is an active development project. Features marked as "PLANOWANE" (planned) in documentation are under development.
