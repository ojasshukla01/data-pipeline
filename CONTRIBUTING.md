# Contributing to Gaming Data Pipeline

Thank you for your interest in contributing! Please follow these guidelines.

## 🔒 Security First

**CRITICAL**: This is a public repository. Never commit:

- ❌ API keys or tokens
- ❌ Passwords or credentials
- ❌ Database files (`.db`, `.sqlite`, `.duckdb`)
- ❌ `.env` files
- ❌ Personal information (PII)
- ❌ Any sensitive data

**Always**:
- ✅ Use `.env` file for secrets (it's in `.gitignore`)
- ✅ Use `.env.example` as a template
- ✅ Review your code before committing
- ✅ Check `git status` before pushing

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/data-pipeline.git
   cd data-pipeline
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```
6. Set up database:
   ```bash
   python src/database/setup_db.py
   ```

## 📝 Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test your changes:
   ```bash
   pytest tests/
   python test_imports.py
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
   **Important**: Review `git status` to ensure no sensitive files are included!

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request on GitHub

## ✅ Pre-Commit Checklist

Before committing, verify:

- [ ] No API keys in code
- [ ] No hardcoded passwords
- [ ] `.env` file is not tracked
- [ ] Database files are not committed
- [ ] Tests pass
- [ ] Code follows project style
- [ ] Documentation updated if needed

## 🧪 Testing

Run tests before submitting:

```bash
# Run all tests
pytest tests/

# Test imports
python test_imports.py

# Test dashboard
python test_dashboard_comprehensive.py
```

## 📚 Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write meaningful commit messages

## 🐛 Reporting Issues

When reporting issues:

1. Check if the issue already exists
2. Provide clear description
3. Include steps to reproduce
4. Add relevant logs/error messages
5. Specify your environment (OS, Python version, etc.)

## 🔄 Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG if applicable
5. Request review from maintainers

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎮
