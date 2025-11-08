# Cosik AI Agent - Changelog

Wszystkie istotne zmiany w projekcie Cosik AI Agent.

## [2.0.0] - 2024 (W trakcie rozwoju)

### ✨ Nowe Funkcje (New Features)

#### 1. **AI Engine - Zaawansowana Integracja AI**
- **Plik:** `src/ai/ai_engine.py`
- **Opis:** Pełna integracja z OpenAI GPT i Anthropic Claude
- **Funkcjonalności:**
  - Zaawansowane parsowanie poleceń w języku naturalnym
  - AI-powered planowanie złożonych zadań
  - Automatyczna analiza błędów i sugestie napraw
  - Kontekstowe rozumienie poleceń
- **API Methods:**
  - `parse_complex_command()` - Parsowanie złożonych poleceń
  - `create_task_plan()` - Tworzenie planu wykonania zadań
  - `analyze_error()` - Analiza błędów i sugestie
- **Konfiguracja:**
  ```yaml
  ai:
    provider: "openai"  # lub "anthropic"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
  ```
- **Wymagania:**
  - Klucz API (OPENAI_API_KEY lub ANTHROPIC_API_KEY w .env)
  - Biblioteki: openai>=1.0.0, anthropic>=0.7.0

#### 2. **Computer Vision - OCR i Rozpoznawanie Obrazów**
- **Plik:** `src/vision/computer_vision.py`
- **Opis:** Zaawansowane możliwości wizji komputerowej
- **Funkcjonalności:**
  - OCR (Optical Character Recognition) - ekstrakcja tekstu z ekranu
  - Template matching - znajdowanie obrazów na ekranie
  - Wykrywanie elementów UI
  - Wyszukiwanie tekstu na ekranie z lokalizacją
  - Wykrywanie wszystkich instancji obrazu
- **API Methods:**
  - `extract_text_from_screen(region)` - OCR z ekranu
  - `extract_text_from_image(path, language)` - OCR z pliku
  - `find_text_on_screen(text, region)` - Znajdź tekst i lokalizację
  - `find_image_on_screen(template, confidence)` - Template matching
  - `find_all_matches(template, confidence)` - Wszystkie dopasowania
  - `detect_ui_elements()` - Automatyczna detekcja UI
- **Przykłady:**
  ```python
  # Znajdź i kliknij na tekst
  await gui.click_text("OK")
  
  # Znajdź i kliknij na obrazek
  await gui.click_image("button_template.png")
  
  # Czekaj aż pojawi się tekst
  await gui.wait_for_text("Welcome", timeout=30)
  
  # OCR z regionu ekranu
  result = await vision.extract_text_from_screen(region=(0, 0, 800, 600))
  print(result['text'])
  
  # Znajdź wszystkie przyciski OK
  result = await vision.find_all_matches("ok_button.png")
  for match in result['matches']:
      print(f"Found at ({match['x']}, {match['y']}) confidence: {match['confidence']}")
  ```
- **Wymagania:**
  - OpenCV: opencv-python>=4.8.0
  - Tesseract OCR: pytesseract>=0.3.10 + Tesseract engine
  - NumPy: numpy>=1.24.0
  - scikit-learn (opcjonalnie): dla analizy kolorów

#### 3. **Plugin Manager - System Zarządzania Pluginami**
- **Plik:** `src/plugins/plugin_manager.py`
- **Opis:** Zaawansowany system zarządzania pluginami z auto-discovery
- **Funkcjonalności:**
  - Automatyczne wykrywanie pluginów
  - Dynamiczne ładowanie/wyładowywanie
  - Zarządzanie cyklem życia pluginów
  - Metadata i capabilities discovery
  - Hot-reload dla development
- **API Methods:**
  - `discover_plugins()` - Wykryj dostępne pluginy
  - `load_plugin(name)` - Załaduj plugin
  - `load_all_plugins()` - Załaduj wszystkie pluginy
  - `unload_plugin(name)` - Wyładuj plugin
  - `execute_plugin(name, command, **kwargs)` - Wykonaj komendę pluginu
  - `get_plugin_capabilities(name)` - Pobierz możliwości pluginu
  - `reload_plugin(name)` - Przeładuj plugin
- **Użycie:**
  ```python
  # Automatyczne ładowanie wszystkich pluginów
  plugin_manager.load_all_plugins()
  
  # Wykonanie komendy na pluginie
  result = await plugin_manager.execute_plugin(
      'scheduler', 
      'schedule',
      task={'intent': 'open_application', 'parameters': {'application': 'notepad'}},
      schedule_time='10:30'
  )
  
  # Lista załadowanych pluginów
  plugins = plugin_manager.list_plugins()
  ```

#### 4. **Scheduler Plugin - Harmonogram Zadań**
- **Plik:** `src/plugins/scheduler_plugin.py`
- **Opis:** Plugin do planowania zadań na określone czasy
- **Komendy:**
  - `schedule` - Zaplanuj nowe zadanie
  - `list` - Lista zaplanowanych zadań
  - `cancel` - Anuluj zadanie
  - `start` - Uruchom scheduler
  - `stop` - Zatrzymaj scheduler
- **Możliwości:**
  - Planowanie na konkretny czas (np. "10:30")
  - Planowanie interwałowe (co X minut/godzin/dni)
  - Pełny datetime (np. "2024-01-01 10:30")
- **Przykłady:**
  ```python
  # Zaplanuj zadanie codziennie o 10:30
  await plugin_manager.execute_plugin(
      'scheduler',
      'schedule',
      task={'intent': 'take_screenshot'},
      schedule_time='10:30'
  )
  
  # Zaplanuj zadanie co 10 minut
  await plugin_manager.execute_plugin(
      'scheduler',
      'schedule',
      task={'intent': 'check_email'},
      interval='every 10 minutes'
  )
  ```

#### 5. **Web Scraper Plugin - Scraping Stron Web**
- **Plik:** `src/plugins/web_scraper_plugin.py`
- **Opis:** Plugin do pobierania i ekstrakcji danych ze stron internetowych
- **Komendy:**
  - `fetch` - Pobierz zawartość strony
  - `extract` - Wyciągnij dane (CSS selectors, XPath)
  - `download` - Pobierz plik
  - `search` - Wyszukaj elementy na stronie
- **Funkcjonalności:**
  - Pobieranie HTML ze stron
  - Ekstrakcja danych za pomocą CSS selectors
  - Wsparcie XPath (wymaga lxml)
  - Pobieranie plików
  - Wyszukiwanie elementów po tagach, klasach, ID, tekście
- **Przykłady:**
  ```python
  # Pobierz stronę
  result = await plugin_manager.execute_plugin(
      'web_scraper',
      'fetch',
      url='https://example.com'
  )
  
  # Wyciągnij wszystkie linki
  result = await plugin_manager.execute_plugin(
      'web_scraper',
      'extract',
      url='https://example.com',
      selector='a'
  )
  
  # Pobierz plik
  result = await plugin_manager.execute_plugin(
      'web_scraper',
      'download',
      url='https://example.com/file.pdf',
      save_path='./downloads/file.pdf'
  )
  ```
- **Wymagania:**
  - requests (HTTP client)
  - beautifulsoup4 (HTML parsing)
  - lxml (opcjonalnie, dla XPath)

### 🔧 Ulepszenia (Improvements)

#### Language Processor
- **Zmieniony:** `src/nlp/language_processor.py`
- **Ulepszenia:**
  - Integracja z AI Engine dla złożonych poleceń
  - Kontekstowe parsowanie z wykorzystaniem historii
  - Fallback na AI gdy pattern matching zawiedzie
- **Nowy parametr:** `ai_engine` w konstruktorze
- **Ulepszona metoda:** `_ai_parse()` teraz wykorzystuje prawdziwy AI

#### GUI Controller
- **Zmieniony:** `src/automation/gui_controller.py`
- **Ulepszenia:**
  - Integracja z Computer Vision module
  - Nowe metody wykorzystujące OCR
  - Click na tekst przez OCR
  - Click na obraz przez template matching
  - Inteligentne czekanie na teksty i obrazy
- **Nowy parametr:** `vision` w konstruktorze
- **Nowe metody:**
  - `click_text(text, region)` - Kliknij na tekst (OCR)
  - `click_image(image_path, confidence)` - Kliknij na obraz (template matching)
  - `wait_for_text(text, timeout, region)` - Czekaj na pojawienie się tekstu
  - `wait_for_image(image_path, timeout)` - Czekaj na pojawienie się obrazu

#### Task Executor
- **Zmieniony:** `src/tasks/task_executor.py`
- **Ulepszenia:**
  - Integracja z AI Engine dla planowania zadań
  - Automatyczne rozwijanie complex_task na kroki
  - AI-powered analiza błędów
- **Nowy parametr:** `ai_engine` w konstruktorze
- **Ulepszona metoda:** `_complex_task()` tworzy plany z AI

#### Main Agent
- **Zmieniony:** `main.py`
- **Ulepszenia:**
  - Inicjalizacja AI Engine
  - Inicjalizacja Computer Vision
  - Automatyczne ładowanie pluginów przy starcie
  - Lepsza orchestracja komponentów
- **Nowe komponenty:**
  - `self.ai_engine` - AI Engine instance
  - `self.vision` - Computer Vision instance
  - `self.plugin_manager` - Plugin Manager instance

### 📊 Statystyki Kodu

**Nowe Pliki:**
- `src/ai/__init__.py` (5 linii)
- `src/ai/ai_engine.py` (450 linii)
- `src/vision/__init__.py` (5 linii)
- `src/vision/computer_vision.py` (380 linii)
- `src/plugins/plugin_manager.py` (295 linii)
- `src/plugins/scheduler_plugin.py` (250 linii)
- `src/plugins/web_scraper_plugin.py` (340 linii)

**Zmodyfikowane Pliki:**
- `main.py` (+12 linii)
- `src/nlp/language_processor.py` (+25 linii)
- `src/automation/gui_controller.py` (+125 linii)
- `src/tasks/task_executor.py` (+35 linii)
- `requirements.txt` (+6 dependencies)

**Łącznie:**
- **Dodane:** ~2,100 linii kodu
- **Nowe moduły:** 7
- **Nowe pluginy:** 2
- **Ulepszonych komponentów:** 4

### 🔌 Pluginy - Struktura

Każdy plugin musi zawierać:

```python
class MyPlugin:
    def __init__(self, config):
        """Inicjalizacja pluginu"""
        pass
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Wykonaj komendę pluginu"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Zwróć listę dostępnych komend"""
        return ['command1', 'command2']
    
    def cleanup(self):
        """Cleanup przy wyładowywaniu"""
        pass

PLUGIN_INFO = {
    'name': 'my_plugin',
    'version': '1.0.0',
    'class': MyPlugin,
    'description': 'Opis pluginu',
    'author': 'Autor'
}
```

### 🚀 Przykłady Użycia

#### Użycie AI Engine

```python
# Parsowanie złożonego polecenia
from src.ai.ai_engine import AIEngine

ai = AIEngine(config)
result = await ai.parse_complex_command(
    "otwórz Chrome, przejdź do Google i wyszukaj Python tutorials"
)

# Tworzenie planu zadań
plan = await ai.create_task_plan(
    "Napisz raport kwartalny i wyślij go emailem do managera",
    context={'current_date': '2024-01-15'}
)

# Analiza błędu
analysis = await ai.analyze_error(
    task={'intent': 'open_application', 'parameters': {'application': 'notepad'}},
    error='Application not found',
    history=[...]
)
```

#### Użycie Plugin Manager

```python
from src.plugins.plugin_manager import PluginManager

# Inicjalizacja
pm = PluginManager(config)
pm.load_all_plugins()

# Lista pluginów
plugins = pm.list_plugins()
for p in plugins:
    print(f"{p['name']} v{p['version']}: {p['description']}")

# Wykonanie komendy
result = await pm.execute_plugin('scheduler', 'list')
print(f"Scheduled jobs: {result['count']}")

# Capabilities
caps = pm.get_plugin_capabilities('web_scraper')
print(f"Web scraper can: {', '.join(caps)}")
```

#### Kompleksowy Workflow

```python
import asyncio
from main import CosikAgent

async def automation_workflow():
    agent = CosikAgent()
    
    # 1. Zaplanuj codzienne screenshoty
    await agent.plugin_manager.execute_plugin(
        'scheduler',
        'schedule',
        task={'intent': 'take_screenshot'},
        schedule_time='09:00'
    )
    
    # 2. Pobierz dane ze strony
    result = await agent.plugin_manager.execute_plugin(
        'web_scraper',
        'extract',
        url='https://example.com/data',
        selector='.data-table tr'
    )
    
    # 3. Zapisz do pliku
    await agent.run("zapisz dane do raport.txt")
    
    # 4. AI zaplanuje złożone zadanie
    await agent.run("przeanalizuj dane i stwórz wykres")

asyncio.run(automation_workflow())
```

### 📝 Konfiguracja

#### Nowe Opcje w config.yaml

```yaml
# AI Configuration (nowe)
ai:
  provider: "openai"  # "openai" lub "anthropic"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

# Plugins (nowe)
plugins:
  auto_load: true
  plugins_dir: "./src/plugins"
  enabled:
    - scheduler
    - web_scraper
    - example_plugin
```

#### Zmienne Środowiskowe (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### 🎯 Roadmap - Następne Kroki

**Phase 2: Enhanced Automation (Dalej)**
- [ ] OCR dla rozpoznawania tekstu na ekranie
- [ ] Computer Vision dla lepszej detekcji elementów GUI
- [ ] Smart waiting mechanisms
- [ ] UI element detection improvements

**Phase 3: Advanced Features**
- [ ] REST API dla zdalnego sterowania
- [ ] Web dashboard
- [ ] Voice command support
- [ ] Multi-agent coordination

**Phase 4: More Plugins**
- [ ] Email plugin (send/receive)
- [ ] Database plugin (SQL operations)
- [ ] Cloud storage plugin (Google Drive, OneDrive)
- [ ] Social media plugin (posts, monitoring)

### 🐛 Znane Problemy

1. **AI Engine wymaga kluczy API** - Bez kluczy AI engine działa w trybie fallback
2. **Pluginy wymagają dodatkowych bibliotek** - requests, beautifulsoup4, lxml, schedule
3. **Windows-only** - Obecnie tylko Windows 10/11

### 💡 Breaking Changes

**Brak breaking changes** - Wszystkie zmiany są wstecznie kompatybilne.

Istniejący kod będzie działał bez modyfikacji. Nowe funkcje są opcjonalne.

### 🔐 Bezpieczeństwo

- AI Engine nie wysyła danych bez zgody użytkownika
- Web scraper respektuje robots.txt (można wyłączyć)
- Pluginy działają w izolacji
- Wszystkie operacje są logowane

### 📚 Dokumentacja

**Zmniejszona do jednego pliku (zgodnie z wymaganiami):**
- Cała dokumentacja zmian w tym pliku (CHANGELOG.md)
- Pozostałe pliki dokumentacji (README.md, API.md, etc.) pozostają niezmienione

---

## [1.0.0] - 2024 (Poprzednia Wersja)

### Podstawowa Implementacja

- Natural Language Processing (Polish & English)
- GUI Automation (pyautogui, pywinauto)
- Memory System (SQLite)
- File Operations
- System Access (Registry, PowerShell)
- Self-modification capabilities
- Basic plugin system

---

**Kontakt:** Finder995
**Licencja:** MIT
**Repository:** https://github.com/Finder995/Cosik
