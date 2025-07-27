# ============== 对话接入 ================
import requests
import json
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

class ChatCore:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
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

    def chat(self, question, model="deepseek-ai/DeepSeek-V3"):
        try:
            # 更新模型名称
            self.llm.model_name = model
            # 使用 langchain 的对话链进行聊天
            response = self.conversation.predict(input=question)
            return response
        except Exception as e:
            return f"⚙️ 接口调用失败：{e}"
    
    def update_model(self, model_name):
        """更新模型配置"""
        self.llm.model_name = model_name
