import sys
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)  # Increased margins
        main_layout.setSpacing(30)  # Increased spacing

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("splash_screen_logo.png")
        logo_label.setPixmap(pixmap)
        logo_label.setScaledContents(True)
        logo_label.setFixedSize(300, 300)  # Larger logo size
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Right-side layout
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)  # Increased spacing

        # Header
        header_label = QLabel("USB Monitor")
        header_label.setStyleSheet("font-size: 36px; font-weight: bold; color: black;")  # Larger font size
        header_label.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(header_label)

        # Subtext
        subtext_label = QLabel("Initializing, please wait...")
        subtext_label.setStyleSheet("font-size: 20px; color: black;")  # Larger font size
        subtext_label.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(subtext_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 10px;
                text-align: center;
                color: black;
                background: #ddd;
            }
            QProgressBar::chunk {
                background-color: #00c853;
                border-radius: 10px;
            }
        """)
        self.progress_bar.setFixedHeight(35)  # Increased height
        right_layout.addWidget(self.progress_bar)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setFixedSize(800, 400)  # Enlarged splash screen size
        self.setStyleSheet("background-color: white;")  # Set white background
        self.center()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def update_progress(self, value):
        self.progress_bar.setValue(value)

def main():
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    # Simulate loading process
    for i in range(101):
        time.sleep(0.03)  # Simulate work being done
        splash.update_progress(i)
        QApplication.processEvents()

    splash.close()

if __name__ == "__main__":
    main()
