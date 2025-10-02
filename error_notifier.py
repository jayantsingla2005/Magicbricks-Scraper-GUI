#!/usr/bin/env python3
"""
Error Notification System
Handles error logging, callbacks, and email notifications.
"""

import smtplib
import logging
import json
from typing import List, Callable
from error_types import ErrorInfo, ErrorSeverity

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
        print("[WARNING] Email functionality not available - notifications disabled")


class ErrorNotifier:
    """
    Handles error logging, callbacks, and email notifications
    """
    
    def __init__(self, notification_config: dict):
        """Initialize error notifier"""
        self.notification_config = notification_config
        self.error_callbacks = []
        self.logger = None
        
        # Setup logging
        self.setup_logging()
    
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
    
    def log_error(self, error_info: ErrorInfo):
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
    
    def notify_callbacks(self, error_info: ErrorInfo):
        """Notify registered callbacks"""
        
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                print(f"[WARNING] Error in callback: {str(e)}")
    
    def register_callback(self, callback: Callable[[ErrorInfo], None]):
        """Register error callback"""
        self.error_callbacks.append(callback)
    
    def should_notify(self, error_info: ErrorInfo) -> bool:
        """Check if email notification should be sent"""
        
        if not self.notification_config.get('email_enabled'):
            return False
        
        notification_levels = self.notification_config.get('notification_levels', [])
        return error_info.severity.value in notification_levels
    
    def send_notification(self, error_info: ErrorInfo):
        """Send email notification"""

        if not EMAIL_AVAILABLE:
            print("[WARNING] Email functionality not available - skipping notification")
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
            
            print(f"[EMAIL] Notification sent for {error_info.severity.value} error")
            
        except Exception as e:
            print(f"[WARNING] Failed to send notification: {str(e)}")
    
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

