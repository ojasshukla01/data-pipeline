# 🔒 Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please **DO NOT** open a public issue. Instead, please email the maintainer directly or create a private security advisory.

## Security Best Practices

### 🔑 API Keys and Secrets

**NEVER commit API keys, passwords, or other sensitive information to the repository.**

1. **Use `.env` file for secrets**:
   - Copy `.env.example` to `.env`
   - Add your API keys to `.env`
   - `.env` is already in `.gitignore` and will NOT be committed

2. **Verify `.env` is ignored**:
   ```bash
   git status
   # .env should NOT appear in the list
   ```

3. **If you accidentally committed secrets**:
   - Rotate/regenerate all exposed API keys immediately
   - Remove the file from git history:
     ```bash
     git rm --cached .env
     git commit -m "Remove .env from tracking"
     ```
   - Consider using `git filter-branch` or BFG Repo-Cleaner for complete removal

### 🗄️ Database Security

- Database files (`.db`, `.sqlite`, `.duckdb`) are automatically ignored
- Never commit database files containing real user data
- Use environment variables for database credentials

### 🔍 Pre-Commit Checklist

Before committing code, verify:

- [ ] No API keys in code files
- [ ] No passwords or tokens hardcoded
- [ ] `.env` file is not tracked
- [ ] Database files are not committed
- [ ] No personal information (PII) in code or data
- [ ] Log files don't contain sensitive information

### 🛡️ Environment Variables

All sensitive configuration should use environment variables:

```python
# ✅ GOOD - Read from environment
api_key = os.getenv("STEAM_API_KEY")

# ❌ BAD - Hardcoded in code
api_key = "ABC123XYZ"
```

### 📝 Code Review

When reviewing pull requests, check for:
- Hardcoded credentials
- Exposed API keys
- Database connection strings with passwords
- Personal information
- Debug logging that might expose secrets

### 🔄 Key Rotation

If you suspect your API keys have been exposed:
1. **Immediately regenerate** the keys from the provider
2. Update your local `.env` file
3. Update any deployed environments
4. Review access logs if available

### 🌐 Public Repository Considerations

This repository is public. Be extra careful:
- Never commit real API keys (even in old commits)
- Use `.env.example` as a template only
- Review git history before making the repo public
- Consider using GitHub Secrets for CI/CD

### 📚 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/secrets.html)

## 🔐 Supported APIs

### OpenDota API
- **No key required** - Safe to use publicly
- Rate limited: 60 requests/minute

### Steam API
- **Requires free API key**
- Store in `.env` file only
- Rate limit: 100,000 requests/day

### Riot Games API
- **Requires free API key**
- Keys expire after 24 hours (free tier)
- Store in `.env` file only
- Rate limit: 100 requests/2 minutes

## ✅ Security Checklist for Contributors

- [ ] I have not committed any API keys
- [ ] I have not committed any passwords
- [ ] I have not committed database files
- [ ] I have not committed `.env` file
- [ ] I have reviewed my code for sensitive data
- [ ] I understand that this is a public repository

---

**Remember: When in doubt, don't commit it!**
