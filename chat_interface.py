# ============== 对话接入 ================
import requests
import json
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from database.database import ChatDatabase
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List
from langchain_core.outputs import LLMResult
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory


class StreamCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器，用于流式输出"""
    def __init__(self, on_new_token_callback=None):
        self.on_new_token_callback = on_new_token_callback
        self.full_response = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """当模型生成新token时调用"""
        self.full_response += token
        if self.on_new_token_callback:
            self.on_new_token_callback(token)

class ChatCore:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        # 初始化数据库管理器

        self.db_manager = ChatDatabase(os.path.join(os.path.dirname(__file__), 'database', 'chat_history.db'))
        # 当前模型
        self.current_model = "deepseek-ai/DeepSeek-V3"
        # 当前对话ID
        self.current_conversation_id = None
        
        # 确保API URL包含协议
        if not api_url.startswith(('http://', 'https://')):
            self.api_url = 'http://' + api_url
        else:
            self.api_url = api_url
        
        # 初始化 langchain 的聊天模型
        self.llm = ChatOpenAI(
            model=self.current_model,
            openai_api_key=api_key,
            openai_api_base=self.api_url.replace("/chat/completions", ""),  # 调整 base URL
            temperature=0.7
        )
        
        # 创建提示模板
        self.prompt = PromptTemplate.from_template("""
        你是一个AI助手，你需要根据用户的提问提供帮助，需要最真实的回答，不允许欺骗用户
        
        历史对话:
        {history}
        
        用户提问: {input}
        AI回答:""")
        
        # 创建对话链
        self.conversation_chain = RunnableWithMessageHistory(
            self.prompt | self.llm,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取会话历史"""
        # 创建一个新的ChatMessageHistory实例
        chat_history = ChatMessageHistory()
        
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 从数据库获取当前对话的历史记录
        history = self.db_manager.get_conversation_history(auth_code, int(session_id))
        
        # 将历史记录加载到ChatMessageHistory中
        for entry in history:
            if entry['is_user']:
                chat_history.add_user_message(entry['message'])
            else:
                chat_history.add_ai_message(entry['message'])
        
        return chat_history

    def chat(self, question, model="gpt-3.5-turbo"):
        # 如果没有当前对话ID，则创建新对话
        if self.current_conversation_id is None:
            # 获取授权码作为用户标识
            auth_code = os.environ.get('AUTH_CODE', 'default_user')
            # 创建新对话，仅使用当前时间作为标题
            from datetime import datetime
            new_conversation_title = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.current_conversation_id = self.db_manager.create_conversation(auth_code, new_conversation_title)
        
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 保存问题到当前对话
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, question, is_user=True)
        
        # 获取回答
        config = {"configurable": {"session_id": str(self.current_conversation_id)}}
        response = self.conversation_chain.invoke({"input": question}, config=config)
        
        # 保存回答到当前对话
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, response.content, is_user=False)
        
        return response.content
    
    def stream_chat(self, question, model="gpt-3.5-turbo"):
        """流式聊天方法"""
        # 如果没有当前对话ID，则创建新对话
        if self.current_conversation_id is None:
            # 获取授权码作为用户标识
            auth_code = os.environ.get('AUTH_CODE', 'default_user')
            # 创建新对话，仅使用当前时间作为标题
            from datetime import datetime
            new_conversation_title = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.current_conversation_id = self.db_manager.create_conversation(auth_code, new_conversation_title)
        
        print("当前对话ID:", self.current_conversation_id)
        print("从stream_chat调用get_session_history")
        
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 保存问题到当前对话
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, question, is_user=True)
        
        # 创建回调处理器
        tokens = []
        def on_new_token(token):
            tokens.append(token)
        
        callback_handler = StreamCallbackHandler(on_new_token_callback=on_new_token)
        
        # 创建带流式输出的模型
        # 确保API URL包含协议
        api_url = self.api_url
        if not api_url.startswith(('http://', 'https://')):
            api_url = 'http://' + api_url
        
        streaming_llm = ChatOpenAI(
            model=self.current_model,
            openai_api_key=self.api_key,
            openai_api_base=api_url.replace("/chat/completions", ""),
            temperature=0.7,
            streaming=True,
            callbacks=[callback_handler]
        )
        
        # 创建对话链
        streaming_conversation_chain = RunnableWithMessageHistory(
            self.prompt | streaming_llm,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
        # 流式获取回答
        config = {"configurable": {"session_id": str(self.current_conversation_id)}}
        # 使用stream方法而不是invoke方法来实现真正的流式输出
        response = streaming_conversation_chain.stream({"input": question}, config=config)
        
        full_response = ""
        # 逐个处理流式返回的token
        for chunk in response:
            full_response += chunk.content
            yield chunk.content
        
        # 保存完整回答到当前对话
        self.db_manager.save_message_to_conversation(auth_code, self.current_conversation_id, full_response, is_user=False)
    
    def update_model(self, model_name):
        """更新模型配置"""
        self.current_model = model_name
        # 重新创建LLM实例以应用新模型
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.api_url.replace("/chat/completions", ""),
            temperature=0.7
        )
        
        # 重新创建对话链
        self.conversation_chain = RunnableWithMessageHistory(
            self.prompt | self.llm,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
    
    
    def get_model(self, model_name):
        """获取指定的模型"""
        # 这里可以根据需要返回不同的模型实例
        # 目前我们只使用一个模型，所以直接返回当前模型
        return self.llm
