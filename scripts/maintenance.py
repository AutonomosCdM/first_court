"""
Automated maintenance script for First Court.
Handles routine maintenance tasks and system cleanup.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List
import json

class MaintenanceManager:
    def __init__(self):
        self.project_root = Path('/Users/autonomos_dev/Projects/first_court')
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for maintenance tasks."""
        logs_dir = self.project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f"maintenance_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Maintenance')
    
    def cleanup_old_logs(self, days: int = 7):
        """Remove log files older than specified days."""
        self.logger.info(f"Cleaning up logs older than {days} days")
        logs_dir = self.project_root / 'logs'
        
        if not logs_dir.exists():
            return
            
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in logs_dir.glob('*.log'):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                log_file.unlink()
                self.logger.info(f"Removed old log file: {log_file}")
    
    def cleanup_temp_files(self):
        """Remove temporary files and directories."""
        self.logger.info("Cleaning up temporary files")
        temp_dirs = [
            self.project_root / '__pycache__',
            self.project_root / '.pytest_cache',
            self.project_root / 'build',
            self.project_root / 'dist'
        ]
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.info(f"Removed temporary directory: {temp_dir}")
    
    def verify_dependencies(self):
        """Verify and log dependency versions."""
        self.logger.info("Verifying dependencies")
        
        # Check poetry.lock
        poetry_lock = self.project_root / 'poetry.lock'
        if poetry_lock.exists():
            self.logger.info("Poetry lock file found")
        else:
            self.logger.warning("Poetry lock file missing")
    
    def backup_config_files(self):
        """Backup important configuration files."""
        self.logger.info("Backing up configuration files")
        backup_dir = self.project_root / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"config_backup_{timestamp}"
        backup_path.mkdir()
        
        config_files = [
            'pyproject.toml',
            'poetry.lock',
            '.env.example',
            'docker-compose.yml'
        ]
        
        for file in config_files:
            src = self.project_root / file
            if src.exists():
                shutil.copy2(src, backup_path / file)
                self.logger.info(f"Backed up {file}")
    
    def run_maintenance(self):
        """Run all maintenance tasks."""
        self.logger.info("Starting maintenance tasks")
        
        try:
            self.cleanup_old_logs()
            self.cleanup_temp_files()
            self.verify_dependencies()
            self.backup_config_files()
            
            self.logger.info("Maintenance tasks completed successfully")
        except Exception as e:
            self.logger.error(f"Maintenance failed: {str(e)}")
            raise

if __name__ == '__main__':
    maintenance = MaintenanceManager()
    maintenance.run_maintenance()
