"""
Email Plugin for Cosik AI Agent.

Features:
- Send emails (SMTP)
- Receive emails (IMAP/POP3)
- Email templates
- Attachments support
- Email filtering and search
- Bulk email operations
- Email automation workflows
"""

import smtplib
import imaplib
import poplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from loguru import logger
import re


class EmailPlugin:
    """
    Email operations plugin for sending and receiving emails.
    
    Features:
    - SMTP for sending
    - IMAP/POP3 for receiving
    - Attachment handling
    - Email templates
    - Search and filter
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email plugin.
        
        Args:
            config: Plugin configuration
        """
        self.config = config
        self.email_config = config.get('plugins', {}).get('email', {})
        
        # Email accounts
        self.accounts = {}
        
        # Email templates
        self.templates = {}
        
        logger.info("Email plugin initialized")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute email operation.
        
        Args:
            command: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Operation result
        """
        action = kwargs.pop('action', 'send')
        
        try:
            if action == 'send':
                return await self._send_email(**kwargs)
            elif action == 'receive':
                return await self._receive_emails(**kwargs)
            elif action == 'search':
                return await self._search_emails(**kwargs)
            elif action == 'delete':
                return await self._delete_email(**kwargs)
            elif action == 'add_account':
                return await self._add_account(**kwargs)
            elif action == 'list_accounts':
                return await self._list_accounts(**kwargs)
            elif action == 'create_template':
                return await self._create_template(**kwargs)
            elif action == 'send_bulk':
                return await self._send_bulk(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
        except Exception as e:
            logger.error(f"Email operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _add_account(self, name: str, smtp_server: str, smtp_port: int,
                          imap_server: Optional[str] = None, imap_port: Optional[int] = None,
                          username: str = '', password: str = '',
                          use_tls: bool = True) -> Dict[str, Any]:
        """Add email account."""
        try:
            self.accounts[name] = {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'imap_server': imap_server,
                'imap_port': imap_port or 993,
                'username': username,
                'password': password,
                'use_tls': use_tls
            }
            
            logger.info(f"Email account added: {name}")
            return {
                'success': True,
                'account': name
            }
        except Exception as e:
            logger.error(f"Add account failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _list_accounts(self) -> Dict[str, Any]:
        """List configured email accounts."""
        return {
            'success': True,
            'accounts': list(self.accounts.keys()),
            'count': len(self.accounts)
        }
    
    async def _send_email(self, account: str, to: Union[str, List[str]], 
                         subject: str, body: str,
                         cc: Optional[Union[str, List[str]]] = None,
                         bcc: Optional[Union[str, List[str]]] = None,
                         attachments: Optional[List[str]] = None,
                         html: bool = False,
                         template: Optional[str] = None,
                         template_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send email."""
        try:
            if account not in self.accounts:
                return {
                    'success': False,
                    'error': f'Account not found: {account}'
                }
            
            acc = self.accounts[account]
            
            # Use template if provided
            if template and template in self.templates:
                body = self.templates[template]
                if template_vars:
                    body = body.format(**template_vars)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = acc['username']
            msg['Subject'] = subject
            
            # Handle recipients
            if isinstance(to, str):
                to = [to]
            msg['To'] = ', '.join(to)
            
            if cc:
                if isinstance(cc, str):
                    cc = [cc]
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    if not Path(file_path).exists():
                        logger.warning(f"Attachment not found: {file_path}")
                        continue
                    
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(file_path).name}'
                    )
                    msg.attach(part)
            
            # Send email
            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                if isinstance(bcc, str):
                    bcc = [bcc]
                recipients.extend(bcc)
            
            with smtplib.SMTP(acc['smtp_server'], acc['smtp_port']) as server:
                if acc['use_tls']:
                    server.starttls()
                
                server.login(acc['username'], acc['password'])
                server.send_message(msg, acc['username'], recipients)
            
            logger.info(f"Email sent to {len(recipients)} recipients")
            return {
                'success': True,
                'recipients': len(recipients),
                'subject': subject
            }
        
        except Exception as e:
            logger.error(f"Send email failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _receive_emails(self, account: str, folder: str = 'INBOX',
                             limit: int = 10, unread_only: bool = True) -> Dict[str, Any]:
        """Receive emails from IMAP."""
        try:
            if account not in self.accounts:
                return {
                    'success': False,
                    'error': f'Account not found: {account}'
                }
            
            acc = self.accounts[account]
            
            if not acc.get('imap_server'):
                return {
                    'success': False,
                    'error': 'IMAP server not configured'
                }
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(acc['imap_server'], acc['imap_port'])
            mail.login(acc['username'], acc['password'])
            mail.select(folder)
            
            # Search for emails
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = mail.search(None, search_criteria)
            
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:]  # Get latest N emails
            
            emails = []
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Extract email details
                        email_info = {
                            'id': email_id.decode(),
                            'from': msg['From'],
                            'to': msg['To'],
                            'subject': msg['Subject'],
                            'date': msg['Date'],
                            'body': self._get_email_body(msg),
                            'has_attachments': self._has_attachments(msg)
                        }
                        
                        emails.append(email_info)
            
            mail.close()
            mail.logout()
            
            logger.info(f"Retrieved {len(emails)} emails from {account}")
            return {
                'success': True,
                'emails': emails,
                'count': len(emails)
            }
        
        except Exception as e:
            logger.error(f"Receive emails failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _search_emails(self, account: str, query: str,
                            folder: str = 'INBOX', limit: int = 50) -> Dict[str, Any]:
        """Search emails."""
        try:
            if account not in self.accounts:
                return {
                    'success': False,
                    'error': f'Account not found: {account}'
                }
            
            acc = self.accounts[account]
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(acc['imap_server'], acc['imap_port'])
            mail.login(acc['username'], acc['password'])
            mail.select(folder)
            
            # Build search query
            # Simple query parsing (can be enhanced)
            search_criteria = f'(SUBJECT "{query}")'
            
            status, messages = mail.search(None, search_criteria)
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:]
            
            emails = []
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        emails.append({
                            'id': email_id.decode(),
                            'from': msg['From'],
                            'subject': msg['Subject'],
                            'date': msg['Date']
                        })
            
            mail.close()
            mail.logout()
            
            logger.info(f"Found {len(emails)} emails matching query")
            return {
                'success': True,
                'emails': emails,
                'count': len(emails)
            }
        
        except Exception as e:
            logger.error(f"Search emails failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _delete_email(self, account: str, email_id: str,
                           folder: str = 'INBOX') -> Dict[str, Any]:
        """Delete email."""
        try:
            if account not in self.accounts:
                return {
                    'success': False,
                    'error': f'Account not found: {account}'
                }
            
            acc = self.accounts[account]
            
            mail = imaplib.IMAP4_SSL(acc['imap_server'], acc['imap_port'])
            mail.login(acc['username'], acc['password'])
            mail.select(folder)
            
            # Mark for deletion
            mail.store(email_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            
            mail.close()
            mail.logout()
            
            logger.info(f"Email deleted: {email_id}")
            return {
                'success': True,
                'email_id': email_id
            }
        
        except Exception as e:
            logger.error(f"Delete email failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_template(self, name: str, content: str) -> Dict[str, Any]:
        """Create email template."""
        try:
            self.templates[name] = content
            
            logger.info(f"Email template created: {name}")
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
    
    async def _send_bulk(self, account: str, recipients: List[str],
                        subject: str, body: str, **kwargs) -> Dict[str, Any]:
        """Send bulk emails."""
        try:
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for recipient in recipients:
                result = await self._send_email(
                    account=account,
                    to=recipient,
                    subject=subject,
                    body=body,
                    **kwargs
                )
                
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'recipient': recipient,
                        'error': result.get('error', 'Unknown error')
                    })
            
            logger.info(f"Bulk email: {results['success']} sent, {results['failed']} failed")
            return {
                'success': True,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Bulk send failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_email_body(self, msg) -> str:
        """Extract email body."""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                pass
        
        return body
    
    def _has_attachments(self, msg) -> bool:
        """Check if email has attachments."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    return True
        return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities."""
        return {
            'name': 'email',
            'version': '1.0.0',
            'description': 'Email operations (send/receive)',
            'actions': [
                'send', 'receive', 'search', 'delete',
                'add_account', 'list_accounts',
                'create_template', 'send_bulk'
            ],
            'protocols': ['SMTP', 'IMAP']
        }


# Plugin metadata
PLUGIN_INFO = {
    'name': 'email',
    'version': '1.0.0',
    'class': EmailPlugin,
    'description': 'Email automation (SMTP, IMAP)',
    'author': 'Finder995',
    'requires': ['smtplib', 'imaplib', 'email']
}
