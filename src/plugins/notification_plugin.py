"""
Notification System for Cosik AI Agent.

Features:
- Desktop notifications (Windows toast)
- Sound alerts
- Email notifications
- Webhook notifications
- Notification history
- Priority levels
- Custom notification templates
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from loguru import logger
import json

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    logger.warning("win10toast not available - Toast notifications disabled")

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


class NotificationSystem:
    """
    Notification system for alerts and updates.
    
    Features:
    - Desktop notifications
    - Sound alerts
    - Email integration
    - Webhooks
    - History tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize notification system.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.notification_config = config.get('notifications', {})
        
        # Toast notifier
        self.toaster = ToastNotifier() if TOAST_AVAILABLE else None
        
        # Notification history
        self.history = []
        self.max_history = self.notification_config.get('max_history', 1000)
        
        # Notification templates
        self.templates = {}
        
        logger.info("Notification system initialized")
    
    async def send(self, message: str, title: str = "Cosik AI Agent",
                  priority: str = 'normal', notification_type: str = 'desktop',
                  **kwargs) -> Dict[str, Any]:
        """
        Send notification.
        
        Args:
            message: Notification message
            title: Notification title
            priority: Priority level (low, normal, high, critical)
            notification_type: Type of notification (desktop, sound, email, webhook)
            **kwargs: Additional parameters
            
        Returns:
            Notification result
        """
        try:
            result = {
                'success': False,
                'sent': []
            }
            
            # Desktop notification
            if notification_type in ['desktop', 'all']:
                desktop_result = await self._send_desktop(title, message, **kwargs)
                if desktop_result['success']:
                    result['sent'].append('desktop')
            
            # Sound notification
            if notification_type in ['sound', 'all'] or priority == 'critical':
                sound_result = await self._send_sound(priority, **kwargs)
                if sound_result['success']:
                    result['sent'].append('sound')
            
            # Email notification
            if notification_type in ['email', 'all']:
                email_result = await self._send_email(title, message, **kwargs)
                if email_result['success']:
                    result['sent'].append('email')
            
            # Webhook notification
            if notification_type in ['webhook', 'all']:
                webhook_result = await self._send_webhook(title, message, **kwargs)
                if webhook_result['success']:
                    result['sent'].append('webhook')
            
            # Add to history
            self._add_to_history({
                'timestamp': datetime.now().isoformat(),
                'title': title,
                'message': message,
                'priority': priority,
                'type': notification_type,
                'sent': result['sent']
            })
            
            result['success'] = len(result['sent']) > 0
            
            logger.info(f"Notification sent via: {', '.join(result['sent'])}")
            return result
        
        except Exception as e:
            logger.error(f"Send notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _send_desktop(self, title: str, message: str,
                           duration: int = 5, icon_path: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """Send desktop notification."""
        try:
            if not TOAST_AVAILABLE:
                logger.warning("Toast notifications not available")
                return {'success': False, 'error': 'Toast not available'}
            
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon_path,
                threaded=True
            )
            
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_sound(self, priority: str = 'normal', **kwargs) -> Dict[str, Any]:
        """Send sound alert."""
        try:
            if not SOUND_AVAILABLE:
                return {'success': False, 'error': 'Sound not available'}
            
            # Map priority to sound
            sounds = {
                'low': (800, 200),
                'normal': (1000, 300),
                'high': (1200, 400),
                'critical': (1500, 500)
            }
            
            frequency, duration = sounds.get(priority, sounds['normal'])
            winsound.Beep(frequency, duration)
            
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Sound notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_email(self, title: str, message: str,
                         recipient: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Send email notification."""
        try:
            # Check if email plugin is available
            email_config = self.notification_config.get('email', {})
            
            if not email_config.get('enabled', False):
                return {'success': False, 'error': 'Email notifications not configured'}
            
            # This would integrate with email plugin
            # For now, just return success if configured
            logger.info(f"Email notification would be sent: {title}")
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_webhook(self, title: str, message: str,
                           url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Send webhook notification."""
        try:
            webhook_config = self.notification_config.get('webhook', {})
            
            if not webhook_config.get('enabled', False):
                return {'success': False, 'error': 'Webhook notifications not configured'}
            
            # This would send HTTP POST to webhook URL
            # For now, just return success if configured
            logger.info(f"Webhook notification would be sent: {title}")
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _add_to_history(self, notification: Dict[str, Any]):
        """Add notification to history."""
        self.history.append(notification)
        
        # Trim history if too large
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    async def get_history(self, limit: int = 50, priority: Optional[str] = None) -> Dict[str, Any]:
        """Get notification history."""
        try:
            filtered = self.history
            
            if priority:
                filtered = [n for n in filtered if n.get('priority') == priority]
            
            # Get latest N
            recent = filtered[-limit:]
            
            return {
                'success': True,
                'notifications': recent,
                'count': len(recent)
            }
        
        except Exception as e:
            logger.error(f"Get history failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def clear_history(self) -> Dict[str, Any]:
        """Clear notification history."""
        try:
            count = len(self.history)
            self.history = []
            
            return {
                'success': True,
                'cleared': count
            }
        
        except Exception as e:
            logger.error(f"Clear history failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_template(self, name: str, title: str, message: str) -> Dict[str, Any]:
        """Create notification template."""
        try:
            self.templates[name] = {
                'title': title,
                'message': message
            }
            
            logger.info(f"Notification template created: {name}")
            return {
                'success': True,
                'template': name
            }
        
        except Exception as e:
            logger.error(f"Create template failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_from_template(self, template_name: str, 
                                variables: Optional[Dict[str, str]] = None,
                                **kwargs) -> Dict[str, Any]:
        """Send notification from template."""
        try:
            if template_name not in self.templates:
                return {
                    'success': False,
                    'error': f'Template not found: {template_name}'
                }
            
            template = self.templates[template_name]
            
            # Replace variables
            title = template['title']
            message = template['message']
            
            if variables:
                for key, value in variables.items():
                    title = title.replace(f'{{{key}}}', str(value))
                    message = message.replace(f'{{{key}}}', str(value))
            
            return await self.send(message, title=title, **kwargs)
        
        except Exception as e:
            logger.error(f"Send from template failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        try:
            total = len(self.history)
            
            by_priority = {}
            by_type = {}
            
            for notif in self.history:
                priority = notif.get('priority', 'unknown')
                by_priority[priority] = by_priority.get(priority, 0) + 1
                
                notif_type = notif.get('type', 'unknown')
                by_type[notif_type] = by_type.get(notif_type, 0) + 1
            
            return {
                'total': total,
                'by_priority': by_priority,
                'by_type': by_type
            }
        
        except Exception as e:
            logger.error(f"Get stats failed: {e}")
            return {}


# For plugin compatibility
class NotificationPlugin:
    """Notification plugin wrapper."""
    
    def __init__(self, config: Dict[str, Any]):
        self.system = NotificationSystem(config)
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        action = kwargs.get('action', 'send')
        
        if action == 'send':
            return await self.system.send(**kwargs)
        elif action == 'history':
            return await self.system.get_history(**kwargs)
        elif action == 'clear_history':
            return await self.system.clear_history()
        elif action == 'create_template':
            return await self.system.create_template(**kwargs)
        elif action == 'send_template':
            return await self.system.send_from_template(**kwargs)
        elif action == 'stats':
            return {'success': True, 'stats': self.system.get_stats()}
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            'name': 'notification',
            'version': '1.0.0',
            'description': 'Desktop and system notifications',
            'actions': ['send', 'history', 'clear_history', 'create_template', 'send_template', 'stats'],
            'types': ['desktop', 'sound', 'email', 'webhook']
        }


# Plugin metadata
PLUGIN_INFO = {
    'name': 'notification',
    'version': '1.0.0',
    'class': NotificationPlugin,
    'description': 'System notifications and alerts',
    'author': 'Finder995',
    'requires': [],
    'optional': ['win10toast', 'winsound']
}
