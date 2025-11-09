# Cosik AI Agent - Quick Start Guide for New Systems

## 🚀 Nowe Zaawansowane Systemy (v2.2.0)

Ten przewodnik pokazuje jak korzystać z nowych zaawansowanych systemów dodanych do Cosik AI Agent.

### 📦 Instalacja

```bash
# Podstawowe zależności
pip install loguru pyyaml python-dotenv psutil

# Opcjonalne (dla REST API i CLI)
pip install fastapi uvicorn aiohttp prompt-toolkit
```

### 🎯 Szybki Start

#### 1. Advanced Task Queue

Kolejka zadań z priorytetami i zależnościami:

```python
from src.tasks.task_queue import AdvancedTaskQueue, Task, TaskPriority

# Utwórz kolejkę
queue = AdvancedTaskQueue(max_concurrent=5)

# Dodaj zadanie z priorytetem
task = Task(
    id="backup",
    intent="backup_files",
    priority=TaskPriority.HIGH,
    timeout=60.0
)
await queue.add_task(task)

# Zadanie z zależnościami
task2 = Task(
    id="cleanup",
    intent="cleanup",
    dependencies=["backup"]  # Czeka na zadanie "backup"
)
await queue.add_task(task2)

# Przetwórz kolejkę
async def execute_task(task):
    print(f"Executing: {task.intent}")
    return {"success": True}

await queue.process_queue(execute_task)
```

#### 2. Error Recovery System

Automatyczne wykrywanie i naprawianie błędów:

```python
from src.system.error_recovery import ErrorRecoverySystem

recovery = ErrorRecoverySystem()

# Zapisz błąd
error = await recovery.record_error(
    "Connection timeout",
    task_info={'intent': 'fetch_data'},
    context={'url': 'example.com'}
)

# Spróbuj naprawić
success = await recovery.attempt_recovery(error)

# Statystyki
stats = recovery.get_error_statistics()
print(f"Recovery rate: {stats['recovery_rate']}")

# Wzorce błędów
patterns = recovery.get_pattern_insights()
for pattern in patterns:
    print(f"{pattern['category']}: {pattern['occurrences']} times")
```

#### 3. Performance Monitor

Monitorowanie wydajności w czasie rzeczywistym:

```python
from src.system.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
await monitor.start_monitoring()

# Mierz operację
async with monitor.measure('file_processing'):
    await process_large_file()

# Statystyki
summary = monitor.get_performance_summary()
print(f"Total operations: {summary['total_operations']}")
print(f"Success rate: {summary['success_rate']}")

# Wąskie gardła
bottlenecks = monitor.identify_bottlenecks()
for bn in bottlenecks:
    print(f"{bn['operation']}: {bn['avg_duration_ms']}ms")

# Eksport raportu
monitor.export_report('./performance.json')
```

#### 4. REST API Server

Zdalne sterowanie agentem:

```python
from src.api.api_server import APIServer

api = APIServer(agent, host="0.0.0.0", port=8000)
print(f"Master Key: {api.master_key}")

# Start serwera (async)
await api.start()

# Lub (blocking)
api.run()
```

Użycie API:
```bash
# Sprawdź status
curl -H "Authorization: Bearer YOUR_KEY" \
     http://localhost:8000/api/status

# Wyślij zadanie
curl -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/tasks \
     -d '{"command": "open notepad"}'
```

#### 5. Command Replay System

Nagrywanie i odtwarzanie sekwencji poleceń:

```python
from src.automation.command_replay import CommandReplaySystem

replay = CommandReplaySystem(agent)

# Nagrywanie
replay.start_recording("backup_workflow")
replay.record("open file manager")
replay.record("copy files to ${backup_path}")
replay.record("create backup archive")
workflow_name = replay.stop_recording()

# Odtwarzanie ze zmiennymi
result = await replay.replay("backup_workflow", variables={
    "backup_path": "D:/Backups/2024-11-09"
})

print(f"Success rate: {result['success_rate']}")

# Lista workflows
workflows = replay.list_workflows()
for wf in workflows:
    print(f"{wf['name']}: {wf['commands_count']} commands")
```

#### 6. Enhanced Interactive CLI

Interaktywna konsola z podpowiedziami:

```python
from src.cli.interactive_cli import run_interactive_cli

# Uruchom CLI
await run_interactive_cli(agent)
```

Komendy CLI:
```
help              - Pomoc
status            - Status agenta
performance       - Metryki wydajności
errors            - Statystyki błędów
queue             - Status kolejki
workflows         - Lista workflow
record <name>     - Nagraj workflow
stop              - Zatrzymaj nagrywanie
replay <name>     - Odtwórz workflow
exit              - Wyjście
```

### 🔧 Pełna Integracja

Przykład użycia wszystkich systemów razem:

```python
import asyncio
from main import CosikAgent
from src.tasks.task_queue import AdvancedTaskQueue
from src.system.error_recovery import ErrorRecoverySystem
from src.system.performance_monitor import PerformanceMonitor
from src.automation.command_replay import CommandReplaySystem

async def main():
    # Stwórz agenta
    agent = CosikAgent()
    
    # Dodaj systemy
    agent.task_queue = AdvancedTaskQueue(max_concurrent=5)
    agent.error_recovery = ErrorRecoverySystem()
    agent.performance_monitor = PerformanceMonitor()
    agent.command_replay = CommandReplaySystem(agent)
    
    # Start monitoring
    await agent.performance_monitor.start_monitoring()
    
    # Użyj systemów
    async with agent.performance_monitor.measure('workflow'):
        try:
            # Wykonaj zadania
            await agent.run("otwórz notepad")
        except Exception as e:
            # Auto recovery
            error = await agent.error_recovery.record_error(str(e), {})
            await agent.error_recovery.attempt_recovery(error)
    
    # Podsumowanie
    print(agent.performance_monitor.get_performance_summary())
    print(agent.error_recovery.get_error_statistics())
    
    await agent.stop()

asyncio.run(main())
```

### 📚 Więcej Przykładów

Zobacz `integration_examples.py` dla kompletnych przykładów użycia.

### 🧪 Testy

```bash
# Uruchom testy
python tests/test_advanced_systems.py

# Lub z pytest
pytest tests/test_advanced_systems.py -v
```

### 📖 Pełna Dokumentacja

Wszystkie szczegóły w **CHANGELOG.md** (skonsolidowana dokumentacja).

### 🎓 Kluczowe Funkcje

| System | Główne Funkcje |
|--------|----------------|
| Task Queue | Priorytety, zależności, równoległość |
| Error Recovery | Auto-klasyfikacja, wzorce, naprawa |
| Performance | Czas wykonania, CPU, pamięć, wąskie gardła |
| REST API | Remote control, WebSocket, webhooks |
| Command Replay | Nagrywanie, szablony, zmienne |
| Interactive CLI | Historia, auto-complete, aliasy |

### 💡 Tips

1. **Graceful Degradation**: Systemy działają niezależnie - brak opcjonalnych zależności nie łamie kodu
2. **Optional Dependencies**: `fastapi`, `prompt-toolkit`, `aiohttp` są opcjonalne
3. **Integration**: Łatwo dodać do istniejącego kodu - patrz `integration_examples.py`
4. **Production Ready**: Wszystkie systemy mają error handling i logging

---

**Autor:** Finder995  
**Wersja:** 2.2.0  
**Data:** 2024-11-09
