"""
Database security and operation tests.
"""

import sys
import os
import sqlite3
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from core.database import SecureDatabase


class TestSecureDatabase:
    """Test SecureDatabase class."""
    
    def test_database_creation(self):
        """Test that SecureDatabase can create connections."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = SecureDatabase(db_path, readonly=False)
            conn = db.connect()
            assert conn is not None
            conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_readonly_mode(self):
        """Test that readonly mode works."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create database with a table
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
            conn.close()
            
            # Open in readonly mode
            db = SecureDatabase(db_path, readonly=True)
            conn = db.connect()
            # Should be able to read
            cursor = conn.execute("SELECT COUNT(*) FROM test")
            assert cursor.fetchone()[0] == 0
            conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_database_backup(self):
        """Test that database backup works."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        backup_dir = tempfile.mkdtemp()
        
        try:
            # Create database with a table
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.execute("INSERT INTO test VALUES (1)")
            conn.commit()
            conn.close()
            
            # Create backup
            db = SecureDatabase(db_path, enable_backup=True, backup_dir=backup_dir)
            backup_path = db.backup()
            
            assert os.path.exists(backup_path)
            
            # Verify backup has data
            backup_conn = sqlite3.connect(backup_path)
            cursor = backup_conn.execute("SELECT COUNT(*) FROM test")
            assert cursor.fetchone()[0] == 1
            backup_conn.close()
            
            # Cleanup
            if os.path.exists(backup_path):
                os.unlink(backup_path)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
            if os.path.exists(backup_dir):
                import shutil
                shutil.rmtree(backup_dir)
    
    def test_database_stats(self):
        """Test that database statistics work."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create database with a table
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
            conn.close()
            
            db = SecureDatabase(db_path)
            stats = db.get_stats()
            
            assert stats["exists"] is True
            assert stats["table_count"] > 0
            assert stats["integrity"] == "ok"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_connection_validation(self):
        """Test that connection validation works."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = SecureDatabase(db_path)
            conn = db.connect()
            assert db.validate_connection(conn) is True
            conn.close()
            
            # Invalid connection
            invalid_conn = sqlite3.connect(":memory:")
            invalid_conn.close()
            assert db.validate_connection(invalid_conn) is False
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

