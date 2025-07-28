import requests
import os
from dotenv import load_dotenv
import sys 

load_dotenv()
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 创建ChatCore实例
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")
print(api_key)

url = "https://api.siliconflow.cn/v1/user/info"

headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)

print(response.json())