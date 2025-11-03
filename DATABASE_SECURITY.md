# Database Security Guide

This guide covers database security best practices for SupplierSync.

## Overview

Database security is critical for protecting sensitive business data. This guide covers:
- Access controls
- Encryption
- Backup procedures
- Security best practices

## Current Implementation

### SQLite Configuration

The system uses SQLite with the following security settings:

```python
# WAL mode for concurrent access
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

# Foreign key constraints
PRAGMA foreign_keys=ON;

# Secure delete (optional, for secure data deletion)
PRAGMA secure_delete=OFF;  # Set to ON for secure deletion
```

### Access Controls

**Read-Only Mode:**
- Dashboard uses read-only database connections
- Only API service can write to database
- WAL mode disabled for dashboard connections

**Connection Validation:**
- All connections validated before use
- Timeout set to 10 seconds
- Connection pooling for performance

## Security Best Practices

### 1. Access Controls

**Current Implementation:**
- ✅ Read-only mode for dashboard
- ✅ Write access only for API service
- ✅ Connection validation

**Production Recommendations:**
- Use database user accounts with minimal permissions
- Implement role-based access control (RBAC)
- Use connection pooling with authentication
- Monitor database access logs

### 2. Encryption

**At Rest:**
- SQLite databases can be encrypted using SQLCipher
- For production, consider:
  - Database-level encryption (SQLCipher)
  - Volume-level encryption (LUKS, BitLocker)
  - Application-level encryption for sensitive fields

**In Transit:**
- Use HTTPS/TLS for all database connections
- Use encrypted database connections (SQLCipher over TLS)

**Current Implementation:**
- ⚠️ No encryption at rest (development system)
- ⚠️ No encryption in transit (local system)

**Production Requirements:**
- ✅ Encrypt database at rest
- ✅ Encrypt database connections
- ✅ Encrypt sensitive fields (PII, financial data)

### 3. Backups

**Backup Script:**
```bash
# Use provided backup script
./suppliersync/scripts/backup_database.sh

# Or manually
sqlite3 suppliersync.db ".backup backup.db"
```

**Backup Best Practices:**
- ✅ Regular automated backups (daily minimum)
- ✅ Store backups in secure location
- ✅ Encrypt backup files
- ✅ Test backup restoration regularly
- ✅ Keep multiple backup versions
- ✅ Off-site backup storage

**Automated Backups:**
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /path/to/suppliersync/scripts/backup_database.sh
```

### 4. Data Retention

**Current Implementation:**
- All data retained indefinitely
- No automatic data purging

**Production Recommendations:**
- Implement data retention policies
- Archive old data
- Secure deletion of sensitive data
- Compliance with data protection regulations (GDPR, CCPA)

### 5. Monitoring and Auditing

**Current Implementation:**
- ✅ Run IDs for traceability
- ✅ Timestamps on all records
- ✅ Agent telemetry logging

**Production Recommendations:**
- Implement database audit logging
- Monitor database access patterns
- Alert on suspicious activity
- Regular security audits

## Database Security Utilities

### SecureDatabase Class

The `core/database.py` module provides a `SecureDatabase` class with:
- Read-only mode support
- Connection validation
- Backup utilities
- Access logging

**Example Usage:**
```python
from core.database import SecureDatabase

# Read-only connection
db = SecureDatabase("suppliersync.db", readonly=True)
conn = db.connect()

# Writable connection with backup
db = SecureDatabase(
    "suppliersync.db",
    readonly=False,
    enable_backup=True,
    backup_dir="backups"
)
conn = db.connect()
```

### Backup Script

The `scripts/backup_database.sh` script provides:
- Automated database backups
- Timestamped backup files
- Compression support
- Old backup cleanup

**Usage:**
```bash
# Set environment variables
export SQLITE_PATH=suppliersync.db
export BACKUP_DIR=backups
export CLEANUP_OLD_BACKUPS=true

# Run backup
./suppliersync/scripts/backup_database.sh
```

## Production Deployment Checklist

Before deploying to production:

- [ ] Database encrypted at rest (SQLCipher or volume encryption)
- [ ] Database connections encrypted (TLS)
- [ ] Access controls implemented (RBAC)
- [ ] Regular backups configured (automated)
- [ ] Backup encryption enabled
- [ ] Backup restoration tested
- [ ] Off-site backup storage configured
- [ ] Database audit logging enabled
- [ ] Monitoring and alerting configured
- [ ] Data retention policies implemented
- [ ] Secure deletion enabled for sensitive data
- [ ] Database access logs reviewed regularly
- [ ] Security updates applied regularly
- [ ] Database permissions reviewed and minimized

## SQLite Security Considerations

### Limitations

SQLite is a file-based database, which has security implications:
- File-based access control (OS-level)
- No built-in user authentication
- Limited encryption support (requires SQLCipher)
- No network-level security (local file system)

### Mitigations

For production deployments:
- Use SQLCipher for encryption
- Implement application-level access controls
- Use secure file system permissions
- Monitor database file access
- Consider migrating to PostgreSQL for production

## Migration to Production Database

For production, consider migrating to PostgreSQL or similar:

**Benefits:**
- Built-in user authentication
- Network-level security
- Better encryption support
- Row-level security
- Better audit logging
- Better performance at scale

**Migration Path:**
1. Use SQLAlchemy ORM (database-agnostic)
2. Test with PostgreSQL in development
3. Migrate schema and data
4. Update connection strings
5. Deploy and monitor

## Resources

- [SQLite Security](https://www.sqlite.org/security.html)
- [SQLCipher](https://www.zetetic.net/sqlcipher/)
- [OWASP Database Security](https://owasp.org/www-project-database-security/)
- [Database Backup Best Practices](https://www.postgresql.org/docs/current/backup.html)

