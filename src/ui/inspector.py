import sys
import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QLabel, QScrollArea
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, ComboBox, CardWidget, FluentIcon as FIF,
    ToolButton, SearchLineEdit, ScrollArea
)
from config import tr, BASE_DIR, BOWLBY_FONT_PATH

def _apply_bowlby_font(label):
    """Apply Bowlby One SC font to a title label via stylesheet"""
    if os.path.exists(BOWLBY_FONT_PATH):
        QFontDatabase.addApplicationFont(BOWLBY_FONT_PATH)
        label.setStyleSheet("font-family: 'Bowlby One SC'; font-size: 32px;")

class GlyphInspectorPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlyphInspectorPage")
        self.setStyleSheet("GlyphInspectorPage { background: transparent; }")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(tr("inspector").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        # Toolbar
        toolLayout = QHBoxLayout()

        self.fontCombo = ComboBox(self)
        self.fontCombo.setPlaceholderText("Select Font")
        self.fontCombo.setMinimumWidth(200)
        self.fontCombo.currentTextChanged.connect(self.load_glyphs)
        toolLayout.addWidget(self.fontCombo)

        self.refreshBtn = ToolButton(FIF.SYNC, self)
        self.refreshBtn.clicked.connect(self.load_fonts)
        toolLayout.addWidget(self.refreshBtn)

        toolLayout.addStretch(1)

        self.vBoxLayout.addLayout(toolLayout)

        # Grid Area
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background-color: transparent; border: none;")

        self.scrollContent = QWidget()
        self.scrollContent.setStyleSheet("background-color: transparent;")
        self.gridLayout = QGridLayout(self.scrollContent)
        self.gridLayout.setSpacing(10)
        self.scrollArea.setWidget(self.scrollContent)

        self.vBoxLayout.addWidget(self.scrollArea)

        self.load_fonts()

    def load_fonts(self):
        self.fontCombo.clear()
        db = QFontDatabase()
        fonts = db.families()
        self.fontCombo.addItems(fonts)
        if fonts:
            self.fontCombo.setCurrentIndex(0)

    def load_glyphs(self, font_family):
        # Clear grid
        for i in reversed(range(self.gridLayout.count())):
            widget = self.gridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not font_family or font_family == "":
            return

        try:
            font = QFont(font_family, 24)

            # Display a range of common glyphs
            row = 0
            col = 0
            max_cols = 8

            # ASCII + Latin-1 Supplement + Common Symbols
            ranges = [(33, 126), (161, 255), (0x20A0, 0x20CF)]

            for start, end in ranges:
                for code in range(start, end + 1):
                    char = chr(code)

                    card = CardWidget(self.scrollContent)
                    card.setFixedSize(80, 80)
                    card.setStyleSheet("""
                        CardWidget {
                            background-color: rgba(255, 255, 255, 0.05);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 8px;
                        }
                        CardWidget:hover {
                            background-color: rgba(255, 255, 255, 0.1);
                            border: 1px solid rgba(255, 255, 255, 0.3);
                        }
                    """)

                    layout = QVBoxLayout(card)
                    layout.setAlignment(Qt.AlignCenter)

                    lbl = QLabel(char, card)
                    lbl.setFont(font)
                    lbl.setAlignment(Qt.AlignCenter)
                    layout.addWidget(lbl)

                    self.gridLayout.addWidget(card, row, col)

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
        except Exception as e:
            print(f"Erreur lors du chargement des glyphes: {e}")
