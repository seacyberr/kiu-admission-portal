#!/usr/bin/env python3
"""
Database Backup Strategy for KIU Admission Portal
Supports: PostgreSQL backups with compression, rotation, and cloud upload
"""
import os
import sys
import gzip
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/backups"))
RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
DB_HOST = os.environ.get("PGHOST", "localhost")
DB_USER = os.environ.get("PGUSER", "kiu_user")
DB_NAME = os.environ.get("PGDATABASE", "kiu_portal")
DB_PASSWORD = os.environ.get("PGPASSWORD", "")

# Cloud storage (optional)
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
S3_BUCKET = os.environ.get("S3_BACKUP_BUCKET", "")

# Google Cloud (optional)
GCS_BUCKET = os.environ.get("GCS_BACKUP_BUCKET", "")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")


def ensure_backup_dir():
    """Ensure backup directory exists"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup directory: {BACKUP_DIR}")


def create_backup_filename():
    """Generate backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"kiu_portal_backup_{timestamp}.sql"


def run_pg_dump(output_file: Path) -> bool:
    """Run pg_dump to create database backup"""
    try:
        env = os.environ.copy()
        if DB_PASSWORD:
            env["PGPASSWORD"] = DB_PASSWORD
        
        cmd = [
            "pg_dump",
            "-h", DB_HOST,
            "-U", DB_USER,
            "-d", DB_NAME,
            "--verbose",
            "--no-owner",
            "--no-acl",
            "-f", str(output_file)
        ]
        
        logger.info(f"Running pg_dump: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"pg_dump completed successfully: {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"pg_dump failed: {e}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during pg_dump: {e}")
        return False


def compress_backup(input_file: Path) -> Path:
    """Compress backup file using gzip"""
    compressed_file = input_file.with_suffix(".sql.gz")
    
    try:
        with open(input_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed file
        input_file.unlink()
        
        # Log compression stats
        original_size = input_file.stat().st_size if input_file.exists() else 0
        compressed_size = compressed_file.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        logger.info(
            f"Compressed: {compressed_file.name} "
            f"({compressed_size / 1024 / 1024:.2f} MB, "
            f"saved {compression_ratio:.1f}%)"
        )
        
        return compressed_file
        
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        return input_file


def upload_to_s3(file_path: Path) -> bool:
    """Upload backup to AWS S3"""
    if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET]):
        logger.info("S3 credentials not configured, skipping S3 upload")
        return False
    
    try:
        import boto3
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        
        s3_key = f"backups/{file_path.name}"
        
        logger.info(f"Uploading to S3: {S3_BUCKET}/{s3_key}")
        s3_client.upload_file(
            str(file_path),
            S3_BUCKET,
            s3_key,
            ExtraArgs={
                'ServerSideEncryption': 'AES256',
                'StorageClass': 'STANDARD_IA'  # Infrequent access for cost savings
            }
        )
        
        logger.info("S3 upload completed successfully")
        return True
        
    except ImportError:
        logger.warning("boto3 not installed, skipping S3 upload")
        return False
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        return False


def upload_to_gcs(file_path: Path) -> bool:
    """Upload backup to Google Cloud Storage"""
    if not all([GCS_BUCKET, GOOGLE_APPLICATION_CREDENTIALS]):
        logger.info("GCS credentials not configured, skipping GCS upload")
        return False
    
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(f"backups/{file_path.name}")
        
        logger.info(f"Uploading to GCS: {GCS_BUCKET}/backups/{file_path.name}")
        blob.upload_from_filename(str(file_path))
        
        logger.info("GCS upload completed successfully")
        return True
        
    except ImportError:
        logger.warning("google-cloud-storage not installed, skipping GCS upload")
        return False
    except Exception as e:
        logger.error(f"GCS upload failed: {e}")
        return False


def cleanup_old_backups():
    """Remove backups older than retention period"""
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    
    deleted_count = 0
    total_freed = 0
    
    for backup_file in BACKUP_DIR.glob("kiu_portal_backup_*.sql*"):
        try:
            # Extract date from filename
            filename = backup_file.name
            date_str = filename.replace("kiu_portal_backup_", "").split(".")[0]
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            
            if file_date < cutoff_date:
                file_size = backup_file.stat().st_size
                backup_file.unlink()
                deleted_count += 1
                total_freed += file_size
                logger.info(f"Deleted old backup: {filename}")
                
        except (ValueError, OSError) as e:
            logger.warning(f"Could not process {backup_file}: {e}")
    
    if deleted_count > 0:
        logger.info(
            f"Cleanup complete: Deleted {deleted_count} old backups, "
            f"freed {total_freed / 1024 / 1024:.2f} MB"
        )


def create_backup_info(backup_file: Path) -> dict:
    """Create metadata about the backup"""
    return {
        "filename": backup_file.name,
        "created_at": datetime.now().isoformat(),
        "size_bytes": backup_file.stat().st_size,
        "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2),
        "database": DB_NAME,
        "host": DB_HOST,
        "compressed": backup_file.suffix == ".gz"
    }


def main():
    """Main backup process"""
    logger.info("=" * 60)
    logger.info("KIU Portal Database Backup Started")
    logger.info("=" * 60)
    
    # Ensure backup directory exists
    ensure_backup_dir()
    
    # Create backup filename
    backup_filename = create_backup_filename()
    backup_path = BACKUP_DIR / backup_filename
    
    # Run pg_dump
    if not run_pg_dump(backup_path):
        logger.error("Backup failed!")
        sys.exit(1)
    
    # Compress backup
    compressed_path = compress_backup(backup_path)
    
    # Upload to cloud storage
    s3_success = upload_to_s3(compressed_path)
    gcs_success = upload_to_gcs(compressed_path)
    
    # Cleanup old backups
    cleanup_old_backups()
    
    # Log backup info
    backup_info = create_backup_info(compressed_path)
    logger.info("=" * 60)
    logger.info("Backup Summary:")
    logger.info(f"  File: {backup_info['filename']}")
    logger.info(f"  Size: {backup_info['size_mb']} MB")
    logger.info(f"  S3 Upload: {'✓' if s3_success else '✗'}")
    logger.info(f"  GCS Upload: {'✓' if gcs_success else '✗'}")
    logger.info("=" * 60)
    logger.info("Backup completed successfully!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
