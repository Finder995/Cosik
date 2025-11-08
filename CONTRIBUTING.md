# Cosik AI Agent - Contributing Guide

Thank you for your interest in contributing to Cosik AI Agent!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, Windows version)
- Relevant logs from `logs/agent.log`

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature already exists or is planned
- Describe the use case clearly
- Explain how it would benefit users
- Consider implementation complexity

### Contributing Code

1. **Fork the Repository**
   ```bash
   git fork https://github.com/Finder995/Cosik.git
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make Changes**
   - Follow the existing code style
   - Add docstrings for new functions/classes
   - Update tests if needed
   - Update documentation

4. **Test Your Changes**
   ```bash
   pytest tests/ -v
   python -m py_compile src/**/*.py
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add: description of changes"
   git push origin feature/my-new-feature
   ```

6. **Create Pull Request**
   - Describe what changed and why
   - Reference any related issues
   - Ensure all tests pass

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use descriptive variable names

Example:
```python
async def process_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Process a user command.
    
    Args:
        command: The command to process
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with result and status
    """
    # Implementation
    pass
```

### Documentation Style

- Use clear, concise language
- Provide examples for complex features
- Keep README up to date
- Document all public APIs

### Commit Messages

Format: `Type: Brief description`

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Improvement to existing feature
- `Docs:` Documentation changes
- `Test:` Test-related changes
- `Refactor:` Code refactoring

Examples:
- `Add: Support for drag and drop operations`
- `Fix: Memory leak in task executor`
- `Update: Improve NLP accuracy for Polish commands`
- `Docs: Add API documentation for plugins`

## Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Finder995/Cosik.git
   cd Cosik
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install black flake8 mypy  # Development tools
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v --cov=src
   ```

## Project Structure

```
Cosik/
├── main.py              # Entry point
├── src/
│   ├── nlp/            # Natural language processing
│   ├── automation/     # GUI automation
│   ├── memory/         # Memory management
│   ├── tasks/          # Task execution
│   ├── system/         # System operations
│   ├── config/         # Configuration
│   └── plugins/        # Plugin system
├── tests/              # Test suite
├── data/               # Runtime data
└── logs/               # Log files
```

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Use pytest fixtures for setup
- Mock external dependencies
- Aim for 80%+ code coverage

Example:
```python
@pytest.mark.asyncio
async def test_parse_command(nlp):
    """Test command parsing."""
    result = await nlp.parse("open notepad")
    assert result['intent'] == 'open_application'
    assert 'notepad' in result['parameters']['application']
```

### Integration Tests

- Test component interactions
- Use temporary directories for file operations
- Clean up resources after tests

### Manual Testing

Before submitting a PR:
1. Test on clean Windows 10 installation
2. Try common use cases
3. Verify documentation accuracy
4. Check for memory leaks

## Adding New Features

### New Intent

1. Add pattern to `src/nlp/language_processor.py`:
   ```python
   'my_intent': [
       r'pattern\s+(.+)',
   ]
   ```

2. Add handler to `src/tasks/task_executor.py`:
   ```python
   async def _my_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
       # Implementation
       pass
   ```

3. Update documentation in `API.md`

4. Add tests in `tests/test_agent.py`

### New Plugin

1. Create file in `src/plugins/my_plugin.py`
2. Implement plugin class with required methods
3. Add PLUGIN_INFO metadata
4. Document usage in README.md

## Code Review Process

All contributions go through code review:

1. **Automated Checks**
   - Syntax validation
   - Test execution
   - Coverage check

2. **Manual Review**
   - Code quality
   - Documentation
   - Best practices
   - Security implications

3. **Approval**
   - At least one maintainer approval required
   - All comments addressed
   - CI/CD passes

## Community Guidelines

- Be respectful and constructive
- Help others learn
- Share knowledge
- Celebrate contributions

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Review documentation
- Ask in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Cosik AI Agent! 🚀
