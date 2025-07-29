import sqlite3
import os
import sys

# 获取当前文件的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 将项目根目录添加到sys.path
ROOT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(ROOT_DIR)

from config.settings import DATABASE_PATH
from utils.logger import Logger

class ChatDatabase:
    def __init__(self, db_path=None):
        """初始化数据库连接"""
        self.db_path = db_path or DATABASE_PATH
        self.logger = Logger()  # 初始化日志记录器
        self.init_db()
    
    def init_db(self):
        """创建数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auth_code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建对话列表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建对话历史表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                conversation_id INTEGER,
                message TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # 检查并添加 conversation_id 列到 chat_history 表
        try:
            cursor.execute("ALTER TABLE chat_history ADD COLUMN conversation_id INTEGER REFERENCES conversations (id)")
        except sqlite3.OperationalError as e:
            # 列已存在，忽略错误
            if "duplicate column name" not in str(e):
                error_msg = f"初始化数据库时出错: {str(e)}"
                self.logger.log_exception(error_msg)
                raise
        
        conn.commit()
        conn.close()
    
    def update_conversation_title(self, auth_code, conversation_id, new_title):
        """更新对话标题"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE conversations 
            SET title = ? 
            WHERE id = ? AND user_id = ?
        """, (new_title, conversation_id, user_id))
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, auth_code):
        """获取或创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 尝试获取现有用户
        cursor.execute("SELECT id FROM users WHERE auth_code = ?", (auth_code,))
        user = cursor.fetchone()
        
        if user is None:
            # 创建新用户
            cursor.execute("INSERT INTO users (auth_code) VALUES (?)", (auth_code,))
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user[0]
        
        conn.close()
        return user_id
    
    def save_message(self, auth_code, message, is_user):
        """保存对话消息"""
        try:
            user_id = self.get_or_create_user(auth_code)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO chat_history (user_id, message, is_user) 
                VALUES (?, ?, ?)
            """, (user_id, message, is_user))
            
            conn.commit()
            conn.close()
        except Exception as e:
            error_msg = f"保存消息时出错: {str(e)}"
            self.logger.log_exception(error_msg)
            raise
    
    def get_chat_history(self, auth_code, limit=50):
        """获取用户的对话历史"""
        try:
            user_id = self.get_or_create_user(auth_code)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message, is_user, timestamp 
                FROM chat_history 
                WHERE user_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            """, (user_id, limit))
            
            history = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            return [dict(row) for row in history]
        except Exception as e:
            error_msg = f"获取聊天历史时出错: {str(e)}"
            self.logger.log_exception(error_msg)
            raise
    
    def clear_user_history(self, auth_code):
        """清除用户的对话历史"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, auth_code, title):
        """为用户创建新对话"""
        try:
            user_id = self.get_or_create_user(auth_code)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations (user_id, title) 
                VALUES (?, ?)
            """, (user_id, title))
            
            conn.commit()
            conversation_id = cursor.lastrowid
            conn.close()
            
            return conversation_id
        except Exception as e:
            error_msg = f"创建对话时出错: {str(e)}"
            self.logger.log_exception(error_msg)
            raise
    
    def get_user_conversations(self, auth_code):
        """获取用户的所有对话"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at
            FROM conversations 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in conversations]
    
    def get_conversation_history(self, auth_code, conversation_id, limit=50, offset=0):
        """获取特定对话的历史记录（支持分页）"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message, is_user, timestamp 
            FROM chat_history 
            WHERE user_id = ? AND conversation_id = ?
            ORDER BY timestamp ASC 
            LIMIT ? OFFSET ?
        """ , (user_id, conversation_id, limit, offset))
        
        history = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in history]
    
    def delete_conversation(self, auth_code, conversation_id):
        """删除对话及其相关历史记录"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 删除对话相关的历史记录
        cursor.execute("DELETE FROM chat_history WHERE user_id = ? AND conversation_id = ?", (user_id, conversation_id))
        
        # 删除对话
        cursor.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id))
        
        conn.commit()
        conn.close()
    
    def save_message_to_conversation(self, auth_code, conversation_id, message, is_user):
        """保存对话消息到特定对话"""
        user_id = self.get_or_create_user(auth_code)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (user_id, conversation_id, message, is_user) 
            VALUES (?, ?, ?, ?)
        """, (user_id, conversation_id, message, is_user))
        
        conn.commit()
        conn.close()