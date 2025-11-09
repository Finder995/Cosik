"""
Usage Examples for New Plugins (v2.3.0).

Demonstracja nowych funkcji:
- Database operations
- Email automation
- Browser automation
- Notifications
- Voice recognition
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.plugins.database_plugin import DatabasePlugin
from src.plugins.email_plugin import EmailPlugin
from src.plugins.browser_automation_plugin import BrowserAutomationPlugin
from src.plugins.notification_plugin import NotificationPlugin
from src.voice.voice_recognition import VoiceRecognitionModule


async def database_examples():
    """Database plugin examples."""
    print("\n=== DATABASE PLUGIN EXAMPLES ===\n")
    
    config = {'plugins': {'database': {}}}
    plugin = DatabasePlugin(config)
    
    # 1. Connect to SQLite database
    print("1. Connecting to SQLite database...")
    result = await plugin.execute('', action='connect', database='demo', path='./data/demo.db')
    print(f"   Connected: {result['success']}")
    
    # 2. Create table
    print("\n2. Creating users table...")
    schema = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT NOT NULL',
        'email': 'TEXT UNIQUE',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    result = await plugin.execute('', action='create_table', table_name='users', schema=schema, database='demo')
    print(f"   Table created: {result['success']}")
    
    # 3. Insert data
    print("\n3. Inserting users...")
    users = [
        {'name': 'Alice', 'email': 'alice@example.com'},
        {'name': 'Bob', 'email': 'bob@example.com'},
        {'name': 'Charlie', 'email': 'charlie@example.com'}
    ]
    
    for user in users:
        result = await plugin.execute('', action='insert', table='users', data=user, database='demo')
        print(f"   Inserted {user['name']}: {result['success']}")
    
    # 4. Query data
    print("\n4. Querying all users...")
    result = await plugin.execute('', action='query', sql='SELECT * FROM users', database='demo')
    if result['success']:
        print(f"   Found {result['row_count']} users:")
        for user in result['rows']:
            print(f"   - {user['name']} ({user['email']})")
    
    # 5. List tables
    print("\n5. Listing tables...")
    result = await plugin.execute('', action='list_tables', database='demo')
    print(f"   Tables: {', '.join(result['tables'])}")
    
    # 6. Backup database
    print("\n6. Creating backup...")
    result = await plugin.execute('', action='backup', database='demo')
    if result['success']:
        print(f"   Backup saved to: {result['backup_path']}")


async def email_examples():
    """Email plugin examples."""
    print("\n=== EMAIL PLUGIN EXAMPLES ===\n")
    
    config = {'plugins': {'email': {}}}
    plugin = EmailPlugin(config)
    
    # 1. Add email account
    print("1. Adding email account...")
    result = await plugin.execute(
        '',
        action='add_account',
        name='demo',
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        imap_server='imap.gmail.com',
        username='demo@example.com',
        password='demo_password',
        use_tls=True
    )
    print(f"   Account added: {result['success']}")
    
    # 2. Create email template
    print("\n2. Creating email template...")
    result = await plugin.execute(
        '',
        action='create_template',
        name='welcome',
        content="""
        Hello {name}!
        
        Welcome to our service. We're glad to have you here.
        
        Best regards,
        The Team
        """
    )
    print(f"   Template created: {result['success']}")
    
    # 3. List accounts
    print("\n3. Listing accounts...")
    result = await plugin.execute('', action='list_accounts')
    print(f"   Accounts: {', '.join(result['accounts'])}")
    
    print("\n   Note: Actual email sending requires valid SMTP credentials")


async def browser_examples():
    """Browser automation plugin examples."""
    print("\n=== BROWSER AUTOMATION PLUGIN EXAMPLES ===\n")
    
    config = {'plugins': {'browser': {}}}
    plugin = BrowserAutomationPlugin(config)
    
    print("   Note: Browser automation requires Selenium WebDriver")
    print("   Install with: pip install selenium")
    print("\n   Example operations:")
    print("   - Start browser (Chrome/Firefox/Edge)")
    print("   - Navigate to URLs")
    print("   - Click elements")
    print("   - Fill forms")
    print("   - Execute JavaScript")
    print("   - Take screenshots")
    
    # Example code (would work if Selenium is installed):
    """
    # Start Chrome browser
    await plugin.execute('', action='start', browser_type='chrome', headless=True)
    
    # Navigate to website
    await plugin.execute('', action='navigate', url='https://example.com')
    
    # Click button
    await plugin.execute('', action='click', selector='#submit-button')
    
    # Type text
    await plugin.execute('', action='type', selector='#search', text='query')
    
    # Take screenshot
    await plugin.execute('', action='screenshot', filename='page.png')
    
    # Stop browser
    await plugin.execute('', action='stop')
    """


async def notification_examples():
    """Notification system examples."""
    print("\n=== NOTIFICATION SYSTEM EXAMPLES ===\n")
    
    config = {'notifications': {'max_history': 100}}
    plugin = NotificationPlugin(config)
    
    # 1. Create notification template
    print("1. Creating notification template...")
    result = await plugin.execute(
        '',
        action='create_template',
        name='task_complete',
        title='Task Complete: {task_name}',
        message='Task {task_name} completed successfully at {time}'
    )
    print(f"   Template created: {result['success']}")
    
    # 2. Add notifications to history (simulated)
    print("\n2. Simulating notifications...")
    from datetime import datetime
    
    notifications = [
        {'title': 'System Start', 'message': 'Agent started', 'priority': 'normal', 'type': 'desktop'},
        {'title': 'Task Complete', 'message': 'File processed', 'priority': 'low', 'type': 'desktop'},
        {'title': 'Error Occurred', 'message': 'Connection failed', 'priority': 'high', 'type': 'desktop'},
        {'title': 'Critical Alert', 'message': 'System overload', 'priority': 'critical', 'type': 'all'}
    ]
    
    for notif in notifications:
        plugin.system.history.append({
            'timestamp': datetime.now().isoformat(),
            **notif,
            'sent': ['desktop']
        })
    
    print(f"   Added {len(notifications)} notifications")
    
    # 3. Get statistics
    print("\n3. Notification statistics...")
    result = await plugin.execute('', action='stats')
    if result['success']:
        stats = result['stats']
        print(f"   Total notifications: {stats['total']}")
        print(f"   By priority: {stats['by_priority']}")
        print(f"   By type: {stats['by_type']}")
    
    # 4. Get history
    print("\n4. Recent notifications...")
    result = await plugin.execute('', action='history', limit=3)
    if result['success']:
        for notif in result['notifications']:
            print(f"   [{notif['priority']}] {notif['title']}: {notif['message']}")


async def voice_examples():
    """Voice recognition module examples."""
    print("\n=== VOICE RECOGNITION EXAMPLES ===\n")
    
    config = {'voice': {'language': 'en-US'}}
    module = VoiceRecognitionModule(config)
    
    # 1. Check status
    print("1. Module status...")
    status = module.get_status()
    print(f"   Available: {status['available']}")
    print(f"   Language: {status['language']}")
    
    # 2. Set language
    print("\n2. Setting language to Polish...")
    result = await module.set_language('pl-PL')
    print(f"   Language set: {result['success']}")
    
    # 3. Add to history (simulated)
    print("\n3. Simulating voice recognition history...")
    from datetime import datetime
    
    recognitions = [
        {'text': 'Open Chrome', 'language': 'en-US', 'source': 'microphone'},
        {'text': 'Send email to John', 'language': 'en-US', 'source': 'microphone'},
        {'text': 'Create new file', 'language': 'en-US', 'source': 'microphone'}
    ]
    
    for rec in recognitions:
        module.history.append({
            'timestamp': datetime.now().isoformat(),
            **rec
        })
    
    print(f"   Added {len(recognitions)} recognition entries")
    
    # 4. Get history
    print("\n4. Recent recognitions...")
    result = await module.get_history(limit=5)
    if result['success']:
        for rec in result['history']:
            print(f"   [{rec['language']}] {rec['text']}")
    
    print("\n   Note: Actual voice recognition requires microphone and SpeechRecognition library")
    print("   Install with: pip install SpeechRecognition pyaudio")


async def integrated_workflow_example():
    """Integrated workflow using multiple plugins."""
    print("\n=== INTEGRATED WORKFLOW EXAMPLE ===\n")
    print("Scenario: Automated report generation and notification")
    print()
    
    # 1. Database: Query data
    print("Step 1: Query data from database...")
    db_config = {'plugins': {'database': {}}}
    db = DatabasePlugin(db_config)
    await db.execute('', action='connect', database='reports', path='./data/reports.db')
    print("   ✓ Database connected")
    
    # 2. Generate report (simulated)
    print("\nStep 2: Generate report...")
    print("   ✓ Report generated: report_2024.pdf")
    
    # 3. Email: Send report
    print("\nStep 3: Send report via email...")
    email_config = {'plugins': {'email': {}}}
    email = EmailPlugin(email_config)
    print("   ✓ Email would be sent with attachment")
    
    # 4. Notification: Notify completion
    print("\nStep 4: Send completion notification...")
    notif_config = {'notifications': {}}
    notif = NotificationPlugin(notif_config)
    print("   ✓ Notification sent")
    
    print("\n✓ Workflow completed successfully!")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("COSIK AI AGENT - NEW PLUGINS EXAMPLES (v2.3.0)")
    print("=" * 60)
    
    try:
        await database_examples()
        await email_examples()
        await browser_examples()
        await notification_examples()
        await voice_examples()
        await integrated_workflow_example()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
