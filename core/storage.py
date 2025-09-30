"""
数据存储模块
使用SQLite存储剪贴板历史记录
"""
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path


class StorageManager:
    """数据存储管理器"""
    
    def __init__(self, db_file='textpin.db'):
        self.db_file = db_file
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # 创建剪贴板历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_favorite INTEGER DEFAULT 0,
                char_count INTEGER,
                word_count INTEGER
            )
        ''')
        
        # 创建配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON clipboard_history(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_favorite 
            ON clipboard_history(is_favorite, timestamp DESC)
        ''')
        
        self.conn.commit()
    
    def _get_content_hash(self, content):
        """获取内容的哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _count_words(self, content):
        """统计单词数"""
        return len(content.split())
    
    def add_history(self, content):
        """添加历史记录"""
        if not content or not content.strip():
            return None
        
        content_hash = self._get_content_hash(content)
        char_count = len(content)
        word_count = self._count_words(content)
        
        cursor = self.conn.cursor()
        
        # 检查是否已存在
        cursor.execute(
            'SELECT id FROM clipboard_history WHERE content_hash = ?',
            (content_hash,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # 更新时间戳
            cursor.execute(
                'UPDATE clipboard_history SET timestamp = ? WHERE id = ?',
                (datetime.now(), existing['id'])
            )
            self.conn.commit()
            return existing['id']
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO clipboard_history 
                (content, content_hash, char_count, word_count) 
                VALUES (?, ?, ?, ?)
            ''', (content, content_hash, char_count, word_count))
            self.conn.commit()
            return cursor.lastrowid
    
    def get_history(self, limit=50, favorites_only=False):
        """获取历史记录列表"""
        cursor = self.conn.cursor()
        
        if favorites_only:
            query = '''
                SELECT * FROM clipboard_history 
                WHERE is_favorite = 1 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
        else:
            query = '''
                SELECT * FROM clipboard_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
        
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    def get_history_by_id(self, history_id):
        """根据ID获取历史记录"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM clipboard_history WHERE id = ?',
            (history_id,)
        )
        return cursor.fetchone()
    
    def search_history(self, keyword, limit=50):
        """搜索历史记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM clipboard_history 
            WHERE content LIKE ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (f'%{keyword}%', limit))
        return cursor.fetchall()
    
    def toggle_favorite(self, history_id):
        """切换收藏状态"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE clipboard_history SET is_favorite = 1 - is_favorite WHERE id = ?',
            (history_id,)
        )
        self.conn.commit()
    
    def delete_history(self, history_id):
        """删除历史记录"""
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM clipboard_history WHERE id = ?',
            (history_id,)
        )
        self.conn.commit()
    
    def clear_history(self, keep_favorites=True):
        """清空历史记录"""
        cursor = self.conn.cursor()
        if keep_favorites:
            cursor.execute('DELETE FROM clipboard_history WHERE is_favorite = 0')
        else:
            cursor.execute('DELETE FROM clipboard_history')
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        """获取设置"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def set_setting(self, key, value):
        """设置配置"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO app_settings (key, value) 
            VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
