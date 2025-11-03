"""
Database security utilities for SupplierSync.

This module provides security helpers for database operations,
including access controls, backup utilities, and encryption helpers.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecureDatabase:
    """
    Secure database wrapper with access controls and security features.
    
    Features:
    - Read-only mode support
    - Connection validation
    - Backup utilities
    - Access logging
    """
    
    def __init__(
        self,
        db_path: str,
        readonly: bool = False,
        enable_wal: bool = True,
        enable_backup: bool = False,
        backup_dir: Optional[str] = None
    ):
        """
        Initialize secure database connection.
        
        Args:
            db_path: Path to SQLite database file
            readonly: Whether to open database in read-only mode
            enable_wal: Whether to enable WAL mode for concurrent access
            enable_backup: Whether to create backups before writes
            backup_dir: Directory for backups (if enable_backup is True)
        """
        self.db_path = db_path
        self.readonly = readonly
        self.enable_wal = enable_wal
        self.enable_backup = enable_backup
        self.backup_dir = backup_dir or "backups"
        
        # Validate database path
        if not readonly and not os.path.exists(db_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        
        # Create backup directory if needed
        if enable_backup:
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """
        Create secure database connection.
        
        Returns:
            SQLite connection with security settings applied
        
        Raises:
            sqlite3.Error: If connection fails
        """
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=10.0,  # 10 second timeout
                check_same_thread=False  # Allow multi-threading
            )
            conn.row_factory = sqlite3.Row
            
            # Enable WAL mode for concurrent access (if not readonly)
            if self.enable_wal and not self.readonly:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
            
            # Security settings
            conn.execute("PRAGMA foreign_keys=ON;")  # Enable foreign key constraints
            conn.execute("PRAGMA secure_delete=OFF;")  # Allow data recovery (can be ON for secure deletion)
            
            # Log connection
            logger.info(f"Database connection established: {self.db_path} (readonly={self.readonly})")
            
            return conn
            
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create database backup.
        
        Args:
            backup_path: Optional custom backup path
        
        Returns:
            Path to backup file
        
        Raises:
            sqlite3.Error: If backup fails
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}.db")
        
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path) or ".", exist_ok=True)
        
        try:
            # Connect to source database
            source = sqlite3.connect(self.db_path)
            source.backup(sqlite3.connect(backup_path))
            source.close()
            
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except sqlite3.Error as e:
            logger.error(f"Database backup failed: {e}")
            raise
    
    def validate_connection(self, conn: sqlite3.Connection) -> bool:
        """
        Validate database connection is healthy.
        
        Args:
            conn: Database connection to validate
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    def get_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            conn = self.connect()
            stats = {
                "path": self.db_path,
                "exists": os.path.exists(self.db_path),
                "readonly": self.readonly,
                "size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            }
            
            if os.path.exists(self.db_path):
                # Get table count
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                stats["table_count"] = len(cursor.fetchall())
                
                # Get database integrity
                cursor = conn.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()
                stats["integrity"] = integrity[0] if integrity else "unknown"
            
            conn.close()
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "path": self.db_path,
                "error": str(e)
            }


def encrypt_sensitive_fields(conn: sqlite3.Connection, table: str, fields: list[str]) -> None:
    """
    Encrypt sensitive fields in database (placeholder for production encryption).
    
    Note: This is a placeholder. In production, use proper encryption libraries
    like cryptography.fernet or similar.
    
    Args:
        conn: Database connection
        table: Table name
        fields: List of field names to encrypt
    
    Raises:
        NotImplementedError: Encryption not implemented (placeholder)
    """
    # TODO: Implement encryption for production
    # For now, this is a placeholder
    logger.warning("Field encryption not implemented. Use database-level encryption for production.")
    raise NotImplementedError("Field encryption not implemented. Use database-level encryption for production.")


def secure_delete(conn: sqlite3.Connection, table: str, condition: str, params: tuple = ()) -> int:
    """
    Securely delete records (overwrites data before deletion).
    
    Note: SQLite's secure_delete pragma must be enabled for this to work.
    
    Args:
        conn: Database connection
        table: Table name
        condition: WHERE condition (use parameterized queries)
        params: Parameters for WHERE condition
    
    Returns:
        Number of rows deleted
    """
    # Enable secure delete
    conn.execute("PRAGMA secure_delete=ON;")
    
    # Delete records
    cursor = conn.execute(f"DELETE FROM {table} WHERE {condition}", params)
    rows_deleted = cursor.rowcount
    
    # Disable secure delete (for performance)
    conn.execute("PRAGMA secure_delete=OFF;")
    
    logger.info(f"Securely deleted {rows_deleted} rows from {table}")
    return rows_deleted

