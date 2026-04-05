# Security Policy

## Supported Versions

Currently, only the latest version of EcoRoute Atlas is supported with security updates.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue**.

### How to Report

**Send an email to:** security@ecoroute.com

Please include:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if known)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate the vulnerability and validate the issue
3. **Resolution**: We will work on a fix and provide an estimated timeline
4. **Disclosure**: We will coordinate disclosure with you

### Security Best Practices

When working with EcoRoute Atlas:

- ✅ Never commit sensitive data (API keys, passwords, tokens)
- ✅ Use environment variables for configuration
- ✅ Keep dependencies updated
- ✅ Run security scans: `make security`
- ✅ Follow secure coding practices
- ✅ Report vulnerabilities responsibly

## Security Features

- ✅ Automated security scanning (Bandit)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (FastAPI automatic escaping)
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ Secret management via environment variables
- ✅ Password hashing with bcrypt

## Security Scanning

This project uses automated security scanning:
- **Bandit** - Python security linter
- **Pre-commit hooks** - Run before commits
- **CI/CD** - Automated security checks on every push

To run locally:
```bash
make security
```
