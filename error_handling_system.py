#!/usr/bin/env python3
"""
Error Handling & Notification System
Comprehensive error handling, user-friendly error display, and notification system for MagicBricks scraper.

REFACTORED: This file now uses composition pattern with specialized modules:
- error_types.py: Error severity, categories, and data classes
- error_analyzer.py: Error analysis and categorization
- error_notifier.py: Logging and email notifications
- error_statistics.py: Statistics, filtering, and export
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# Import modular components
from error_types import ErrorSeverity, ErrorCategory, ErrorInfo
from error_analyzer import ErrorAnalyzer
from error_notifier import ErrorNotifier
from error_statistics import ErrorStatistics


class ErrorHandlingSystem:
    """
    Comprehensive error handling and notification system

    REFACTORED: Uses composition pattern with specialized modules for:
    - Error analysis and categorization (ErrorAnalyzer)
    - Logging and notifications (ErrorNotifier)
    - Statistics and export (ErrorStatistics)

    Maintains 100% backward compatibility with original interface.
    """

    def __init__(self, config_file: str = 'error_config.json'):
        """Initialize error handling system with modular components"""

        self.config_file = Path(config_file)
        self.notification_config = {}

        # Load configuration
        self.load_configuration()

        # Initialize modular components
        self.analyzer = ErrorAnalyzer()
        self.notifier = ErrorNotifier(self.notification_config)
        self.statistics = ErrorStatistics(
            max_error_log_size=self.notification_config.get('max_error_log_size', 1000)
        )

        # Maintain backward compatibility
        self.error_log = self.statistics.error_log
        self.error_callbacks = self.notifier.error_callbacks
        self.error_patterns = self.analyzer.error_patterns
        self.logger = self.notifier.logger

        print("[SYSTEM] Error Handling System Initialized")
        print(f"   [EMAIL] Email notifications: {'Enabled' if self.notification_config.get('email_enabled') else 'Disabled'}")
        print(f"   [LOG] Error logging: Enabled")
    
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
                print(f"[WARNING] Error loading config: {str(e)}, using defaults")
        
        self.notification_config = default_config
    
    def save_configuration(self):
        """Save error handling configuration"""

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.notification_config, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Error saving config: {str(e)}")

    def setup_logging(self):
        """Setup enhanced logging system (delegates to notifier)"""
        self.notifier.setup_logging()
        self.logger = self.notifier.logger
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None,
                    user_action: str = None, session_id: str = None) -> ErrorInfo:
        """Handle an error with comprehensive analysis and suggestions (delegates to modules)"""

        # Analyze error (delegates to analyzer)
        error_info = self.analyzer.analyze_error(error, context, user_action, session_id)

        # Log error (delegates to notifier)
        self.notifier.log_error(error_info)

        # Store in error log (delegates to statistics)
        self.statistics.add_error(error_info)

        # Notify callbacks (delegates to notifier)
        self.notifier.notify_callbacks(error_info)

        # Send notifications if configured (delegates to notifier)
        if self.notifier.should_notify(error_info):
            self.notifier.send_notification(error_info)

        return error_info
    
    def register_callback(self, callback: Callable[[ErrorInfo], None]):
        """Register error callback (delegates to notifier)"""
        self.notifier.register_callback(callback)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics (delegates to statistics)"""
        return self.statistics.get_error_summary()

    def get_filtered_errors(self, severity: ErrorSeverity = None,
                           category: ErrorCategory = None,
                           hours: int = None) -> List[ErrorInfo]:
        """Get filtered error list (delegates to statistics)"""
        return self.statistics.get_filtered_errors(severity, category, hours)

    def clear_error_log(self):
        """Clear error log (delegates to statistics)"""
        self.statistics.clear_error_log()

    def export_error_log(self, filename: str = None) -> str:
        """Export error log to JSON file (delegates to statistics)"""
        return self.statistics.export_error_log(filename)


def main():
    """Test the error handling system"""
    
    try:
        print("[TEST] TESTING ERROR HANDLING SYSTEM")
        print("="*50)
        
        # Initialize system
        error_system = ErrorHandlingSystem()
        
        # Test different types of errors
        print("\n[TEST] Testing error handling...")
        
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
        print("\n[STATS] Error summary:")
        summary = error_system.get_error_summary()
        print(f"Total errors: {summary['total_errors']}")
        print(f"Recent errors: {summary['recent_errors']}")
        print(f"Severity counts: {summary['severity_counts']}")
        
        # Test export
        print("\n[TEST] Testing export...")
        export_file = error_system.export_error_log()
        if export_file:
            print(f"Export successful: {export_file}")
        
        print("\n[SUCCESS] Error handling system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error handling system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
