"""Memory management system for the AI agent."""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger


class MemoryManager:
    """Manage agent memory, including interactions, tasks, and learning."""
    
    def __init__(self, config):
        """Initialize memory manager."""
        self.config = config
        self.enabled = config.get('memory.enabled', True)
        self.storage_path = Path(config.get('memory.storage_path', './data/memory'))
        self.max_history = config.get('memory.max_history', 1000)
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / 'memory.db'
        self._init_database()
        
        logger.info("Memory manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database for memory storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    parsed_result TEXT,
                    context TEXT
                )
            ''')
            
            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    parameters TEXT,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            ''')
            
            # Create errors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    task_id INTEGER,
                    error_message TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')
            
            # Create self_modifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS self_modifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    modification_type TEXT,
                    details TEXT,
                    success INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    async def add_interaction(self, input_text: str, parsed_result: Dict[str, Any], 
                            timestamp: Optional[datetime] = None) -> int:
        """
        Add an interaction to memory.
        
        Args:
            input_text: User input text
            parsed_result: Parsed NLP result
            timestamp: Timestamp (default: now)
            
        Returns:
            Interaction ID
        """
        if not self.enabled:
            return -1
        
        try:
            ts = timestamp or datetime.now()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interactions (timestamp, input_text, parsed_result)
                VALUES (?, ?, ?)
            ''', (ts.isoformat(), input_text, json.dumps(parsed_result)))
            
            interaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.debug(f"Added interaction {interaction_id}")
            return interaction_id
        except Exception as e:
            logger.error(f"Error adding interaction: {e}")
            return -1
    
    async def add_task_result(self, task: Dict[str, Any], result: Dict[str, Any]) -> int:
        """
        Add task result to memory.
        
        Args:
            task: Task dictionary
            result: Task execution result
            
        Returns:
            Task ID
        """
        if not self.enabled:
            return -1
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            status = 'completed' if result.get('success') else 'failed'
            
            cursor.execute('''
                INSERT INTO tasks (timestamp, intent, parameters, status, result, retry_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                task.get('intent', 'unknown'),
                json.dumps(task.get('parameters', {})),
                status,
                json.dumps(result),
                task.get('retry_count', 0)
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.debug(f"Added task result {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Error adding task result: {e}")
            return -1
    
    async def add_error(self, task: Dict[str, Any], error_message: str) -> int:
        """
        Add error to memory.
        
        Args:
            task: Task that failed
            error_message: Error message
            
        Returns:
            Error ID
        """
        if not self.enabled:
            return -1
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO errors (timestamp, error_message)
                VALUES (?, ?)
            ''', (datetime.now().isoformat(), error_message))
            
            error_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.debug(f"Added error {error_id}")
            return error_id
        except Exception as e:
            logger.error(f"Error adding error: {e}")
            return -1
    
    async def add_self_modification(self, modification: Dict[str, Any]) -> int:
        """
        Add self-modification record to memory.
        
        Args:
            modification: Modification details
            
        Returns:
            Modification ID
        """
        if not self.enabled:
            return -1
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO self_modifications (timestamp, modification_type, details, success)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                modification.get('type', 'unknown'),
                json.dumps(modification),
                1 if modification.get('success') else 0
            ))
            
            mod_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.debug(f"Added self-modification {mod_id}")
            return mod_id
        except Exception as e:
            logger.error(f"Error adding self-modification: {e}")
            return -1
    
    async def get_incomplete_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of incomplete tasks for auto-continuation.
        
        Returns:
            List of incomplete tasks
        """
        if not self.enabled:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, intent, parameters, retry_count
                FROM tasks
                WHERE status = 'pending'
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append({
                    'id': row[0],
                    'intent': row[1],
                    'parameters': json.loads(row[2]) if row[2] else {},
                    'retry_count': row[3]
                })
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting incomplete tasks: {e}")
            return []
    
    async def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent interactions.
        
        Args:
            limit: Maximum number of interactions
            
        Returns:
            List of interactions
        """
        if not self.enabled:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, input_text, parsed_result
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            interactions = []
            for row in rows:
                interactions.append({
                    'timestamp': row[0],
                    'input_text': row[1],
                    'parsed_result': json.loads(row[2]) if row[2] else {}
                })
            
            return interactions
        except Exception as e:
            logger.error(f"Error getting recent interactions: {e}")
            return []
    
    async def save_state(self):
        """Save current agent state to disk."""
        if not self.enabled:
            return
        
        try:
            state_file = self.storage_path / 'agent_state.json'
            state = {
                'timestamp': datetime.now().isoformat(),
                'recent_tasks': await self.get_incomplete_tasks(),
                'recent_interactions': await self.get_recent_interactions(5)
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            logger.info("Agent state saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    async def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Load previously saved agent state.
        
        Returns:
            State dictionary or None
        """
        if not self.enabled:
            return None
        
        try:
            state_file = self.storage_path / 'agent_state.json'
            
            if not state_file.exists():
                return None
            
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            logger.info("Agent state loaded")
            return state
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None
