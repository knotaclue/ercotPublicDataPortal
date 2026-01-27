# Contributing to ERCOT API Query Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🌟 Ways to Contribute

- **Report bugs**: Open an issue describing the problem
- **Suggest features**: Open an issue with your idea
- **Improve documentation**: Fix typos, add examples, clarify instructions
- **Share query examples**: Add useful query configurations
- **Submit code improvements**: Fix bugs or add features

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/ercot-api-query.git
   cd ercot-api-query
   ```

2. **Set up your development environment**
   ```bash
   # Run the setup script
   ./setup.sh
   
   # Or manually:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create a branch for your changes**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

## 📝 Contribution Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **Comments**: Write clear, helpful comments explaining WHY, not just WHAT
- **Documentation**: Remember this project is for code-aware non-developers
- **Simplicity**: Prefer clear code over clever code

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for CSV output format"
git commit -m "Fix authentication token refresh bug"
git commit -m "Update README with new endpoints"

# Not as helpful
git commit -m "Update code"
git commit -m "Fix bug"
```

### Documentation

- Update relevant documentation files when adding features
- Add examples to EXAMPLES.md for new functionality
- Update CHANGELOG.md with your changes
- Include inline comments in code changes

### Testing

Before submitting:

1. **Test your changes**:
   ```bash
   python3 ercot_query.py --config queries/realtime_system_load.json
   ```

2. **Verify documentation is accurate**

3. **Check for sensitive information**:
   - Never commit `.env` files
   - Remove any test credentials
   - Clear any personal data from examples

## 🔍 Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Go to GitHub and click "New Pull Request"
   - Provide a clear title and description
   - Reference any related issues (#issue-number)
   - Explain what your changes do and why

4. **Pull Request Template**:
   ```markdown
   ## Description
   Brief description of what this PR does
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   How did you test these changes?
   
   ## Related Issues
   Fixes #issue-number
   
   ## Checklist
   - [ ] Code follows project style
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Tested changes
   - [ ] No sensitive data included
   ```

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: What happened?
2. **Expected behavior**: What should have happened?
3. **Steps to reproduce**:
   ```bash
   1. Run command X
   2. See error Y
   ```
4. **Environment**:
   - OS: (e.g., Ubuntu 22.04, macOS 13, Windows 11)
   - Python version: `python3 --version`
   - Package versions: `pip list`
5. **Error messages**: Full error output
6. **Query configuration**: (remove sensitive data!)

## 💡 Suggesting Features

When suggesting features:

1. **Use case**: Why do you need this feature?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: What else did you think about?
4. **Additional context**: Any other relevant information

## 📚 Documentation Contributions

Documentation improvements are always welcome!

### What to improve:

- Fix typos and grammar
- Add clarity to confusing sections
- Include more examples
- Update outdated information
- Add troubleshooting tips

### Style guidelines:

- Use clear, simple language
- Include examples where helpful
- Organize with headers
- Use bullet points for lists
- Add code blocks for commands

## 🔄 Query Configuration Contributions

Sharing useful query configurations helps everyone!

### To contribute a query:

1. Create a descriptive JSON file in `queries/`
2. Add comments in a separate `.md` file if needed
3. Add an example to `EXAMPLES.md`
4. Verify the query works
5. Remove any sensitive data (dates, locations OK)

### Example contribution:

```json
{
  "endpoint": "/api/v1/fuel_mix",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-31"
  },
  "output_file": "output/fuel_mix_jan2025.json"
}
```

With documentation in EXAMPLES.md:

```markdown
### Example X: Fuel Mix Data

**Use Case**: Get generation by fuel type

**Configuration** (`queries/fuel_mix.json`):
[JSON example above]

**Note**: Useful for analyzing renewable vs non-renewable generation
```

## 🏗️ Code Contribution Guidelines

### Before writing code:

1. **Check existing issues**: Someone might already be working on it
2. **Open an issue**: Discuss your approach first for major changes
3. **Keep it simple**: Remember the audience (code-aware non-developers)

### When writing code:

1. **Maintain style**: Match existing code style
2. **Add comments**: Explain complex logic
3. **Handle errors**: Add appropriate error handling
4. **Update docs**: Keep documentation in sync

### Example code contribution:

```python
def new_feature(self, parameter):
    """
    Brief description of what this does.
    
    Args:
        parameter (type): What this parameter is for
    
    Returns:
        type: What this returns
    """
    # Explain any non-obvious logic
    result = some_operation(parameter)
    
    # Handle potential errors
    if not result:
        print(f"✗ Operation failed: reason")
        return None
    
    return result
```

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- CHANGELOG.md (for significant contributions)
- README.md (for major features)

## 📞 Questions?

- **General questions**: Open a discussion on GitHub
- **Bug reports**: Open an issue
- **Feature requests**: Open an issue
- **Security issues**: Contact maintainer directly (don't open public issue)

## 🎯 Good First Issues

Looking to start contributing? Check issues labeled:
- `good first issue`: Good for newcomers
- `documentation`: Documentation improvements
- `help wanted`: Need community assistance

---

Thank you for contributing to make this tool better for everyone! 🎉
