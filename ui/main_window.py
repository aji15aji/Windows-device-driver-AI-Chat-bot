from backend.bridge import ask_backend
from PySide6.QtCore import QThread
from backend.worker import InferenceWorker
from PySide6.QtWidgets import QMessageBox

from PySide6.QtWidgets import (
    QWidget, QTextEdit, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Device Driver Support Bot")
        self.setMinimumSize(700, 550)

        self.is_processing = False
        self.current_thread = None
        
        self._build_ui()

    def _build_ui(self):
        title = QLabel("🧠 Windows Device Driver Support Bot")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask a driver question...")
        self.input_box.setMinimumHeight(40)
        self.input_box.setStyleSheet("font-size: 14px; padding: 6px;")

        self.send_btn = QPushButton("Send")
        self.send_btn.setMinimumHeight(40)
        self.send_btn.setMinimumWidth(80)
        self.send_btn.setStyleSheet("font-size: 14px;")

        self.send_btn.clicked.connect(self.on_send_clicked)
        self.input_box.returnPressed.connect(self.on_send_clicked)

        bottom = QHBoxLayout()
        bottom.addWidget(self.input_box)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.chat_view)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def append_message(self, sender, text):
        self.chat_view.append(f"**{sender}:** {text}")
        self.chat_view.ensureCursorVisible()
        
    def replace_last_ai_message(self, text):
        cursor = self.chat_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        self.chat_view.append(f"<b>Bot:</b> {text}")

    def on_processing_complete(self):
        self.is_processing = False
        self.input_box.setEnabled(True)
        self.send_btn.setEnabled(True)
        
    def on_answer_ready(self, answer: str):
        self.replace_last_ai_message(answer)

    def on_error(self, error: str):
        self.replace_last_ai_message(f"Error: {error}")

    def on_send_clicked(self):

        if self.is_processing:
            QMessageBox.information(self, "Please Wait", 
                "One query is being executed.\nPlease wait while it completes.")
            return
        
        question = self.input_box.text().strip()
        if not question:
            return

        self.is_processing = True
        self.input_box.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.chat_view.append(f"<b>Query:</b> {question} ")
        self.input_box.clear()
        self.chat_view.append(f"<b>Bot:</b> Thinking...")
        
        self.current_thread = QThread()
        self.worker = InferenceWorker(ask_backend, question)

        self.worker.moveToThread(self.current_thread)

        self.current_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_answer_ready)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.on_processing_complete)
        self.worker.error.connect(self.on_processing_complete)

        self.worker.finished.connect(self.current_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.current_thread.finished.connect(self.current_thread.deleteLater)

        self.current_thread.start()

        #answer = ask_backend(question)

        # Remove "Thinking..."
        #cursor = self.chat_view.textCursor()
        #cursor.movePosition(QTextCursor.End)
        #cursor.select(QTextCursor.BlockUnderCursor)
        #cursor.removeSelectedText()
        #cursor.deletePreviousChar()

        #self.chat_view.append(f"<b>Bot:</b> {answer}")
