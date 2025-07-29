from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QComboBox, QSplitter, QMenu, QAction, QInputDialog, QDialog, QGroupBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from chat_interface import ChatCore
from chat_widget import ChatWidget
from dotenv import load_dotenv
from utils.logger import Logger
import os
import sys
import requests
from config.settings import API_MODELS, THEMES, THEME_NAME_TO_QSS, DEFAULT_QSS, AUTH_MARKER_FILE_PATH

# 加载.env
load_dotenv()

class SettingsDialog(QDialog):
    """设置对话框，用于主题和语言设置"""
    def __init__(self, parent=None, current_theme="深色主题", current_language="中文"):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(400, 500)  # 增加高度以容纳用户信息
        self.current_theme = current_theme
        self.current_language = current_language
        
        # 获取用户信息
        self.user_info = self.get_user_info()
        
        # 应用当前主题样式
        self.apply_theme()
        
        # 创建UI
        self.init_ui()
    
    def get_user_info(self):
        """获取用户基本信息"""
        try:
            api_key = os.getenv("API_KEY")
            url = "https://api.siliconflow.cn/v1/user/info"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"获取用户信息失败: {response.status_code}"
                print(error_msg)
                # 记录错误日志
                if hasattr(self, 'parent') and hasattr(self.parent(), 'logger'):
                    self.parent().logger.log_error(error_msg)
                return None
        except Exception as e:
            error_msg = f"获取用户信息时出错: {e}"
            print(error_msg)
            # 记录异常日志
            if hasattr(self, 'parent') and hasattr(self.parent(), 'logger'):
                self.parent().logger.log_exception(error_msg)
            return None
    
    def apply_theme(self):
        """应用当前主题样式"""
        # 根据当前主题加载对应的QSS样式表
        qss_file = THEME_NAME_TO_QSS.get(self.current_theme, DEFAULT_QSS)
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                self.setStyleSheet(style_sheet)
        except FileNotFoundError:
            print(f"警告：未找到{qss_file}文件，使用默认样式。")
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 用户信息显示
        user_info_group = QGroupBox("用户信息")
        user_info_layout = QVBoxLayout()
        
        if self.user_info and 'data' in self.user_info:
            data = self.user_info['data']
            # 为每个QLabel设置最小高度以确保完全显示，并添加间距
            user_id_label = QLabel(f"用户ID: {data.get('id', 'N/A')}")
            user_id_label.setMinimumHeight(20)
            user_id_label.setWordWrap(True)
            user_id_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(user_id_label)
        
            
            admin_label = QLabel(f"Admin: {data.get('isAdmin', 'N/A')}")
            admin_label.setMinimumHeight(20)
            admin_label.setWordWrap(True)
            admin_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(admin_label)
         
            
            balance_label = QLabel(f"API额度: {data.get('balance', 'N/A')}")
            balance_label.setMinimumHeight(20)
            balance_label.setWordWrap(True)
            balance_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(balance_label)
       
            
            total_balance_label = QLabel(f"API总额度: {data.get('totalBalance', 'N/A')}")
            total_balance_label.setMinimumHeight(20)
            total_balance_label.setWordWrap(True)
            total_balance_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(total_balance_label)
            
            
            user_type_label = QLabel(f"用户类型: {data.get('name', 'N/A')}")
            user_type_label.setMinimumHeight(20)
            user_type_label.setWordWrap(True)
            user_type_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(user_type_label)
          
            
            user_status_label = QLabel(f"用户状态: {data.get('status', 'N/A')}")
            user_status_label.setMinimumHeight(20)
            user_status_label.setWordWrap(True)
            user_status_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(user_status_label)
          
            
            # 添加底部间距
            user_info_layout.addStretch()
        else:
            no_info_label = QLabel("无法获取用户信息")
            no_info_label.setMinimumHeight(20)
            no_info_label.setStyleSheet("font-size: 14px;color: #666666;")
            user_info_layout.addWidget(no_info_label)
            
            # 添加底部间距
            user_info_layout.addStretch()
        
        user_info_group.setLayout(user_info_layout)
        
        layout.addWidget(user_info_group)
        
        # 主题设置
        theme_label = QLabel("外观主题")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES)
        self.theme_combo.setCurrentText(self.current_theme)
        
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        
        # 语言设置
        language_label = QLabel("语言设置")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        self.language_combo.setCurrentText(self.current_language)
        
        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

# ===============对话主窗口====================
class NLPDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kieran-NLP")
        self.resize(1280, 720)
        
        # 初始化日志记录器
        self.logger = Logger()

        # 左侧侧边栏
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # API切换
        api_label = QLabel("API 切换")
        self.api_combo = QComboBox()
        self.api_combo.addItems(API_MODELS)
        
        # 添加模型切换提示标签
        self.model_tip_label = QLabel("")
        self.model_tip_label.setStyleSheet("color: green; font-weight: bold;")
        
        sidebar_layout.addWidget(api_label)
        sidebar_layout.addWidget(self.api_combo)
        sidebar_layout.addWidget(self.model_tip_label)
        
        # 连接信号槽，实现在切换模型时提醒用户
        self.api_combo.currentTextChanged.connect(self.on_model_changed)

        # 主题切换（已隐藏）
        theme_label = QLabel("主题切换")
        theme_label.setVisible(False)  # 隐藏主题标签
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.theme_combo.setVisible(False)  # 隐藏主题选择框

        sidebar_layout.addWidget(theme_label)
        sidebar_layout.addWidget(self.theme_combo)
        
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

        # 添加用户头像和状态信息到最下方
        # 创建一个水平布局来放置头像和状态信息
        user_info_layout = QHBoxLayout()
        
        # 用户头像
        self.user_avatar = QLabel()
        self.user_avatar.setFixedSize(40, 40)
        self.user_avatar.setPixmap(QPixmap("./asset/user.png").scaled(40, 40))
        self.user_avatar.setCursor(Qt.PointingHandCursor)  # 设置鼠标手势
        user_info_layout.addWidget(self.user_avatar)
        
        # 从文件获取当前授权码
        with open(AUTH_MARKER_FILE_PATH, 'r') as f:
            content = f.read()
            if "Authorized = 「" in content:
                authorized_code = content.split("「")[1].split("」")[0]
                # 用户状态
                user_label = QLabel(f"用户：已登录 授权码: {authorized_code}")
                user_info_layout.addWidget(user_label)
        
        # 将用户信息布局添加到侧边栏底部
        sidebar_layout.addStretch()  # 添加弹性空间
        sidebar_layout.addLayout(user_info_layout)
        
        # 连接用户头像点击事件
        self.user_avatar.mousePressEvent = self.show_settings_dialog

        

        # 右侧主内容区
        self.tabs = QTabWidget()
        api_key = os.getenv("API_KEY")
        api_url = os.getenv("API_URL")
        chat_core = ChatCore(api_key=api_key, api_url=api_url)
        
        # 不再需要手动加载对话历史，RunnableWithMessageHistory会自动处理

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
        qss_file = THEME_NAME_TO_QSS.get(theme_name, DEFAULT_QSS)  # 默认使用iPhone风格
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
        # 检查是否有正在进行的对话生成
        if self.model_tab.is_worker_running():
            # 显示提示信息
            QMessageBox.warning(self, "提示", "当前对话正在生成中，请等待生成结束后再切换对话。")
            return
        
        # 停止当前可能正在运行的worker线程
        self.model_tab.stop_worker()
        
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
                
                # 获取对话历史（分页加载）
                history = self.model_tab.chat_core.db_manager.get_conversation_history(
                    auth_code, conv['id'], limit=100)  # 一次性获取前100条消息
                
                # 清空聊天界面
                self.model_tab.clear_chat()
                
                # 显示对话历史
                self.model_tab.display_history_messages(history)
                
                # 滚动到对话底部
                QTimer.singleShot(0, lambda: self.model_tab.scroll_area.verticalScrollBar().setValue(
                    self.model_tab.scroll_area.verticalScrollBar().maximum()))
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
                        
                        # 获取对话历史（分页加载）
                        history = self.model_tab.chat_core.db_manager.get_conversation_history(
                            auth_code, first_conv['id'], limit=100)  # 一次性获取前100条消息
                        
                        # 清空聊天界面
                        self.model_tab.clear_chat()
                        
                        # 显示对话历史
                        self.model_tab.display_history_messages(history)
                    else:
                        # 没有剩余对话，清空聊天界面
                        self.model_tab.clear_chat()
                
                # 重新加载对话列表
                self.init_conversation_list()
    
    def show_settings_dialog(self, event):
        """显示设置对话框"""
        # 获取当前主题
        current_theme = self.theme_combo.currentText()
        
        # 创建并显示设置对话框
        settings_dialog = SettingsDialog(self, current_theme)
        result = settings_dialog.exec_()
        
        # 如果用户点击了确定按钮
        if result == QDialog.Accepted:
            # 获取选择的主题
            selected_theme = settings_dialog.theme_combo.currentText()
            
            # 如果主题发生变化，更新主题
            if selected_theme != current_theme:
                self.theme_combo.setCurrentText(selected_theme)
                self.on_theme_changed(selected_theme)
    
    def display_chat_history(self):
        """显示聊天历史记录（分页加载）"""
        # 获取授权码作为用户标识
        auth_code = os.environ.get('AUTH_CODE', 'default_user')
        # 检查是否有当前对话ID
        if self.model_tab.chat_core.current_conversation_id:
            # 从数据库获取当前对话的历史（分页加载）
            history = self.model_tab.chat_core.db_manager.get_conversation_history(
                auth_code, self.model_tab.chat_core.current_conversation_id, limit=100)  # 一次性获取前100条消息
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
        # 从授权标记文件中读取授权码并设置环境变量
        with open(AUTH_MARKER_FILE_PATH, 'r') as f:
            content = f.read()
            if "Authorized = 「" in content:
                auth_code = content.split("「")[1].split("」")[0]
                os.environ['AUTH_CODE'] = auth_code
        # 启动主窗口
        window = NLPDesktopApp()
        # 加载用户的对话历史
        window.init_conversation_list()
        window.show()
        sys.exit(app.exec_())