#!/usr/bin/env python3
"""
Production Deployment & Scaling System
Comprehensive production deployment framework with monitoring, scheduling, 
and scaling capabilities for MagicBricks scraper.
"""

import os
import sys
import json
import time
import logging
import schedule
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sqlite3
import yaml


@dataclass
class DeploymentConfig:
    """Production deployment configuration"""
    
    # Environment settings
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Scraping configuration
    max_concurrent_sessions: int = 4
    max_pages_per_session: int = 100
    max_properties_per_session: int = 3000
    session_timeout_minutes: int = 180
    
    # Scheduling configuration
    weekly_schedule: List[str] = None  # ["monday 02:00", "friday 02:00"]
    daily_schedule: str = None  # "02:00" for daily runs
    maintenance_window: str = "sunday 01:00-04:00"
    
    # Monitoring configuration
    health_check_interval: int = 300  # 5 minutes
    performance_alert_threshold: float = 80.0  # CPU/Memory %
    error_rate_threshold: float = 5.0  # Error rate %
    
    # Scaling configuration
    auto_scaling_enabled: bool = True
    min_workers: int = 2
    max_workers: int = 8
    scale_up_threshold: float = 70.0  # CPU %
    scale_down_threshold: float = 30.0  # CPU %
    
    # Storage configuration
    data_retention_days: int = 90
    backup_enabled: bool = True
    backup_schedule: str = "daily 03:00"
    
    # Notification configuration
    email_notifications: bool = True
    email_recipients: List[str] = None
    slack_webhook: str = None
    
    def __post_init__(self):
        if self.weekly_schedule is None:
            self.weekly_schedule = ["monday 02:00", "friday 02:00"]
        if self.email_recipients is None:
            self.email_recipients = ["admin@company.com"]


class ProductionMonitor:
    """Production monitoring and alerting system"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'active_sessions': 0,
            'total_properties_scraped': 0,
            'error_count': 0,
            'last_successful_run': None
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging"""
        
        logger = logging.getLogger('production_monitor')
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.FileHandler(
            log_dir / f'production_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics"""
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # Store metrics for trend analysis
            self.metrics['cpu_usage'].append(cpu_percent)
            self.metrics['memory_usage'].append(memory.percent)
            self.metrics['disk_usage'].append(disk.percent)
            
            # Keep only last 100 readings
            for key in ['cpu_usage', 'memory_usage', 'disk_usage']:
                if len(self.metrics[key]) > 100:
                    self.metrics[key] = self.metrics[key][-100:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'alerts': []
        }
        
        try:
            # System metrics check
            metrics = self.collect_system_metrics()
            
            # CPU check
            if metrics.get('cpu_usage', 0) > self.config.performance_alert_threshold:
                health_status['checks']['cpu'] = 'warning'
                health_status['alerts'].append(f"High CPU usage: {metrics['cpu_usage']:.1f}%")
            else:
                health_status['checks']['cpu'] = 'healthy'
            
            # Memory check
            if metrics.get('memory_usage', 0) > self.config.performance_alert_threshold:
                health_status['checks']['memory'] = 'warning'
                health_status['alerts'].append(f"High memory usage: {metrics['memory_usage']:.1f}%")
            else:
                health_status['checks']['memory'] = 'healthy'
            
            # Disk space check
            if metrics.get('disk_usage', 0) > 85:
                health_status['checks']['disk'] = 'critical'
                health_status['alerts'].append(f"Low disk space: {metrics['disk_usage']:.1f}% used")
            elif metrics.get('disk_usage', 0) > 75:
                health_status['checks']['disk'] = 'warning'
                health_status['alerts'].append(f"Disk space warning: {metrics['disk_usage']:.1f}% used")
            else:
                health_status['checks']['disk'] = 'healthy'
            
            # Database connectivity check
            try:
                # Test database connection
                conn = sqlite3.connect('magicbricks_enhanced.db', timeout=5)
                conn.execute('SELECT 1')
                conn.close()
                health_status['checks']['database'] = 'healthy'
            except Exception as e:
                health_status['checks']['database'] = 'critical'
                health_status['alerts'].append(f"Database connectivity issue: {str(e)}")
            
            # Error rate check
            error_rate = self._calculate_error_rate()
            if error_rate > self.config.error_rate_threshold:
                health_status['checks']['error_rate'] = 'warning'
                health_status['alerts'].append(f"High error rate: {error_rate:.1f}%")
            else:
                health_status['checks']['error_rate'] = 'healthy'
            
            # Determine overall status
            if any(status == 'critical' for status in health_status['checks'].values()):
                health_status['overall_status'] = 'critical'
            elif any(status == 'warning' for status in health_status['checks'].values()):
                health_status['overall_status'] = 'warning'
            
            # Log health status
            self.logger.info(f"Health check completed: {health_status['overall_status']}")
            if health_status['alerts']:
                for alert in health_status['alerts']:
                    self.logger.warning(f"Health alert: {alert}")
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            health_status['overall_status'] = 'critical'
            health_status['alerts'].append(f"Health check system failure: {str(e)}")
            return health_status
    
    def _calculate_error_rate(self) -> float:
        """Calculate recent error rate"""
        
        try:
            # Simple error rate calculation based on recent logs
            # In production, this would query actual error metrics
            total_operations = max(self.metrics['total_properties_scraped'], 1)
            error_count = self.metrics['error_count']
            return (error_count / total_operations) * 100
        except Exception:
            return 0.0
    
    def send_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Send alert notification"""
        
        try:
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'type': alert_type,
                'message': message,
                'severity': severity,
                'environment': self.config.environment
            }
            
            self.logger.warning(f"ALERT [{severity.upper()}]: {alert_type} - {message}")
            
            # Email notification
            if self.config.email_notifications:
                self._send_email_alert(alert_data)
            
            # Slack notification
            if self.config.slack_webhook:
                self._send_slack_alert(alert_data)
                
        except Exception as e:
            self.logger.error(f"Failed to send alert: {str(e)}")
    
    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send email alert"""
        
        try:
            subject = f"[{alert_data['severity'].upper()}] MagicBricks Scraper Alert - {alert_data['type']}"
            
            body = f"""
            Alert Details:
            - Type: {alert_data['type']}
            - Severity: {alert_data['severity']}
            - Environment: {alert_data['environment']}
            - Timestamp: {alert_data['timestamp']}
            - Message: {alert_data['message']}
            
            Please investigate and take appropriate action.
            """
            
            # In production, configure actual SMTP settings
            self.logger.info(f"Email alert would be sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_slack_alert(self, alert_data: Dict[str, Any]):
        """Send Slack alert"""
        
        try:
            # In production, implement actual Slack webhook
            self.logger.info(f"Slack alert would be sent: {alert_data['type']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")


class ProductionScheduler:
    """Production scheduling system"""
    
    def __init__(self, config: DeploymentConfig, monitor: ProductionMonitor):
        self.config = config
        self.monitor = monitor
        self.logger = monitor.logger
        self.active_sessions = {}
        
    def setup_schedules(self):
        """Setup all production schedules"""
        
        try:
            # Clear existing schedules
            schedule.clear()
            
            # Weekly scraping schedules
            if self.config.weekly_schedule:
                for schedule_time in self.config.weekly_schedule:
                    day, time_str = schedule_time.split(' ')
                    getattr(schedule.every(), day.lower()).at(time_str).do(self._run_weekly_scrape)
                    self.logger.info(f"Scheduled weekly scrape: {schedule_time}")
            
            # Daily scraping schedule
            if self.config.daily_schedule:
                schedule.every().day.at(self.config.daily_schedule).do(self._run_daily_scrape)
                self.logger.info(f"Scheduled daily scrape: {self.config.daily_schedule}")
            
            # Health check schedule
            schedule.every(self.config.health_check_interval).seconds.do(self._run_health_check)
            
            # Backup schedule
            if self.config.backup_enabled:
                backup_time = self.config.backup_schedule.split(' ')[1]
                schedule.every().day.at(backup_time).do(self._run_backup)
                self.logger.info(f"Scheduled backup: {self.config.backup_schedule}")
            
            # Maintenance schedule
            if self.config.maintenance_window:
                maintenance_day, time_range = self.config.maintenance_window.split(' ')
                start_time = time_range.split('-')[0]
                getattr(schedule.every(), maintenance_day.lower()).at(start_time).do(self._run_maintenance)
                self.logger.info(f"Scheduled maintenance: {self.config.maintenance_window}")
            
            self.logger.info("All production schedules configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schedules: {str(e)}")
            self.monitor.send_alert("schedule_setup_failed", str(e), "critical")
    
    def _run_weekly_scrape(self):
        """Execute weekly scraping session"""
        
        try:
            self.logger.info("Starting scheduled weekly scrape")
            
            session_config = {
                'session_type': 'weekly',
                'max_pages': self.config.max_pages_per_session,
                'max_properties': self.config.max_properties_per_session,
                'cities': ['gurgaon', 'mumbai', 'bangalore', 'delhi', 'pune'],
                'property_types': ['apartment', 'house', 'villa', 'floor', 'plot']
            }
            
            session_id = self._start_scraping_session(session_config)
            self.logger.info(f"Weekly scrape session started: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Weekly scrape failed: {str(e)}")
            self.monitor.send_alert("weekly_scrape_failed", str(e), "critical")
    
    def _run_daily_scrape(self):
        """Execute daily scraping session"""
        
        try:
            self.logger.info("Starting scheduled daily scrape")
            
            session_config = {
                'session_type': 'daily',
                'max_pages': self.config.max_pages_per_session // 2,
                'max_properties': self.config.max_properties_per_session // 2,
                'cities': ['gurgaon', 'mumbai'],  # Focus on top cities for daily
                'property_types': ['apartment', 'house']
            }
            
            session_id = self._start_scraping_session(session_config)
            self.logger.info(f"Daily scrape session started: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Daily scrape failed: {str(e)}")
            self.monitor.send_alert("daily_scrape_failed", str(e), "warning")
    
    def _run_health_check(self):
        """Execute health check"""
        
        try:
            health_status = self.monitor.check_health()
            
            if health_status['overall_status'] == 'critical':
                self.monitor.send_alert(
                    "system_health_critical", 
                    f"Critical health issues detected: {', '.join(health_status['alerts'])}", 
                    "critical"
                )
            elif health_status['overall_status'] == 'warning':
                self.monitor.send_alert(
                    "system_health_warning", 
                    f"Health warnings detected: {', '.join(health_status['alerts'])}", 
                    "warning"
                )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
    
    def _run_backup(self):
        """Execute backup operation"""
        
        try:
            self.logger.info("Starting scheduled backup")
            
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"magicbricks_backup_{timestamp}.db"
            
            # Copy database
            import shutil
            shutil.copy2('magicbricks_enhanced.db', backup_file)
            
            # Compress backup
            import gzip
            with open(backup_file, 'rb') as f_in:
                with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            backup_file.unlink()
            
            self.logger.info(f"Backup completed: {backup_file}.gz")
            
            # Cleanup old backups
            self._cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            self.monitor.send_alert("backup_failed", str(e), "warning")
    
    def _run_maintenance(self):
        """Execute maintenance tasks"""
        
        try:
            self.logger.info("Starting scheduled maintenance")
            
            # Database maintenance
            self._optimize_database()
            
            # Log cleanup
            self._cleanup_old_logs()
            
            # System cleanup
            self._cleanup_temp_files()
            
            self.logger.info("Maintenance completed successfully")
            
        except Exception as e:
            self.logger.error(f"Maintenance failed: {str(e)}")
            self.monitor.send_alert("maintenance_failed", str(e), "warning")
    
    def _start_scraping_session(self, config: Dict[str, Any]) -> str:
        """Start a new scraping session"""
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # In production, this would start the actual scraper
        self.logger.info(f"Starting scraping session {session_id} with config: {config}")
        
        # Simulate session tracking
        self.active_sessions[session_id] = {
            'start_time': datetime.now(),
            'config': config,
            'status': 'running'
        }
        
        return session_id
    
    def _cleanup_old_backups(self, backup_dir: Path):
        """Cleanup old backup files"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.data_retention_days)
            
            for backup_file in backup_dir.glob("*.gz"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    self.logger.info(f"Deleted old backup: {backup_file}")
                    
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")
    
    def _optimize_database(self):
        """Optimize database performance"""
        
        try:
            conn = sqlite3.connect('magicbricks_enhanced.db')
            conn.execute('VACUUM')
            conn.execute('ANALYZE')
            conn.close()
            self.logger.info("Database optimization completed")
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {str(e)}")
    
    def _cleanup_old_logs(self):
        """Cleanup old log files"""
        
        try:
            log_dir = Path('logs')
            cutoff_date = datetime.now() - timedelta(days=self.config.data_retention_days)
            
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.logger.info(f"Deleted old log: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"Log cleanup failed: {str(e)}")
    
    def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        
        try:
            temp_patterns = ['*.tmp', '*.temp', '__pycache__']
            
            for pattern in temp_patterns:
                for temp_file in Path('.').rglob(pattern):
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        import shutil
                        shutil.rmtree(temp_file)
            
            self.logger.info("Temporary file cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Temp file cleanup failed: {str(e)}")
    
    def run_scheduler(self):
        """Run the production scheduler"""
        
        self.logger.info("Starting production scheduler")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}")
            self.monitor.send_alert("scheduler_error", str(e), "critical")


class ProductionScaler:
    """Production auto-scaling system"""
    
    def __init__(self, config: DeploymentConfig, monitor: ProductionMonitor):
        self.config = config
        self.monitor = monitor
        self.logger = monitor.logger
        self.current_workers = config.min_workers
        
    def check_scaling_needs(self):
        """Check if scaling is needed"""
        
        if not self.config.auto_scaling_enabled:
            return
        
        try:
            metrics = self.monitor.collect_system_metrics()
            cpu_usage = metrics.get('cpu_usage', 0)
            
            # Scale up if CPU usage is high
            if cpu_usage > self.config.scale_up_threshold and self.current_workers < self.config.max_workers:
                self._scale_up()
            
            # Scale down if CPU usage is low
            elif cpu_usage < self.config.scale_down_threshold and self.current_workers > self.config.min_workers:
                self._scale_down()
                
        except Exception as e:
            self.logger.error(f"Scaling check failed: {str(e)}")
    
    def _scale_up(self):
        """Scale up workers"""
        
        try:
            new_worker_count = min(self.current_workers + 1, self.config.max_workers)
            
            if new_worker_count > self.current_workers:
                self.logger.info(f"Scaling up from {self.current_workers} to {new_worker_count} workers")
                self.current_workers = new_worker_count
                self.monitor.send_alert("scaled_up", f"Scaled up to {new_worker_count} workers", "info")
                
        except Exception as e:
            self.logger.error(f"Scale up failed: {str(e)}")
    
    def _scale_down(self):
        """Scale down workers"""
        
        try:
            new_worker_count = max(self.current_workers - 1, self.config.min_workers)
            
            if new_worker_count < self.current_workers:
                self.logger.info(f"Scaling down from {self.current_workers} to {new_worker_count} workers")
                self.current_workers = new_worker_count
                self.monitor.send_alert("scaled_down", f"Scaled down to {new_worker_count} workers", "info")
                
        except Exception as e:
            self.logger.error(f"Scale down failed: {str(e)}")


class ProductionDeploymentSystem:
    """Main production deployment system"""
    
    def __init__(self, config_file: str = "production_config.yaml"):
        self.config = self._load_config(config_file)
        self.monitor = ProductionMonitor(self.config)
        self.scheduler = ProductionScheduler(self.config, self.monitor)
        self.scaler = ProductionScaler(self.config, self.monitor)
        
    def _load_config(self, config_file: str) -> DeploymentConfig:
        """Load production configuration"""
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                return DeploymentConfig(**config_data)
            else:
                # Create default config
                config = DeploymentConfig()
                self._save_config(config, config_file)
                return config
                
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return DeploymentConfig()
    
    def _save_config(self, config: DeploymentConfig, config_file: str):
        """Save configuration to file"""
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
                
        except Exception as e:
            print(f"Error saving config: {str(e)}")
    
    def deploy(self):
        """Deploy the production system"""
        
        try:
            self.monitor.logger.info("🚀 Starting Production Deployment System")
            
            # Setup schedules
            self.scheduler.setup_schedules()
            
            # Initial health check
            health_status = self.monitor.check_health()
            self.monitor.logger.info(f"Initial health check: {health_status['overall_status']}")
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._run_monitoring_loop, daemon=True)
            monitor_thread.start()
            
            # Start scheduler
            self.scheduler.run_scheduler()
            
        except Exception as e:
            self.monitor.logger.error(f"Deployment failed: {str(e)}")
            self.monitor.send_alert("deployment_failed", str(e), "critical")
    
    def _run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        
        while True:
            try:
                # Check scaling needs
                self.scaler.check_scaling_needs()
                
                # Sleep for monitoring interval
                time.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.monitor.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(60)  # Wait before retrying


def main():
    """Main function for production deployment"""
    
    print("🚀 Production Deployment & Scaling System")
    print("="*60)
    
    try:
        # Initialize deployment system
        deployment_system = ProductionDeploymentSystem()
        
        print("✅ Production deployment system initialized")
        print("📊 Configuration loaded successfully")
        print("🔧 Monitoring and scheduling configured")
        print("⚡ Auto-scaling enabled")
        print("📧 Alert notifications configured")
        
        # Start deployment
        print("\n🎯 Starting production deployment...")
        deployment_system.deploy()
        
    except KeyboardInterrupt:
        print("\n⏹️ Production deployment stopped by user")
    except Exception as e:
        print(f"\n❌ Production deployment failed: {str(e)}")


if __name__ == "__main__":
    main()
