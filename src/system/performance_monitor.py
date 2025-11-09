"""
Performance Monitoring System for Cosik AI Agent.

Features:
- Task execution time tracking
- Resource usage monitoring (CPU, memory)
- Performance bottleneck detection
- Historical performance data
- Performance alerts and recommendations
"""

import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from contextlib import asynccontextmanager
from loguru import logger


@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: float
    disk_io_write: float
    active_tasks: int


class PerformanceMonitor:
    """
    Performance monitoring system for tracking and analyzing agent performance.
    
    Features:
    - Execution time tracking
    - Resource usage monitoring
    - Bottleneck detection
    - Performance trends
    - Automatic alerts for performance issues
    """
    
    def __init__(
        self,
        history_size: int = 1000,
        snapshot_interval: float = 5.0,
        enable_profiling: bool = True
    ):
        """
        Initialize the performance monitor.
        
        Args:
            history_size: Number of metrics to keep in memory
            snapshot_interval: Seconds between resource snapshots
            enable_profiling: Enable detailed profiling
        """
        self.history_size = history_size
        self.snapshot_interval = snapshot_interval
        self.enable_profiling = enable_profiling
        
        # Metrics storage
        self.metrics: deque = deque(maxlen=history_size)
        self.resource_snapshots: deque = deque(maxlen=history_size)
        
        # Current measurements
        self.active_operations: Dict[str, PerformanceMetric] = {}
        
        # Aggregated stats
        self.operation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'avg_duration': 0.0,
            'failures': 0
        })
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'operation_duration_ms': 5000.0  # 5 seconds
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Background monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Process handle
        self.process = psutil.Process()
        
        logger.info(f"Performance Monitor initialized (history={history_size}, profiling={enable_profiling})")
    
    async def start_monitoring(self):
        """Start background resource monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Background monitoring started")
    
    async def stop_monitoring(self):
        """Stop background resource monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Background monitoring stopped")
    
    async def _monitor_loop(self):
        """Background loop for resource monitoring."""
        while self.is_monitoring:
            try:
                await self._take_resource_snapshot()
                await asyncio.sleep(self.snapshot_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.snapshot_interval)
    
    async def _take_resource_snapshot(self):
        """Take a snapshot of current resource usage."""
        try:
            # CPU and memory
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = self.process.memory_percent()
            
            # Disk I/O
            io_counters = self.process.io_counters() if hasattr(self.process, 'io_counters') else None
            disk_read = io_counters.read_bytes / (1024 * 1024) if io_counters else 0
            disk_write = io_counters.write_bytes / (1024 * 1024) if io_counters else 0
            
            snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                disk_io_read=disk_read,
                disk_io_write=disk_write,
                active_tasks=len(self.active_operations)
            )
            
            self.resource_snapshots.append(snapshot)
            
            # Check thresholds and alert
            await self._check_thresholds(snapshot)
            
        except Exception as e:
            logger.error(f"Failed to take resource snapshot: {e}")
    
    async def _check_thresholds(self, snapshot: ResourceSnapshot):
        """Check if any thresholds are exceeded and trigger alerts."""
        alerts = []
        
        if snapshot.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'high_cpu',
                'value': snapshot.cpu_percent,
                'threshold': self.thresholds['cpu_percent']
            })
        
        if snapshot.memory_percent > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'high_memory',
                'value': snapshot.memory_percent,
                'threshold': self.thresholds['memory_percent']
            })
        
        # Trigger callbacks
        for alert in alerts:
            logger.warning(f"Performance alert: {alert['type']} = {alert['value']:.1f}% (threshold: {alert['threshold']}%)")
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    @asynccontextmanager
    async def measure(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for measuring operation performance.
        
        Args:
            operation: Name of the operation being measured
            metadata: Additional metadata to store
            
        Example:
            async with monitor.measure('file_processing', {'file': 'data.txt'}):
                await process_file('data.txt')
        """
        metric = PerformanceMetric(
            operation=operation,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        # Get initial resource usage
        start_cpu = self.process.cpu_percent()
        start_memory = self.process.memory_info().rss / (1024 * 1024)
        
        operation_id = f"{operation}_{id(metric)}"
        self.active_operations[operation_id] = metric
        
        start = time.perf_counter()
        
        try:
            yield metric
            metric.success = True
        except Exception as e:
            metric.success = False
            metric.metadata['error'] = str(e)
            raise
        finally:
            # Calculate duration
            end = time.perf_counter()
            metric.end_time = datetime.now()
            metric.duration_ms = (end - start) * 1000
            
            # Get final resource usage
            metric.cpu_percent = self.process.cpu_percent() - start_cpu
            metric.memory_mb = (self.process.memory_info().rss / (1024 * 1024)) - start_memory
            
            # Store metric
            self.metrics.append(metric)
            del self.active_operations[operation_id]
            
            # Update aggregated stats
            self._update_stats(metric)
            
            # Check for slow operations
            if metric.duration_ms > self.thresholds['operation_duration_ms']:
                logger.warning(
                    f"Slow operation detected: {operation} took {metric.duration_ms:.0f}ms "
                    f"(threshold: {self.thresholds['operation_duration_ms']:.0f}ms)"
                )
    
    def _update_stats(self, metric: PerformanceMetric):
        """Update aggregated statistics for an operation."""
        stats = self.operation_stats[metric.operation]
        
        stats['count'] += 1
        stats['total_duration'] += metric.duration_ms
        
        if metric.duration_ms < stats['min_duration']:
            stats['min_duration'] = metric.duration_ms
        
        if metric.duration_ms > stats['max_duration']:
            stats['max_duration'] = metric.duration_ms
        
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        
        if not metric.success:
            stats['failures'] += 1
    
    def get_operation_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for specific operation or all operations.
        
        Args:
            operation: Specific operation name, or None for all
            
        Returns:
            Statistics dictionary
        """
        if operation:
            return dict(self.operation_stats.get(operation, {}))
        
        return {op: dict(stats) for op, stats in self.operation_stats.items()}
    
    def get_recent_metrics(self, count: int = 10, operation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent performance metrics.
        
        Args:
            count: Number of metrics to return
            operation: Filter by operation name
            
        Returns:
            List of metric dictionaries
        """
        filtered = self.metrics
        
        if operation:
            filtered = [m for m in self.metrics if m.operation == operation]
        
        recent = list(filtered)[-count:]
        
        return [
            {
                'operation': m.operation,
                'duration_ms': m.duration_ms,
                'cpu_percent': m.cpu_percent,
                'memory_mb': m.memory_mb,
                'success': m.success,
                'timestamp': m.start_time.isoformat(),
                'metadata': m.metadata
            }
            for m in recent
        ]
    
    def get_resource_trends(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get resource usage trends over time.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            Trend statistics
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_snapshots = [s for s in self.resource_snapshots if s.timestamp > cutoff]
        
        if not recent_snapshots:
            return {
                'error': 'No data available for the specified time window'
            }
        
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        memory_values = [s.memory_percent for s in recent_snapshots]
        
        return {
            'time_window_minutes': minutes,
            'snapshots_count': len(recent_snapshots),
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current': memory_values[-1] if memory_values else 0,
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0
            }
        }
    
    def identify_bottlenecks(self, threshold_percentile: float = 90.0) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks.
        
        Args:
            threshold_percentile: Percentile threshold for slow operations
            
        Returns:
            List of bottleneck descriptions
        """
        bottlenecks = []
        
        for operation, stats in self.operation_stats.items():
            if stats['count'] < 3:  # Need at least 3 samples
                continue
            
            # Check if operation is consistently slow
            if stats['avg_duration'] > stats['max_duration'] * (threshold_percentile / 100):
                bottlenecks.append({
                    'operation': operation,
                    'avg_duration_ms': stats['avg_duration'],
                    'max_duration_ms': stats['max_duration'],
                    'count': stats['count'],
                    'severity': 'high' if stats['avg_duration'] > 5000 else 'medium'
                })
        
        # Sort by average duration
        bottlenecks.sort(key=lambda x: x['avg_duration_ms'], reverse=True)
        
        return bottlenecks
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        total_operations = sum(stats['count'] for stats in self.operation_stats.values())
        total_failures = sum(stats['failures'] for stats in self.operation_stats.values())
        
        # Find slowest operation
        slowest = None
        if self.operation_stats:
            slowest = max(
                self.operation_stats.items(),
                key=lambda x: x[1]['avg_duration']
            )
        
        return {
            'total_operations': total_operations,
            'total_failures': total_failures,
            'success_rate': f"{((total_operations - total_failures) / total_operations * 100):.1f}%" if total_operations > 0 else "N/A",
            'unique_operations': len(self.operation_stats),
            'slowest_operation': {
                'name': slowest[0],
                'avg_duration_ms': slowest[1]['avg_duration']
            } if slowest else None,
            'active_operations': len(self.active_operations),
            'resource_trends': self.get_resource_trends(60),
            'bottlenecks': self.identify_bottlenecks()
        }
    
    def export_report(self, filepath: str):
        """Export performance report to JSON file."""
        import json
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_performance_summary(),
            'operation_stats': self.get_operation_stats(),
            'recent_metrics': self.get_recent_metrics(50),
            'bottlenecks': self.identify_bottlenecks()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report exported to {filepath}")
    
    def register_alert_callback(self, callback: Callable):
        """Register a callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, metric: str, value: float):
        """Set a performance threshold."""
        if metric in self.thresholds:
            self.thresholds[metric] = value
            logger.info(f"Threshold updated: {metric} = {value}")
        else:
            logger.warning(f"Unknown threshold metric: {metric}")
