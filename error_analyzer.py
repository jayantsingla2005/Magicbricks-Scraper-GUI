#!/usr/bin/env python3
"""
Error Analysis and Categorization
Analyzes errors, determines severity, categorizes them, and provides helpful suggestions.
"""

import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from error_types import ErrorSeverity, ErrorCategory, ErrorInfo


class ErrorAnalyzer:
    """
    Analyzes errors and provides categorization and suggestions
    """
    
    def __init__(self):
        """Initialize error analyzer with pattern matching rules"""
        self.error_patterns = self._initialize_error_patterns()
    
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
    
    def analyze_error(self, error: Exception, context: Dict[str, Any] = None,
                     user_action: str = None, session_id: str = None) -> ErrorInfo:
        """Analyze error and provide comprehensive information with suggestions"""
        
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
        """Determine error severity based on error type and message"""
        
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
        """Categorize error and provide helpful suggestion"""
        
        message_lower = message.lower()
        
        # Match against known error patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(pattern in message_lower for pattern in pattern_info['pattern']):
                category = ErrorCategory(pattern_info['category'])
                suggestion = pattern_info['suggestion']
                return category, suggestion
        
        # Default categorization for unknown errors
        if 'input' in message_lower or 'parameter' in message_lower:
            return ErrorCategory.USER_INPUT, "Please check your input parameters and try again."
        else:
            return ErrorCategory.SYSTEM, "An unexpected error occurred. Please try again or contact support."
    
    def _get_error_details(self, error: Exception) -> str:
        """Get detailed error information for debugging"""
        
        details = []
        details.append(f"Error Type: {type(error).__name__}")
        details.append(f"Error Message: {str(error)}")
        
        if hasattr(error, 'args') and error.args:
            details.append(f"Error Args: {error.args}")
        
        if hasattr(error, '__cause__') and error.__cause__:
            details.append(f"Caused by: {error.__cause__}")
        
        return "\n".join(details)
    
    def get_error_patterns(self) -> Dict[str, Dict[str, str]]:
        """Get all error patterns for reference"""
        return self.error_patterns.copy()

