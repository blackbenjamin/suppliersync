# Dependency Security Guide

This guide covers dependency security best practices for SupplierSync.

## Overview

Dependency security is critical for maintaining the security of the application. This guide provides:
- Dependency vulnerability scanning
- Update procedures
- Security best practices

## Python Dependencies

### Installing Security Scanner

```bash
pip install safety
```

### Running Security Checks

```bash
# From project root
cd suppliersync
safety check

# Or use the provided script
./scripts/check_dependencies.sh
```

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages (careful!)
pip install --upgrade -r requirements.txt

# Or use the provided script
./scripts/update_dependencies.sh
```

### Automated Scanning

Add to CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Check Python dependencies
  run: |
    pip install safety
    cd suppliersync
    safety check --json
```

## Node.js Dependencies

### Running Security Checks

```bash
# From dashboard directory
cd dashboard
npm audit

# Fix automatically fixable issues
npm audit fix

# Or use the provided script
./scripts/check_dependencies.sh
```

### Updating Dependencies

```bash
# Check for outdated packages
npm outdated

# Update specific package
npm install package-name@latest

# Update all packages
npm update

# Or use the provided script
./scripts/update_dependencies.sh
```

### Automated Scanning

Add to CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Check Node.js dependencies
  run: |
    cd dashboard
    npm audit --audit-level=moderate
```

## Best Practices

### 1. Regular Updates
- Check for updates weekly
- Review changelogs before updating
- Test thoroughly after updates
- Update dependencies in separate commits

### 2. Pinning Versions
- Pin exact versions in production (`==1.2.3`)
- Use version ranges in development (`>=1.2.0,<2.0.0`)
- Document breaking changes

### 3. Security Advisories
- Subscribe to security advisories
- Monitor CVE databases
- Respond to critical vulnerabilities immediately

### 4. Automated Scanning
- Integrate dependency scanning in CI/CD
- Set up automated alerts
- Block merges with critical vulnerabilities

### 5. Dependency Review
- Review all new dependencies before adding
- Prefer well-maintained packages
- Check license compatibility
- Review security history

## Current Dependencies

### Python (suppliersync/requirements.txt)
- `openai>=1.51.0` - OpenAI API client
- `langchain>=0.2.16` - LLM framework
- `fastapi>=0.115.0` - Web framework
- `pydantic>=2.8` - Data validation
- `slowapi>=0.1.9` - Rate limiting

### Node.js (dashboard/package.json)
- `next@^14.2.33` - React framework
- `react@18.2.0` - UI library
- `better-sqlite3@9.6.0` - Database client

## Vulnerability Scanning Tools

### Python
- **safety**: Checks for known vulnerabilities in Python packages
- **pip-audit**: Alternative vulnerability scanner
- **dependabot**: GitHub's automated dependency updates

### Node.js
- **npm audit**: Built-in vulnerability scanner
- **snyk**: Commercial security platform
- **dependabot**: GitHub's automated dependency updates

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  pull_request:
    paths:
      - 'suppliersync/requirements.txt'
      - 'dashboard/package.json'

jobs:
  python-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install safety
        run: pip install safety
      - name: Check dependencies
        run: |
          cd suppliersync
          safety check --json

  node-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: |
          cd dashboard
          npm ci
      - name: Audit dependencies
        run: |
          cd dashboard
          npm audit --audit-level=moderate
```

## Handling Vulnerabilities

### Critical Vulnerabilities
1. **Immediate Action**: Update or replace vulnerable package
2. **Test Thoroughly**: Ensure update doesn't break functionality
3. **Deploy Quickly**: Push fix to production ASAP
4. **Document**: Document the vulnerability and fix

### Moderate Vulnerabilities
1. **Plan Update**: Schedule update within 30 days
2. **Test in Development**: Test update in dev environment
3. **Deploy**: Deploy during maintenance window
4. **Monitor**: Watch for any issues

### Low Vulnerabilities
1. **Review**: Review if update is necessary
2. **Update**: Update during regular dependency updates
3. **Monitor**: Monitor for any issues

## Resources

- [Python Safety](https://pyup.io/safety/)
- [npm Audit](https://docs.npmjs.com/cli/audit)
- [Snyk](https://snyk.io/)
- [CVE Database](https://cve.mitre.org/)
- [GitHub Security Advisories](https://github.com/advisories)

