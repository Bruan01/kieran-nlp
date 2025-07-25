from PyQt5.QtWidgets import QWidget
from chat_interface import ChatCore
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from chat_interface import ChatCore
from chat_widget import ChatWidget

# ===============对话主窗口====================
class NLPDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NLP 工作台")
        self.resize(900, 600)

        self.tabs = QTabWidget()
        # 配置你的API KEY和URL

        chat_core = ChatCore(api_key="sk-wopmheqzfejiqbtefflzawoalyqaqiaoqbsmmfpspiekyrcx", 
                             api_url="https://api.siliconflow.cn/v1/chat/completions")
        
        self.rag_tab = ChatWidget(chat_core)
        self.model_tab = QWidget()
        self.api_tab = QWidget()

        self.tabs.addTab(self.rag_tab, "RAG 问答")
        self.tabs.addTab(self.model_tab, "模型推理")
        self.tabs.addTab(self.api_tab, "API 控制台")

        self.setCentralWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NLPDesktopApp()
    window.show()
    sys.exit(app.exec_())