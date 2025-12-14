import os
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsOpacityEffect, QWidget, QScrollArea, QFrame
)
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CaptionLabel, PrimaryPushButton,
    PushButton, ToolButton, FluentIcon as FIF, TextEdit
)

from config import tr
from core import create_preview_pixmap

class FontPreviewWindow(QDialog):
    """
    Modal window for detailed font preview and actions.
    Liquid Glass style.
    """
    def __init__(self, font_data, parent=None):
        super().__init__(parent)
        self.font_data = font_data
        self.setWindowTitle(tr("preview_text"))
        self.resize(800, 600)

        # Frameless window for custom styling
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container with Glass effect
        self.container = QWidget(self)
        self.container.setObjectName("previewContainer")

        # Dynamic style based on theme (handled by qfluentwidgets usually, but here we force glass)
        # We can use a generic glass style that looks good on both or check theme
        from qfluentwidgets import isDarkTheme
        bg_color = "rgba(32, 32, 32, 0.95)" if isDarkTheme() else "rgba(240, 240, 240, 0.95)"
        border_color = "rgba(255, 255, 255, 0.15)" if isDarkTheme() else "rgba(0, 0, 0, 0.1)"
        text_color = "white" if isDarkTheme() else "black"
        edit_bg = "rgba(255, 255, 255, 0.05)" if isDarkTheme() else "rgba(0, 0, 0, 0.05)"

        self.container.setStyleSheet(f"""
            QWidget#previewContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 16px;
            }}
            QLabel {{
                color: {text_color};
            }}
            QTextEdit {{
                background-color: {edit_bg};
                border: 1px solid {border_color};
                border-radius: 8px;
                color: {text_color};
                padding: 10px;
            }}
        """)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(20)

        self.setup_header()
        self.setup_metadata()
        self.setup_preview_area()
        self.setup_actions()

        self.main_layout.addWidget(self.container)

        # Center on parent
        if parent:
            self.move(
                parent.window().geometry().center() - self.rect().center()
            )

    def setup_header(self):
        header_layout = QHBoxLayout()

        # Font Name
        family = self.font_data.get('metadata', {}).get('family', 'Unknown Font')
        self.title_lbl = SubtitleLabel(family, self)
        self.title_lbl.setFont(QFont("Segoe UI Variable Display", 24, QFont.Bold))
        header_layout.addWidget(self.title_lbl)

        header_layout.addStretch(1)

        # Close Button
        self.close_btn = ToolButton(FIF.CLOSE, self)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        self.layout.addLayout(header_layout)

    def setup_metadata(self):
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(40)

        metadata = self.font_data.get('metadata', {})

        # Helper to create meta column
        def add_meta_item(label, value):
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            lbl = CaptionLabel(label, self)
            lbl.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))
            val = BodyLabel(str(value), self)
            item_layout.addWidget(lbl)
            item_layout.addWidget(val)
            meta_layout.addLayout(item_layout)

        add_meta_item(tr("style"), metadata.get('style', 'Regular'))
        add_meta_item(tr("version"), metadata.get('version', '1.0'))

        # File size
        try:
            size_kb = os.path.getsize(self.font_data.get('path', '')) // 1024
            add_meta_item(tr("size"), f"{size_kb} KB")
        except:
            add_meta_item(tr("size"), tr("unknown"))

        meta_layout.addStretch(1)
        self.layout.addLayout(meta_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); max-height: 1px;")
        self.layout.addWidget(line)

    def setup_preview_area(self):
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(content)
        scroll_layout.setSpacing(20)

        # Font for preview
        font_path = self.font_data.get('path')
        # Note: In a real app we would load the font ID.
        # For now we rely on the system if installed, or we might need QFontDatabase.addApplicationFont
        # But since we are just previewing, we assume the user wants to see the font applied.
        # If it's not installed, we can't easily apply it to a QLabel without loading it.
        # We'll try to load it temporarily.

        font_id = -1
        if font_path and os.path.exists(font_path):
            from PySide6.QtGui import QFontDatabase
            font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id != -1:
            loaded_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            preview_font = QFont(loaded_family, 12)
        else:
            # Fallback if load fails or already installed (try by family name)
            preview_font = QFont(self.font_data.get('metadata', {}).get('family', 'Segoe UI'), 12)

        # Preview Texts
        texts = [
            (tr("alphabet"), "ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz"),
            (tr("numbers"), "0123456789"),
            (tr("symbols"), "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            (tr("pangram"), "Portez ce vieux whisky au juge blond qui fume.\nThe quick brown fox jumps over the lazy dog.")
        ]

        for title, text in texts:
            lbl_title = CaptionLabel(title, self)
            lbl_title.setTextColor(QColor(100, 200, 255), QColor(100, 200, 255))
            scroll_layout.addWidget(lbl_title)

            edit = TextEdit(self)
            edit.setPlainText(text)
            edit.setFont(preview_font)
            # Increase font size for preview
            f = edit.font()
            f.setPointSize(24)
            edit.setFont(f)
            edit.setFixedHeight(120) # Fixed height for each block
            scroll_layout.addWidget(edit)

        scroll_layout.addStretch(1)
        self.scroll.setWidget(content)
        self.layout.addWidget(self.scroll)

    def setup_actions(self):
        action_layout = QHBoxLayout()
        action_layout.addStretch(1)

        # Determine action based on installation status
        is_installed = self.font_data.get('installed', False)

        if is_installed:
            self.action_btn = PushButton(tr("uninstall"), self)
            self.action_btn.clicked.connect(self.request_uninstall)
            # Style for delete
            self.action_btn.setStyleSheet("""
                PushButton {
                    background-color: rgba(255, 68, 68, 0.2);
                    color: #ff4444;
                    border: 1px solid rgba(255, 68, 68, 0.5);
                }
                PushButton:hover {
                    background-color: rgba(255, 68, 68, 0.3);
                }
            """)
        else:
            self.action_btn = PrimaryPushButton(tr("install_all"), self) # Reusing install_all string or similar
            self.action_btn.setText(tr("install")) # Explicit text
            self.action_btn.clicked.connect(self.request_install)

        self.action_btn.setFixedWidth(150)
        action_layout.addWidget(self.action_btn)

        self.layout.addLayout(action_layout)

    def request_install(self):
        # This needs to communicate back to the main window or controller
        # For now we'll just close and let the parent handle it if we emit a signal
        # But since we don't have a direct signal here, we might need to pass a callback or use a custom signal
        # Let's add a custom signal to the window
        self.install_requested.emit(self.font_data['path'])
        self.close()

    def request_uninstall(self):
        self.uninstall_requested.emit(self.font_data['path'])
        self.close()

    # Signals
    install_requested = Signal(str)
    uninstall_requested = Signal(str)
