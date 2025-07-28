# ============== 对话接入 ================
import requests
import json
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from database.database import ChatDatabase

class ChatCore:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        # 初始化数据库管理器
        self.db_manager = ChatDatabase()
        # 当前模型
        self.current_model = "gpt-3.5-turbo"
        # 当前对话ID
        self.current_conversation_id = None
        
        # 初始化 langchain 的聊天模型
        self.llm = ChatOpenAI(
            model="deepseek-ai/DeepSeek-V3",
            openai_api_key=api_key,
            openai_api_base=api_url.replace("/chat/completions", ""),  # 调整 base URL
            temperature=0.7
        )
        # 初始化记忆组件
        self.memory = ConversationBufferMemory()
        # 创建对话链
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )

    def chat(self, question, model="gpt-3.5-turbo"):
        # 如果没有当前对话ID，则创建新对话
        if self.current_conversation_id is None:
            # 获取授权码作为用户标识
            auth_code = os.environ.get('AUTH_CODE', 'default_user')
            # 创建新对话，仅使用当前时间作为标题
            from datetime import datetime
            new_conversation_title = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.current_conversation_id = self.db_manager.create_conversation(auth_code, new_conversation_title)
        
        # 使用当前对话的历史记录初始化内存历史记录
        self.load_chat_history()
        
        # 获取当前模型
        current_model = self.get_model(model)
        
        # 创建对话链
        conversation = ConversationChain(
            llm=current_model,
            memory=self.memory,
            verbose=False
        )
        
        # 获取回答
        response = conversation.predict(input=question)
        
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 保存问题和回答到当前对话
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, question, is_user=True)
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, response, is_user=False)
        
        return response
    
    def update_model(self, model_name):
        """更新模型配置"""
        self.llm.model_name = model_name
    
    def get_model(self, model_name):
        """获取指定的模型"""
        # 这里可以根据需要返回不同的模型实例
        # 目前我们只使用一个模型，所以直接返回当前模型
        return self.llm
    
    def load_chat_history(self):
        """从数据库加载当前对话的历史记录到内存中"""
        # 清空当前内存历史记录
        self.memory.clear()
        
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 如果没有当前对话ID，则获取用户的第一个对话
        if self.current_conversation_id is None:
            conversations = self.db_manager.get_user_conversations(auth_code)
            if conversations:
                self.current_conversation_id = conversations[0]['id']
            else:
                # 如果用户没有任何对话，创建一个新对话
                # 使用默认标题，因为这里没有用户问题
                from datetime import datetime
                default_title = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.current_conversation_id = self.db_manager.create_conversation(auth_code, default_title)
        
        # 从数据库获取当前对话的历史记录
        history = self.db_manager.get_conversation_history(auth_code, self.current_conversation_id)
        
        # 将历史记录加载到内存中
        for entry in history:
            if entry['is_user']:
                self.memory.chat_memory.add_user_message(entry['message'])
            else:
                self.memory.chat_memory.add_ai_message(entry['message'])
