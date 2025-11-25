import sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QTextOption
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTextEdit, QSlider, QLabel
from PySide6.QtMultimedia import QSoundEffect
from qfluentwidgets import (
    TitleLabel, ComboBox, ToolButton, FluentIcon as FIF,
    Slider, SwitchButton, isDarkTheme
)
from config import tr

class TypewriterPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TypewriterPage")
        self.setStyleSheet("TypewriterPage { background: transparent; }")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        # Header
        self.titleLabel = TitleLabel(tr("typewriter_mode").upper(), self)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        # Toolbar
        toolLayout = QHBoxLayout()

        self.fontCombo = ComboBox(self)
        self.fontCombo.setPlaceholderText(tr("select_font"))
        self.fontCombo.setMinimumWidth(200)
        self.fontCombo.currentTextChanged.connect(self.change_font)
        toolLayout.addWidget(self.fontCombo)

        self.sizeSlider = Slider(Qt.Horizontal, self)
        self.sizeSlider.setRange(8, 72)
        self.sizeSlider.setValue(24)
        self.sizeSlider.setFixedWidth(150)
        self.sizeSlider.valueChanged.connect(self.change_size)
        toolLayout.addWidget(self.sizeSlider)

        self.sizeLabel = QLabel("24px", self)
        toolLayout.addWidget(self.sizeLabel)

        toolLayout.addStretch(1)

        self.centerSwitch = SwitchButton(self)
        self.centerSwitch.setOnText(tr("center"))
        self.centerSwitch.setOffText(tr("left"))
        self.centerSwitch.checkedChanged.connect(self.toggle_align)
        toolLayout.addWidget(self.centerSwitch)

        self.soundSwitch = SwitchButton(self)
        self.soundSwitch.setOnText(tr("sound_on"))
        self.soundSwitch.setOffText(tr("sound_off"))
        self.soundSwitch.setChecked(True)
        toolLayout.addWidget(self.soundSwitch)

        self.vBoxLayout.addLayout(toolLayout)

        # Text Area
        self.textArea = QTextEdit(self)
        self.textArea.setPlaceholderText(tr("typewriter_placeholder"))
        self.update_style()
        self.textArea.textChanged.connect(self.on_text_changed)
        self.vBoxLayout.addWidget(self.textArea)

        # Sound effects
        self.sound_enabled = True
        self.keystroke_sound = QSoundEffect()
        # Create a simple beep sound programmatically or use a WAV file if available
        self.last_text_length = 0

        self.load_fonts()
        self.change_font(self.fontCombo.currentText())

    def update_style(self):
        """Update style based on theme"""
        is_dark = isDarkTheme()
        text_color = "white" if is_dark else "black"
        bg_color = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(0, 0, 0, 0.05)"
        border_color = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)"

        self.textArea.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 20px;
                color: {text_color};
            }}
            QTextEdit:focus {{
                border: 1px solid rgba(255, 255, 255, 0.3);
                background-color: rgba(255, 255, 255, 0.08);
            }}
        """)

    def load_fonts(self):
        self.fontCombo.clear()
        db = QFontDatabase()
        fonts = db.families()
        self.fontCombo.addItems(fonts)
        if fonts:
            self.fontCombo.setCurrentIndex(0)

    def change_font(self, font_family):
        if not font_family: return
        font = QFont(font_family, self.sizeSlider.value())
        self.textArea.setFont(font)

    def change_size(self, value):
        self.sizeLabel.setText(f"{value}px")
        font = self.textArea.font()
        font.setPointSize(value)
        self.textArea.setFont(font)

    def toggle_align(self, checked):
        if checked:
            self.textArea.setAlignment(Qt.AlignCenter)
        else:
            self.textArea.setAlignment(Qt.AlignLeft)

    def on_text_changed(self):
        """Play sound effect when typing"""
        if not self.soundSwitch.isChecked():
            return

        current_length = len(self.textArea.toPlainText())
        if current_length > self.last_text_length:
            # Typing (character added)
            try:
                # Generate a beep sound using Windows API
                import winsound
                winsound.Beep(800, 50)  # 800Hz for 50ms
            except:
                pass
        self.last_text_length = current_length
