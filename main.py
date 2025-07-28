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
        self.setWindowTitle("Kieran-NLP")
        self.resize(1280, 720)

        # 左侧侧边栏
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # API切换
        api_label = QLabel("API 切换")
        self.api_combo = QComboBox()
        self.api_combo.addItems(["deepseek-ai/DeepSeek-V3",
        "Qwen/QwQ-32B",
        "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "tencent/Hunyuan-A13B-Instruct",
        "Tongyi-Zhiwen/QwenLong-L1-32B"])
        
        # 添加模型切换提示标签
        self.model_tip_label = QLabel("")
        self.model_tip_label.setStyleSheet("color: green; font-weight: bold;")
        
        sidebar_layout.addWidget(api_label)
        sidebar_layout.addWidget(self.api_combo)
        sidebar_layout.addWidget(self.model_tip_label)
        
        # 连接信号槽，实现在切换模型时提醒用户
        self.api_combo.currentTextChanged.connect(self.on_model_changed)

        # 主题切换
        theme_label = QLabel("主题切换")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "浅粉色少女心主题", "科技风格主题"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        # 从文件获取当前授权码
        with open(AUTH_MARKER_FILE_PATH, 'r') as f:
            content = f.read()
            if "Authorized = 「" in content:
                authorized_code = content.split("「")[1].split("」")[0]
                # 用户状态
                user_label = QLabel(f"用户：已登录 授权码: {authorized_code}")
                sidebar_layout.addWidget(theme_label)
                sidebar_layout.addWidget(self.theme_combo)
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
        self.model_tab = ChatWidget(chat_core, get_model_func)
        self.rag_tab = QWidget()
        self.api_tab = QWidget()
        self.tabs.addTab(self.model_tab, "模型推理")
        self.tabs.addTab(self.rag_tab, "RAG 问答")
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
        
        # 初始化时显示当前模型
        self.on_model_changed(self.api_combo.currentText())
        
        # 初始化默认主题
        self.on_theme_changed(self.theme_combo.currentText())

    def on_model_changed(self, model_name):
        """当模型切换时更新提示信息和ChatCore配置"""
        self.model_tip_label.setText(f"当前模型: {model_name}")
        # 更新ChatCore中的模型配置
        self.model_tab.chat_core.update_model(model_name)
        
    def on_theme_changed(self, theme_name):
        """当主题切换时更新界面样式"""
        # 定义浅色主题样式
        light_theme = """
        QWidget {
            background-color: #f0f0f0;
            color: #333;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
            border-radius: 10px;
        }
        QTabBar::tab {
            background: #e0e0e0;
            padding: 8px 16px;
            border-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
        }
        QComboBox {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 4px;
        }
        QListWidget {
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        """
        
        # 定义深色主题样式
        dark_theme = """
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            border-radius: 10px;
        }
        QTabBar::tab {
            background: #3d3d3d;
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #4d4d4d;
        }
        QLabel {
            color: #ffffff;
        }
        QComboBox {
            border: 1px solid #555;
            border-radius: 8px;
            padding: 4px;
            background: #3d3d3d;
            color: #ffffff;
        }
        QListWidget {
            border: 1px solid #555;
            border-radius: 8px;
        }
        """
        
        # 定义浅粉色少女心主题样式
        pink_theme = """
        QWidget {
            background-color: #fff0f5;
            color: #333;
        }
        QTabWidget::pane {
            border: 1px solid #ffc0cb;
            border-radius: 10px;
        }
        QTabBar::tab {
            background: #ffc0cb;
            color: #333;
            padding: 8px 16px;
            border-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
        }
        QComboBox {
            border: 1px solid #ffc0cb;
            border-radius: 8px;
            padding: 4px;
        }
        QListWidget {
            border: 1px solid #ffc0cb;
            border-radius: 8px;
        }
        """
        
        # 定义科技风格主题样式
        tech_theme = """
        QWidget {
            background-color: #000000;
            color: #00ff00;
        }
        QTabWidget::pane {
            border: 1px solid #00ff00;
            border-radius: 10px;
        }
        QTabBar::tab {
            background: #001100;
            color: #00ff00;
            padding: 8px 16px;
            border-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #002200;
        }
        QLabel {
            color: #00ff00;
        }
        QComboBox {
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 4px;
            background: #001100;
            color: #00ff00;
        }
        QListWidget {
            border: 1px solid #00ff00;
            border-radius: 8px;
        }
        """
        
        # 应用相应主题
        if theme_name == "浅色主题":
            self.setStyleSheet(light_theme)
        elif theme_name == "深色主题":
            self.setStyleSheet(dark_theme)
        elif theme_name == "浅粉色少女心主题":
            self.setStyleSheet(pink_theme)
        elif theme_name == "科技风格主题":
            self.setStyleSheet(tech_theme)
        
        # 通知聊天组件更新主题
        self.model_tab.update_theme(theme_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用程序图标
    from PyQt5.QtGui import QIcon
    app.setWindowIcon(QIcon('asset/kieran-nlp.png'))
    
    # 授权码验证（仅在首次使用时）
    import sys
    import os
    from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
    
    # 定义授权标记文件路径
    AUTH_MARKER_FILE = "./authorized/kieran_nlp_authorized"
    AUTH_CODE_LIST_FILE = './authorized/auth_code.txt'
    # 预设的授权码 从加密文件中获取
    with open(AUTH_CODE_LIST_FILE, 'r') as f:
        PRESET_AUTH_CODE_list = f.read().split('\n')


    # 检查授权标记文件是否存在
    AUTH_MARKER_FILE_PATH = os.path.join(os.getcwd(), 'authorized', 'kieran_nlp_authorized')
    if not os.path.exists(AUTH_MARKER_FILE_PATH):
        # 授权标记文件不存在，需要进行授权验证
        # 弹出输入对话框获取授权码
        auth_code, ok = QInputDialog.getText(None, '首次使用授权验证', '请输入授权码:')

        for PRESET_AUTH_CODE in PRESET_AUTH_CODE_list:
            if ok and auth_code == PRESET_AUTH_CODE:
                # 确保授权标记文件所在目录存在，不存在则创建
                os.makedirs(os.path.dirname(AUTH_MARKER_FILE), exist_ok=True)
                with open(AUTH_MARKER_FILE, 'w') as f:
                    f.write(f"Authorized = 「{auth_code}」")
                    # 并且设置为环境变量
                    os.environ['AUTH_CODE'] = auth_code
                # 启动主窗口
                window = NLPDesktopApp()
                window.show()
                sys.exit(app.exec_())
        # 授权码错误或用户取消输入，显示错误信息并退出
        QMessageBox.critical(None, '授权失败', '授权码错误或未输入，程序将退出。')
        sys.exit(1)

    else:
        # 启动主窗口
        window = NLPDesktopApp()
        window.show()
        sys.exit(app.exec_())