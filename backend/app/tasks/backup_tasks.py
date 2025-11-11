"""Database backup and maintenance tasks."""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from celery import shared_task
from app.database import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def daily_database_backup(self):
    """
    Perform daily database backup.

    Runs daily and creates a compressed backup of the database.
    Automatically cleans up old backups based on retention policy.
    """
    try:
        logger.info("Starting daily database backup...")

        backup_dir = "/backups"
        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/backup_{timestamp}.sql.gz"

        # Create backup
        db_url = engine.url
        cmd = [
            "pg_dump",
            "-h",
            db_url.host or "localhost",
            "-U",
            db_url.username or "postgres",
            "-d",
            db_url.database or "euint",
            "-F",
            "c",  # Custom format
            "-v",  # Verbose
        ]

        # Pipe through gzip for compression
        with open(backup_file, "wb") as f:
            dump_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False
            )

            gzip_process = subprocess.Popen(
                ["gzip", "-9"],
                stdin=dump_process.stdout,
                stdout=f,
                stderr=subprocess.PIPE,
            )

            dump_process.stdout.close()
            _, gzip_err = gzip_process.communicate()

            if gzip_process.returncode != 0:
                logger.error(f"Backup compression failed: {gzip_err}")
                raise Exception("Backup compression failed")

        file_size = Path(backup_file).stat().st_size / (1024 * 1024)
        logger.info(
            f"Daily database backup completed: {backup_file} ({file_size:.2f}MB)"
        )

        return {
            "status": "success",
            "backup_file": backup_file,
            "size_mb": round(file_size, 2),
            "timestamp": timestamp,
        }

    except Exception as exc:
        logger.error(f"Daily backup failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=3600)  # Retry in 1 hour


@shared_task(bind=True)
def cleanup_old_backups(self, retention_days: int = 7):
    """
    Clean up backups older than retention period.

    Args:
        retention_days: Number of days to retain backups
    """
    try:
        logger.info(f"Starting backup cleanup (retention: {retention_days} days)...")

        backup_dir = Path("/backups")
        if not backup_dir.exists():
            return {"status": "no_backups"}

        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=retention_days)

        removed_count = 0
        total_freed_mb = 0

        for backup_file in backup_dir.glob("backup_*.sql*"):
            file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

            if file_mtime < cutoff_date:
                try:
                    file_size_mb = backup_file.stat().st_size / (1024 * 1024)
                    backup_file.unlink()
                    logger.info(
                        f"Deleted old backup: {backup_file.name} ({file_size_mb:.2f}MB)"
                    )
                    removed_count += 1
                    total_freed_mb += file_size_mb
                except OSError as e:
                    logger.error(f"Failed to delete backup {backup_file.name}: {e}")

        logger.info(
            f"Backup cleanup completed: removed {removed_count} files, freed {total_freed_mb:.2f}MB"
        )

        return {
            "status": "success",
            "removed_count": removed_count,
            "freed_mb": round(total_freed_mb, 2),
        }

    except Exception as exc:
        logger.error(f"Backup cleanup failed: {str(exc)}")
        return {"status": "error", "error": str(exc)}


@shared_task
def verify_backup_integrity(backup_file: str) -> dict:
    """
    Verify the integrity of a backup file.

    Args:
        backup_file: Path to backup file

    Returns:
        Verification result
    """
    try:
        logger.info(f"Verifying backup: {backup_file}")

        file_path = Path(backup_file)
        if not file_path.exists():
            return {"status": "error", "error": "Backup file not found"}

        # For gzip files, test compression integrity
        if file_path.suffix == ".gz":
            result = subprocess.run(
                ["gzip", "-t", backup_file], capture_output=True, timeout=300
            )

            if result.returncode == 0:
                file_size = file_path.stat().st_size / (1024 * 1024)
                logger.info(
                    f"Backup verification successful: {backup_file} ({file_size:.2f}MB)"
                )
                return {
                    "status": "success",
                    "integrity": "valid",
                    "size_mb": round(file_size, 2),
                }
            else:
                logger.error(f"Backup verification failed: {result.stderr.decode()}")
                return {
                    "status": "error",
                    "integrity": "invalid",
                    "error": "Compression integrity check failed",
                }

        return {"status": "success", "integrity": "valid"}

    except Exception as exc:
        logger.error(f"Backup verification error: {str(exc)}")
        return {"status": "error", "error": str(exc)}


@shared_task
def database_health_check() -> dict:
    """
    Perform database health check.

    Returns:
        Health check result
    """
    try:
        from app.database import SessionLocal

        db = SessionLocal()

        # Test basic connectivity
        result = db.execute(text("SELECT 1"))

        # Get database size
        db_size = db.execute(
            text("SELECT pg_database_size(current_database())")
        ).scalar()

        # Get table count
        table_count = db.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
            )
        ).scalar()

        # Get active connections
        active_connections = db.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        ).scalar()

        total_sources = db.execute(text("SELECT COUNT(*) FROM news_sources")).scalar()
        total_enabled_sources = db.execute(
            text("SELECT COUNT(*) FROM news_sources WHERE enabled = TRUE")
        ).scalar()

        db.close()

        return {
            "status": "healthy",
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "table_count": table_count,
            "active_connections": active_connections,
            "total_sources": total_sources,
            "enabled_sources": total_enabled_sources,
        }

    except Exception as exc:
        logger.error(f"Database health check failed: {str(exc)}")
        return {"status": "unhealthy", "error": str(exc)}
