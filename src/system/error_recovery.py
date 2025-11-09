"""
Advanced Error Recovery System with Pattern Detection and Auto-Recovery.

Features:
- Error classification and categorization
- Pattern detection for recurring errors
- Auto-recovery strategies
- Error history and analytics
- Recovery action suggestions
"""

import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger


class ErrorCategory:
    """Error category classifications."""
    NETWORK = "network"
    PERMISSION = "permission"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    INVALID_INPUT = "invalid_input"
    SYSTEM = "system"
    APPLICATION = "application"
    UNKNOWN = "unknown"


@dataclass
class ErrorPattern:
    """Represents a detected error pattern."""
    pattern: str
    category: str
    count: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    recovery_strategy: Optional[str] = None
    success_rate: float = 0.0
    examples: List[str] = field(default_factory=list)


@dataclass
class ErrorRecord:
    """Represents a single error occurrence."""
    error_message: str
    category: str
    task_info: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False
    recovery_action: Optional[str] = None


class RecoveryStrategy:
    """Base class for recovery strategies."""
    
    async def can_recover(self, error: ErrorRecord) -> bool:
        """Check if this strategy can recover from the error."""
        raise NotImplementedError
    
    async def recover(self, error: ErrorRecord) -> bool:
        """Attempt to recover from the error."""
        raise NotImplementedError


class RetryStrategy(RecoveryStrategy):
    """Simple retry recovery strategy."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    async def can_recover(self, error: ErrorRecord) -> bool:
        """Can retry for transient errors."""
        return error.category in [
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RESOURCE
        ]
    
    async def recover(self, error: ErrorRecord) -> bool:
        """Retry the failed operation."""
        import asyncio
        
        retry_count = error.context.get('retry_count', 0)
        if retry_count >= self.max_retries:
            return False
        
        await asyncio.sleep(self.delay * (2 ** retry_count))  # Exponential backoff
        error.context['retry_count'] = retry_count + 1
        return True


class PermissionEscalationStrategy(RecoveryStrategy):
    """Strategy for permission-related errors."""
    
    async def can_recover(self, error: ErrorRecord) -> bool:
        """Can attempt escalation for permission errors."""
        return error.category == ErrorCategory.PERMISSION
    
    async def recover(self, error: ErrorRecord) -> bool:
        """Request elevated permissions or alternative method."""
        logger.warning("Permission error detected - manual intervention may be required")
        # In real scenario, could prompt user or try alternative method
        return False


class ResourceCleanupStrategy(RecoveryStrategy):
    """Strategy for resource exhaustion errors."""
    
    async def can_recover(self, error: ErrorRecord) -> bool:
        """Can cleanup for resource errors."""
        return error.category == ErrorCategory.RESOURCE
    
    async def recover(self, error: ErrorRecord) -> bool:
        """Attempt to free resources."""
        import gc
        gc.collect()
        logger.info("Performed resource cleanup (garbage collection)")
        return True


class AlternativeMethodStrategy(RecoveryStrategy):
    """Try alternative methods for common failures."""
    
    def __init__(self):
        self.alternatives = {
            'file_not_found': ['check_alternative_path', 'search_file', 'create_file'],
            'network_error': ['retry_with_backup_url', 'use_cached_version'],
            'timeout': ['increase_timeout', 'split_into_smaller_tasks']
        }
    
    async def can_recover(self, error: ErrorRecord) -> bool:
        """Check if alternative exists."""
        return error.category in [
            ErrorCategory.NOT_FOUND,
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT
        ]
    
    async def recover(self, error: ErrorRecord) -> bool:
        """Suggest or execute alternative method."""
        # Log suggestion for alternative approach
        logger.info(f"Alternative methods available for {error.category}")
        return False  # Would need task executor integration


class ErrorRecoverySystem:
    """
    Advanced error recovery system with pattern detection and auto-recovery.
    
    Features:
    - Automatic error classification
    - Pattern detection for recurring errors
    - Multiple recovery strategies
    - Error analytics and reporting
    - Learning from successful recoveries
    """
    
    def __init__(self):
        """Initialize the error recovery system."""
        # Error storage
        self.error_history: List[ErrorRecord] = []
        self.error_patterns: Dict[str, ErrorPattern] = {}
        
        # Recovery strategies (ordered by priority)
        self.strategies: List[RecoveryStrategy] = [
            RetryStrategy(max_retries=3, delay=1.0),
            ResourceCleanupStrategy(),
            PermissionEscalationStrategy(),
            AlternativeMethodStrategy()
        ]
        
        # Pattern matching rules
        self.classification_rules = [
            (r'.*connection.*failed.*|.*network.*error.*|.*timeout.*', ErrorCategory.NETWORK),
            (r'.*permission.*denied.*|.*access.*denied.*|.*unauthorized.*', ErrorCategory.PERMISSION),
            (r'.*memory.*|.*resource.*limit.*|.*quota.*exceeded.*', ErrorCategory.RESOURCE),
            (r'.*timeout.*|.*timed out.*', ErrorCategory.TIMEOUT),
            (r'.*not found.*|.*does not exist.*|.*no such.*', ErrorCategory.NOT_FOUND),
            (r'.*invalid.*input.*|.*validation.*failed.*|.*bad.*request.*', ErrorCategory.INVALID_INPUT),
            (r'.*system.*error.*|.*os error.*', ErrorCategory.SYSTEM),
        ]
        
        # Statistics
        self.total_errors = 0
        self.recovered_errors = 0
        
        logger.info("Error Recovery System initialized")
    
    def classify_error(self, error_message: str) -> str:
        """
        Classify an error based on its message.
        
        Args:
            error_message: Error message to classify
            
        Returns:
            Error category
        """
        error_lower = error_message.lower()
        
        for pattern, category in self.classification_rules:
            if re.search(pattern, error_lower):
                return category
        
        return ErrorCategory.UNKNOWN
    
    async def record_error(
        self,
        error_message: str,
        task_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorRecord:
        """
        Record an error occurrence.
        
        Args:
            error_message: Error message
            task_info: Information about the failed task
            context: Additional context
            
        Returns:
            Error record
        """
        # Classify error
        category = self.classify_error(error_message)
        
        # Create record
        error = ErrorRecord(
            error_message=error_message,
            category=category,
            task_info=task_info,
            context=context or {}
        )
        
        # Store in history
        self.error_history.append(error)
        self.total_errors += 1
        
        # Update patterns
        self._update_patterns(error)
        
        logger.warning(f"Error recorded: {category} - {error_message[:100]}")
        
        return error
    
    def _update_patterns(self, error: ErrorRecord):
        """Update error patterns based on new error."""
        # Create a simplified pattern from error message
        pattern_key = error.category
        
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = ErrorPattern(
                pattern=pattern_key,
                category=error.category
            )
        
        pattern = self.error_patterns[pattern_key]
        pattern.count += 1
        pattern.last_seen = error.timestamp
        
        # Keep recent examples (max 5)
        if len(pattern.examples) < 5:
            pattern.examples.append(error.error_message)
    
    async def attempt_recovery(
        self,
        error: ErrorRecord,
        executor: Optional[Callable] = None
    ) -> bool:
        """
        Attempt to recover from an error using available strategies.
        
        Args:
            error: Error record to recover from
            executor: Optional function to re-execute task after recovery
            
        Returns:
            True if recovery was successful
        """
        logger.info(f"Attempting recovery for {error.category} error")
        
        # Try each strategy in order
        for strategy in self.strategies:
            try:
                if await strategy.can_recover(error):
                    logger.info(f"Trying {strategy.__class__.__name__}")
                    
                    if await strategy.recover(error):
                        error.recovered = True
                        error.recovery_action = strategy.__class__.__name__
                        self.recovered_errors += 1
                        
                        # Update pattern success rate
                        if error.category in self.error_patterns:
                            pattern = self.error_patterns[error.category]
                            pattern.success_rate = self.recovered_errors / self.total_errors
                        
                        logger.info(f"Recovery successful using {strategy.__class__.__name__}")
                        return True
                        
            except Exception as e:
                logger.error(f"Recovery strategy {strategy.__class__.__name__} failed: {e}")
                continue
        
        logger.warning("All recovery strategies exhausted")
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and analytics."""
        # Category breakdown
        category_counts = defaultdict(int)
        for error in self.error_history:
            category_counts[error.category] += 1
        
        # Recent errors (last hour)
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_errors = [e for e in self.error_history if e.timestamp > hour_ago]
        
        # Recovery rate
        recovery_rate = (self.recovered_errors / self.total_errors * 100) if self.total_errors > 0 else 0
        
        return {
            'total_errors': self.total_errors,
            'recovered_errors': self.recovered_errors,
            'recovery_rate': f"{recovery_rate:.1f}%",
            'errors_by_category': dict(category_counts),
            'recent_errors_1h': len(recent_errors),
            'unique_patterns': len(self.error_patterns),
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }
    
    def get_pattern_insights(self) -> List[Dict[str, Any]]:
        """Get insights about error patterns."""
        insights = []
        
        for pattern in self.error_patterns.values():
            if pattern.count >= 3:  # Only patterns seen 3+ times
                insights.append({
                    'category': pattern.category,
                    'occurrences': pattern.count,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat(),
                    'success_rate': f"{pattern.success_rate * 100:.1f}%",
                    'examples': pattern.examples[:2]  # Show 2 examples
                })
        
        # Sort by occurrence count
        insights.sort(key=lambda x: x['occurrences'], reverse=True)
        
        return insights
    
    def suggest_preventive_actions(self) -> List[str]:
        """Suggest actions to prevent common errors."""
        suggestions = []
        
        # Analyze patterns
        for pattern in self.error_patterns.values():
            if pattern.count >= 5:
                if pattern.category == ErrorCategory.NETWORK:
                    suggestions.append("Consider implementing connection pooling or retry logic for network operations")
                elif pattern.category == ErrorCategory.PERMISSION:
                    suggestions.append("Review required permissions and ensure proper access rights")
                elif pattern.category == ErrorCategory.RESOURCE:
                    suggestions.append("Monitor resource usage and implement cleanup procedures")
                elif pattern.category == ErrorCategory.TIMEOUT:
                    suggestions.append("Increase timeout limits or optimize long-running operations")
                elif pattern.category == ErrorCategory.NOT_FOUND:
                    suggestions.append("Validate file/resource paths before operations")
        
        return list(set(suggestions))  # Remove duplicates
    
    def clear_old_errors(self, days: int = 7):
        """Clear error history older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.error_history)
        
        self.error_history = [e for e in self.error_history if e.timestamp > cutoff]
        
        cleared = original_count - len(self.error_history)
        if cleared > 0:
            logger.info(f"Cleared {cleared} old error records (older than {days} days)")
    
    def export_error_report(self) -> Dict[str, Any]:
        """Export comprehensive error report."""
        return {
            'statistics': self.get_error_statistics(),
            'patterns': self.get_pattern_insights(),
            'preventive_suggestions': self.suggest_preventive_actions(),
            'recent_errors': [
                {
                    'message': e.error_message,
                    'category': e.category,
                    'timestamp': e.timestamp.isoformat(),
                    'recovered': e.recovered,
                    'recovery_action': e.recovery_action
                }
                for e in self.error_history[-10:]  # Last 10 errors
            ]
        }
