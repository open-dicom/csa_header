# Contributing to csa_header

Thank you for your interest in contributing to csa_header! This project aims to provide reliable CSA header parsing for Siemens MRI DICOM files, and we welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md) inspired by the NIPY community. We value open, collaborative, and respectful communication. Please review the guidelines to understand our community standards.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/csa_header.git
   cd csa_header
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/open-dicom/csa_header.git
   ```

## Development Setup

This project uses [Hatch](https://hatch.pypa.io/) for environment management and task execution.

### Prerequisites

- Python 3.9 or higher
- Hatch (install with `pip install hatch`)

### Install Development Dependencies

Hatch will automatically create isolated environments with all necessary dependencies:

```bash
# The default environment includes pre-commit and ipython
hatch shell

# Or run commands directly without activating the shell
hatch run <command>
```

### Set up Pre-commit Hooks

Pre-commit hooks ensure code quality and consistency:

```bash
hatch run pre-commit install
```

This will run checks automatically before each commit, including:
- Code formatting (black)
- Linting (ruff)
- YAML/TOML validation
- Trailing whitespace removal
- And more...

## Making Changes

### Branching Strategy

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Use descriptive branch names:
   - `feature/add-something` for new features
   - `fix/fix-something` for bug fixes
   - `docs/improve-something` for documentation
   - `refactor/improve-something` for refactoring

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat: add support for CSA header type 3

Implement parsing for the newer CSA header format found in
Siemens MRI scanners from 2020 onwards.

Closes #123
```

```
fix: correct endianness handling in unpacker

The unpacker was not correctly handling big-endian systems.
Added tests to verify both little-endian and big-endian parsing.

Fixes #456
```

## Testing

**All contributions must include appropriate tests.** We maintain 96%+ test coverage.

### Running Tests

```bash
# Run all tests
hatch run test:test

# Run with coverage report
hatch run test:cov

# Run specific test file
hatch run test:test tests/test_header.py

# Run specific test class or method
hatch run test:test tests/test_header.py::CsaHeaderReadTestCase
```

### Writing Tests

- Place tests in the `tests/` directory
- Use `unittest.TestCase` for test classes
- Name test files as `test_*.py`
- Aim for descriptive test names that explain what's being tested
- Include docstrings for complex test scenarios
- Test both success and error paths

**Example test structure:**
```python
import unittest
from csa_header import CsaHeader

class TestNewFeature(unittest.TestCase):
    """Tests for the new feature."""

    def test_basic_functionality(self):
        """Test that basic functionality works as expected."""
        # Arrange
        data = b'...'

        # Act
        result = CsaHeader(data).read()

        # Assert
        self.assertEqual(result['expected_key'], 'expected_value')
```

### Test Coverage Requirements

- New features must have 90%+ test coverage
- Bug fixes should include regression tests
- Aim for 100% coverage on critical parsing code

Check coverage:
```bash
hatch run test:cov-html
# Open htmlcov/index.html in your browser
```

## Code Style

We use automated tools to maintain consistent code style:

### Formatting

- **Black**: Code formatter (line length: 120)
- **Ruff**: Fast linter and formatter

```bash
# Check style
hatch run lint:style

# Auto-fix issues
hatch run lint:fmt

# Type checking
hatch run lint:typing
```

### Style Guidelines

- Line length: 120 characters
- Use type hints for all public functions
- Write docstrings for modules, classes, and public functions
- Follow PEP 8 conventions
- Use modern Python idioms (Python 3.9+)
  - Union types: `X | Y` instead of `Union[X, Y]`
  - Optional: `X | None` instead of `Optional[X]`

### Type Hints

All public APIs must have complete type hints:

```python
def parse_tag(self, data: bytes) -> dict[str, int | float | str]:
    """Parse a CSA header tag.

    Parameters
    ----------
    data : bytes
        Binary tag data

    Returns
    -------
    dict
        Parsed tag with name, value, and metadata
    """
    ...
```

## Submitting Changes

### Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks locally**:
   ```bash
   # Tests
   hatch run test:test

   # Coverage
   hatch run test:cov

   # Style
   hatch run lint:all
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub with:
   - Clear title and description
   - Reference any related issues
   - Description of changes and motivation
   - Test plan or testing evidence
   - Screenshots for UI changes (if applicable)

### PR Requirements

- ✅ All tests pass
- ✅ Code coverage maintained or improved
- ✅ Type checking passes (mypy)
- ✅ Linting passes (ruff, black)
- ✅ Commit messages follow conventional commits format
- ✅ Documentation updated (if needed)
- ✅ CHANGELOG.md updated (for user-facing changes)

### Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, maintainers will merge your PR

## Reporting Issues

### Bug Reports

Use the bug report template and include:

- Clear, descriptive title
- Steps to reproduce
- Expected vs. actual behavior
- Python version and environment info
- Minimal code example
- Sample data (if possible and not confidential)

### Feature Requests

Use the feature request template and include:

- Clear description of the feature
- Use case and motivation
- Proposed API or implementation (if you have ideas)
- Willingness to implement it yourself

### Questions

- Check existing issues and documentation first
- Open a GitHub issue with the "question" label
- Provide context about what you're trying to achieve

## Development Tips

### Useful Commands

```bash
# Enter development shell
hatch shell

# Run tests in watch mode (if using pytest-watch)
hatch run test:test -- --watch

# Generate coverage report
hatch run test:cov-html

# Run pre-commit on all files
hatch run pre-commit run --all-files

# Clean up caches
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

### Working with Test Data

- Test data files are in `tests/data/`
- Use existing CSA header samples when possible
- For synthetic test data, use `struct.pack()` to create binary data
- Document test data format and source

### Documentation

- Update docstrings for any API changes
- Keep README.md up to date
- Add examples for new features
- Update type hints

## Project Structure

```
csa_header/
├── csa_header/          # Source code
│   ├── __init__.py      # Package exports
│   ├── header.py        # Main CSA header parser
│   ├── unpacker.py      # Binary stream reader
│   ├── utils.py         # Utility functions
│   └── ascii/           # ASCII ASCCONV parser
├── tests/               # Test suite
│   ├── test_header.py
│   ├── test_unpacker.py
│   ├── fixtures.py
│   └── data/            # Test data files
├── pyproject.toml       # Project configuration
├── README.md
└── CONTRIBUTING.md      # This file
```

## Getting Help

- Open an issue on GitHub
- Check existing issues and discussions
- Read the documentation in README.md
- Explore the test suite for usage examples

## Recognition

Contributors will be recognized in:
- Git commit history
- GitHub contributors page
- Release notes for significant contributions

Thank you for contributing to csa_header! Your efforts help make medical imaging data more accessible.
