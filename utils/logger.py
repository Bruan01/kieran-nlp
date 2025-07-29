"""
1. 在main.py文件中：
   - 当SettingsDialog类的get_user_info方法无法获取用户信息时，会调用logger.log_error记录错误日志。
   - 当SettingsDialog类的get_user_info方法在获取用户信息时发生异常，会调用logger.log_exception记录异常日志。

2. 在chat_widget.py文件中：
   - 当StreamChatWorker类在流式生成对话时发生异常，会调用logger.log_exception记录异常日志。

3. 在database/database.py文件中：
   - 当ChatDatabase类在初始化数据库时发生异常，会调用logger.log_exception记录异常日志。
   - 当ChatDatabase类在保存消息时发生异常，会调用logger.log_exception记录异常日志。
   - 当ChatDatabase类在获取聊天历史时发生异常，会调用logger.log_exception记录异常日志。
   - 当ChatDatabase类在创建对话时发生异常，会调用logger.log_exception记录异常日志。
   
所有日志记录都使用utils/logger.py中定义的Logger类，该类会将日志写入log目录下的error.log文件中。
"""

import os
import logging
import sys

# 获取当前文件的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 将项目根目录添加到sys.path
ROOT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(ROOT_DIR)

from config.settings import LOG_DIR
from datetime import datetime

class Logger:
    def __init__(self, log_dir=None, log_file="error.log"):
        """初始化日志记录器"""
        self.log_dir = log_dir or LOG_DIR
        self.log_file = log_file
        self.log_path = os.path.join(self.log_dir, self.log_file)
        
        # 创建日志目录（如果不存在）
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 配置日志记录器
        self.logger = logging.getLogger("NLPDesktopApp")
        self.logger.setLevel(logging.ERROR)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler(self.log_path, encoding='utf-8')
            file_handler.setLevel(logging.ERROR)
            
            # 创建格式器并添加到处理器
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # 添加处理器到日志记录器
            self.logger.addHandler(file_handler)
    
    def log_error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def log_exception(self, message):
        """记录异常日志"""
        self.logger.exception(message)