#!/usr/bin/env python3
"""
Error Handling & Notification System
Comprehensive error handling, user-friendly error display, and notification system for MagicBricks scraper.
"""

import smtplib
import logging
import traceback
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Email imports with fallback
try:
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    try:
        from email.MIMEText import MIMEText as MimeText
        from email.MIMEMultipart import MIMEMultipart as MimeMultipart
        EMAIL_AVAILABLE = True
    except ImportError:
        EMAIL_AVAILABLE = False
        print("⚠️ Email functionality not available - notifications disabled")


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    NETWORK = "network"
    PARSING = "parsing"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    SYSTEM = "system"
    USER_INPUT = "user_input"


@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    title: str
    message: str
    details: str
    suggestion: str
    context: Dict[str, Any]
    traceback_info: Optional[str] = None
    session_id: Optional[str] = None
    user_action: Optional[str] = None


class ErrorHandlingSystem:
    """
    Comprehensive error handling and notification system
    """
    
    def __init__(self, config_file: str = 'error_config.json'):
        """Initialize error handling system"""
        
        self.config_file = Path(config_file)
        self.error_log = []
        self.error_callbacks = []
        self.notification_config = {}
        
        # Load configuration
        self.load_configuration()
        
        # Setup logging
        self.setup_logging()
        
        # Error patterns and suggestions
        self.error_patterns = self._initialize_error_patterns()
        
        print("🛡️ Error Handling System Initialized")
        print(f"   📧 Email notifications: {'Enabled' if self.notification_config.get('email_enabled') else 'Disabled'}")
        print(f"   📝 Error logging: Enabled")
    
    def load_configuration(self):
        """Load error handling configuration"""
        
        default_config = {
            'email_enabled': False,
            'email_smtp_server': 'smtp.gmail.com',
            'email_smtp_port': 587,
            'email_username': '',
            'email_password': '',
            'email_recipients': [],
            'notification_levels': ['error', 'critical'],
            'max_error_log_size': 1000,
            'auto_recovery_enabled': True,
            'detailed_logging': True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"⚠️ Error loading config: {str(e)}, using defaults")
        
        self.notification_config = default_config
    
    def save_configuration(self):
        """Save error handling configuration"""
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.notification_config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving config: {str(e)}")
    
    def setup_logging(self):
        """Setup enhanced logging system"""
        
        # Create custom logger
        self.logger = logging.getLogger('magicbricks_scraper')
        self.logger.setLevel(logging.DEBUG if self.notification_config.get('detailed_logging') else logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler('magicbricks_errors.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _initialize_error_patterns(self) -> Dict[str, Dict[str, str]]:
        """Initialize error patterns and suggestions"""
        
        return {
            'connection_error': {
                'pattern': ['connection', 'timeout', 'network', 'unreachable'],
                'category': ErrorCategory.NETWORK.value,
                'suggestion': 'Check your internet connection and try again. If the problem persists, the website might be temporarily unavailable.',
                'recovery': 'retry_with_delay'
            },
            'selenium_error': {
                'pattern': ['webdriver', 'selenium', 'chrome', 'browser'],
                'category': ErrorCategory.SYSTEM.value,
                'suggestion': 'Make sure Chrome browser is installed and updated. Try restarting the application.',
                'recovery': 'restart_browser'
            },
            'parsing_error': {
                'pattern': ['parsing', 'selector', 'element not found', 'beautifulsoup'],
                'category': ErrorCategory.PARSING.value,
                'suggestion': 'The website structure may have changed. This is usually temporary - try again later.',
                'recovery': 'use_fallback_selectors'
            },
            'database_error': {
                'pattern': ['database', 'sqlite', 'sql', 'table'],
                'category': ErrorCategory.DATABASE.value,
                'suggestion': 'Database connection issue. Check if the database file is accessible and not corrupted.',
                'recovery': 'recreate_database'
            },
            'validation_error': {
                'pattern': ['validation', 'invalid', 'format', 'type'],
                'category': ErrorCategory.VALIDATION.value,
                'suggestion': 'Please check your input values and try again with valid data.',
                'recovery': 'show_validation_help'
            },
            'permission_error': {
                'pattern': ['permission', 'access', 'denied', 'forbidden'],
                'category': ErrorCategory.SYSTEM.value,
                'suggestion': 'Permission denied. Try running as administrator or check file permissions.',
                'recovery': 'check_permissions'
            }
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    user_action: str = None, session_id: str = None) -> ErrorInfo:
        """Handle an error with comprehensive analysis and suggestions"""
        
        # Analyze error
        error_info = self._analyze_error(error, context, user_action, session_id)
        
        # Log error
        self._log_error(error_info)
        
        # Store in error log
        self.error_log.append(error_info)
        
        # Trim error log if too large
        if len(self.error_log) > self.notification_config.get('max_error_log_size', 1000):
            self.error_log = self.error_log[-500:]  # Keep last 500 errors
        
        # Notify callbacks
        self._notify_callbacks(error_info)
        
        # Send notifications if configured
        if self._should_notify(error_info):
            self._send_notification(error_info)
        
        return error_info
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any] = None,
                      user_action: str = None, session_id: str = None) -> ErrorInfo:
        """Analyze error and provide suggestions"""
        
        error_message = str(error)
        error_type = type(error).__name__
        
        # Determine severity
        severity = self._determine_severity(error, error_message)
        
        # Categorize error and get suggestions
        category, suggestion = self._categorize_error(error_message, error_type)
        
        # Create error info
        error_info = ErrorInfo(
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            title=f"{error_type}: {error_message[:100]}",
            message=error_message,
            details=self._get_error_details(error),
            suggestion=suggestion,
            context=context or {},
            traceback_info=traceback.format_exc(),
            session_id=session_id,
            user_action=user_action
        )
        
        return error_info
    
    def _determine_severity(self, error: Exception, message: str) -> ErrorSeverity:
        """Determine error severity"""
        
        critical_patterns = ['critical', 'fatal', 'system', 'memory', 'disk']
        error_patterns = ['error', 'failed', 'exception', 'invalid']
        warning_patterns = ['warning', 'deprecated', 'timeout', 'retry']
        
        message_lower = message.lower()
        
        if any(pattern in message_lower for pattern in critical_patterns):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (ConnectionError, TimeoutError, PermissionError)):
            return ErrorSeverity.ERROR
        elif any(pattern in message_lower for pattern in error_patterns):
            return ErrorSeverity.ERROR
        elif any(pattern in message_lower for pattern in warning_patterns):
            return ErrorSeverity.WARNING
        else:
            return ErrorSeverity.INFO
    
    def _categorize_error(self, message: str, error_type: str) -> tuple:
        """Categorize error and provide suggestion"""
        
        message_lower = message.lower()
        
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(pattern in message_lower for pattern in pattern_info['pattern']):
                category = ErrorCategory(pattern_info['category'])
                suggestion = pattern_info['suggestion']
                return category, suggestion
        
        # Default categorization
        if 'input' in message_lower or 'parameter' in message_lower:
            return ErrorCategory.USER_INPUT, "Please check your input parameters and try again."
        else:
            return ErrorCategory.SYSTEM, "An unexpected error occurred. Please try again or contact support."
    
    def _get_error_details(self, error: Exception) -> str:
        """Get detailed error information"""
        
        details = []
        details.append(f"Error Type: {type(error).__name__}")
        details.append(f"Error Message: {str(error)}")
        
        if hasattr(error, 'args') and error.args:
            details.append(f"Error Args: {error.args}")
        
        if hasattr(error, '__cause__') and error.__cause__:
            details.append(f"Caused by: {error.__cause__}")
        
        return "\n".join(details)
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error to file and console"""
        
        log_message = f"[{error_info.category.value.upper()}] {error_info.title}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log details if detailed logging is enabled
        if self.notification_config.get('detailed_logging'):
            self.logger.debug(f"Details: {error_info.details}")
            self.logger.debug(f"Context: {error_info.context}")
            if error_info.traceback_info:
                self.logger.debug(f"Traceback: {error_info.traceback_info}")
    
    def _notify_callbacks(self, error_info: ErrorInfo):
        """Notify registered callbacks"""
        
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                print(f"⚠️ Error in callback: {str(e)}")
    
    def _should_notify(self, error_info: ErrorInfo) -> bool:
        """Check if notification should be sent"""
        
        if not self.notification_config.get('email_enabled'):
            return False
        
        notification_levels = self.notification_config.get('notification_levels', [])
        return error_info.severity.value in notification_levels
    
    def _send_notification(self, error_info: ErrorInfo):
        """Send email notification"""

        if not EMAIL_AVAILABLE:
            print("⚠️ Email functionality not available - skipping notification")
            return

        try:
            # Create email message
            msg = MimeMultipart()
            msg['From'] = self.notification_config.get('email_username')
            msg['To'] = ', '.join(self.notification_config.get('email_recipients', []))
            msg['Subject'] = f"MagicBricks Scraper {error_info.severity.value.upper()}: {error_info.title}"
            
            # Email body
            body = self._create_email_body(error_info)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(
                self.notification_config.get('email_smtp_server'),
                self.notification_config.get('email_smtp_port')
            )
            server.starttls()
            server.login(
                self.notification_config.get('email_username'),
                self.notification_config.get('email_password')
            )
            
            text = msg.as_string()
            server.sendmail(
                self.notification_config.get('email_username'),
                self.notification_config.get('email_recipients'),
                text
            )
            server.quit()
            
            print(f"📧 Notification sent for {error_info.severity.value} error")
            
        except Exception as e:
            print(f"⚠️ Failed to send notification: {str(e)}")
    
    def _create_email_body(self, error_info: ErrorInfo) -> str:
        """Create HTML email body"""
        
        severity_colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#6f42c1'
        }
        
        color = severity_colors.get(error_info.severity.value, '#6c757d')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color}; margin-top: 0;">
                    {error_info.severity.value.upper()}: MagicBricks Scraper Error
                </h2>
                
                <p><strong>Time:</strong> {error_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Category:</strong> {error_info.category.value.title()}</p>
                <p><strong>Session ID:</strong> {error_info.session_id or 'N/A'}</p>
                <p><strong>User Action:</strong> {error_info.user_action or 'N/A'}</p>
                
                <h3>Error Details:</h3>
                <p style="background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {error_info.message}
                </p>
                
                <h3>Suggestion:</h3>
                <p style="background-color: #d4edda; padding: 10px; border-radius: 4px; color: #155724;">
                    {error_info.suggestion}
                </p>
                
                <h3>Context:</h3>
                <pre style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto;">
{json.dumps(error_info.context, indent=2)}
                </pre>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def register_callback(self, callback: Callable[[ErrorInfo], None]):
        """Register error callback"""
        self.error_callbacks.append(callback)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        
        if not self.error_log:
            return {'total_errors': 0}
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = len([e for e in self.error_log if e.severity == severity])
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = len([e for e in self.error_log if e.category == category])
        
        # Recent errors (last 24 hours)
        recent_errors = [
            e for e in self.error_log 
            if (datetime.now() - e.timestamp).total_seconds() < 86400
        ]
        
        return {
            'total_errors': len(self.error_log),
            'recent_errors': len(recent_errors),
            'severity_counts': severity_counts,
            'category_counts': category_counts,
            'last_error': self.error_log[-1].timestamp.isoformat() if self.error_log else None
        }
    
    def get_filtered_errors(self, severity: ErrorSeverity = None, 
                           category: ErrorCategory = None,
                           hours: int = None) -> List[ErrorInfo]:
        """Get filtered error list"""
        
        filtered_errors = self.error_log.copy()
        
        if severity:
            filtered_errors = [e for e in filtered_errors if e.severity == severity]
        
        if category:
            filtered_errors = [e for e in filtered_errors if e.category == category]
        
        if hours:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            filtered_errors = [e for e in filtered_errors if e.timestamp.timestamp() > cutoff_time]
        
        return filtered_errors
    
    def clear_error_log(self):
        """Clear error log"""
        self.error_log.clear()
        print("🗑️ Error log cleared")
    
    def export_error_log(self, filename: str = None) -> str:
        """Export error log to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_log_{timestamp}.json"
        
        try:
            export_data = []
            for error in self.error_log:
                export_data.append({
                    'timestamp': error.timestamp.isoformat(),
                    'severity': error.severity.value,
                    'category': error.category.value,
                    'title': error.title,
                    'message': error.message,
                    'details': error.details,
                    'suggestion': error.suggestion,
                    'context': error.context,
                    'session_id': error.session_id,
                    'user_action': error.user_action
                })
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"📁 Error log exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"⚠️ Error exporting log: {str(e)}")
            return None


def main():
    """Test the error handling system"""
    
    try:
        print("🧪 TESTING ERROR HANDLING SYSTEM")
        print("="*50)
        
        # Initialize system
        error_system = ErrorHandlingSystem()
        
        # Test different types of errors
        print("\n🔍 Testing error handling...")
        
        # Test network error
        try:
            raise ConnectionError("Failed to connect to magicbricks.com")
        except Exception as e:
            error_info = error_system.handle_error(e, {'url': 'https://magicbricks.com'}, 'scraping_start')
            print(f"Network error handled: {error_info.category.value} - {error_info.suggestion}")
        
        # Test parsing error
        try:
            raise ValueError("Element not found: div.property-card")
        except Exception as e:
            error_info = error_system.handle_error(e, {'page': 1, 'selector': 'div.property-card'}, 'property_extraction')
            print(f"Parsing error handled: {error_info.category.value} - {error_info.suggestion}")
        
        # Test validation error
        try:
            raise TypeError("Invalid city parameter: must be string")
        except Exception as e:
            error_info = error_system.handle_error(e, {'city': 123}, 'city_validation')
            print(f"Validation error handled: {error_info.category.value} - {error_info.suggestion}")
        
        # Test error summary
        print("\n📊 Error summary:")
        summary = error_system.get_error_summary()
        print(f"Total errors: {summary['total_errors']}")
        print(f"Recent errors: {summary['recent_errors']}")
        print(f"Severity counts: {summary['severity_counts']}")
        
        # Test export
        print("\n📁 Testing export...")
        export_file = error_system.export_error_log()
        if export_file:
            print(f"Export successful: {export_file}")
        
        print("\n✅ Error handling system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
