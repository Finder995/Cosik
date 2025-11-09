# Cosik AI Agent

> Zaawansowany desktopowy agent AI wykorzystujący gotowe modele AI (GPT, Gemini, Llama) do automatyzacji pulpitu, kontroli GUI oraz tworzenia programów i gier.

## 🎯 Wizja

Cosik został zaprojektowany jako potężny asystent AI do pracy na komputerze:
- **Wykorzystuje gotowe modele AI** (OpenAI GPT, Google Gemini, Meta Llama, Anthropic Claude)
- **Automatyzuje pracę na pulpicie** w środowisku graficznym (Windows 10+)
- **Tworzy programy i gry** poprzez generowanie kodu przez AI
- **Obsługuje aplikacje** z inteligentną automatyzacją GUI
- **Rozumie język naturalny** (polski i angielski)

## ✨ Główne Funkcje

### 🤖 Integracja z Wieloma Modelami AI
- **OpenAI**: GPT-4 Turbo, GPT-4 Vision, GPT-3.5 Turbo, DALL-E 3
- **Google**: Gemini Ultra/Pro/Nano, Gemini Vision
- **Meta**: Llama 2/3, Code Llama (lokalnie lub API)
- **Anthropic**: Claude 3 Opus/Sonnet/Haiku
- **Open Source**: Mistral, Phi-2, Vicuna i inne
- Auto-routing i łańcuchy fallback dla niezawodności
- Optymalizacja kosztów poprzez inteligentny wybór modelu
- Opcja lokalnego uruchamiania dla prywatności

### 🖥️ Automatyzacja Pulpitu
- Nawigacja i kontrola GUI kierowana przez AI
- Samoleczące się automatyzacje dostosowujące się do zmian interfejsu
- Zarządzanie wieloma oknami i aplikacjami
- Vision AI do rozumienia ekranu i wykrywania elementów
- Integracja z aplikacjami (Office, przeglądarki, IDE, gry)
- Tłumaczenie języka naturalnego na akcje GUI

### 💻 Generowanie Kodu
- **Języki**: Python, JavaScript, C#, C++, HTML/CSS, SQL
- Pełne tworzenie struktury projektów z opisów
- Refaktoryzacja i optymalizacja kodu
- Automatyczne testowanie i dokumentacja
- Naprawianie błędów poprzez analizę AI
- Implementacja wzorców projektowych

### 🎮 Tworzenie Gier
- **Integracja Unity**: Tworzenie scen, manipulacja GameObjects, skrypty C#
- **Unreal Engine**: Generowanie Blueprintów, kod C++, design poziomów
- **Godot**: Generowanie GDScript, zarządzanie scenami
- Generowanie mechanik gry (kontroler gracza, AI, ekwipunek, walka)
- Generowanie zasobów przez AI (sprites, tekstury, dźwięki)
- Framework do botów do gier

### 🔄 Automatyzacja Workflow
- Inteligentna dekompozycja i planowanie zadań
- Nagrywanie i odtwarzanie workflow
- Automatyzacja wieloetapowa z zależnościami
- Odzyskiwanie po błędach i strategie retry
- Uczenie się wzorców z zachowania użytkownika

### 🧠 Zaawansowane Możliwości
- Długoterminowa pamięć z wektorową bazą danych
- Podejmowanie decyzji świadome kontekstu
- Multimodalne rozumowanie (tekst + obraz + dźwięk)
- Rozpoznawanie i kontrola głosowa
- Ekosystem wtyczek dla rozszerzalności

## 📋 Obecny Status

Agent obecnie zawiera:
- ✅ Podstawowe NLP i przetwarzanie języka
- ✅ Framework automatyzacji GUI (PyAutoGUI, pywinauto)
- ✅ Wizja komputerowa (OpenCV, OCR)
- ✅ Podstawowa integracja AI (OpenAI, Anthropic)
- ✅ System pamięci (SQLite)
- ✅ Wykonywanie zadań i orkiestracja workflow
- ✅ System wtyczek z wieloma wtyczkami
- ✅ Serwer REST API
- ✅ Rozpoznawanie głosu

## 🚀 Mapa Drogowa

### Faza 1: Integracja Wielu Modeli AI (1-2 miesiące)
- Pełna integracja z GPT, Gemini, Llama, Claude
- Implementacja routingu i fallbacku modeli
- Dodanie wsparcia dla modeli vision
- Optymalizacja strategii promptowania

### Faza 2: Automatyzacja Pulpitu (1-3 miesiące)
- Nawigacja GUI kierowana przez AI
- Samoleczące się automatyzacje
- Zaawansowana analiza ekranu
- Integracja z aplikacjami i grami

### Faza 3: Tworzenie Kodu i Gier (2-4 miesiące)
- Generowanie kodu dla wielu języków
- Integracja Unity i Unreal Engine
- Generowanie mechanik gry
- Tworzenie zasobów przez AI

### Faza 4: Workflow i Produktywność (3-5 miesiące)
- Inteligentna automatyzacja zadań
- Narzędzia produktywności
- Przetwarzanie i analiza danych
- Automatyzacja komunikacji

### Faza 5: Zaawansowane Funkcje (4-6 miesiące)
- Optymalizacja wydajności
- Zaawansowane uczenie i adaptacja
- Rozumowanie wieloetapowe
- Funkcje współpracy zespołowej

### Faza 6: Rozszerzenie Platformy (6-12 miesięcy)
- Wsparcie cross-platform (macOS, Linux)
- Marketplace wtyczek
- Integracje zewnętrzne
- Narzędzia i SDK dla developerów

## 🛠️ Stos Technologiczny

**Modele i Frameworki AI:**
- OpenAI GPT, Google Gemini, Meta Llama, Anthropic Claude
- LangChain, LlamaIndex, AutoGen
- Ollama, llama.cpp dla lokalnego wdrożenia
- LiteLLM dla zunifikowanego API

**Automatyzacja Pulpitu:**
- PyAutoGUI, pywinauto dla automatyzacji Windows
- OpenCV, Tesseract dla wizji komputerowej
- Playwright/Selenium dla automatyzacji przeglądarki

**Silniki Gier:**
- Unity (C#), Unreal Engine (C++/Blueprints), Godot (GDScript)

**Development:**
- Python 3.8+
- FastAPI dla REST API
- SQLite + Vector DB dla pamięci
- Docker dla konteneryzacji

## 📦 Instalacja

```bash
# Sklonuj repozytorium
git clone https://github.com/Finder995/Cosik.git
cd Cosik

# Zainstaluj zależności
pip install -r requirements.txt

# Skonfiguruj klucze API (skopiuj i edytuj)
cp .env.example .env

# Uruchom agenta
python main.py
```

## 💡 Przykłady Użycia

```python
# Prosta komenda
python main.py --command "otwórz notepad i napisz Hello World"

# Tryb interaktywny
python main.py --interactive

# Wygeneruj skrypt Python
python main.py --command "stwórz skrypt Python do sortowania plików"

# Stwórz prostą grę
python main.py --command "stwórz prostą grę platformową w Unity"
```

## 📖 Dokumentacja

- [AGENT_DOCUMENTATION.txt](AGENT_DOCUMENTATION.txt) - Pełna dokumentacja funkcji
- [DEVELOPMENT_PLAN.txt](DEVELOPMENT_PLAN.txt) - Szczegółowa mapa rozwoju
- [config.yaml](config.yaml) - Referencja konfiguracji

## 🤝 Wkład w Projekt

Wkłady są mile widziane! Prosimy o przeczytanie naszych wytycznych dla kontrybutorów.

## 📄 Licencja

Zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 🔗 Linki

- **GitHub**: https://github.com/Finder995/Cosik
- **Issues**: https://github.com/Finder995/Cosik/issues

## 🙏 Podziękowania

Ten projekt wykorzystuje niesamowite modele AI i narzędzia od:
- OpenAI (GPT, DALL-E, Whisper)
- Google (Gemini)
- Meta (Llama)
- Anthropic (Claude)
- I wielu kontrybutorów open source

---

**Uwaga**: To jest aktywnie rozwijany projekt. Funkcje oznaczone jako "PLANOWANE" w dokumentacji są w trakcie rozwoju.
