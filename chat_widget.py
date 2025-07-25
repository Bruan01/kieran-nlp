from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

class ChatWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, chat_core, question):
        super().__init__()
        self.chat_core = chat_core
        self.question = question
    def run(self):
        answer = self.chat_core.chat(self.question)
        self.finished.emit(answer)

class ChatWidget(QWidget):
    def __init__(self, chat_core):
        super().__init__()
        self.chat_core = chat_core
        self.init_ui()

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

    def add_message(self, text, is_user=True):
        msg_layout = QHBoxLayout()
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        if is_user:
            avatar.setPixmap(QPixmap("./asset/user.png").scaled(40, 40))
            msg_label = QLabel(text)
            msg_label.setStyleSheet("background: #10a37f; color: white; border-radius: 8px; padding: 8px 16px;")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            msg_layout.addStretch()
            msg_layout.addWidget(msg_label)
            msg_layout.addWidget(avatar)
        else:
            avatar.setPixmap(QPixmap("./asset/bot2.png").scaled(40, 40))
            msg_label = QLabel(text)
            msg_label.setStyleSheet("background: #f1f1f1; color: #333; border-radius: 8px; padding: 8px 16px;")
            msg_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            msg_layout.addWidget(avatar)
            msg_layout.addWidget(msg_label)
            msg_layout.addStretch()
        self.chat_layout.addLayout(msg_layout)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def run_rag(self):
        question = self.rag_input.toPlainText().strip()
        if question:
            self.add_message(question, is_user=True)
            self.rag_input.clear()
            # 显示加载提示
            self.add_message("正在生成，请稍候...", is_user=False)
            # 启动异步线程
            self.worker = ChatWorker(self.chat_core, question)
            self.worker.finished.connect(self.on_answer)
            self.worker.start()

    def on_answer(self, answer):
        # 移除“正在生成...”提示
        # 假设最后一条消息就是加载提示
        last_layout = self.chat_layout.takeAt(self.chat_layout.count()-1)
        if last_layout:
            while last_layout.count():
                item = last_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        # 添加真正的回复
        self.add_message(answer, is_user=False)

