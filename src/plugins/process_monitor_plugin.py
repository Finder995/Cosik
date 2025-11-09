"""
Process Monitor Plugin for tracking system processes.
Allows the AI agent to monitor CPU, memory usage, and manage processes.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed. Install with: pip install psutil")


class ProcessMonitorPlugin:
    """Plugin for monitoring and managing system processes."""
    
    def __init__(self, config):
        """Initialize process monitor plugin."""
        self.config = config
        self.monitoring = False
        self.monitor_task = None
        self.process_history = []
        self.max_history = config.get('plugins.process_monitor.max_history', 100)
        self.alert_thresholds = {
            'cpu_percent': config.get('plugins.process_monitor.cpu_threshold', 80.0),
            'memory_percent': config.get('plugins.process_monitor.memory_threshold', 80.0)
        }
        
        if not PSUTIL_AVAILABLE:
            logger.warning("Process monitor plugin initialized but psutil is not available")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute process monitor command.
        
        Commands:
        - list: List all running processes
        - info: Get detailed info about a process
        - kill: Kill a process by PID or name
        - top: Get top processes by CPU or memory
        - system: Get system-wide statistics
        - monitor_start: Start monitoring processes
        - monitor_stop: Stop monitoring processes
        - history: Get monitoring history
        """
        if not PSUTIL_AVAILABLE:
            return {
                'success': False,
                'error': 'psutil not installed',
                'message': 'Install psutil to use process monitoring features'
            }
        
        try:
            if command == 'list':
                return await self._list_processes(**kwargs)
            elif command == 'info':
                return await self._process_info(**kwargs)
            elif command == 'kill':
                return await self._kill_process(**kwargs)
            elif command == 'top':
                return await self._top_processes(**kwargs)
            elif command == 'system':
                return await self._system_stats(**kwargs)
            elif command == 'monitor_start':
                return await self._start_monitoring(**kwargs)
            elif command == 'monitor_stop':
                return await self._stop_monitoring(**kwargs)
            elif command == 'history':
                return await self._get_history(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}',
                    'available_commands': self.get_capabilities()
                }
        except Exception as e:
            logger.error(f"Process monitor plugin error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _list_processes(self, filter_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """List running processes."""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    
                    # Filter by name if specified
                    if filter_name and filter_name.lower() not in pinfo['name'].lower():
                        continue
                    
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'status': pinfo['status'],
                        'cpu_percent': round(pinfo['cpu_percent'], 2),
                        'memory_percent': round(pinfo['memory_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'success': True,
                'processes': processes,
                'count': len(processes),
                'filter': filter_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to list processes: {e}'
            }
    
    async def _process_info(self, pid: Optional[int] = None, name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get detailed information about a process."""
        try:
            if pid:
                proc = psutil.Process(pid)
            elif name:
                # Find process by name
                found = None
                for p in psutil.process_iter(['pid', 'name']):
                    if p.info['name'].lower() == name.lower():
                        found = p
                        break
                
                if not found:
                    return {
                        'success': False,
                        'error': f'Process not found: {name}'
                    }
                proc = found
            else:
                return {
                    'success': False,
                    'error': 'Must provide either pid or name'
                }
            
            # Get detailed info
            with proc.oneshot():
                info = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(interval=0.1),
                    'memory_percent': proc.memory_percent(),
                    'memory_info': proc.memory_info()._asdict(),
                    'num_threads': proc.num_threads(),
                    'username': proc.username() if hasattr(proc, 'username') else None,
                    'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
                }
                
                try:
                    info['cmdline'] = proc.cmdline()
                    info['cwd'] = proc.cwd()
                    info['exe'] = proc.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
            
            return {
                'success': True,
                'process': info
            }
            
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'error': 'Process not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get process info: {e}'
            }
    
    async def _kill_process(self, pid: Optional[int] = None, name: Optional[str] = None, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Kill a process."""
        try:
            if pid:
                proc = psutil.Process(pid)
            elif name:
                # Find and kill all processes with this name
                killed = []
                for p in psutil.process_iter(['pid', 'name']):
                    if p.info['name'].lower() == name.lower():
                        try:
                            if force:
                                p.kill()
                            else:
                                p.terminate()
                            killed.append(p.info['pid'])
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                if not killed:
                    return {
                        'success': False,
                        'error': f'No processes found with name: {name}'
                    }
                
                return {
                    'success': True,
                    'message': f'Killed {len(killed)} process(es)',
                    'killed_pids': killed
                }
            else:
                return {
                    'success': False,
                    'error': 'Must provide either pid or name'
                }
            
            # Kill single process by PID
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            logger.info(f"Killed process {pid} ({proc.name()})")
            return {
                'success': True,
                'message': f'Process killed: {pid}',
                'pid': pid
            }
            
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'error': 'Process not found'
            }
        except psutil.AccessDenied:
            return {
                'success': False,
                'error': 'Access denied - insufficient permissions'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to kill process: {e}'
            }
    
    async def _top_processes(self, limit: int = 10, sort_by: str = 'cpu', **kwargs) -> Dict[str, Any]:
        """Get top processes by CPU or memory usage."""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': round(pinfo['cpu_percent'], 2),
                        'memory_percent': round(pinfo['memory_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort processes
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            top = processes[:limit]
            
            return {
                'success': True,
                'processes': top,
                'sort_by': sort_by,
                'count': len(top)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get top processes: {e}'
            }
    
    async def _system_stats(self, **kwargs) -> Dict[str, Any]:
        """Get system-wide statistics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'count_logical': psutil.cpu_count(logical=True)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'process_count': len(psutil.pids())
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get system stats: {e}'
            }
    
    async def _start_monitoring(self, interval: float = 5.0, **kwargs) -> Dict[str, Any]:
        """Start monitoring processes."""
        if self.monitoring:
            return {
                'success': False,
                'message': 'Monitoring already active'
            }
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        
        logger.info(f"Started process monitoring (interval: {interval}s)")
        return {
            'success': True,
            'message': f'Started monitoring processes every {interval}s'
        }
    
    async def _stop_monitoring(self, **kwargs) -> Dict[str, Any]:
        """Stop monitoring processes."""
        if not self.monitoring:
            return {
                'success': False,
                'message': 'Monitoring not active'
            }
        
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped process monitoring")
        return {
            'success': True,
            'message': 'Stopped process monitoring'
        }
    
    async def _monitor_loop(self, interval: float):
        """Monitor processes periodically."""
        try:
            while self.monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    
                    entry = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_percent': round(memory_percent, 2),
                        'process_count': len(psutil.pids())
                    }
                    
                    # Check thresholds
                    alerts = []
                    if cpu_percent > self.alert_thresholds['cpu_percent']:
                        alerts.append(f"High CPU usage: {cpu_percent}%")
                    if memory_percent > self.alert_thresholds['memory_percent']:
                        alerts.append(f"High memory usage: {memory_percent}%")
                    
                    if alerts:
                        entry['alerts'] = alerts
                        logger.warning(f"System alerts: {', '.join(alerts)}")
                    
                    self.process_history.append(entry)
                    
                    # Trim history
                    if len(self.process_history) > self.max_history:
                        self.process_history = self.process_history[-self.max_history:]
                    
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in process monitoring: {e}")
                    await asyncio.sleep(interval)
                    
        except asyncio.CancelledError:
            logger.info("Process monitoring cancelled")
    
    async def _get_history(self, limit: int = 20, **kwargs) -> Dict[str, Any]:
        """Get monitoring history."""
        history_items = self.process_history[-limit:] if limit > 0 else self.process_history
        
        return {
            'success': True,
            'history': history_items,
            'total_entries': len(self.process_history),
            'returned_entries': len(history_items)
        }
    
    def get_capabilities(self) -> List[str]:
        """Return list of available commands."""
        return [
            'list',
            'info',
            'kill',
            'top',
            'system',
            'monitor_start',
            'monitor_stop',
            'history'
        ]
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_task:
                self.monitor_task.cancel()
        
        logger.info("Process monitor plugin cleaned up")


# Plugin metadata
PLUGIN_INFO = {
    'name': 'process_monitor',
    'version': '1.0.0',
    'class': ProcessMonitorPlugin,
    'description': 'Monitor and manage system processes',
    'author': 'Cosik Team',
    'requires': ['psutil']
}
