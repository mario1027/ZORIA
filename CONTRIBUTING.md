# Contributing to ZORIA

Thank you for your interest in contributing to ZORIA! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, hardware)
- Screenshots or error messages if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature already exists or has been requested
- Clearly describe the feature and its use case
- Explain why it would benefit the project

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ZORIA.git
   cd ZORIA
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Make your changes**
   - Follow PEP 8 style guide
   - Add docstrings to functions and classes
   - Update documentation if needed
   - Add tests for new features

5. **Test your changes**
   ```bash
   pytest tests/ -v
   python -m pylint lib/ pages/
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Use conventional commit format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Build process or auxiliary tool changes

7. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Maximum line length: 100 characters
- Use type hints where appropriate

Example:
```python
def calculate_impedance(frequency: float, resistance: float, 
                       capacitance: float) -> complex:
    """
    Calculate impedance of RC series circuit.
    
    Args:
        frequency: Frequency in Hz
        resistance: Resistance in Ohms
        capacitance: Capacitance in Farads
        
    Returns:
        Complex impedance value
    """
    omega = 2 * np.pi * frequency
    z_c = 1 / (1j * omega * capacitance)
    return resistance + z_c
```

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Update README.md if adding new features
- Comment complex algorithms or non-obvious code

### Testing

- Write unit tests for new functionality
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names

Example:
```python
def test_impedance_calculation_positive_values():
    """Test impedance calculation with valid positive values."""
    result = calculate_impedance(1000, 100, 1e-6)
    assert abs(result.real - 100) < 0.01
```

## 🔍 Code Review Process

All contributions will be reviewed by maintainers. We look for:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable, maintainable, and follows best practices?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it well documented?
- **Compatibility**: Does it break existing functionality?

## 🐛 Debugging Hardware Issues

When working with EVAL-ADMX2001 hardware:

1. **Test with virtual device first** (if mock available)
2. **Document hardware setup** in bug reports
3. **Include serial communication logs** for connection issues
4. **Verify with official software** to isolate hardware vs software issues

## 📦 Adding Dependencies

- Discuss major new dependencies in an issue first
- Keep dependencies minimal and well-maintained
- Update `requirements.txt`
- Explain why the dependency is needed

## 🌐 Internationalization

When adding UI text:
- Use translation keys instead of hardcoded strings
- Add translations for both English and Spanish
- Keep text concise for responsive design

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

Feel free to:
- Open an issue for questions
- Join discussions on GitHub Discussions
- Email the maintainers at mariomontero942@gmail.com

## 🎯 Good First Issues

Look for issues labeled `good first issue` or `help wanted` to get started!

---

Thank you for contributing to ZORIA! 🚀
