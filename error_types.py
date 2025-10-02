#!/usr/bin/env python3
"""
Error Types and Data Classes
Defines error severity levels, categories, and comprehensive error information structure.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


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

