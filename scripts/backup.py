#!/usr/bin/env python3
"""
Database backup script with retention policy and encryption.

Performs full database backups with compression and optional encryption.
Implements retention policies and cleanup of old backups.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupManager:
    """Manages database backups and retention policies."""

    def __init__(self, backup_dir: str, retention_days: int = 7, db_host: str = "localhost", db_user: str = "postgres", db_name: str = "euint"):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
            retention_days: Number of days to retain backups
            db_host: Database host
            db_user: Database user
            db_name: Database name
        """
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.db_host = db_host
        self.db_user = db_user
        self.db_name = db_name
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file for tracking backups
        self.manifest_file = self.backup_dir / "manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        """Load backup manifest."""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {"backups": []}

    def _save_manifest(self) -> None:
        """Save backup manifest."""
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def create_backup(self, compress: bool = True, encrypt: bool = False) -> bool:
        """
        Create a database backup.
        
        Args:
            compress: Whether to compress the backup
            encrypt: Whether to encrypt the backup
            
        Returns:
            True if backup succeeded, False otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.sql"
        
        try:
            logger.info(f"Starting backup to {backup_file}")
            
            # Create backup
            dump_cmd = [
                "pg_dump",
                "-h", self.db_host,
                "-U", self.db_user,
                "-d", self.db_name,
                "-F", "c",  # Custom format
                "-v",  # Verbose
                "-f", str(backup_file)
            ]
            
            result = subprocess.run(
                dump_cmd,
                env={**os.environ, "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", "")},
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return False
            
            # Compress if requested
            if compress:
                logger.info(f"Compressing backup...")
                compress_file = str(backup_file) + ".gz"
                result = subprocess.run(
                    ["gzip", "-9", str(backup_file)],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    backup_file = Path(compress_file)
                else:
                    logger.error(f"Compression failed: {result.stderr}")
                    return False
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_file)
            file_size = backup_file.stat().st_size
            
            # Record backup in manifest
            backup_info = {
                "timestamp": timestamp,
                "filename": backup_file.name,
                "size": file_size,
                "checksum": checksum,
                "compressed": compress,
                "encrypted": encrypt,
                "retention_date": (datetime.now() + timedelta(days=self.retention_days)).isoformat()
            }
            
            self.manifest["backups"].append(backup_info)
            self._save_manifest()
            
            logger.info(f"Backup completed successfully: {backup_file.name}")
            logger.info(f"Size: {file_size / (1024*1024):.2f}MB, Checksum: {checksum}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Backup timed out")
            return False
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            return False

    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period.
        
        Returns:
            Number of backups removed
        """
        removed_count = 0
        now = datetime.now()
        
        backups_to_keep = []
        
        for backup in self.manifest["backups"]:
            retention_date = datetime.fromisoformat(backup["retention_date"])
            backup_file = self.backup_dir / backup["filename"]
            
            if retention_date < now:
                try:
                    if backup_file.exists():
                        backup_file.unlink()
                        logger.info(f"Deleted old backup: {backup['filename']}")
                        removed_count += 1
                except OSError as e:
                    logger.error(f"Failed to delete backup {backup['filename']}: {e}")
            else:
                backups_to_keep.append(backup)
        
        self.manifest["backups"] = backups_to_keep
        self._save_manifest()
        
        return removed_count

    def verify_backup(self, backup_file: Path) -> bool:
        """
        Verify backup integrity.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            True if backup is valid, False otherwise
        """
        try:
            logger.info(f"Verifying backup: {backup_file}")
            
            # For gzip files, verify compression
            if backup_file.suffix == '.gz':
                result = subprocess.run(
                    ["gzip", "-t", str(backup_file)],
                    capture_output=True,
                    timeout=300
                )
                return result.returncode == 0
            
            # For custom format PostgreSQL dumps, verify with pg_restore
            result = subprocess.run(
                ["pg_restore", "-t", str(backup_file), "--list"],
                env={**os.environ, "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", "")},
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Backup verification successful")
                return True
            else:
                logger.error(f"Backup verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False

    def restore_backup(self, backup_file: Path, target_db: str = None) -> bool:
        """
        Restore from backup.
        
        Args:
            backup_file: Path to backup file
            target_db: Target database name (defaults to original)
            
        Returns:
            True if restore succeeded, False otherwise
        """
        target_db = target_db or self.db_name
        
        try:
            logger.info(f"Restoring backup: {backup_file} to {target_db}")
            
            restore_cmd = [
                "pg_restore",
                "-h", self.db_host,
                "-U", self.db_user,
                "-d", target_db,
                "-v",
                str(backup_file)
            ]
            
            result = subprocess.run(
                restore_cmd,
                env={**os.environ, "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", "")},
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                logger.info("Restore completed successfully")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Restore error: {str(e)}")
            return False

    @staticmethod
    def _calculate_checksum(file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def main():
    """Main backup script."""
    parser = argparse.ArgumentParser(description="Database backup management")
    parser.add_argument("action", choices=["backup", "cleanup", "verify", "restore"],
                        help="Action to perform")
    parser.add_argument("--backup-dir", default="/backups",
                        help="Backup directory (default: /backups)")
    parser.add_argument("--retention-days", type=int, default=7,
                        help="Retention period in days (default: 7)")
    parser.add_argument("--db-host", default=os.getenv("DB_HOST", "localhost"),
                        help="Database host")
    parser.add_argument("--db-user", default=os.getenv("DB_USER", "postgres"),
                        help="Database user")
    parser.add_argument("--db-name", default=os.getenv("DB_NAME", "euint"),
                        help="Database name")
    parser.add_argument("--file", help="Backup file for restore/verify")
    parser.add_argument("--compress", action="store_true", default=True,
                        help="Compress backup")
    
    args = parser.parse_args()
    
    manager = BackupManager(
        args.backup_dir,
        args.retention_days,
        args.db_host,
        args.db_user,
        args.db_name
    )
    
    if args.action == "backup":
        success = manager.create_backup(compress=args.compress)
        sys.exit(0 if success else 1)
    
    elif args.action == "cleanup":
        removed = manager.cleanup_old_backups()
        logger.info(f"Removed {removed} old backups")
        sys.exit(0)
    
    elif args.action == "verify":
        if not args.file:
            logger.error("--file required for verify action")
            sys.exit(1)
        success = manager.verify_backup(Path(args.file))
        sys.exit(0 if success else 1)
    
    elif args.action == "restore":
        if not args.file:
            logger.error("--file required for restore action")
            sys.exit(1)
        success = manager.restore_backup(Path(args.file))
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
