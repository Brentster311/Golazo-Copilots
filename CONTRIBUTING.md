# Contributing to Golazo-Copilots

Thank you for your interest in contributing to Golazo-Copilots! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Golazo-Copilots.git
   cd Golazo-Copilots
   ```
3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### 1. Create a Branch

Create a branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

Ensure all tests pass:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=golazo_copilots --cov-report=html

# Run specific test file
pytest tests/unit/test_workflow_manager.py
```

### 4. Format and Lint

Format and check your code:
```bash
# Format with black
black golazo_copilots/ tests/

# Lint with ruff
ruff check golazo_copilots/ tests/

# Type check with mypy
mypy golazo_copilots/
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:
```bash
git add .
git commit -m "Add feature: description of your changes"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for modules, classes, and functions

### Docstring Format

Use Google-style docstrings:

```python
def create_ticket(title: str, description: str) -> Ticket:
    """Create a new work ticket.
    
    Args:
        title: The ticket title
        description: Detailed description of the work
        
    Returns:
        The created Ticket instance
        
    Raises:
        ValueError: If title is empty
    """
```

### Testing

- Write unit tests for individual components
- Write integration tests for workflows
- Aim for high test coverage
- Use descriptive test names

Example test structure:
```python
class TestFeature:
    """Tests for Feature component."""
    
    def test_basic_functionality(self):
        """Test basic feature operation."""
        # Arrange
        feature = Feature()
        
        # Act
        result = feature.do_something()
        
        # Assert
        assert result == expected_value
```

## Project Structure

```
golazo_copilots/
├── models/              # Data models
├── servers/             # MCP server implementation
├── orchestrator/        # Workflow orchestration
│   ├── workflow_manager.py
│   └── orchestrator.py
└── cli.py              # Command-line interface

tests/
├── unit/               # Unit tests
└── integration/        # Integration tests

examples/               # Usage examples
docs/                   # Documentation
```

## Adding New Features

When adding new features:

1. **Start with tests** - Write tests that define the behavior
2. **Implement minimally** - Add only what's needed
3. **Document** - Update README and docstrings
4. **Add examples** - Show how to use the feature

### Adding MCP Tools

To add a new MCP tool:

1. Add the tool definition in `servers/golazo_server.py`:
   ```python
   Tool(
       name="your_tool_name",
       description="What the tool does",
       inputSchema={...}
   )
   ```

2. Add the tool handler:
   ```python
   elif name == "your_tool_name":
       result = self.workflow_manager.your_method(...)
       return [TextContent(type="text", text=result)]
   ```

3. Add tests in `tests/unit/` or `tests/integration/`
4. Document in README.md

### Adding Workflow Actions

To add a new workflow action:

1. Add handler to `orchestrator/orchestrator.py`:
   ```python
   def _handle_your_action(self, params: dict[str, Any]) -> str:
       """Handle your custom action."""
       return self.workflow_manager.your_method(**params)
   ```

2. Register in `_register_default_handlers()`:
   ```python
   self.action_handlers["your_action"] = self._handle_your_action
   ```

3. Add tests and documentation

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Add docstrings to all public APIs
- Provide examples for new features

## Pull Request Guidelines

### PR Title

Use clear, descriptive titles:
- ✅ "Add support for custom workflow policies"
- ✅ "Fix WIP limit enforcement bug"
- ❌ "Update code"
- ❌ "Fix bug"

### PR Description

Include:
- **What**: What changes are being made
- **Why**: Why these changes are needed
- **How**: How the changes work (if not obvious)
- **Testing**: How the changes were tested

Example:
```markdown
## What
Add support for custom workflow policies

## Why
Users need to configure policies like minimum approvals and review requirements

## How
- Extended WorkflowPolicy model with new fields
- Added validation in workflow execution
- Updated documentation

## Testing
- Added unit tests for policy validation
- Added integration test for custom policy workflow
- Ran full test suite
```

### Checklist

Before submitting a PR:

- [ ] Tests added/updated and passing
- [ ] Code formatted with black
- [ ] Code linted with ruff
- [ ] Type checked with mypy
- [ ] Documentation updated
- [ ] Examples added (if applicable)
- [ ] CHANGELOG updated (if applicable)

## Code Review Process

1. **Automated checks** run on all PRs
2. **Maintainer review** for code quality and design
3. **Discussion** and iteration as needed
4. **Merge** once approved

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Reach out to maintainers for guidance

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
