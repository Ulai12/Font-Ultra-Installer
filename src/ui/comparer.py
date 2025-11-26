import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, CardWidget, ScrollArea,
    ComboBox, LineEdit, FluentIcon as FIF, ImageLabel
)

from config import tr, BASE_DIR, BOWLBY_FONT_PATH
from core import create_preview_pixmap

def _apply_bowlby_font(label):
    """Apply Bowlby One SC font to a title label via stylesheet"""
    if os.path.exists(BOWLBY_FONT_PATH):
        QFontDatabase.addApplicationFont(BOWLBY_FONT_PATH)
        label.setStyleSheet("font-family: 'Bowlby One SC'; font-size: 32px;")

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
        _apply_bowlby_font(self.titleLabel)
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
        font1CardLayout.setSpacing(12)

        self.font1NameLabel = SubtitleLabel("Font 1", self)
        font1CardLayout.addWidget(self.font1NameLabel)

        self.font1Preview = ImageLabel()
        self.font1Preview.setMinimumHeight(80)
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
        font2CardLayout.setSpacing(12)

        self.font2NameLabel = SubtitleLabel("Font 2", self)
        font2CardLayout.addWidget(self.font2NameLabel)

        self.font2Preview = ImageLabel()
        self.font2Preview.setMinimumHeight(80)
        font2CardLayout.addWidget(self.font2Preview)

        self.scrollLayout.addWidget(self.font2Card)

        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)

        # Cache for font file paths
        self.font_cache = {}

        # Load fonts
        self.load_fonts()

    def load_fonts(self):
        """Load installed fonts into combo boxes"""
        font_names = sorted(QFontDatabase.families())

        self.font1Combo.addItems(font_names)
        self.font2Combo.addItems(font_names)

        if len(font_names) > 1:
            self.font2Combo.setCurrentIndex(1)

        self.update_comparison()

    def _get_font_file(self, font_name):
        """Get font file path, using cache for performance"""
        if font_name in self.font_cache:
            return self.font_cache[font_name]

        fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
        try:
            # Simple heuristic: look for files starting with font name
            for filename in os.listdir(fonts_dir):
                if filename.lower().endswith(('.ttf', '.otf')):
                    full_path = os.path.join(fonts_dir, filename)
                    # Check if filename matches the font name
                    base_name = os.path.splitext(filename)[0]
                    if font_name.lower() in base_name.lower() or base_name.lower() in font_name.lower():
                        self.font_cache[font_name] = full_path
                        return full_path
        except:
            pass

        return None

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
        font1_file = self._get_font_file(font1_name)
        if font1_file and os.path.exists(font1_file):
            pixmap = create_preview_pixmap(font1_file, text, size=(450, 100))
            if pixmap:
                self.font1Preview = ImageLabel(image=pixmap, parent=self.font1Card)
                self.font1Preview.setMinimumHeight(80)
                # Replace in layout
                layout = self.font1Card.layout()
                if layout.count() > 1:
                    old = layout.itemAt(1).widget()
                    if old:
                        layout.replaceWidget(old, self.font1Preview)
                        old.deleteLater()

        # Update Font 2
        self.font2NameLabel.setText(font2_name)
        font2_file = self._get_font_file(font2_name)
        if font2_file and os.path.exists(font2_file):
            pixmap = create_preview_pixmap(font2_file, text, size=(450, 100))
            if pixmap:
                self.font2Preview = ImageLabel(image=pixmap, parent=self.font2Card)
                self.font2Preview.setMinimumHeight(80)
                # Replace in layout
                layout = self.font2Card.layout()
                if layout.count() > 1:
                    old = layout.itemAt(1).widget()
                    if old:
                        layout.replaceWidget(old, self.font2Preview)
                        old.deleteLater()
