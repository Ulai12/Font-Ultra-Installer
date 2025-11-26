import os
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from qfluentwidgets import SubtitleLabel, CaptionLabel

from config import BASE_DIR

class SplashScreen(QWidget):
    """Splash screen overlay widget for main window"""
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SplashScreen")
        self.setStyleSheet("""
            QWidget#SplashScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 40, 60, 255),
                    stop:1 rgba(50, 70, 100, 255)
                );
                border: none;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add spacing at top
        layout.addStretch(1)

        # Logo
        self.logo_label = QLabel()
        logo_path = os.path.join(BASE_DIR, "FontUltraInstaller.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("🔤")
            font = QFont()
            font.setPointSize(72)
            self.logo_label.setFont(font)

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        # Title
        self.title_label = SubtitleLabel("Ultra Font Installer", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white;")
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = CaptionLabel("Initializing...", self)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        layout.addWidget(self.subtitle_label)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF,
                    stop:1 #0099FF
                );
                border-radius: 6px;
            }
        """)
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setMaximumWidth(300)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add spacing at bottom
        layout.addStretch(1)

        # Progress animation
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.increment_progress)

        self.current_progress = 0
        self.loading_steps = 0

    def start_animation(self):
        """Start the splash screen animation"""
        self.show()
        self.progress_timer.start(50)

    def increment_progress(self):
        """Increment progress bar with easing"""
        if self.current_progress < 95:
            increment = max(1, (95 - self.current_progress) // 15)
            self.current_progress += increment
            self.progress_bar.setValue(self.current_progress)

            steps = ["Initializing...", "Loading fonts...", "Setting up UI...", "Almost ready..."]
            self.loading_steps = (self.loading_steps + 1) % len(steps)
            self.subtitle_label.setText(steps[self.loading_steps])

    def finish(self):
        """Complete the loading and emit finished signal"""
        self.progress_timer.stop()
        self.progress_bar.setValue(100)
        self.subtitle_label.setText("Ready!")

        # Fade out effect
        QTimer.singleShot(500, self.hide)
        QTimer.singleShot(600, self.finished.emit)
