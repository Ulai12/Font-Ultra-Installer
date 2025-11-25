import os
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel, CardWidget, 
    ScrollArea, ComboBox, PushButton, FluentIcon as FIF
)

from config import tr
from core import get_installed_fonts, analyze_font

class FontPairingPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FontPairingPage")
        self.setStyleSheet("FontPairingPage { background: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)
        
        # Header
        self.titleLabel = TitleLabel("🤝 Font Pairing Assistant", self)
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.descLabel = BodyLabel("Trouvez la police parfaite pour accompagner votre sélection", self)
        self.vBoxLayout.addWidget(self.descLabel)
        
        # Font Selector
        selectorLayout = QHBoxLayout()
        selectorLayout.addWidget(SubtitleLabel("Police principale:", self))
        self.fontCombo = ComboBox(self)
        selectorLayout.addWidget(self.fontCombo)
        
        self.btnSuggest = PushButton(FIF.ROBOT, "Suggérer des paires", self)
        self.btnSuggest.clicked.connect(self.suggest_pairings)
        selectorLayout.addWidget(self.btnSuggest)
        
        self.vBoxLayout.addLayout(selectorLayout)
        
        # Suggestions Area
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background: transparent;")
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setSpacing(15)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)
        
        # Load fonts
        self.load_fonts()
        
    def load_fonts(self):
        """Load installed fonts"""
        fonts = get_installed_fonts()
        self.font_paths = fonts
        font_names = [os.path.splitext(os.path.basename(f))[0] for f in fonts[:100]]
        self.fontCombo.addItems(font_names)
        
    def suggest_pairings(self):
        """Suggest font pairings based on simple rules"""
        # Clear previous suggestions
        while self.scrollLayout.count():
            child = self.scrollLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        primary_font = self.fontCombo.currentText()
        
        # Simple AI-like algorithm based on font characteristics
        suggestions = self.find_compatible_fonts(primary_font)
        
        for i, (font_name, reason) in enumerate(suggestions[:5]):
            card = self.create_pairing_card(primary_font, font_name, reason, i+1)
            self.scrollLayout.addWidget(card)
    
    def find_compatible_fonts(self, primary_font):
        """Simple algorithm to find compatible fonts"""
        suggestions = []
        
        # Categorize primary font
        is_serif = any(keyword in primary_font.lower() for keyword in ['serif', 'times', 'garamond', 'baskerville'])
        is_mono = any(keyword in primary_font.lower() for keyword in ['mono', 'courier', 'console', 'code'])
        is_script = any(keyword in primary_font.lower() for keyword in ['script', 'cursive', 'hand'])
        
        # Get all fonts
        all_fonts = [os.path.splitext(os.path.basename(f))[0] for f in self.font_paths]
        
        # Rule 1: Pair Serif with Sans-Serif
        if is_serif:
            for font in all_fonts:
                if 'sans' in font.lower() and font != primary_font:
                    suggestions.append((font, "Contraste Serif/Sans-Serif classique"))
                    if len(suggestions) >= 10:
                        break
        
        # Rule 2: Pair Sans with Serif
        elif not is_serif and not is_mono and not is_script:
            for font in all_fonts:
                if any(kw in font.lower() for kw in ['serif', 'times', 'garamond']) and 'sans' not in font.lower():
                    suggestions.append((font, "Équilibre moderne/traditionnel"))
                    if len(suggestions) >= 10:
                        break
        
        # Rule 3: Monospace pairs with anything clean
        if is_mono:
            for font in all_fonts:
                if 'sans' in font.lower() and font != primary_font:
                    suggestions.append((font, "Clarté code/interface"))
                    if len(suggestions) >= 10:
                        break
        
        # Rule 4: Add some random popular pairings
        popular = ['Arial', 'Helvetica', 'Georgia', 'Verdana', 'Calibri']
        for font in popular:
            if font in all_fonts and font != primary_font and font not in [s[0] for s in suggestions]:
                suggestions.append((font, "Choix populaire et lisible"))
        
        # Shuffle and return
        random.shuffle(suggestions)
        return suggestions[:5] if suggestions else [(all_fonts[0], "Suggestion aléatoire")]
    
    def create_pairing_card(self, primary, secondary, reason, rank):
        """Create a pairing suggestion card"""
        card = CardWidget(self)
        card.setStyleSheet("""
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
            CardWidget:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Rank
        rankLabel = CaptionLabel(f"#{rank} · {reason}", self)
        rankLabel.setTextColor(QColor("#00CC6A"), QColor("#00CC6A"))
        layout.addWidget(rankLabel)
        
        # Primary Font
        primaryLabel = BodyLabel(f"Titre: {primary}", self)
        layout.addWidget(primaryLabel)
        
        primaryPreview = SubtitleLabel("The Quick Brown Fox", self)
        primaryPreview.setFont(QFont(primary, 16))
        layout.addWidget(primaryPreview)
        
        # Secondary Font
        secondaryLabel = BodyLabel(f"Corps: {secondary}", self)
        layout.addWidget(secondaryLabel)
        
        secondaryPreview = BodyLabel("Lorem ipsum dolor sit amet, consectetur adipiscing elit.", self)
        secondaryPreview.setFont(QFont(secondary, 12))
        secondaryPreview.setWordWrap(True)
        layout.addWidget(secondaryPreview)
        
        return card
