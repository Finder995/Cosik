# Cosik AI Agent

**Inteligentny agent AI dla Windows 10 z obsługą GUI i automatyzacją zadań**

Cosik to zaawansowany agent AI zaprojektowany do obsługi systemu Windows 10 oraz aplikacji z interfejsem graficznym. Agent rozumie naturalny język, automatycznie kontynuuje swoją pracę i posiada zdolność do samo-modyfikacji.

## Funkcjonalności

### 🧠 Rozumienie Języka Naturalnego
- Parsowanie poleceń w języku polskim i angielskim
- Automatyczne rozpoznawanie intencji i parametrów
- Obsługa złożonych planów wieloetapowych

### 🖥️ Automatyzacja GUI
- Kontrola myszy i klawiatury
- Rozpoznawanie elementów na ekranie
- Zarządzanie oknami aplikacji
- Wykonywanie kliknięć, wpisywanie tekstu
- Robienie zrzutów ekranu

### 🔄 Auto-kontynuacja
- Automatyczne kontynuowanie rozpoczętych zadań
- Pamięć stanu i kontekstu
- System ponawiania nieudanych operacji
- Zarządzanie kolejką zadań

### 💾 Pamięć i Świadomość
- Trwała pamięć interakcji
- Baza danych historii zadań
- Kontekst wcześniejszych działań
- Analiza błędów i uczenie się

### 📁 Operacje na Plikach
- Czytanie, pisanie i modyfikowanie plików
- Automatyczne tworzenie kopii zapasowych
- Obsługa wielu formatów
- Zarządzanie katalogami

### ⚙️ Dostęp do Systemu
- Dostęp do rejestru Windows
- Wykonywanie poleceń systemowych
- Skrypty PowerShell
- Zarządzanie procesami

### 🔧 Samo-modyfikacja
- Możliwość modyfikacji własnego kodu
- Dynamiczne ładowanie pluginów
- Aktualizacja konfiguracji
- System backupów przed zmianami

## Instalacja

### Wymagania
- Python 3.8 lub nowszy
- Windows 10
- Prawa administratora (opcjonalnie, dla niektórych funkcji)

### Kroki instalacji

1. Sklonuj repozytorium:
```bash
git clone https://github.com/Finder995/Cosik.git
cd Cosik
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. (Opcjonalnie) Skonfiguruj plik `.env` z kluczami API:
```bash
OPENAI_API_KEY=twoj_klucz_api
```

4. Uruchom agenta:
```bash
python main.py
```

## Użycie

### Tryb Interaktywny

Uruchom agenta w trybie interaktywnym:
```bash
python main.py --interactive
```

Następnie możesz wpisywać polecenia w języku naturalnym:
```
Cosik> otwórz notatnik
Cosik> wpisz "Hello World"
Cosik> zapisz plik jako test.txt
Cosik> zrób screenshot
```

### Pojedyncze Polecenie

Wykonaj pojedyncze polecenie:
```bash
python main.py --command "otwórz Chrome i przejdź do Google"
```

### Przykładowe Komendy

**Otwarcie aplikacji:**
```
otwórz notepad
uruchom calculator
włącz Chrome
```

**Operacje na plikach:**
```
przeczytaj plik data.txt
zapisz do pliku output.txt
modyfikuj config.yaml
```

**Automatyzacja GUI:**
```
kliknij przycisk OK
wpisz "mój tekst"
przesuń mysz do 500, 300
zrób screenshot
```

**Polecenia systemowe:**
```
wykonaj polecenie ipconfig
zmień ustawienie głośności
znajdź plik document.pdf
```

## Konfiguracja

Edytuj plik `config.yaml` aby dostosować zachowanie agenta:

```yaml
agent:
  auto_continuation: true  # Auto-kontynuacja
  max_retries: 3          # Maksymalna liczba prób

memory:
  enabled: true           # Włącz pamięć
  max_history: 1000      # Maksymalna historia

gui:
  confidence_threshold: 0.8  # Próg pewności dla rozpoznawania
  failsafe: true            # Bezpieczne przerwanie

self_modification:
  enabled: true              # Włącz samo-modyfikację
  require_confirmation: false # Wymagaj potwierdzenia
```

## Architektura

```
Cosik/
├── main.py                 # Główny plik agenta
├── config.yaml            # Konfiguracja
├── requirements.txt       # Zależności
├── src/
│   ├── nlp/              # Przetwarzanie języka naturalnego
│   │   └── language_processor.py
│   ├── automation/       # Automatyzacja GUI
│   │   └── gui_controller.py
│   ├── memory/           # System pamięci
│   │   └── memory_manager.py
│   ├── tasks/            # Wykonywanie zadań
│   │   └── task_executor.py
│   ├── system/           # Operacje systemowe
│   │   └── system_manager.py
│   ├── config/           # Zarządzanie konfiguracją
│   │   └── config_loader.py
│   └── plugins/          # Pluginy
│       └── example_plugin.py
├── data/                 # Dane i pamięć
│   ├── memory/
│   ├── vector_store/
│   └── backups/
└── logs/                 # Logi
```

## Bezpieczeństwo

### Tryb Bezpieczny

Włącz tryb bezpieczny w `config.yaml`:
```yaml
system:
  safe_mode: true
```

W trybie bezpiecznym:
- Zablokowane usuwanie plików
- Zablokowane modyfikacje rejestru
- Zablokowane wykonywanie PowerShell
- Wymagane potwierdzenie dla wrażliwych operacji

### Kopie Zapasowe

Agent automatycznie tworzy kopie zapasowe przed:
- Modyfikacją plików
- Samo-modyfikacją
- Zmianami w konfiguracji

## Rozwój i Rozszerzenia

### Tworzenie Własnych Pluginów

1. Utwórz nowy plik w `src/plugins/`:
```python
class MojPlugin:
    def __init__(self, agent):
        self.agent = agent
    
    async def execute(self, command, **kwargs):
        # Twoja logika
        pass

PLUGIN_INFO = {
    'name': 'moj_plugin',
    'version': '1.0.0',
    'class': MojPlugin
}
```

2. Agent automatycznie załaduje plugin przy starcie

### Dodawanie Nowych Intencji

Edytuj `src/nlp/language_processor.py`:
```python
self.intent_patterns = {
    'moja_intencja': [
        r'moje\s+polecenie\s+(.+)',
    ]
}
```

## Licencja

MIT License - szczegóły w pliku LICENSE

## Autor

Finder995

## Wsparcie

W razie problemów lub pytań:
- Otwórz issue na GitHub
- Sprawdź logi w `logs/agent.log`
- Włącz tryb DEBUG w konfiguracji

## Roadmap

- [ ] Integracja z GPT-4 dla zaawansowanego planowania
- [ ] Obsługa obrazu (Computer Vision)
- [ ] Harmonogram zadań
- [ ] Web dashboard
- [ ] API REST
- [ ] Wsparcie dla macOS i Linux
- [ ] Zaawansowane uczenie maszynowe
- [ ] Rozszerzony system pluginów

## Przykłady Użycia

### Automatyzacja Raportów
```python
# Agent automatycznie:
# 1. Otwiera Excel
# 2. Wczytuje dane
# 3. Generuje wykresy
# 4. Zapisuje raport
# 5. Wysyła email
```

### Zarządzanie Systemem
```python
# Agent może:
# - Monitorować zasoby systemu
# - Zamykać nieużywane aplikacje
# - Organizować pliki
# - Tworzyć kopie zapasowe
```

### Automatyzacja Testów
```python
# Agent może testować aplikacje:
# - Klikać przyciski
# - Wypełniać formularze
# - Weryfikować wyniki
# - Raportować błędy
```