#!/bin/bash
# Database backup script
# Creates a timestamped backup of the SQLite database

set -e

DB_PATH="${SQLITE_PATH:-suppliersync.db}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/suppliersync_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if [ ! -f "${DB_PATH}" ]; then
    echo "❌ Error: Database file not found: ${DB_PATH}"
    exit 1
fi

echo "📦 Creating database backup..."
echo "   Source: ${DB_PATH}"
echo "   Destination: ${BACKUP_FILE}"

# Create backup using SQLite backup command
sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'" || cp "${DB_PATH}" "${BACKUP_FILE}"

# Compress backup
if command -v gzip &> /dev/null; then
    echo "🗜️  Compressing backup..."
    gzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE}.gz"
fi

# Get file size
if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup created successfully!"
    echo "   File: ${BACKUP_FILE}"
    echo "   Size: ${SIZE}"
    
    # Optional: Clean up old backups (keep last 7 days)
    if [ "${CLEANUP_OLD_BACKUPS:-false}" = "true" ]; then
        echo "🧹 Cleaning up old backups (older than 7 days)..."
        find "${BACKUP_DIR}" -name "suppliersync_*.db*" -mtime +7 -delete
    fi
else
    echo "❌ Error: Backup failed!"
    exit 1
fi

echo ""
echo "💡 Tips:"
echo "   - Schedule regular backups: crontab -e"
echo "   - Example daily backup: 0 2 * * * /path/to/backup_database.sh"
echo "   - Store backups in secure location (encrypted, off-site)"

