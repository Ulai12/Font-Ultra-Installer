import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, CardWidget, ScrollArea,
    ComboBox, PushButton, FluentIcon as FIF
)

from config import tr
from core import get_installed_fonts, create_preview_pixmap

class VersusComparerPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VersusComparerPage")
        self.setStyleSheet("VersusComparerPage { background: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        # Header
        self.titleLabel = TitleLabel(tr("versus_comparer").upper(), self)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        self.descLabel = BodyLabel(tr("versus_desc"), self)
        self.vBoxLayout.addWidget(self.descLabel, 0, Qt.AlignCenter)

        # Font Selectors
        selectorLayout = QHBoxLayout()

        # Font 1
        font1Layout = QVBoxLayout()
        font1Layout.addWidget(SubtitleLabel(tr("font_1"), self))
        self.font1Combo = ComboBox(self)
        self.font1Combo.currentTextChanged.connect(self.update_comparison)
        font1Layout.addWidget(self.font1Combo)
        selectorLayout.addLayout(font1Layout)

        # VS Label
        vsLabel = TitleLabel("VS", self)
        vsLabel.setAlignment(Qt.AlignCenter)
        selectorLayout.addWidget(vsLabel)

        # Font 2
        font2Layout = QVBoxLayout()
        font2Layout.addWidget(SubtitleLabel(tr("font_2"), self))
        self.font2Combo = ComboBox(self)
        self.font2Combo.currentTextChanged.connect(self.update_comparison)
        font2Layout.addWidget(self.font2Combo)
        selectorLayout.addLayout(font2Layout)

        self.vBoxLayout.addLayout(selectorLayout)

        # Preview Text Input
        previewLayout = QHBoxLayout()
        previewLayout.addWidget(SubtitleLabel(tr("text_label"), self))
        from qfluentwidgets import LineEdit
        self.previewText = LineEdit(self)
        self.previewText.setText(tr("pangram"))
        self.previewText.textChanged.connect(self.update_comparison)
        previewLayout.addWidget(self.previewText)
        self.vBoxLayout.addLayout(previewLayout)

        # Comparison Area
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")

        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background: transparent;")
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setSpacing(20)

        # Font 1 Card
        self.font1Card = CardWidget(self)
        self.font1Card.setStyleSheet("""
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        font1CardLayout = QVBoxLayout(self.font1Card)
        font1CardLayout.setContentsMargins(20, 20, 20, 20)

        self.font1NameLabel = SubtitleLabel("Font 1", self)
        font1CardLayout.addWidget(self.font1NameLabel)

        self.font1Preview = BodyLabel("", self)
        self.font1Preview.setWordWrap(True)
        font1CardLayout.addWidget(self.font1Preview)

        self.scrollLayout.addWidget(self.font1Card)

        # Font 2 Card
        self.font2Card = CardWidget(self)
        self.font2Card.setStyleSheet("""
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        font2CardLayout = QVBoxLayout(self.font2Card)
        font2CardLayout.setContentsMargins(20, 20, 20, 20)

        self.font2NameLabel = SubtitleLabel("Font 2", self)
        font2CardLayout.addWidget(self.font2NameLabel)

        self.font2Preview = BodyLabel("", self)
        self.font2Preview.setWordWrap(True)
        font2CardLayout.addWidget(self.font2Preview)

        self.scrollLayout.addWidget(self.font2Card)

        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)

        # Load fonts
        self.load_fonts()

    def load_fonts(self):
        """Load installed fonts into combo boxes"""
        from PySide6.QtGui import QFontDatabase
        font_names = QFontDatabase.families()

        self.font1Combo.addItems(font_names)
        self.font2Combo.addItems(font_names)

        if len(font_names) > 1:
            self.font2Combo.setCurrentIndex(1)

        self.update_comparison()

    def update_comparison(self):
        """Update the comparison preview"""
        font1_name = self.font1Combo.currentText()
        font2_name = self.font2Combo.currentText()
        text = self.previewText.text()

        if not font1_name or not font2_name:
            return

        if not text:
            text = tr("pangram")

        # Update Font 1
        self.font1NameLabel.setText(font1_name)
        self.font1Preview.setText(text)
        self.font1Preview.setFont(QFont(font1_name, 18))

        # Update Font 2
        self.font2NameLabel.setText(font2_name)
        self.font2Preview.setText(text)
        self.font2Preview.setFont(QFont(font2_name, 18))
