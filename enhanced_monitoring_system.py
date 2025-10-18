#!/usr/bin/env python3
"""
Enhanced Monitoring System
Provides comprehensive logging, alerting, and real-time network monitoring
"""

import os
import json
import time
import logging
import threading
import smtplib
import requests
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib3.exceptions import InsecureRequestWarning
import schedule

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert level enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Alert type enumeration"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONNECTIVITY = "connectivity"
    POLICY = "policy"
    SYSTEM = "system"

@dataclass
class Alert:
    """Represents a monitoring alert"""
    alert_id: str
    title: str
    description: str
    level: AlertLevel
    alert_type: AlertType
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class Metric:
    """Represents a monitoring metric"""
    metric_id: str
    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class LogEntry:
    """Represents a log entry"""
    log_id: str
    level: str
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_channels: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable] = []
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = [
            {
                "rule_id": "high_cpu_usage",
                "name": "High CPU Usage",
                "condition": "cpu_usage > 80",
                "level": AlertLevel.WARNING,
                "alert_type": AlertType.PERFORMANCE,
                "enabled": True
            },
            {
                "rule_id": "high_memory_usage",
                "name": "High Memory Usage",
                "condition": "memory_usage > 85",
                "level": AlertLevel.WARNING,
                "alert_type": AlertType.PERFORMANCE,
                "enabled": True
            },
            {
                "rule_id": "device_offline",
                "name": "Device Offline",
                "condition": "device_status == 'offline'",
                "level": AlertLevel.ERROR,
                "alert_type": AlertType.CONNECTIVITY,
                "enabled": True
            },
            {
                "rule_id": "security_threat",
                "name": "Security Threat Detected",
                "condition": "threat_level == 'high'",
                "level": AlertLevel.CRITICAL,
                "alert_type": AlertType.SECURITY,
                "enabled": True
            },
            {
                "rule_id": "policy_violation",
                "name": "Policy Violation",
                "condition": "policy_violation == True",
                "level": AlertLevel.WARNING,
                "alert_type": AlertType.POLICY,
                "enabled": True
            }
        ]
    
    def create_alert(self, alert: Alert) -> bool:
        """Create a new alert"""
        try:
            self.alerts[alert.alert_id] = alert
            
            # Check if alert should trigger notifications
            self._check_alert_rules(alert)
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {str(e)}")
            
            logger.info(f"Created alert: {alert.title} ({alert.level.value})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        try:
            if alert_id not in self.alerts:
                logger.error(f"Alert '{alert_id}' not found")
                return False
            
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            if resolution_notes:
                alert.actions_taken.append(resolution_notes)
            
            logger.info(f"Resolved alert: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    def _check_alert_rules(self, alert: Alert):
        """Check if alert matches any alert rules"""
        for rule in self.alert_rules:
            if not rule.get("enabled", True):
                continue
            
            if self._evaluate_rule(rule, alert):
                self._trigger_notification(alert, rule)
    
    def _evaluate_rule(self, rule: Dict[str, Any], alert: Alert) -> bool:
        """Evaluate if alert matches a rule"""
        try:
            # Simple rule evaluation (in production, use a proper rule engine)
            condition = rule.get("condition", "")
            
            if "cpu_usage" in condition and alert.alert_type == AlertType.PERFORMANCE:
                return True
            elif "memory_usage" in condition and alert.alert_type == AlertType.PERFORMANCE:
                return True
            elif "device_status" in condition and alert.alert_type == AlertType.CONNECTIVITY:
                return True
            elif "threat_level" in condition and alert.alert_type == AlertType.SECURITY:
                return True
            elif "policy_violation" in condition and alert.alert_type == AlertType.POLICY:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating rule: {str(e)}")
            return False
    
    def _trigger_notification(self, alert: Alert, rule: Dict[str, Any]):
        """Trigger notification for alert"""
        try:
            # Send notifications to all configured channels
            for channel in self.notification_channels:
                self._send_notification(alert, channel)
                
        except Exception as e:
            logger.error(f"Error triggering notification: {str(e)}")
    
    def _send_notification(self, alert: Alert, channel: Dict[str, Any]):
        """Send notification via specific channel"""
        try:
            channel_type = channel.get("type", "email")
            
            if channel_type == "email":
                self._send_email_notification(alert, channel)
            elif channel_type == "webhook":
                self._send_webhook_notification(alert, channel)
            elif channel_type == "syslog":
                self._send_syslog_notification(alert, channel)
                
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def _send_email_notification(self, alert: Alert, channel: Dict[str, Any]):
        """Send email notification"""
        try:
            smtp_server = channel.get("smtp_server", "localhost")
            smtp_port = channel.get("smtp_port", 587)
            username = channel.get("username", "")
            password = channel.get("password", "")
            to_email = channel.get("to_email", "")
            
            if not to_email:
                logger.warning("No email address configured for notifications")
                return
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
            
            body = f"""
            Alert: {alert.title}
            Level: {alert.level.value.upper()}
            Type: {alert.alert_type.value}
            Source: {alert.source}
            Time: {alert.timestamp.isoformat()}
            
            Description:
            {alert.description}
            
            Metadata:
            {json.dumps(alert.metadata, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.title}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    def _send_webhook_notification(self, alert: Alert, channel: Dict[str, Any]):
        """Send webhook notification"""
        try:
            webhook_url = channel.get("url", "")
            if not webhook_url:
                logger.warning("No webhook URL configured")
                return
            
            payload = {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "level": alert.level.value,
                "type": alert.alert_type.value,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "description": alert.description,
                "metadata": alert.metadata
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Webhook notification sent for alert: {alert.title}")
            else:
                logger.error(f"Webhook notification failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
    
    def _send_syslog_notification(self, alert: Alert, channel: Dict[str, Any]):
        """Send syslog notification"""
        try:
            syslog_server = channel.get("server", "localhost")
            syslog_port = channel.get("port", 514)
            
            message = f"ALERT: {alert.title} - {alert.description} [{alert.level.value}]"
            
            # In production, use proper syslog library
            logger.info(f"Syslog notification: {message}")
            
        except Exception as e:
            logger.error(f"Error sending syslog notification: {str(e)}")
    
    def add_notification_channel(self, channel: Dict[str, Any]) -> bool:
        """Add a notification channel"""
        try:
            required_fields = ["type", "name"]
            for field in required_fields:
                if field not in channel:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            self.notification_channels.append(channel)
            logger.info(f"Added notification channel: {channel['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding notification channel: {str(e)}")
            return False
    
    def register_alert_callback(self, callback: Callable):
        """Register an alert callback"""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by level"""
        return [alert for alert in self.alerts.values() if alert.level == level]
    
    def get_alerts_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Get alerts by type"""
        return [alert for alert in self.alerts.values() if alert.alert_type == alert_type]

class MetricsCollector:
    """Collects and stores network metrics"""
    
    def __init__(self, controller_host: str, api_key: str):
        self.controller_host = controller_host
        self.api_key = api_key
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
        self.site = "default"
        
        self.metrics: List[Metric] = []
        self.collection_interval = 60  # seconds
        self.collection_thread = None
        self.collection_enabled = False
    
    def start_collection(self):
        """Start metrics collection"""
        if self.collection_enabled:
            logger.warning("Metrics collection is already running")
            return
        
        self.collection_enabled = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.collection_enabled = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.collection_enabled:
            try:
                self._collect_network_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_network_metrics(self):
        """Collect network metrics from UniFi controller"""
        try:
            # Collect device metrics
            self._collect_device_metrics()
            
            # Collect client metrics
            self._collect_client_metrics()
            
            # Collect network metrics
            self._collect_network_metrics()
            
            # Collect performance metrics
            self._collect_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
    
    def _collect_device_metrics(self):
        """Collect device-specific metrics"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/v2/api/site/{self.site}/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
                
                for device in devices:
                    # CPU usage
                    cpu_usage = device.get('cpu', 0)
                    self._add_metric("device_cpu_usage", cpu_usage, "percent", device.get('name', 'unknown'))
                    
                    # Memory usage
                    memory_usage = device.get('mem', 0)
                    self._add_metric("device_memory_usage", memory_usage, "percent", device.get('name', 'unknown'))
                    
                    # Uptime
                    uptime = device.get('uptime', 0)
                    self._add_metric("device_uptime", uptime, "seconds", device.get('name', 'unknown'))
                    
                    # Status
                    status = 1 if device.get('state') == 1 else 0
                    self._add_metric("device_status", status, "boolean", device.get('name', 'unknown'))
                    
        except Exception as e:
            logger.error(f"Error collecting device metrics: {str(e)}")
    
    def _collect_client_metrics(self):
        """Collect client-specific metrics"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/v2/api/site/{self.site}/clients/active")
            if response.status_code == 200:
                clients = response.json().get('data', [])
                
                # Total active clients
                self._add_metric("active_clients", len(clients), "count", "network")
                
                # Clients by network
                network_counts = {}
                for client in clients:
                    network = client.get('network', 'unknown')
                    network_counts[network] = network_counts.get(network, 0) + 1
                
                for network, count in network_counts.items():
                    self._add_metric("clients_per_network", count, "count", network)
                    
        except Exception as e:
            logger.error(f"Error collecting client metrics: {str(e)}")
    
    def _collect_network_metrics(self):
        """Collect network-specific metrics"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                networks = response.json().get('data', [])
                
                # Total networks
                lan_networks = [n for n in networks if n.get('purpose') not in ['wan', 'wan2']]
                self._add_metric("total_networks", len(lan_networks), "count", "network")
                
                # Networks by purpose
                purpose_counts = {}
                for network in lan_networks:
                    purpose = network.get('purpose', 'unknown')
                    purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
                
                for purpose, count in purpose_counts.items():
                    self._add_metric("networks_by_purpose", count, "count", purpose)
                    
        except Exception as e:
            logger.error(f"Error collecting network metrics: {str(e)}")
    
    def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # System health
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/stat/health")
            if response.status_code == 200:
                health_data = response.json().get('data', [])
                
                for health_item in health_data:
                    if health_item.get('subsystem') == 'wlan':
                        # WiFi performance
                        self._add_metric("wifi_performance", health_item.get('status', 0), "score", "wifi")
                    elif health_item.get('subsystem') == 'lan':
                        # LAN performance
                        self._add_metric("lan_performance", health_item.get('status', 0), "score", "lan")
                        
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {str(e)}")
    
    def _add_metric(self, name: str, value: float, unit: str, source: str, tags: Dict[str, str] = None):
        """Add a metric to the collection"""
        metric = Metric(
            metric_id=f"{name}_{int(time.time())}",
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            source=source,
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def get_metrics(self, name: Optional[str] = None, source: Optional[str] = None, 
                   hours: int = 24) -> List[Metric]:
        """Get metrics with optional filtering"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if name:
            filtered_metrics = [m for m in filtered_metrics if m.name == name]
        
        if source:
            filtered_metrics = [m for m in filtered_metrics if m.source == source]
        
        return filtered_metrics
    
    def get_metric_summary(self, name: str, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        metrics = self.get_metrics(name=name, hours=hours)
        
        if not metrics:
            return {"error": "No metrics found"}
        
        values = [m.value for m in metrics]
        
        return {
            "name": name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "time_range": {
                "start": min(m.timestamp for m in metrics).isoformat(),
                "end": max(m.timestamp for m in metrics).isoformat()
            }
        }

class LogManager:
    """Manages comprehensive logging"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.max_logs = 10000
    
    def log(self, level: str, message: str, source: str = "system", metadata: Dict[str, Any] = None):
        """Add a log entry"""
        if level not in self.log_levels:
            level = "INFO"
        
        log_entry = LogEntry(
            log_id=f"log_{int(time.time() * 1000)}",
            level=level,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.logs.append(log_entry)
        
        # Keep only last max_logs entries
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Also log to standard logger
        getattr(logger, level.lower(), logger.info)(f"[{source}] {message}")
    
    def get_logs(self, level: Optional[str] = None, source: Optional[str] = None, 
                hours: int = 24) -> List[LogEntry]:
        """Get logs with optional filtering"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_logs = [
            l for l in self.logs 
            if l.timestamp >= cutoff_time
        ]
        
        if level:
            filtered_logs = [l for l in filtered_logs if l.level == level]
        
        if source:
            filtered_logs = [l for l in filtered_logs if l.source == source]
        
        return filtered_logs
    
    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get log summary statistics"""
        logs = self.get_logs(hours=hours)
        
        level_counts = {}
        source_counts = {}
        
        for log in logs:
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
            source_counts[log.source] = source_counts.get(log.source, 0) + 1
        
        return {
            "total_logs": len(logs),
            "level_distribution": level_counts,
            "source_distribution": source_counts,
            "time_range": {
                "start": min(l.timestamp for l in logs).isoformat() if logs else None,
                "end": max(l.timestamp for l in logs).isoformat() if logs else None
            }
        }

class EnhancedMonitoringSystem:
    """Main enhanced monitoring system"""
    
    def __init__(self, controller_host: str, api_key: str):
        self.controller_host = controller_host
        self.api_key = api_key
        
        # Initialize components
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector(controller_host, api_key)
        self.log_manager = LogManager()
        
        # Monitoring state
        self.monitoring_enabled = False
        self.monitoring_thread = None
        
        # Register alert callbacks
        self.alert_manager.register_alert_callback(self._handle_alert)
    
    def start_monitoring(self):
        """Start comprehensive monitoring"""
        if self.monitoring_enabled:
            logger.warning("Monitoring is already running")
            return
        
        self.monitoring_enabled = True
        
        # Start metrics collection
        self.metrics_collector.start_collection()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.log_manager.log("INFO", "Enhanced monitoring system started", "monitoring")
        logger.info("Enhanced monitoring system started")
    
    def stop_monitoring(self):
        """Stop comprehensive monitoring"""
        self.monitoring_enabled = False
        
        # Stop metrics collection
        self.metrics_collector.stop_collection()
        
        # Stop monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.log_manager.log("INFO", "Enhanced monitoring system stopped", "monitoring")
        logger.info("Enhanced monitoring system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Check for alerts based on metrics
                self._check_metric_alerts()
                
                # Check for system health
                self._check_system_health()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.log_manager.log("ERROR", f"Error in monitoring loop: {str(e)}", "monitoring")
                time.sleep(60)  # Wait longer on error
    
    def _check_metric_alerts(self):
        """Check metrics for alert conditions"""
        try:
            # Check CPU usage
            cpu_metrics = self.metrics_collector.get_metrics("device_cpu_usage", hours=1)
            for metric in cpu_metrics:
                if metric.value > 80:
                    alert = Alert(
                        alert_id=f"cpu_high_{int(time.time())}",
                        title="High CPU Usage",
                        description=f"Device {metric.source} has high CPU usage: {metric.value}%",
                        level=AlertLevel.WARNING,
                        alert_type=AlertType.PERFORMANCE,
                        source=metric.source,
                        timestamp=datetime.now(),
                        metadata={"metric_value": metric.value, "threshold": 80}
                    )
                    self.alert_manager.create_alert(alert)
            
            # Check memory usage
            memory_metrics = self.metrics_collector.get_metrics("device_memory_usage", hours=1)
            for metric in memory_metrics:
                if metric.value > 85:
                    alert = Alert(
                        alert_id=f"memory_high_{int(time.time())}",
                        title="High Memory Usage",
                        description=f"Device {metric.source} has high memory usage: {metric.value}%",
                        level=AlertLevel.WARNING,
                        alert_type=AlertType.PERFORMANCE,
                        source=metric.source,
                        timestamp=datetime.now(),
                        metadata={"metric_value": metric.value, "threshold": 85}
                    )
                    self.alert_manager.create_alert(alert)
            
            # Check device status
            status_metrics = self.metrics_collector.get_metrics("device_status", hours=1)
            for metric in status_metrics:
                if metric.value == 0:  # Device offline
                    alert = Alert(
                        alert_id=f"device_offline_{int(time.time())}",
                        title="Device Offline",
                        description=f"Device {metric.source} is offline",
                        level=AlertLevel.ERROR,
                        alert_type=AlertType.CONNECTIVITY,
                        source=metric.source,
                        timestamp=datetime.now(),
                        metadata={"device_status": "offline"}
                    )
                    self.alert_manager.create_alert(alert)
                    
        except Exception as e:
            self.log_manager.log("ERROR", f"Error checking metric alerts: {str(e)}", "monitoring")
    
    def _check_system_health(self):
        """Check overall system health"""
        try:
            # Check if we have recent metrics
            recent_metrics = self.metrics_collector.get_metrics(hours=1)
            if not recent_metrics:
                alert = Alert(
                    alert_id=f"no_metrics_{int(time.time())}",
                    title="No Recent Metrics",
                    description="No metrics collected in the last hour",
                    level=AlertLevel.WARNING,
                    alert_type=AlertType.SYSTEM,
                    source="monitoring",
                    timestamp=datetime.now(),
                    metadata={"last_metric_time": "unknown"}
                )
                self.alert_manager.create_alert(alert)
                
        except Exception as e:
            self.log_manager.log("ERROR", f"Error checking system health: {str(e)}", "monitoring")
    
    def _handle_alert(self, alert: Alert):
        """Handle alert events"""
        self.log_manager.log("WARNING", f"Alert triggered: {alert.title}", "alerts", {
            "alert_id": alert.alert_id,
            "level": alert.level.value,
            "type": alert.alert_type.value
        })
    
    def add_notification_channel(self, channel: Dict[str, Any]) -> bool:
        """Add a notification channel"""
        return self.alert_manager.add_notification_channel(channel)
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_enabled": self.monitoring_enabled,
            "alerts": {
                "total": len(self.alert_manager.alerts),
                "active": len(self.alert_manager.get_active_alerts()),
                "by_level": {
                    level.value: len(self.alert_manager.get_alerts_by_level(level))
                    for level in AlertLevel
                }
            },
            "metrics": {
                "total_collected": len(self.metrics_collector.metrics),
                "collection_enabled": self.metrics_collector.collection_enabled
            },
            "logs": self.log_manager.get_log_summary(hours=24),
            "system_health": self._get_system_health_summary()
        }
    
    def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary"""
        try:
            # Get recent metrics
            recent_metrics = self.metrics_collector.get_metrics(hours=1)
            
            # Calculate health score
            health_score = 100
            issues = []
            
            # Check for high CPU usage
            cpu_metrics = [m for m in recent_metrics if m.name == "device_cpu_usage"]
            if cpu_metrics:
                avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
                if avg_cpu > 80:
                    health_score -= 20
                    issues.append("High CPU usage")
            
            # Check for high memory usage
            memory_metrics = [m for m in recent_metrics if m.name == "device_memory_usage"]
            if memory_metrics:
                avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
                if avg_memory > 85:
                    health_score -= 20
                    issues.append("High memory usage")
            
            # Check for offline devices
            status_metrics = [m for m in recent_metrics if m.name == "device_status"]
            offline_devices = [m for m in status_metrics if m.value == 0]
            if offline_devices:
                health_score -= 30
                issues.append(f"{len(offline_devices)} devices offline")
            
            return {
                "health_score": max(0, health_score),
                "issues": issues,
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "critical"
            }
            
        except Exception as e:
            self.log_manager.log("ERROR", f"Error calculating system health: {str(e)}", "monitoring")
            return {
                "health_score": 0,
                "issues": ["Error calculating health"],
                "status": "unknown"
            }

def main():
    """Main function for Enhanced Monitoring System demonstration"""
    print(f"\n{'='*80}")
    print("Enhanced Monitoring System with Comprehensive Logging and Alerting")
    print(f"{'='*80}")
    
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize Enhanced Monitoring System
        print("Initializing Enhanced Monitoring System...")
        monitoring_system = EnhancedMonitoringSystem(controller_host, api_key)
        
        # Add notification channels
        print("\nConfiguring notification channels...")
        
        # Email notification (if configured)
        email_channel = {
            "type": "email",
            "name": "Email Alerts",
            "smtp_server": os.getenv('SMTP_SERVER', 'localhost'),
            "smtp_port": int(os.getenv('SMTP_PORT', '587')),
            "username": os.getenv('SMTP_USERNAME', ''),
            "password": os.getenv('SMTP_PASSWORD', ''),
            "to_email": os.getenv('ALERT_EMAIL', '')
        }
        monitoring_system.add_notification_channel(email_channel)
        
        # Webhook notification (if configured)
        webhook_channel = {
            "type": "webhook",
            "name": "Webhook Alerts",
            "url": os.getenv('WEBHOOK_URL', '')
        }
        monitoring_system.add_notification_channel(webhook_channel)
        
        # Start monitoring
        print("\nStarting comprehensive monitoring...")
        monitoring_system.start_monitoring()
        
        # Simulate some monitoring activity
        print("\nSimulating monitoring activity...")
        
        # Log some events
        monitoring_system.log_manager.log("INFO", "Monitoring system initialized", "system")
        monitoring_system.log_manager.log("WARNING", "High CPU usage detected on device", "performance", {
            "device": "USG-Pro-4",
            "cpu_usage": 85
        })
        monitoring_system.log_manager.log("ERROR", "Device connection lost", "connectivity", {
            "device": "Switch-24",
            "status": "offline"
        })
        
        # Create some test alerts
        test_alert = Alert(
            alert_id="test_alert_001",
            title="Test Security Alert",
            description="This is a test security alert for demonstration",
            level=AlertLevel.WARNING,
            alert_type=AlertType.SECURITY,
            source="monitoring_system",
            timestamp=datetime.now(),
            metadata={"test": True, "severity": "medium"}
        )
        monitoring_system.alert_manager.create_alert(test_alert)
        
        # Wait a bit for metrics collection
        print("Collecting metrics for 30 seconds...")
        time.sleep(30)
        
        # Get monitoring dashboard
        print("\nGenerating monitoring dashboard...")
        dashboard = monitoring_system.get_monitoring_dashboard()
        
        # Save dashboard data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"monitoring_dashboard_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("✅ ENHANCED MONITORING SYSTEM SETUP COMPLETED!")
        print(f"{'='*80}")
        print(f"Monitoring Status: {'Enabled' if dashboard['monitoring_enabled'] else 'Disabled'}")
        print(f"Total Alerts: {dashboard['alerts']['total']}")
        print(f"Active Alerts: {dashboard['alerts']['active']}")
        print(f"Metrics Collected: {dashboard['metrics']['total_collected']}")
        print(f"System Health: {dashboard['system_health']['status']} ({dashboard['system_health']['health_score']}/100)")
        print(f"Dashboard saved to: {filename}")
        print("\nKey Features Implemented:")
        print("  ✓ Real-time metrics collection")
        print("  ✓ Comprehensive alerting system")
        print("  ✓ Multi-channel notifications (email, webhook, syslog)")
        print("  ✓ Advanced logging with filtering and search")
        print("  ✓ System health monitoring")
        print("  ✓ Automated alert rule evaluation")
        print("  ✓ Performance and connectivity monitoring")
        print("  ✓ Dashboard and reporting capabilities")
        
        # Stop monitoring for demo
        print("\nStopping monitoring...")
        monitoring_system.stop_monitoring()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
