#!/usr/bin/env python3
"""
Error Statistics and Export
Provides error summary statistics, filtering, and export functionality.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from error_types import ErrorInfo, ErrorSeverity, ErrorCategory


class ErrorStatistics:
    """
    Manages error statistics, filtering, and export functionality
    """
    
    def __init__(self, max_error_log_size: int = 1000):
        """Initialize error statistics manager"""
        self.error_log = []
        self.max_error_log_size = max_error_log_size
    
    def add_error(self, error_info: ErrorInfo):
        """Add error to log"""
        self.error_log.append(error_info)
        
        # Trim error log if too large
        if len(self.error_log) > self.max_error_log_size:
            self.error_log = self.error_log[-500:]  # Keep last 500 errors
    
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
        print("[SYSTEM] Error log cleared")
    
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
            
            print(f"[EXPORT] Error log exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"[WARNING] Error exporting log: {str(e)}")
            return None
    
    def get_error_count(self) -> int:
        """Get total error count"""
        return len(self.error_log)
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorInfo]:
        """Get most recent errors"""
        return self.error_log[-count:] if self.error_log else []

