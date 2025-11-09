"""
Database Integration Plugin for Cosik AI Agent.

Features:
- SQLite database operations
- PostgreSQL support (optional)
- Query execution and data retrieval
- Database schema management
- Transaction support
- Connection pooling
- Query builder helpers
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from loguru import logger
import asyncio

try:
    import psycopg2
    import psycopg2.pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("psycopg2 not available - PostgreSQL support disabled")


class DatabasePlugin:
    """
    Database operations plugin supporting SQLite and PostgreSQL.
    
    Provides:
    - Connection management
    - Query execution
    - Schema management
    - Transaction handling
    - Data migration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database plugin.
        
        Args:
            config: Plugin configuration
        """
        self.config = config
        self.db_config = config.get('plugins', {}).get('database', {})
        self.connections = {}
        self.postgres_pools = {}
        
        logger.info("Database plugin initialized")
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute database operation.
        
        Args:
            command: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Operation result
        """
        action = kwargs.pop('action', 'query')
        
        try:
            if action == 'connect':
                return await self._connect(**kwargs)
            elif action == 'disconnect':
                return await self._disconnect(**kwargs)
            elif action == 'query':
                return await self._query(**kwargs)
            elif action == 'execute':
                return await self._execute(**kwargs)
            elif action == 'create_table':
                return await self._create_table(**kwargs)
            elif action == 'insert':
                return await self._insert(**kwargs)
            elif action == 'update':
                return await self._update(**kwargs)
            elif action == 'delete':
                return await self._delete(**kwargs)
            elif action == 'backup':
                return await self._backup(**kwargs)
            elif action == 'list_tables':
                return await self._list_tables(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _connect(self, db_type: str = 'sqlite', **kwargs) -> Dict[str, Any]:
        """Connect to database."""
        db_name = kwargs.get('database', 'default')
        
        try:
            if db_type == 'sqlite':
                db_path = kwargs.get('path', './data/databases/default.db')
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                self.connections[db_name] = {
                    'type': 'sqlite',
                    'connection': conn,
                    'path': db_path
                }
                
                logger.info(f"Connected to SQLite database: {db_path}")
                return {
                    'success': True,
                    'database': db_name,
                    'type': 'sqlite',
                    'path': db_path
                }
            
            elif db_type == 'postgres' and POSTGRES_AVAILABLE:
                host = kwargs.get('host', 'localhost')
                port = kwargs.get('port', 5432)
                user = kwargs.get('user', 'postgres')
                password = kwargs.get('password', '')
                database = kwargs.get('dbname', 'postgres')
                
                pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database
                )
                
                self.postgres_pools[db_name] = pool
                
                logger.info(f"Connected to PostgreSQL: {host}:{port}/{database}")
                return {
                    'success': True,
                    'database': db_name,
                    'type': 'postgres',
                    'host': host,
                    'port': port
                }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported database type: {db_type}'
                }
        
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _disconnect(self, database: str = 'default') -> Dict[str, Any]:
        """Disconnect from database."""
        try:
            if database in self.connections:
                conn_info = self.connections[database]
                if conn_info['type'] == 'sqlite':
                    conn_info['connection'].close()
                del self.connections[database]
                
                logger.info(f"Disconnected from database: {database}")
            
            if database in self.postgres_pools:
                self.postgres_pools[database].closeall()
                del self.postgres_pools[database]
            
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _query(self, sql: str, database: str = 'default', params: tuple = None) -> Dict[str, Any]:
        """Execute SELECT query."""
        try:
            # Auto-connect if not connected
            if database not in self.connections and database not in self.postgres_pools:
                await self._connect(database=database)
            
            if database in self.connections:
                # SQLite
                conn = self.connections[database]['connection']
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                rows = cursor.fetchall()
                
                # Convert to list of dicts
                result = []
                for row in rows:
                    result.append(dict(row))
                
                return {
                    'success': True,
                    'rows': result,
                    'row_count': len(result)
                }
            
            elif database in self.postgres_pools:
                # PostgreSQL
                pool = self.postgres_pools[database]
                conn = pool.getconn()
                
                try:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    result = []
                    for row in rows:
                        result.append(dict(zip(columns, row)))
                    
                    return {
                        'success': True,
                        'rows': result,
                        'row_count': len(result)
                    }
                finally:
                    pool.putconn(conn)
            
            else:
                return {
                    'success': False,
                    'error': f'No connection for database: {database}'
                }
        
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute(self, sql: str, database: str = 'default', params: tuple = None) -> Dict[str, Any]:
        """Execute INSERT/UPDATE/DELETE query."""
        try:
            if database not in self.connections and database not in self.postgres_pools:
                await self._connect(database=database)
            
            if database in self.connections:
                # SQLite
                conn = self.connections[database]['connection']
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                conn.commit()
                
                return {
                    'success': True,
                    'affected_rows': cursor.rowcount,
                    'last_id': cursor.lastrowid
                }
            
            elif database in self.postgres_pools:
                # PostgreSQL
                pool = self.postgres_pools[database]
                conn = pool.getconn()
                
                try:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount
                    }
                finally:
                    pool.putconn(conn)
            
            else:
                return {
                    'success': False,
                    'error': f'No connection for database: {database}'
                }
        
        except Exception as e:
            logger.error(f"Execute failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_table(self, table_name: str, schema: Dict[str, str], 
                           database: str = 'default') -> Dict[str, Any]:
        """Create table with schema."""
        try:
            # Build CREATE TABLE statement
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            
            result = await self._execute(sql, database=database)
            
            if result['success']:
                logger.info(f"Table created: {table_name}")
            
            return result
        
        except Exception as e:
            logger.error(f"Create table failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _insert(self, table: str, data: Dict[str, Any], 
                     database: str = 'default') -> Dict[str, Any]:
        """Insert data into table."""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' if database in self.connections else '%s'] * len(data))
            values = tuple(data.values())
            
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            return await self._execute(sql, database=database, params=values)
        
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update(self, table: str, data: Dict[str, Any], where: str,
                     database: str = 'default', params: tuple = None) -> Dict[str, Any]:
        """Update table data."""
        try:
            placeholder = '?' if database in self.connections else '%s'
            set_clause = ', '.join([f"{k} = {placeholder}" for k in data.keys()])
            values = tuple(data.values())
            
            if params:
                values = values + params
            
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            
            return await self._execute(sql, database=database, params=values)
        
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _delete(self, table: str, where: str, database: str = 'default',
                     params: tuple = None) -> Dict[str, Any]:
        """Delete from table."""
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            return await self._execute(sql, database=database, params=params)
        
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _backup(self, database: str = 'default', 
                     backup_path: Optional[str] = None) -> Dict[str, Any]:
        """Backup database."""
        try:
            if database not in self.connections:
                return {
                    'success': False,
                    'error': 'Only SQLite databases can be backed up'
                }
            
            conn_info = self.connections[database]
            if conn_info['type'] != 'sqlite':
                return {
                    'success': False,
                    'error': 'Only SQLite databases can be backed up'
                }
            
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"./data/backups/db_{database}_{timestamp}.db"
            
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup
            source_conn = conn_info['connection']
            backup_conn = sqlite3.connect(backup_path)
            
            with backup_conn:
                source_conn.backup(backup_conn)
            
            backup_conn.close()
            
            logger.info(f"Database backed up to: {backup_path}")
            return {
                'success': True,
                'backup_path': backup_path
            }
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _list_tables(self, database: str = 'default') -> Dict[str, Any]:
        """List all tables in database."""
        try:
            if database in self.connections:
                # SQLite
                sql = "SELECT name FROM sqlite_master WHERE type='table'"
            elif database in self.postgres_pools:
                # PostgreSQL
                sql = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            else:
                return {
                    'success': False,
                    'error': f'No connection for database: {database}'
                }
            
            result = await self._query(sql, database=database)
            
            if result['success']:
                if database in self.connections:
                    tables = [row['name'] for row in result['rows']]
                else:
                    tables = [row['tablename'] for row in result['rows']]
                
                return {
                    'success': True,
                    'tables': tables,
                    'count': len(tables)
                }
            
            return result
        
        except Exception as e:
            logger.error(f"List tables failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities."""
        return {
            'name': 'database',
            'version': '1.0.0',
            'description': 'Database operations (SQLite, PostgreSQL)',
            'actions': [
                'connect', 'disconnect', 'query', 'execute',
                'create_table', 'insert', 'update', 'delete',
                'backup', 'list_tables'
            ],
            'supported_databases': ['sqlite', 'postgres'] if POSTGRES_AVAILABLE else ['sqlite']
        }


# Plugin metadata
PLUGIN_INFO = {
    'name': 'database',
    'version': '1.0.0',
    'class': DatabasePlugin,
    'description': 'Database integration (SQLite, PostgreSQL)',
    'author': 'Finder995',
    'requires': ['sqlite3'],
    'optional': ['psycopg2']
}
