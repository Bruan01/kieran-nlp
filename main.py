import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QTabWidget, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class NLPDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NLP 工作台")
        self.resize(900, 600)

        self.tabs = QTabWidget()
        self.rag_tab = QWidget()
        self.model_tab = QWidget()
        self.api_tab = QWidget()

        self.tabs.addTab(self.rag_tab, "RAG 问答")
        self.tabs.addTab(self.model_tab, "模型推理")
        self.tabs.addTab(self.api_tab, "API 控制台")

        self.init_rag_ui()
        self.setCentralWidget(self.tabs)

    def init_rag_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        title = QLabel("OpenAI 风格问答")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")

        # 消息区
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_widget)

        # 输入区
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
        self.rag_tab.setLayout(main_layout)

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
        # 自动滚动到底部
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def run_rag(self):
        question = self.rag_input.toPlainText().strip()
        if question:
            self.add_message(question, is_user=True)
            answer = f"你输入的问题是：{question}"
            self.add_message(answer, is_user=False)
            self.rag_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NLPDesktopApp()
    window.show()
    sys.exit(app.exec_())