import requests

url = "https://api.siliconflow.cn/v1/chat/completions"


payload = {
    "model": "deepseek-ai/DeepSeek-V3",
    "messages": [
        {
            "role": "user",
            "content": "What opportunities and challenges will the Chinese large model industry face in 2025?"
        }
    ]
}
headers = {
    "Authorization": "Bearer sk-wopmheqzfejiqbtefflzawoalyqaqiaoqbsmmfpspiekyrcx",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)