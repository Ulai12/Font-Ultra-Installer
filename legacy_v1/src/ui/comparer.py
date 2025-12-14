import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, CardWidget, ScrollArea,
    ComboBox, LineEdit, isDarkTheme
)

from config import tr, BOWLBY_FONT_PATH
from core import create_preview_pixmap


def _apply_bowlby_font(label):
    """Appliquer la police Bowlby One SC à un label de titre"""
    if os.path.exists(BOWLBY_FONT_PATH):
        QFontDatabase.addApplicationFont(BOWLBY_FONT_PATH)
        label.setStyleSheet("font-family: 'Bowlby One SC'; font-size: 32px;")


class VersusComparerPage(QFrame):
    """Page de comparaison de polices côte à côte"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VersusComparerPage")
        self.setStyleSheet("VersusComparerPage { background: transparent; }")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(24)

        # En-tête
        self.titleLabel = TitleLabel(tr("versus_comparer").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        self.descLabel = BodyLabel(tr("versus_desc"), self)
        self.descLabel.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.descLabel, 0, Qt.AlignCenter)

        # Zone de texte de prévisualisation
        previewCard = CardWidget(self)
        previewCard.setStyleSheet(self._card_style())
        previewLayout = QHBoxLayout(previewCard)
        previewLayout.setContentsMargins(16, 12, 16, 12)

        textLabel = SubtitleLabel(tr("text_label"), self)
        previewLayout.addWidget(textLabel)

        self.previewText = LineEdit(self)
        self.previewText.setText(tr("pangram"))
        self.previewText.setPlaceholderText("Entrez le texte à afficher...")
        self.previewText.textChanged.connect(self.update_comparison)
        previewLayout.addWidget(self.previewText, 1)

        self.vBoxLayout.addWidget(previewCard)

        # Zone de comparaison principale
        comparisonLayout = QHBoxLayout()
        comparisonLayout.setSpacing(20)

        # Carte Police 1
        self.font1Card = self._create_font_card("1")
        comparisonLayout.addWidget(self.font1Card, 1)

        # Séparateur VS
        vsContainer = QWidget()
        vsLayout = QVBoxLayout(vsContainer)
        vsLayout.setAlignment(Qt.AlignCenter)
        vsLabel = TitleLabel("VS", self)
        vsLabel.setStyleSheet("font-size: 28px; font-weight: bold; color: rgba(255, 255, 255, 0.5);")
        vsLayout.addWidget(vsLabel)
        comparisonLayout.addWidget(vsContainer)

        # Carte Police 2
        self.font2Card = self._create_font_card("2")
        comparisonLayout.addWidget(self.font2Card, 1)

        self.vBoxLayout.addLayout(comparisonLayout, 1)

        # Cache pour les chemins des polices
        self.font_cache = {}

        # Charger les polices
        self.load_fonts()

    def _card_style(self):
        """Style commun pour les cartes"""
        return """
            CardWidget {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
            }
        """

    def _create_font_card(self, num):
        """Créer une carte de prévisualisation de police"""
        card = CardWidget(self)
        card.setStyleSheet(self._card_style())
        card.setMinimumHeight(200)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Sélecteur de police
        combo = ComboBox(self)
        combo.setMinimumWidth(180)
        combo.currentTextChanged.connect(self.update_comparison)
        layout.addWidget(combo, 0, Qt.AlignCenter)

        # Nom de la police
        nameLabel = SubtitleLabel(f"Police {num}", self)
        nameLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(nameLabel, 0, Qt.AlignCenter)

        # Zone de prévisualisation
        previewLabel = QLabel(self)
        previewLabel.setMinimumHeight(100)
        previewLabel.setAlignment(Qt.AlignCenter)
        previewLabel.setStyleSheet("background: transparent;")
        layout.addWidget(previewLabel, 1)

        # Stocker les références
        if num == "1":
            self.font1Combo = combo
            self.font1NameLabel = nameLabel
            self.font1Preview = previewLabel
        else:
            self.font2Combo = combo
            self.font2NameLabel = nameLabel
            self.font2Preview = previewLabel

        return card

    def load_fonts(self):
        """Charger les polices installées dans les combo boxes"""
        font_names = sorted(QFontDatabase.families())

        self.font1Combo.addItems(font_names)
        self.font2Combo.addItems(font_names)

        # Sélectionner des polices différentes par défaut
        if len(font_names) > 1:
            self.font1Combo.setCurrentIndex(0)
            self.font2Combo.setCurrentIndex(1)

        self.update_comparison()

    def _get_font_file(self, font_name):
        """Obtenir le chemin du fichier de police avec cache"""
        if font_name in self.font_cache:
            return self.font_cache[font_name]

        fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        try:
            for filename in os.listdir(fonts_dir):
                if filename.lower().endswith(('.ttf', '.otf')):
                    full_path = os.path.join(fonts_dir, filename)
                    base_name = os.path.splitext(filename)[0].lower()
                    font_lower = font_name.lower().replace(' ', '')

                    if font_lower in base_name.replace(' ', '') or base_name.replace(' ', '') in font_lower:
                        self.font_cache[font_name] = full_path
                        return full_path
        except Exception as e:
            print(f"Erreur lors de la recherche de police: {e}")

        return None

    def update_comparison(self):
        """Mettre à jour les prévisualisations"""
        font1_name = self.font1Combo.currentText()
        font2_name = self.font2Combo.currentText()
        text = self.previewText.text() or tr("pangram")

        # Mettre à jour Police 1
        if font1_name:
            self.font1NameLabel.setText(font1_name)
            self._update_preview(self.font1Preview, font1_name, text)

        # Mettre à jour Police 2
        if font2_name:
            self.font2NameLabel.setText(font2_name)
            self._update_preview(self.font2Preview, font2_name, text)

    def _update_preview(self, preview_label, font_name, text):
        """Mettre à jour une prévisualisation individuelle"""
        font_file = self._get_font_file(font_name)

        if font_file and os.path.exists(font_file):
            # Utiliser create_preview_pixmap avec le fichier de police
            pixmap = create_preview_pixmap(font_file, text, size=(350, 100))
            if pixmap:
                preview_label.setPixmap(pixmap)
                preview_label.setScaledContents(False)
                return

        # Fallback: utiliser QFont directement
        preview_label.setText(text)
        font = QFont(font_name, 32)
        preview_label.setFont(font)

        # Couleur adaptée au thème
        text_color = "#ffffff" if isDarkTheme() else "#000000"
        preview_label.setStyleSheet(f"color: {text_color}; background: transparent;")
