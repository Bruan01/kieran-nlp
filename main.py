from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QComboBox, QSplitter, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt
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
        self.dialog_list = QListWidget()
        self.dialog_list.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义上下文菜单
        self.dialog_list.customContextMenuRequested.connect(self.show_conversation_context_menu)
        # 添加新对话按钮
        new_dialog_btn = QPushButton("+ 新对话")
        new_dialog_btn.clicked.connect(self.create_new_conversation)
        
        sidebar_layout.addWidget(dialog_label)
        sidebar_layout.addWidget(self.dialog_list)
        sidebar_layout.addWidget(new_dialog_btn)
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
        self.tabs.addTab(self.rag_tab, "RAG")
        self.tabs.addTab(self.api_tab, "MCP")
        self.tabs.setMinimumWidth(10)

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
        
        # 初始化对话列表
        self.init_conversation_list()
        
        # 连接对话列表的点击事件
        self.dialog_list.itemClicked.connect(self.switch_conversation)
        
        # 连接对话列表的右键菜单事件
        self.dialog_list.customContextMenuRequested.connect(self.show_conversation_context_menu)
        
        # 清空聊天界面，确保一开始展示空白界面
        self.model_tab.clear_chat()

    def on_model_changed(self, model_name):
        """当模型切换时更新提示信息和ChatCore配置"""
        self.model_tip_label.setText(f"当前模型: {model_name}")
        # 更新ChatCore中的模型配置
        self.model_tab.chat_core.update_model(model_name)
        
    def on_theme_changed(self, theme_name):
        """当主题切换时更新界面样式"""
        # 根据主题名称加载对应的QSS样式表
        theme_name2qss_dir = { 
            "浅色主题":"./style/iphone_style.qss", 
            "深色主题":"./style/dark_style.qss", 
            "浅粉色少女心主题":"./style/pink_style.qss", 
            "科技风格主题":"./style/technology_style.qss" 
         }
        qss_file = theme_name2qss_dir.get(theme_name, 'iphone_style.qss')  # 默认使用iPhone风格
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                self.setStyleSheet(style_sheet)
        except FileNotFoundError:
            print(f"警告：未找到{qss_file}文件，使用默认样式。")
        
        # 通知聊天组件更新主题
        self.model_tab.update_theme(theme_name)
    
    def init_conversation_list(self):
        """初始化对话列表"""
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        # 从数据库获取用户的对话列表
        conversations = self.model_tab.chat_core.db_manager.get_user_conversations(auth_code)
        
        # 清空当前列表
        self.dialog_list.clear()
        
        # 添加对话到列表
        for conv in conversations:
            self.dialog_list.addItem(conv['title'])
        
        # 如果没有对话，不创建默认对话，等待用户输入第一个问题时再创建
    
    def create_new_conversation(self, first_question=""):
        """创建新对话"""
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        
        # 生成基于当前时间的标题
        from datetime import datetime
        new_conversation_title = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建新对话
        conversation_id = self.model_tab.chat_core.db_manager.create_conversation(auth_code, new_conversation_title)
        
        # 更新ChatCore的当前对话ID
        self.model_tab.chat_core.current_conversation_id = conversation_id
        
        # 清空聊天界面
        self.model_tab.clear_chat()
        
        # 重新加载对话列表
        self.init_conversation_list()
    
    def switch_conversation(self, item):
        """切换对话"""
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        # 获取选中的对话标题
        selected_title = item.text()
        
        # 从数据库获取用户的对话列表
        conversations = self.model_tab.chat_core.db_manager.get_user_conversations(auth_code)
        
        # 找到选中对话的ID
        for conv in conversations:
            if conv['title'] == selected_title:
                # 更新ChatCore的当前对话ID
                self.model_tab.chat_core.current_conversation_id = conv['id']
                
                # 获取对话历史
                history = self.model_tab.chat_core.db_manager.get_conversation_history(auth_code, conv['id'])
                
                # 清空聊天界面
                self.model_tab.clear_chat()
                
                # 显示对话历史
                self.model_tab.display_history_messages(history)
                break
    
    def show_conversation_context_menu(self, position):
        """显示对话列表的上下文菜单"""
        # 获取右键点击的项
        item = self.dialog_list.itemAt(position)
        if item is not None:
            # 创建菜单
            menu = QMenu()
            rename_action = QAction("重命名", self)
            delete_action = QAction("删除", self)
            
            # 连接动作
            rename_action.triggered.connect(lambda: self.rename_conversation(item))
            delete_action.triggered.connect(lambda: self.delete_conversation(item))
            
            # 添加动作到菜单
            menu.addAction(rename_action)
            menu.addAction(delete_action)
            
            # 显示菜单
            menu.exec_(self.dialog_list.mapToGlobal(position))
    
    def rename_conversation(self, item):
        """重命名对话"""
        # 获取当前对话标题
        current_title = item.text()
        
        # 弹出输入对话框获取新标题
        new_title, ok = QInputDialog.getText(self, "重命名对话", "请输入新标题:", text=current_title)
        
        if ok and new_title:
            # 获取授权码作为用户标识
            auth_code = os.environ.get('AUTH_CODE', 'default_user')
            
            # 从数据库获取用户的对话列表
            conversations = self.model_tab.chat_core.db_manager.get_user_conversations(auth_code)
            
            # 找到选中对话的ID
            conversation_id = None
            for conv in conversations:
                if conv['title'] == current_title:
                    conversation_id = conv['id']
                    break
            
            if conversation_id is not None:
                # 更新数据库中的对话标题
                self.model_tab.chat_core.db_manager.update_conversation_title(auth_code, conversation_id, new_title)
                
                # 更新列表项的显示
                item.setText(new_title)
                
                # 如果是当前对话，更新ChatCore的当前对话标题
                if self.model_tab.chat_core.current_conversation_id == conversation_id:
                    # 重新加载对话列表
                    self.init_conversation_list()
    
    def delete_conversation(self, item):
        """删除对话"""
        # 获取当前对话标题
        current_title = item.text()
        
        # 确认删除操作
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, '确认删除', f'确定要删除对话 "{current_title}" 吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 获取授权码作为用户标识
            auth_code = os.environ.get('AUTH_CODE', 'default_user')
            
            # 从数据库获取用户的对话列表
            conversations = self.model_tab.chat_core.db_manager.get_user_conversations(auth_code)
            
            # 找到选中对话的ID
            conversation_id = None
            for conv in conversations:
                if conv['title'] == current_title:
                    conversation_id = conv['id']
                    break
            
            if conversation_id is not None:
                # 从数据库删除对话
                self.model_tab.chat_core.db_manager.delete_conversation(auth_code, conversation_id)
                
                # 从列表中移除项
                self.dialog_list.takeItem(self.dialog_list.row(item))
                
                # 如果删除的是当前对话，切换到第一个对话或创建新对话
                if self.model_tab.chat_core.current_conversation_id == conversation_id:
                    # 重置当前对话ID
                    self.model_tab.chat_core.current_conversation_id = None
                    
                    # 获取剩余的对话列表
                    remaining_conversations = self.model_tab.chat_core.db_manager.get_user_conversations(auth_code)
                    
                    if remaining_conversations:
                        # 切换到第一个对话
                        first_conv = remaining_conversations[0]
                        self.model_tab.chat_core.current_conversation_id = first_conv['id']
                        
                        # 获取对话历史
                        history = self.model_tab.chat_core.db_manager.get_conversation_history(auth_code, first_conv['id'])
                        
                        # 清空聊天界面
                        self.model_tab.clear_chat()
                        
                        # 显示对话历史
                        self.model_tab.display_history_messages(history)
                    else:
                        # 没有剩余对话，清空聊天界面
                        self.model_tab.clear_chat()
                
                # 重新加载对话列表
                self.init_conversation_list()
    
    def display_chat_history(self):
        """显示聊天历史记录"""
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        # 检查是否有当前对话ID
        if self.model_tab.chat_core.current_conversation_id:
            # 从数据库获取当前对话的历史
            history = self.model_tab.chat_core.db_manager.get_conversation_history(auth_code, self.model_tab.chat_core.current_conversation_id)
            # 在聊天界面显示历史消息
            self.model_tab.display_history_messages(history)
        else:
            # 如果没有当前对话，清空聊天界面
            self.model_tab.clear_chat()


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
                # 不加载用户的对话历史，保持空白界面
                window.show()
                sys.exit(app.exec_())
        # 授权码错误或用户取消输入，显示错误信息并退出
        QMessageBox.critical(None, '授权失败', '授权码错误或未输入，程序将退出。')
        sys.exit(1)

    else:
        # 启动主窗口
        window = NLPDesktopApp()
        # 不加载用户的对话历史，保持空白界面
        window.show()
        sys.exit(app.exec_())