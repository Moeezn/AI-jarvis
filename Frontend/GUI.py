from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import (
    QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
old_chat_message = ""

# Directory paths
current_dir = os.getcwd()
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# ✅ TempDirectoryPath function
def TempDirectoryPath(filename=""):
    return os.path.join(current_dir, "Frontend", "Files", filename)


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 'can you', "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath("Mic.data"), 'w', encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(TempDirectoryPath("Mic.data"), 'r', encoding='utf-8') as file:
        Status = file.read().strip()
    return Status


def SetAsssistantStatus(Status):
    with open(TempDirectoryPath("Status.data"), 'w', encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    with open(TempDirectoryPath("Status.data"), 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status


def MicButtonInitiated():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def ShowTextToScreen(Text):
    with open(TempDirectoryPath("Responses.data"), 'w', encoding='utf-8') as file:
        file.write(Text)


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(os.path.join(GraphicsDirPath, "Jarvis.gif"))
        movie.setScaledSize(QSize(500, 550))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

        self.background_label = QLabel(self)
        box_pixmap = QPixmap(os.path.join(GraphicsDirPath, "Box.png"))
        box_pixmap = box_pixmap.scaled(screen_width, screen_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(box_pixmap)
        self.background_label.setGeometry(0, 0, screen_width, screen_height)
        self.background_label.lower()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 150)
        content_layout.setAlignment(Qt.AlignCenter)

        gif_label = QLabel()
        movie = QMovie(os.path.join(GraphicsDirPath, "Jarvis.gif"))
        movie.setScaledSize(QSize(500, 550))
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        self.icon_label = QLabel()
        pixmap = QPixmap(os.path.join(GraphicsDirPath, "Mic_on.png"))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")

        content_layout.addWidget(gif_label)
        content_layout.addWidget(self.label)
        content_layout.addWidget(self.icon_label)

        self.setLayout(content_layout)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(os.path.join(GraphicsDirPath, "Mic_on.png"), 60, 60)
            MicButtonInitiated()
        else:
            self.load_icon(os.path.join(GraphicsDirPath, "Mic_off.png"), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton("   Home")
        home_button.setIcon(QIcon(os.path.join(GraphicsDirPath, "Home.png")))
        home_button.setStyleSheet("height:40px; background-color:white; color: black")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        message_button = QPushButton("   Message")
        message_button.setIcon(QIcon(os.path.join(GraphicsDirPath, "Message.png")))
        message_button.setStyleSheet("height:40px; background-color:white; color: black")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(os.path.join(GraphicsDirPath, "Minimize.png")))
        minimize_button.setFlat(True)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.parent().showMinimized)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(os.path.join(GraphicsDirPath, "Maximize.png"))
        self.restore_icon = QIcon(os.path.join(GraphicsDirPath, "Restore.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(os.path.join(GraphicsDirPath, "Close.png")))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.parent().close)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        top_bar = CustomTopBar(self, stacked_widget)

        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(),
                         QApplication.desktop().screenGeometry().height())
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        self.setStyleSheet("background-color: black;")


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
