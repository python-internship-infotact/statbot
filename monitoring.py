"""
Production monitoring and metrics collection for StatBot Pro
Provides comprehensive monitoring, logging, and alerting capabilities
"""

import time
import psutil
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'labels': self.labels or {}
        }

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    disk_used_gb: float
    active_connections: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    active_sessions: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    charts_generated: int
    errors_count: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_points: int = 1000):
        """
        Initialize metrics collector
        
        Args:
            max_points: Maximum number of metric points to store
        """
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        
        # Request tracking
        self.request_times: deque = deque(maxlen=1000)
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        
        logger.info("Metrics collector initialized")
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self._lock:
            self.counters[name] += value
            self.metrics[name].append(MetricPoint(
                timestamp=datetime.now(),
                value=self.counters[name],
                labels=labels
            ))
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        with self._lock:
            self.gauges[name] = value
            self.metrics[name].append(MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels
            ))
    
    def record_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Record a timing metric"""
        with self._lock:
            self.timers[name].append(duration)
            # Keep only recent timings
            if len(self.timers[name]) > 100:
                self.timers[name] = self.timers[name][-100:]
            
            avg_duration = sum(self.timers[name]) / len(self.timers[name])
            self.metrics[f"{name}_avg"].append(MetricPoint(
                timestamp=datetime.now(),
                value=avg_duration,
                labels=labels
            ))
    
    def record_request(self, duration: float, success: bool = True):
        """Record request metrics"""
        with self._lock:
            self.request_count += 1
            self.request_times.append(duration)
            
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        with self._lock:
            # Calculate averages
            avg_response_time = 0
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
            
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'request_metrics': {
                    'total_requests': self.request_count,
                    'successful_requests': self.success_count,
                    'failed_requests': self.error_count,
                    'avg_response_time': avg_response_time,
                    'success_rate': self.success_count / max(self.request_count, 1) * 100
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def get_metric_history(self, name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for a metric"""
        with self._lock:
            if name not in self.metrics:
                return []
            
            points = list(self.metrics[name])[-limit:]
            return [point.to_dict() for point in points]

class SystemMonitor:
    """Monitors system resources and health"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Initialize system monitor
        
        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics = metrics_collector
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 30):
        """
        Start system monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge('system_cpu_percent', cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics.set_gauge('system_memory_percent', memory.percent)
            self.metrics.set_gauge('system_memory_used_mb', memory.used / (1024 * 1024))
            
            # Disk metrics
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics.set_gauge('system_disk_percent', disk_percent)
            self.metrics.set_gauge('system_disk_used_gb', disk.used / (1024 * 1024 * 1024))
            
            # Network connections (if available)
            try:
                connections = len(psutil.net_connections())
                self.metrics.set_gauge('system_connections', connections)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            return SystemMetrics(
                cpu_percent=psutil.cpu_percent(),
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_percent=(disk.used / disk.total) * 100,
                disk_used_gb=disk.used / (1024 * 1024 * 1024),
                active_connections=len(psutil.net_connections()) if hasattr(psutil, 'net_connections') else 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting current system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0, memory_percent=0, memory_used_mb=0,
                disk_percent=0, disk_used_gb=0, active_connections=0,
                timestamp=datetime.now()
            )

class HealthChecker:
    """Performs health checks and alerting"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Initialize health checker
        
        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics = metrics_collector
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 90.0,
            'disk_percent': 95.0,
            'error_rate': 10.0,  # Percentage
            'response_time': 30.0  # Seconds
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Health status dictionary
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'alerts': []
        }
        
        try:
            # System resource checks
            system_health = self._check_system_resources()
            health_status['checks']['system'] = system_health
            
            # Application health checks
            app_health = self._check_application_health()
            health_status['checks']['application'] = app_health
            
            # Determine overall status
            if any(check['status'] == 'critical' for check in health_status['checks'].values()):
                health_status['status'] = 'critical'
            elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
                health_status['status'] = 'warning'
            
            # Add recent alerts
            health_status['alerts'] = self.alerts[-10:]  # Last 10 alerts
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            health_status['status'] = 'error'
            health_status['error'] = str(e)
        
        return health_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource health"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            cpu_percent = psutil.cpu_percent()
            
            checks = {
                'cpu': {
                    'value': cpu_percent,
                    'threshold': self.thresholds['cpu_percent'],
                    'status': 'critical' if cpu_percent > self.thresholds['cpu_percent'] else 'healthy'
                },
                'memory': {
                    'value': memory.percent,
                    'threshold': self.thresholds['memory_percent'],
                    'status': 'critical' if memory.percent > self.thresholds['memory_percent'] else 'healthy'
                },
                'disk': {
                    'value': (disk.used / disk.total) * 100,
                    'threshold': self.thresholds['disk_percent'],
                    'status': 'critical' if (disk.used / disk.total) * 100 > self.thresholds['disk_percent'] else 'healthy'
                }
            }
            
            # Determine overall system status
            overall_status = 'healthy'
            if any(check['status'] == 'critical' for check in checks.values()):
                overall_status = 'critical'
            
            return {
                'status': overall_status,
                'checks': checks
            }
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application-specific health"""
        try:
            metrics_summary = self.metrics.get_metrics_summary()
            request_metrics = metrics_summary['request_metrics']
            
            # Calculate error rate
            error_rate = 0
            if request_metrics['total_requests'] > 0:
                error_rate = (request_metrics['failed_requests'] / request_metrics['total_requests']) * 100
            
            checks = {
                'error_rate': {
                    'value': error_rate,
                    'threshold': self.thresholds['error_rate'],
                    'status': 'warning' if error_rate > self.thresholds['error_rate'] else 'healthy'
                },
                'response_time': {
                    'value': request_metrics['avg_response_time'],
                    'threshold': self.thresholds['response_time'],
                    'status': 'warning' if request_metrics['avg_response_time'] > self.thresholds['response_time'] else 'healthy'
                }
            }
            
            # Determine overall application status
            overall_status = 'healthy'
            if any(check['status'] == 'critical' for check in checks.values()):
                overall_status = 'critical'
            elif any(check['status'] == 'warning' for check in checks.values()):
                overall_status = 'warning'
            
            return {
                'status': overall_status,
                'checks': checks,
                'metrics': request_metrics
            }
            
        except Exception as e:
            logger.error(f"Error checking application health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def add_alert(self, level: str, message: str, details: Dict[str, Any] = None):
        """
        Add an alert
        
        Args:
            level: Alert level (info, warning, critical)
            message: Alert message
            details: Additional alert details
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'details': details or {}
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"Alert [{level}]: {message}")

class MetricsExporter:
    """Exports metrics in various formats"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Initialize metrics exporter
        
        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics = metrics_collector
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        summary = self.metrics.get_metrics_summary()
        
        # Counters
        for name, value in summary['counters'].items():
            lines.append(f"# TYPE statbot_{name} counter")
            lines.append(f"statbot_{name} {value}")
        
        # Gauges
        for name, value in summary['gauges'].items():
            lines.append(f"# TYPE statbot_{name} gauge")
            lines.append(f"statbot_{name} {value}")
        
        # Request metrics
        request_metrics = summary['request_metrics']
        for name, value in request_metrics.items():
            lines.append(f"# TYPE statbot_request_{name} gauge")
            lines.append(f"statbot_request_{name} {value}")
        
        return '\n'.join(lines)
    
    def export_json(self) -> str:
        """Export metrics in JSON format"""
        return json.dumps(self.metrics.get_metrics_summary(), indent=2)
    
    def save_metrics(self, filepath: Path, format: str = 'json'):
        """
        Save metrics to file
        
        Args:
            filepath: File path to save metrics
            format: Export format (json, prometheus)
        """
        try:
            if format == 'prometheus':
                content = self.export_prometheus()
            else:
                content = self.export_json()
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            logger.info(f"Metrics saved to {filepath} in {format} format")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

# Global monitoring instances
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
health_checker = HealthChecker(metrics_collector)
metrics_exporter = MetricsExporter(metrics_collector)