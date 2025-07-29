import os

# 数据库路径配置
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'chat_history.db')

# 日志目录配置
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')

# API模型列表
API_MODELS = [
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
    "deepseek-ai/deepseek-vl2",
    "Qwen/QwQ-32B",
    "Qwen/Qwen2.5-VL-32B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen3-235B-A22B-Instruct-2507",
    "Tongyi-Zhiwen/QwenLong-L1-32B",
    "tencent/Hunyuan-A13B-Instruct",
    "Tongyi-Zhiwen/QwenLong-L1-32B",
    "THUDM/glm-4-9b-chat",
    "THUDM/GLM-4.1V-9B-Thinking",
    "THUDM/GLM-Z1-32B-0414",
    "baidu/ERNIE-4.5-300B-A47B",
]

# 默认模型
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3"

# 主题列表
THEMES = [
    "浅色主题",
    "深色主题",
    "浅粉色少女心主题",
    "科技风格主题"
]

# 主题到QSS文件的映射
THEME_NAME_TO_QSS = {
    "浅色主题": "./style/iphone_style.qss",
    "深色主题": "./style/dark_style.qss",
    "浅粉色少女心主题": "./style/pink_style.qss",
    "科技风格主题": "./style/technology_style.qss"
}

# 默认QSS文件
DEFAULT_QSS = "./style/iphone_style.qss"

# 授权码文件路径
AUTH_MARKER_FILE_PATH = "./authorized/auth_marker.txt"