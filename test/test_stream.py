import os
import sys
from dotenv import load_dotenv

# 添加上级目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_interface import ChatCore

# 加载环境变量
load_dotenv()

# 设置授权码
os.environ['AUTH_CODE'] = 'test_user'

# 创建ChatCore实例
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
chat_core = ChatCore(api_key=api_key, api_url=api_url)

# 测试流式聊天功能
print("Testing stream chat functionality...")
question = "简单介绍一下人工智能的发展历程"

print(f"Question: {question}")
print("Answer: ", end='', flush=True)

# 使用流式聊天方法
for chunk in chat_core.stream_chat(question):
    print(chunk, end='', flush=True)

print("\n\nStream chat test completed.")