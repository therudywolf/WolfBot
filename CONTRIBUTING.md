# Contributing to WolfBot

Thank you for your interest in contributing to WolfBot! This document provides guidelines for contributing code, reporting issues, and participating in the community.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Report inappropriate behavior

## Getting Started

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- Git
- Discord.py knowledge (helpful but not required)
- GitHub account

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/WolfBot.git
cd WolfBot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest black ruff mypy  # (optional, for code quality)
```

## Types of Contributions

### 🐛 Reporting Bugs

Before submitting, check if the issue already exists.

**Include:**
- Python version and OS
- Discord.py version
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages/logs
- Bot configuration (without secrets)

**Issue Template:**
```markdown
**Description:** Clear description of the bug

**Steps to Reproduce:**
1. ...
2. ...

**Expected Behavior:** What should happen

**Actual Behavior:** What actually happens

**Environment:**
- Python: 3.11
- discord.py: 2.3
- OS: Linux/Windows/macOS

**Error Output:**
```
...error message...
```
```

### 💡 Feature Requests

**Include:**
- Clear use case and motivation
- Proposed solution or ideas
- Alternative approaches considered
- Related issues/discussions

**Issue Template:**
```markdown
**Description:** What feature would improve WolfBot?

**Problem:** What problem does this solve?

**Solution:** How should this work?

**Alternative Solutions:** Other approaches?

**Additional Context:** Examples, mockups, etc.
```

### 📝 Code Contributions

#### Fork & Branch

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/issue-description
```

**Branch Naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code cleanup
- `test/description` - Tests

#### Code Style

Follow PEP 8 with these specific guidelines:

```python
# Type hints where possible
def get_user_stats(user_id: int, guild_id: int) -> dict:
    """Get user statistics.
    
    Args:
        user_id: Discord user ID
        guild_id: Discord guild ID
        
    Returns:
        Dictionary with user statistics
    """
    pass

# Docstrings for all functions/classes
# Line length: ~100 characters for code, longer for strings

# Comments for complex logic
# Use descriptive variable names
```

#### Testing

```bash
# Run tests (when test suite exists)
python -m pytest tests/ -v

# Check code quality (optional)
ruff check .
black --check .
mypy .
```

#### Commit Messages

Follow conventional commits format:

```
type(scope): description

body (optional)

footer (optional)
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (no logic change)
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

**Examples:**
```
feat(commands): add user ban statistics command

fix(discord): handle permission errors gracefully

docs(readme): update docker setup instructions

refactor(database): consolidate query functions
```

#### Push & Pull Request

```bash
# Push your branch
git push origin feature/amazing-feature
```

**Pull Request Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How to test these changes:
1. ...
2. ...

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed my code
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated (if applicable)
- [ ] No hardcoded secrets or credentials
```

### 📚 Documentation

Help improve docs by:
- Adding/updating README sections
- Creating/improving guides
- Fixing typos and errors
- Adding code examples
- Clarifying confusing sections

**Documentation guidelines:**
- Use clear, concise language
- Include code examples
- Update related files (e.g., if changing features, update README AND FOSS.md)
- Use markdown formatting properly

### 🎮 Testing Contributions

Test suggestions are valuable! Help by:
- Testing features on different systems
- Trying edge cases
- Testing with different Python versions
- Docker testing
- Documentation accuracy checks

## Review Process

1. **Automated Checks**: GitHub Actions verify code (when available)
2. **Review**: Maintainer reviews for:
   - Code quality and style
   - Functionality and logic
   - Testing coverage
   - Documentation
3. **Feedback**: Reviewer may request changes
4. **Approval & Merge**: Approved PRs are merged

### Addressing Review Comments

- Be open to feedback
- Discuss concerns respectfully
- Make requested changes
- Push updates (don't force-push on public branches)
- Request re-review when ready

## Licensing

By contributing, you agree that:
- Your code will be licensed under AGPLv3
- You have rights to the code you submit
- Contributions will be used to improve the project

See [LICENSE](LICENSE) and [FOSS.md](FOSS.md) for details.

## Recognition

Contributors are:
- Added to CONTRIBUTORS.md (when created)
- Mentioned in releases
- Credited in commit history

## Development Tips

### Local Testing

```bash
# Test with your Discord server
# Set OWNER_ID in .env to your user ID
python wolfbot.py

# Test web dashboard
python web_dashboard.py
# Visit http://localhost:5000
```

### Database Testing

```bash
# View database contents
sqlite3 bot_database.db
sqlite> SELECT * FROM users;
sqlite> .exit
```

### Common Issues

**"discord.py not installed"**
```bash
pip install -r requirements.txt
```

**"DISCORD_TOKEN not set"**
```bash
cp .env.example .env
# Edit .env with your token
```

**"Port 5000 already in use"**
```bash
# Change WEB_PORT in .env or use:
WEB_PORT=5001 python web_dashboard.py
```

## Communication

- **Issues**: Use for bugs and features
- **Discussions**: For questions and ideas (when available)
- **Pull Requests**: For code changes
- **Email**: therudywolf (maintainer)

## Resources

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Commit Convention](https://www.conventionalcommits.org/)
- [GitHub Help](https://docs.github.com/)

## Questions?

- Check existing issues and PRs
- Read documentation
- Ask in GitHub discussions (when available)
- Open a new issue with `[QUESTION]` tag

---

## Thank You! 🙏

Every contribution, no matter how small, helps WolfBot improve. Whether it's code, documentation, bug reports, or suggestions - your help is appreciated!

**Made with ❤️ by the WolfBot community**
