# Contributing to Sinhala Word Processor

Thank you for your interest in contributing to the Sinhala Word Processor! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/sinhala-word.git
   cd sinhala-word
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Code Style

We follow these code style guidelines:

- **Black** for code formatting (line length: 88 characters)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for static type checking

### Running Code Quality Checks

```bash
# Format code
black app/ ui/

# Sort imports
isort app/ ui/

# Run linting
flake8 app/ ui/

# Run type checking
mypy app/ ui/

# Or run all checks via pre-commit
pre-commit run --all-files
```

## Testing

We use pytest for testing. Please ensure all tests pass before submitting a pull request.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov=ui

# Run specific test file
pytest tests/test_transliterator.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names: `test_<functionality>_<expected_behavior>`
- Include both unit tests and integration tests
- For GUI tests, use `pytest-qt`

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(transliterator): add fuzzy matching for suggestions

fix(keyboard): resolve button size issue on high DPI displays

docs(readme): update installation instructions
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest
   black --check app/ ui/
   flake8 app/ ui/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feat/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your feature branch
   - Fill in the PR template with details about your changes

### Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Include tests for new functionality
- Update documentation for significant changes
- Ensure all CI checks pass
- Request review from maintainers

## Code Review Process

- All PRs require at least one approval
- Address review comments promptly
- Be open to suggestions and constructive feedback
- PRs will be merged by maintainers after approval

## Reporting Bugs

When reporting bugs, please include:

- **OS and Python version**: Windows 10, Python 3.9, PySide6 6.6.0
- **Steps to reproduce**: Detailed steps to recreate the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Error messages**: Full error messages and stack traces
- **Log files**: Relevant log excerpts from `~/.local/share/sinhala-word/logs/`

## Feature Requests

Before requesting a new feature:

1. Check existing issues to avoid duplicates
2. Clearly describe the feature and its use case
3. Explain why this feature would be valuable
4. Consider implementation complexity

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Join discussions in existing issues
- Contact the maintainer: L.J.Amila Prasad Perera

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (CC - Free to use by crediting the owner).

Thank you for contributing! 🎉
