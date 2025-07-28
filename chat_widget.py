from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QSizePolicy, QApplication, QMessageBox
    ,QToolTip
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal ,QTimer
from PyQt5.QtGui import QPixmap
import markdown

class ChatWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, chat_core, question,model_name ):
        super().__init__()
        self.chat_core = chat_core
        self.question = question
        self.model_name = model_name
        
    def run(self):
        answer = self.chat_core.chat(self.question, model=self.model_name)
        self.finished.emit(answer)

class ChatWidget(QWidget):
    def __init__(self, chat_core,get_model_func):
        super().__init__()
        self.chat_core = chat_core
        self.init_ui()
        self.get_model_func = get_model_func
    
        

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create title with property for styling
        title = QLabel("OpenAI 风格问答")
        title.setProperty("title", True)  # For QSS styling
        title.setAlignment(Qt.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)  # Reduce spacing between messages
        self.chat_widget.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_widget)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.model_base_input = QTextEdit()
        self.model_base_input.setFixedHeight(60)
        self.model_base_input.setPlaceholderText("输入消息...")
        
        self.model_base_button = QPushButton("发送")
        self.model_base_button.setFixedHeight(40)
        
        input_layout.addWidget(self.model_base_input)
        input_layout.addWidget(self.model_base_button)

        main_layout.addWidget(title)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(input_layout)

        self.model_base_button.clicked.connect(self.run_model_base)
        # 添加使用 Enter 键发送消息的功能
        self.model_base_input.installEventFilter(self)
        self.setLayout(main_layout)
        
        # 初始化主题
        self.current_theme = "浅色主题"
        
    def apply_qss_style(self):
        """应用QSS样式"""
        try:
            with open('iphone_style.qss', 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                # 避免递归调用
                if self.styleSheet() != style_sheet:
                    self.setStyleSheet(style_sheet)
        except FileNotFoundError:
            print("警告：未找到iphone_style.qss文件，使用默认样式。")
        
        # Initialize theme styles (now handled by QSS)
        self.light_theme_styles = {}
        self.dark_theme_styles = {}
        self.pink_theme_styles = {}
        self.tech_theme_styles = {}
        
        # 应用初始QSS样式
        self.apply_qss_style()
    
    def display_history_messages(self, history):
        """显示从数据库加载的历史消息"""
        for entry in history:
            is_user = entry['is_user']
            message = entry['message']
            self.add_message(message, is_user=is_user, show_copy=not is_user)

    def add_message(self, text, is_user=True, question=None,show_copy=False):
        msg_layout = QHBoxLayout()
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        text_html = markdown.markdown(text=text)
        msg_label = QLabel(text_html)
        msg_label.setTextFormat(Qt.RichText)
        msg_label.setWordWrap(True)
        msg_label.setMaximumWidth(500)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if is_user:
            avatar.setPixmap(QPixmap("./asset/user.png").scaled(40, 40))
            # Set message type property for QSS styling
            msg_label.setProperty("msgType", "user")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            msg_layout.addStretch()
            msg_layout.addWidget(msg_label)
            msg_layout.addWidget(avatar)
        else:
            avatar.setPixmap(QPixmap("./asset/bot2.png").scaled(40, 40))
            # Set message type property for QSS styling
            msg_label.setProperty("msgType", "assistant")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            # 按钮区
            btn_layout = QHBoxLayout()
            # 是否显示复制按钮与逻辑
            if show_copy:
                copy_btn = QPushButton("复制")
                copy_btn.setProperty("copyButton", True)  # For QSS styling
                copy_btn.setFixedSize(50, 28)
                def copy_and_notify():
                    QApplication.clipboard().setText(text)
                    QToolTip.showText(copy_btn.mapToGlobal(copy_btn.rect().bottomRight()), "复制成功！", copy_btn)
                    QTimer.singleShot(1200, QToolTip.hideText)  # 1.2秒后自动消失
                copy_btn.clicked.connect(copy_and_notify)
                btn_layout.addWidget(copy_btn)
   
            btn_layout.addStretch()
            # 垂直布局：气泡在上，按钮在下
            bubble_layout = QVBoxLayout()
            bubble_layout.addWidget(msg_label)
            bubble_layout.addLayout(btn_layout)
            msg_layout.addWidget(avatar)
            msg_layout.addLayout(bubble_layout)
            msg_layout.addStretch()
        self.chat_layout.addLayout(msg_layout)
        # 确保发送新消息后滚动到对话列表的最底部
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))

    def run_model_base(self):
        question = self.model_base_input.toPlainText().strip()
        if question:
            self.add_message(question, is_user=True,show_copy=True)
            self.model_base_input.clear()
            # 显示加载提示
            model = self.get_model_func()  # 动态获取
            self.add_message("嗯🤔,让我想想哈～", is_user=False,show_copy=False)
            # 启动异步线程
            self.worker = ChatWorker(self.chat_core, question,model_name = model)
            self.worker.finished.connect(lambda answer: self.on_answer(answer, question))
            self.worker.start()
    
    def eventFilter(self, source, event):
        # 添加使用 Enter 键发送消息的功能
        if source == self.model_base_input and event.type() == event.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # 检查是否按下了 Shift 键
                if event.modifiers() & Qt.ShiftModifier:
                    # 如果按下了 Shift 键，则插入换行符
                    cursor = self.model_base_input.textCursor()
                    cursor.insertText("\n")
                    return True
                else:
                    # 如果没有按下 Shift 键，则发送消息
                    self.run_model_base()
                    return True
        return super().eventFilter(source, event)

    def on_answer(self, answer, question):
        # 移除“嗯🤔 让我想想哈～”提示
        last_layout = self.chat_layout.takeAt(self.chat_layout.count()-1)
        if last_layout:
            # 遍历布局中的所有项目并删除它们
            while last_layout.count():
                item = last_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    # 如果项目是布局，则递归删除其内容
                    sub_layout = item.layout()
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        if sub_item.widget():
                            sub_item.widget().deleteLater()
                        elif sub_item.layout():
                            # 进一步递归处理嵌套布局
                            self._clear_layout(sub_item.layout())
                    # 删除空的布局
                    sub_layout.deleteLater()
        # 添加真正的回复，并带问题用于重新生成
        self.add_message(answer, is_user=False, question=question,show_copy=True)

    def _clear_layout(self, layout):
        """递归清除布局中的所有控件和子布局"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        layout.deleteLater()


    

    def update_theme(self, theme_name):
        """更新聊天界面主题"""
        self.current_theme = theme_name
        # 更新已有消息的样式
        self._update_existing_messages()
        # 重新应用QSS样式 (避免递归调用)
        # self.apply_qss_style()
    
    def _update_existing_messages(self):
        """更新已有消息的样式"""
        for i in range(self.chat_layout.count()):
            layout_item = self.chat_layout.itemAt(i)
            if layout_item and layout_item.layout():
                self._update_layout_widgets(layout_item.layout())
    
    def _update_layout_widgets(self, layout):
        """递归更新布局中的控件样式"""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                self._update_widget_style(item.widget())
            elif item.layout():
                self._update_layout_widgets(item.layout())
    
    def _update_widget_style(self, widget):
        """更新单个控件的样式"""
        # 现在样式由QSS文件统一管理，无需在这里单独设置
        pass
    
    def clear_chat(self):
         """清空聊天界面"""
         # 清空聊天记录显示区域
         # 逐个删除布局中的所有项目
         while self.chat_layout.count():
             item = self.chat_layout.takeAt(0)
             if item.widget():
                 item.widget().deleteLater()
             elif item.layout():
                 # 递归删除布局中的所有控件
                 self._clear_layout(item.layout())
         
         # 注意：我们不重新初始化整个UI，只需要清空聊天记录即可
         # self.init_ui()
