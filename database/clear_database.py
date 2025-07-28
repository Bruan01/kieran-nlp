import sqlite3
import os

def clear_database(db_path="chat_history.db"):
    """清空数据库中的所有内容"""
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 删除所有聊天历史记录
    cursor.execute("DELETE FROM chat_history")
    print("已清空聊天历史记录")
    
    # 删除所有对话
    cursor.execute("DELETE FROM conversations")
    print("已清空对话记录")
    
    # 删除所有用户
    cursor.execute("DELETE FROM users")
    print("已清空用户记录")
    
    conn.commit()
    conn.close()
    
    print("数据库已清空")

if __name__ == "__main__":
    clear_database()