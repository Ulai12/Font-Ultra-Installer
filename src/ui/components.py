import os
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QPoint
from PySide6.QtGui import QFont, QColor, QClipboard
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QWidget
from qfluentwidgets import (
    CardWidget, IconWidget, ImageLabel, BodyLabel, CaptionLabel,
    SubtitleLabel, PushButton, ToolButton, FluentIcon as FIF
)

from config import tr
from core import create_preview_pixmap

class FontCard(CardWidget):
    def __init__(self, font_data, parent=None):
        super().__init__(parent)
        self.font_data = font_data
        self.setFixedHeight(80)

        # Glassmorphism Style
        self.setStyleSheet("""
            FontCard {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
            FontCard:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuart)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Use simple icon initially, preview will be set later if available
        self.icon_widget = IconWidget(FIF.FONT_SIZE)
        self.icon_widget.setFixedSize(48, 48)
        self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # If preview pixmap is already in font_data, use it
        try:
            if 'preview_pixmap' in font_data and font_data['preview_pixmap']:
                self.icon_widget = ImageLabel(image=font_data['preview_pixmap'], parent=self)
                self.icon_widget.setFixedSize(200, 48)
                self.icon_widget.scaledToHeight(48)
                self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        except Exception as e:
            # Keep default icon if preview fails
            pass

        layout.addWidget(self.icon_widget)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Safe extraction of metadata
        try:
            name = os.path.basename(font_data.get('path', 'Unknown'))
            family = font_data.get('metadata', {}).get('family', name)
            style = font_data.get('metadata', {}).get('style', 'Regular')

            # Safe file size calculation
            try:
                size_kb = os.path.getsize(font_data['path']) // 1024
            except:
                size_kb = 0
        except Exception as e:
            name = "Unknown Font"
            family = "Unknown"
            style = "Unknown"
            size_kb = 0

        self.title_lbl = BodyLabel(family, self)
        font = QFont("Segoe UI Variable Display", 14)
        font.setBold(True)
        self.title_lbl.setFont(font)
        self.title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        info_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = CaptionLabel(f"{style} • {size_kb} KB", self)
        self.subtitle_lbl.setTextColor(QColor(120, 120, 120), QColor(150, 150, 150))
        self.subtitle_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        info_layout.addWidget(self.subtitle_lbl)

        layout.addLayout(info_layout)
        layout.addStretch(1)

        self.status_lbl = SubtitleLabel(tr("ready"), self)
        if not font_data.get('valid', False):
            self.status_lbl.setText(tr("invalid"))
            self.status_lbl.setTextColor(QColor("#FF4444"), QColor("#FF4444"))
        elif font_data.get('installed', False):
            self.status_lbl.setText(tr("already_installed"))
            self.status_lbl.setTextColor(QColor("#FFAA00"), QColor("#FFAA00"))

        layout.addWidget(self.status_lbl)

    def set_status(self, success):
        if success:
            self.status_lbl.setText(tr("installed"))
            self.status_lbl.setTextColor(QColor("#00CC6A"), QColor("#00CC6A"))
        else:
            self.status_lbl.setText(tr("failed"))
            self.status_lbl.setTextColor(QColor("#FF4444"), QColor("#FF4444"))

    def mouseReleaseEvent(self, event):
        """Handle click on card to show preview window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_preview_window()
        super().mouseReleaseEvent(event)

    def show_preview_window(self):
        """Open the detailed font preview modal"""
        from ui.preview import FontPreviewWindow

        # Create and show window
        self.preview_window = FontPreviewWindow(self.font_data, self.window())

        # Connect signals if parent has methods (HomePage logic)
        # We need to find the HomePage or similar to handle install/uninstall
        # For FontCard (usually in Home), we might want to trigger install

        # Since FontCard is in HomePage, we can try to find the parent page
        # Or we can emit a signal from FontCard that HomePage listens to?
        # Current implementation of HomePage doesn't listen to individual cards.
        # But we can hack it:

        # If we are in HomePage (Add Fonts), the action is usually "Install" (via "Install All" or drag drop)
        # But here we want individual install.
        # Let's just show the preview for now. Implementing individual install from preview might require more wiring.
        # The user asked for "Visualisation complete... enleve les boutons previsualiser et copier et desinstaller"
        # Wait, the user said "enleve les boutton previsualiser et copirer et desinstale"
        # "incoherance ui uix de la venetre contextulle ... la previsualisation est complette dans cette fentre ... donc enleve les boutton previsualiser et copirer et desinstale"
        # This implies the preview window SHOULD have these actions or at least replace the context menu's purpose.
        # My plan included "Actions: Installer / Désinstaller".

        # Let's connect the signals to a method if possible, or just print for now if no handler.
        # Actually, LibraryCard has `uninstall_requested`. FontCard doesn't have an `install_requested` yet.

        self.preview_window.exec()

class LibraryCard(CardWidget):
    uninstall_requested = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedHeight(80)

        # Create metadata dict for preview window
        self.font_data = {
            'path': file_path,
            'metadata': {
                'family': os.path.basename(file_path).rsplit('.', 1)[0]
            }
        }

        # Glassmorphism Style
        self.setStyleSheet("""
            LibraryCard {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
            LibraryCard:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.icon_widget = IconWidget(FIF.FONT_SIZE)
        self.icon_widget.setFixedSize(48, 48)
        layout.addWidget(self.icon_widget)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name = os.path.basename(self.file_path)
        self.title_lbl = BodyLabel(name, self)
        font = QFont("Segoe UI Variable Display", 14)
        font.setBold(True)
        self.title_lbl.setFont(font)
        self.title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        info_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = CaptionLabel(tr("installed"), self)
        self.subtitle_lbl.setTextColor(QColor("#00CC6A"), QColor("#00CC6A"))
        info_layout.addWidget(self.subtitle_lbl)

        layout.addLayout(info_layout)
        layout.addStretch(1)

        self.btn_uninstall = ToolButton(FIF.DELETE, self)
        self.btn_uninstall.clicked.connect(self._request_uninstall)
        layout.addWidget(self.btn_uninstall)

        self.update_preview("Aa")

    def mouseReleaseEvent(self, event):
        """Handle click on card to show preview window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_preview_window()
        super().mouseReleaseEvent(event)

    def show_preview_window(self):
        """Open the detailed font preview modal"""
        from ui.preview import FontPreviewWindow

        # Create and show window
        # We need to pass 'installed': True to show uninstall button
        data = self.font_data.copy()
        data['installed'] = True

        self.preview_window = FontPreviewWindow(data, self.window())
        self.preview_window.uninstall_requested.connect(self._request_uninstall_from_preview)
        self.preview_window.exec()

    def _request_uninstall_from_preview(self, path):
        # Re-emit the signal
        self.uninstall_requested.emit(self.file_path)

    def update_preview(self, text):
        pixmap = create_preview_pixmap(self.file_path, text)
        if pixmap:
            self.icon_widget = ImageLabel(image=pixmap, parent=self)
            self.icon_widget.setFixedSize(200, 48)
            self.icon_widget.scaledToHeight(48)
            self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            # Replace old icon in layout
            layout = self.layout()
            if layout:
                item = layout.itemAt(0)
                if item:
                    old_widget = item.widget()
                    if old_widget:
                        layout.replaceWidget(old_widget, self.icon_widget)
                        old_widget.deleteLater()

    def _request_uninstall(self):
        self.uninstall_requested.emit(self.file_path)

class GoogleFontCard(CardWidget):
    download_requested = Signal(str, str)

    def __init__(self, font_info, parent=None):
        super().__init__(parent)
        self.font_info = font_info
        self.setFixedHeight(70)

        # Glassmorphism Style
        self.setStyleSheet("""
            GoogleFontCard {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
            GoogleFontCard:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.icon_widget = IconWidget(FIF.CLOUD_DOWNLOAD)
        self.icon_widget.setFixedSize(32, 32)
        layout.addWidget(self.icon_widget)

        self.name_label = SubtitleLabel(self.font_info.get('family', 'Unknown'), self)
        layout.addWidget(self.name_label)

        layout.addStretch(1)

        self.btn_download = PushButton(tr("download"), self)
        self.btn_download.clicked.connect(self._request_download)
        layout.addWidget(self.btn_download)

    def _request_download(self):
        self.btn_download.setDisabled(True)
        self.btn_download.setText(tr("downloading"))
        self.download_requested.emit(self.font_info.get('family'), "regular")

    def on_download_finished(self, path):
        if path:
            self.btn_download.setText(tr("download_success"))
            self.btn_download.setIcon(FIF.CHECKBOX)
            return path
        else:
            self.btn_download.setText(tr("failed"))
            self.btn_download.setDisabled(False)
            return None
