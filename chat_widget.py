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
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        title = QLabel("OpenAI 风格问答")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_widget)

        input_layout = QHBoxLayout()
        self.rag_input = QTextEdit()
        self.rag_input.setFixedHeight(50)
        self.rag_input.setStyleSheet("font-size: 16px; border-radius: 8px;")
        self.rag_button = QPushButton("发送")
        self.rag_button.setStyleSheet("font-size: 16px; padding: 10px 24px; background: #10a37f; color: white; border-radius: 8px;")
        input_layout.addWidget(self.rag_input)
        input_layout.addWidget(self.rag_button)

        main_layout.addWidget(title)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(input_layout)

        self.rag_button.clicked.connect(self.run_rag)
        self.setLayout(main_layout)

    def add_message(self, text, is_user=True, question=None):
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
            msg_label.setStyleSheet("background: #10a37f; color: white; border-radius: 8px; padding: 8px 16px;")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            msg_layout.addStretch()
            msg_layout.addWidget(msg_label)
            msg_layout.addWidget(avatar)
        else:
            avatar.setPixmap(QPixmap("./asset/bot2.png").scaled(40, 40))
            msg_label.setStyleSheet("background: #f1f1f1; color: #333; border-radius: 8px; padding: 8px 16px;")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            # 按钮区
            btn_layout = QHBoxLayout()
            copy_btn = QPushButton("复制")
            copy_btn.setFixedSize(50, 28)
            copy_btn.setStyleSheet("background: #10a37f; color: white; border-radius: 6px;")
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
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def run_rag(self):
        question = self.rag_input.toPlainText().strip()
        if question:
            self.add_message(question, is_user=True)
            self.rag_input.clear()
            # 显示加载提示
            model = self.get_model_func()  # 动态获取
            self.add_message("嗯🤔,让我想想哈～", is_user=False)
            # 启动异步线程
            self.worker = ChatWorker(self.chat_core, question,model_name = model)
            self.worker.finished.connect(lambda answer: self.on_answer(answer, question))
            self.worker.start()

    def on_answer(self, answer, question):
        # 移除“正在生成...”提示
        last_layout = self.chat_layout.takeAt(self.chat_layout.count()-1)
        if last_layout:
            while last_layout.count():
                item = last_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        # 添加真正的回复，并带问题用于重新生成
        self.add_message(answer, is_user=False, question=question)


    def replace_answer(self, msg_layout, answer, question):
        # 清空旧内容
        for i in reversed(range(msg_layout.count())):
            widget = msg_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # 重新添加助手回复、复制和重新生成按钮
        avatar = QLabel()
        avatar.setPixmap(QPixmap("./asset/bot2.png").scaled(40, 40))
        avatar.setFixedSize(40, 40)
        text_html = markdown.markdown(text=answer)
        msg_label = QLabel(text_html)
        msg_label.setTextFormat(Qt.RichText)
        msg_label.setWordWrap(True)  # 启用自动换行
        msg_label.setMaximumWidth(500)  # 设置最大宽度，超出自动换行
        msg_label.setStyleSheet("background: #f1f1f1; color: #333; border-radius: 8px; padding: 8px 16px;")
        msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        copy_btn = QPushButton("复制")
        copy_btn.setFixedSize(50, 28)
        copy_btn.setStyleSheet("background: #10a37f; color: white; border-radius: 6px;")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(answer))
        msg_layout.addWidget(avatar)
        msg_layout.addWidget(msg_label)
        msg_layout.addWidget(copy_btn)
        msg_layout.addWidget(regen_btn)
        msg_layout.addStretch()

