#!/usr/bin/env python3

import os
import sys
import time
import dotenv

# 加载环境变量
dotenv.load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_interface import ChatCore

# 设置环境变量
os.environ['AUTH_CODE'] = 'test_user'

# 创建ChatCore实例
# 注意：这里需要提供有效的API密钥和URL
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")


chat_core = ChatCore(api_key, api_url)

# 测试流式输出
print("开始测试流式输出...")
question = "你好，你能告诉我一些关于人工智能的知识吗？"

print(f"问题: {question}")
print("回答: ", end="", flush=True)

try:
    for chunk in chat_core.stream_chat(question):
        print(chunk, end="", flush=True)
        time.sleep(0.05)  # 模拟网络延迟
    
    print("\n\n流式输出测试完成。")
except Exception as e:
    print(f"\n\n测试过程中出现错误: {e}")
    import traceback
    traceback.print_exc()