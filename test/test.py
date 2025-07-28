import requests

url = "https://api.siliconflow.cn/v1/chat/completions"


payload = {
    "model": "deepseek-ai/DeepSeek-V3",
    "messages": [
        {
            "role": "user",
            "content": "What opportunities and challenges will the Chinese large model industry face in 2025?"
        }
    ],
    "stream": True
}
headers = {
    "Authorization": "Bearer sk-wopmheqzfejiqbtefflzawoalyqaqiaoqbsmmfpspiekyrcx",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, stream=True)

# 流式输出响应
for chunk in response.iter_lines():
    if chunk:
        decoded_chunk = chunk.decode('utf-8')
        if decoded_chunk.startswith('data: '):
            data = decoded_chunk[6:]
            if data != '[DONE]':
                import json
                try:
                    json_data = json.loads(data)
                    if 'choices' in json_data and len(json_data['choices']) > 0:
                        delta = json_data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            print(content, end='', flush=True)
                except json.JSONDecodeError:
                    pass