from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QComboBox, QSplitter
)
from chat_interface import ChatCore
from chat_widget import ChatWidget
from dotenv import load_dotenv
import os
import sys

# 加载.env
load_dotenv()

# ===============对话主窗口====================
class NLPDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NLP 工作台")
        self.resize(1100, 700)

        # 左侧侧边栏
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # API切换
        api_label = QLabel("API 切换")
        self.api_combo = QComboBox()
        self.api_combo.addItems(["deepseek-ai/DeepSeek-V3", "Qwen/QwQ-32B"])
        
        sidebar_layout.addWidget(api_label)
        sidebar_layout.addWidget(self.api_combo)

        # 用户状态
        user_label = QLabel("用户：已登录")
        sidebar_layout.addWidget(user_label)

        # 对话列表
        dialog_label = QLabel("对话列表")
        dialog_list = QListWidget()
        dialog_list.addItems(["对话1", "对话2"])
        sidebar_layout.addWidget(dialog_label)
        sidebar_layout.addWidget(dialog_list)
        sidebar_layout.addStretch()

        # 右侧主内容区
        self.tabs = QTabWidget()
        api_key = os.getenv("API_KEY")
        api_url = os.getenv("API_URL")
        chat_core = ChatCore(api_key=api_key, api_url=api_url)
        get_model_func = lambda: self.api_combo.currentText()
        self.rag_tab = ChatWidget(chat_core, get_model_func)
        self.model_tab = QWidget()
        self.api_tab = QWidget()
        self.tabs.addTab(self.rag_tab, "RAG 问答")
        self.tabs.addTab(self.model_tab, "模型推理")
        self.tabs.addTab(self.api_tab, "API 控制台")

        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # 可拖动分割
        splitter = QSplitter()
        splitter.addWidget(sidebar)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 880])

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NLPDesktopApp()
    window.show()
    sys.exit(app.exec_())