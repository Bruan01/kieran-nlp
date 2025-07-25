# ============== 对话接入 ================
import requests
import json

class ChatCore:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def chat(self, question):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": question}],
            "stream": True
        }
        try:
            with requests.post(self.api_url, json=payload, headers=headers, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                result = ""
                for line in resp.iter_lines():
                    if line:
                        try:
                            text = line.decode("utf-8").strip()
                            if text.startswith("data:"):
                                text = text[5:].strip()
                            if not text:
                                continue
                            data = json.loads(text)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            result += content
                        except Exception as e:
                            print(f"解析出错: {e}")
                return result
        except Exception as e:
            return f"⚙️ 接口调用失败：{e}"
