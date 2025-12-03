import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QFont, QFontDatabase
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    CardWidget, IconWidget, ImageLabel, PushButton, PrimaryPushButton, ToolButton,
    ScrollArea, ProgressBar, SearchLineEdit, LineEdit, ComboBox, SwitchButton,
    MessageBox, InfoBar, InfoBarPosition, Theme, setTheme, FluentIcon as FIF
)

from config import tr, SETTINGS, GOOGLE_FONTS, BASE_DIR, BOWLBY_FONT_PATH
from core import (
    AnalyzeWorker, InstallWorker, LoadLibraryWorker, DownloadWorker, GoogleFontsWorker,
    uninstall_font_system, restart_explorer, install_font_system, extract_archive
)
from ui.components import FontCard, LibraryCard, GoogleFontCard

def _apply_bowlby_font(label):
    """Apply Bowlby One SC font to a title label via stylesheet"""
    if os.path.exists(BOWLBY_FONT_PATH):
        QFontDatabase.addApplicationFont(BOWLBY_FONT_PATH)
        label.setStyleSheet("font-family: 'Bowlby One SC'; font-size: 32px;")

class HomePage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        self.setStyleSheet("HomePage { background: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(tr("window_title").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        self.dropArea = CardWidget(self)
        self.dropArea.setFixedHeight(120)
        self.dropArea.setAcceptDrops(True)
        self.dropArea.setStyleSheet("""
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 12px;
            }
            CardWidget:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px dashed rgba(255, 255, 255, 0.5);
            }
        """)
        dropLayout = QVBoxLayout(self.dropArea)

        self.dropIcon = IconWidget(FIF.DOWNLOAD, self.dropArea)
        self.dropIcon.setFixedSize(32, 32)
        dropLayout.addWidget(self.dropIcon, 0, Qt.AlignCenter)

        self.dropLabel = SubtitleLabel(tr("drag_drop"), self.dropArea)
        dropLayout.addWidget(self.dropLabel, 0, Qt.AlignCenter)

        self.vBoxLayout.addWidget(self.dropArea)

        actionLayout = QHBoxLayout()
        self.btnAddFiles = PushButton(FIF.ADD, tr("add_files"), self)
        self.btnAddFiles.clicked.connect(self.add_files)
        actionLayout.addWidget(self.btnAddFiles)

        self.btnAddFolder = PushButton(FIF.FOLDER, tr("add_folder"), self)
        self.btnAddFolder.clicked.connect(self.add_folder)
        actionLayout.addWidget(self.btnAddFolder)

        self.btnClear = PushButton(FIF.DELETE, tr("clear_list"), self)
        self.btnClear.clicked.connect(self.clear_list)
        actionLayout.addWidget(self.btnClear)

        self.btnRefresh = PushButton(FIF.SYNC, tr("refresh"), self)
        self.btnRefresh.clicked.connect(self.clear_list)
        actionLayout.addWidget(self.btnRefresh)

        actionLayout.addStretch(1)

        self.btnInstall = PrimaryPushButton(FIF.SAVE, tr("install_all"), self)
        self.btnInstall.clicked.connect(self.install_fonts)
        actionLayout.addWidget(self.btnInstall)

        self.vBoxLayout.addLayout(actionLayout)

        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background-color: transparent; border: none;")
        self.scrollContent = QWidget()
        self.scrollContent.setStyleSheet("background-color: transparent;")
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(10)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.scrollContent)

        self.vBoxLayout.addWidget(self.scrollArea)

        self.progressBar = ProgressBar(self)
        self.progressBar.hide()
        self.vBoxLayout.addWidget(self.progressBar)

        self.fonts = []
        self.cards = {}
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.process_files(files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Fonts", "", "Fonts & Archives (*.ttf *.otf *.woff *.ttc *.zip)")
        if files:
            self.process_files(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith(('.ttf', '.otf', '.woff', '.ttc')):
                        files.append(os.path.join(root, filename))
            self.process_files(files)

    def process_files(self, files):
        processed_files = []

        for file_path in files:
            if file_path.lower().endswith('.zip'):
                # Extract archive
                extract_dir = extract_archive(file_path)
                if extract_dir:
                    for root, _, filenames in os.walk(extract_dir):
                        for filename in filenames:
                            if filename.lower().endswith(('.ttf', '.otf', '.woff', '.ttc')):
                                processed_files.append(os.path.join(root, filename))
            elif file_path.lower().endswith(('.ttf', '.otf', '.woff', '.ttc')):
                processed_files.append(file_path)

        new_files = [f for f in processed_files if f not in [x['path'] for x in self.fonts]]
        if not new_files: return

        self.worker = AnalyzeWorker(new_files)
        self.worker.font_analyzed.connect(self.add_font_card)
        self.worker.start()

    def add_font_card(self, font_data):
        """Add a font card to the list with error handling"""
        try:
            if not font_data or 'path' not in font_data:
                return

            self.fonts.append(font_data)
            card = FontCard(font_data)
            self.scrollLayout.addWidget(card)
            self.cards[font_data['path']] = card
            card.setVisible(True)
        except Exception as e:
            # Silently skip errors
            pass

    def clear_list(self):
        for i in reversed(range(self.scrollLayout.count())):
            self.scrollLayout.itemAt(i).widget().setParent(None)
        self.fonts.clear()
        self.cards.clear()

    def install_fonts(self):
        if not self.fonts: return

        self.progressBar.setValue(0)
        self.progressBar.show()
        self.btnInstall.setDisabled(True)

        self.install_worker = InstallWorker(self.fonts)
        self.install_worker.progress.connect(self.update_progress)
        self.install_worker.item_updated.connect(self.update_card_status)
        self.install_worker.finished.connect(self.install_finished)
        self.install_worker.start()

    def update_progress(self, current, total, filename):
        val = int((current / total) * 100)
        self.progressBar.setValue(val)

    def update_card_status(self, path, success):
        if path in self.cards:
            self.cards[path].set_status(success)

    def install_finished(self, count):
        self.progressBar.setValue(100)
        self.btnInstall.setDisabled(False)
        InfoBar.success(
            title=tr("success_title"),
            content=tr("success_msg").format(count),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )
        if SETTINGS["auto_restart"]:
            restart_explorer()

class LibraryPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LibraryPage")
        self.setStyleSheet("LibraryPage { background: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(tr("library").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        # Toolbar
        toolLayout = QHBoxLayout()
        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText(tr("search_fonts"))
        self.searchBox.textChanged.connect(self.filter_list)
        toolLayout.addWidget(self.searchBox)

        self.previewBox = LineEdit(self)
        self.previewBox.setPlaceholderText(tr("preview_text"))
        self.previewBox.textChanged.connect(self.update_previews)
        toolLayout.addWidget(self.previewBox)

        self.btnRefresh = ToolButton(FIF.SYNC, self)
        self.btnRefresh.clicked.connect(self.load_fonts)
        toolLayout.addWidget(self.btnRefresh)

        self.vBoxLayout.addLayout(toolLayout)

        # List
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background-color: transparent; border: none;")
        self.scrollContent = QWidget()
        self.scrollContent.setStyleSheet("background-color: transparent;")
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(10)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.scrollContent)

        self.vBoxLayout.addWidget(self.scrollArea)

        self.font_cards = []

        self.load_fonts()

    def load_fonts(self):
        for i in reversed(range(self.scrollLayout.count())):
            self.scrollLayout.itemAt(i).widget().setParent(None)
        self.font_cards.clear()

        self.worker = LoadLibraryWorker()
        self.worker.font_found.connect(self.add_font_item)
        self.worker.start()

    def add_font_item(self, file_path):
        card = LibraryCard(file_path)
        card.uninstall_requested.connect(self.uninstall_font)
        self.scrollLayout.addWidget(card)
        self.font_cards.append((os.path.basename(file_path).lower(), card))

    def filter_list(self, text):
        text = text.lower()
        for name, card in self.font_cards:
            if text in name: card.show()
            else: card.hide()

    def update_previews(self, text):
        for _, card in self.font_cards:
            if card.isVisible():
                card.update_preview(text)

    def uninstall_font(self, file_path):
        name = os.path.basename(file_path)
        w = MessageBox(tr("uninstall"), tr("uninstall_confirm").format(name), self)
        if w.exec():
            if uninstall_font_system(name):
                InfoBar.success(tr("success_title"), tr("uninstall_success"), duration=3000, parent=self)
                self.load_fonts()
            else:
                InfoBar.error("Error", "Failed to uninstall font.", duration=3000, parent=self)

class GoogleFontsPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GoogleFontsPage")
        self.setStyleSheet("GoogleFontsPage { background: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)

        self.titleLabel = TitleLabel(tr("store").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        # Toolbar
        toolLayout = QHBoxLayout()
        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText(tr("search_fonts"))
        self.searchBox.textChanged.connect(self.filter_list)
        toolLayout.addWidget(self.searchBox)

        self.btnRefresh = ToolButton(FIF.SYNC, self)
        self.btnRefresh.clicked.connect(self.load_fonts)
        toolLayout.addWidget(self.btnRefresh)

        self.vBoxLayout.addLayout(toolLayout)

        # List
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background-color: transparent; border: none;")
        self.scrollContent = QWidget()
        self.scrollContent.setStyleSheet("background-color: transparent;")
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(10)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.scrollContent)

        self.vBoxLayout.addWidget(self.scrollArea)

        self.font_cards = []
        self.download_workers = {}

        self.load_fonts()

    def load_fonts(self):
        for i in reversed(range(self.scrollLayout.count())):
            self.scrollLayout.itemAt(i).widget().setParent(None)
        self.font_cards.clear()

        self.worker = GoogleFontsWorker()
        self.worker.font_found.connect(self.add_font_card)
        self.worker.start()

    def add_font_card(self, font_data):
        card = GoogleFontCard(font_data)
        card.download_requested.connect(self.download_font)
        self.scrollLayout.addWidget(card)
        self.font_cards.append((font_data['family'].lower(), card))

    def filter_list(self, text):
        text = text.lower()
        for name, card in self.font_cards:
            if text in name: card.show()
            else: card.hide()

    def download_font(self, family, style):
        """Download and install a font from Google Fonts"""
        # Find the font data
        url = None
        for name, card in self.font_cards:
            if card.font_info.get('family') == family:
                url = card.font_info.get('url')
                break

        if url:
            filename = f"{family.replace(' ', '_')}.ttf"
            worker = DownloadWorker(url, filename)
            worker.finished.connect(lambda u, path: self.on_download_finished(u, path, family))
            worker.start()
            self.download_workers[family] = worker

    def on_download_finished(self, url, local_path, family):
        """Handle downloaded font"""
        # Find the card that requested this download
        for name, card in self.font_cards:
            if card.font_info.get('family') == family:
                if local_path and os.path.exists(local_path):
                    card.on_download_finished(local_path)

                    # Auto-install the downloaded font
                    try:
                        success = install_font_system(local_path)
                        if success:
                            from qfluentwidgets import InfoBar, InfoBarPosition
                            InfoBar.success(
                                tr("success_title"),
                                f"Police {family} installée avec succès",
                                duration=3000,
                                position=InfoBarPosition.TOP_RIGHT,
                                parent=self
                            )
                        else:
                            from qfluentwidgets import InfoBar, InfoBarPosition
                            InfoBar.error(
                                "Erreur",
                                f"Échec de l'installation de {family}",
                                duration=3000,
                                position=InfoBarPosition.TOP_RIGHT,
                                parent=self
                            )
                    except Exception as e:
                        from qfluentwidgets import InfoBar, InfoBarPosition
                        InfoBar.error(
                            "Erreur",
                            f"Erreur: {str(e)}",
                            duration=3000,
                            position=InfoBarPosition.TOP_RIGHT,
                            parent=self
                        )
                else:
                    card.on_download_finished(None)
                break

class SettingsPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self.setStyleSheet("""
            SettingsPage { background: transparent; }
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.titleLabel = TitleLabel(tr("settings").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        # Theme
        self.themeCard = CardWidget(self)
        themeLayout = QHBoxLayout(self.themeCard)
        themeLayout.setContentsMargins(16, 16, 16, 16)

        themeInfo = QVBoxLayout()
        themeInfo.addWidget(SubtitleLabel(tr("app_theme"), self))
        themeInfo.addWidget(CaptionLabel(tr("change_appearance"), self))
        themeLayout.addLayout(themeInfo)

        self.themeCombo = ComboBox(self)
        self.themeCombo.addItems(["System", "Light", "Dark"])
        self.themeCombo.setCurrentText(SETTINGS["theme"])
        self.themeCombo.currentTextChanged.connect(self.change_theme)
        themeLayout.addWidget(self.themeCombo)

        self.vBoxLayout.addWidget(self.themeCard)

        # Language
        self.langCard = CardWidget(self)
        langLayout = QHBoxLayout(self.langCard)
        langLayout.setContentsMargins(16, 16, 16, 16)

        langInfo = QVBoxLayout()
        langInfo.addWidget(SubtitleLabel(tr("language"), self))
        langInfo.addWidget(CaptionLabel(tr("change_lang"), self))
        langLayout.addLayout(langInfo)

        self.langCombo = ComboBox(self)
        self.langCombo.addItems(["System", "en", "fr"])
        self.langCombo.setCurrentText(SETTINGS["language"])
        self.langCombo.currentTextChanged.connect(self.change_lang)
        langLayout.addWidget(self.langCombo)

        self.vBoxLayout.addWidget(self.langCard)

        # Auto Restart
        self.restartCard = CardWidget(self)
        restartLayout = QHBoxLayout(self.restartCard)
        restartLayout.setContentsMargins(16, 16, 16, 16)

        restartInfo = QVBoxLayout()
        restartInfo.addWidget(SubtitleLabel(tr("auto_restart"), self))
        restartInfo.addWidget(CaptionLabel(tr("restart_desc"), self))
        restartLayout.addLayout(restartInfo)

        self.restartSwitch = SwitchButton(self)
        self.restartSwitch.setChecked(SETTINGS["auto_restart"])
        self.restartSwitch.checkedChanged.connect(self.toggle_restart)
        restartLayout.addWidget(self.restartSwitch)

        self.vBoxLayout.addWidget(self.restartCard)

        # Animated Background
        self.animBgCard = CardWidget(self)
        animBgLayout = QHBoxLayout(self.animBgCard)
        animBgLayout.setContentsMargins(16, 16, 16, 16)

        animBgInfo = QVBoxLayout()
        animBgInfo.addWidget(SubtitleLabel(tr("animated_bg"), self))
        animBgInfo.addWidget(CaptionLabel(tr("animated_bg_desc"), self))
        animBgLayout.addLayout(animBgInfo)

        self.animBgSwitch = SwitchButton(self)
        self.animBgSwitch.setChecked(SETTINGS["animated_bg"])
        self.animBgSwitch.checkedChanged.connect(self.toggle_animation)
        animBgLayout.addWidget(self.animBgSwitch)

        self.vBoxLayout.addWidget(self.animBgCard)

        # Transparency
        self.transparencyCard = CardWidget(self)
        transparencyLayout = QHBoxLayout(self.transparencyCard)
        transparencyLayout.setContentsMargins(16, 16, 16, 16)

        transparencyInfo = QVBoxLayout()
        transparencyInfo.addWidget(SubtitleLabel(tr("window_effect"), self))
        transparencyInfo.addWidget(CaptionLabel(tr("window_effect_desc"), self))
        transparencyLayout.addLayout(transparencyInfo)

        self.transparencyCombo = ComboBox(self)
        self.transparencyCombo.addItems(["None", "Mica", "Acrylic", "Aero"])
        self.transparencyCombo.setCurrentText(SETTINGS.get("transparency", "Mica"))
        self.transparencyCombo.currentTextChanged.connect(self.change_transparency)
        transparencyLayout.addWidget(self.transparencyCombo)

        self.vBoxLayout.addWidget(self.transparencyCard)

    def change_theme(self, text):
        from config import save_settings
        SETTINGS["theme"] = text
        save_settings()

        if text == "System":
            setTheme(Theme.AUTO)
        elif text == "Light":
            setTheme(Theme.LIGHT)
        elif text == "Dark":
            setTheme(Theme.DARK)

        # Update background when theme changes
        if hasattr(self.window(), 'update_background'):
            self.window().update_background()

    def change_lang(self, text):
        from config import save_settings
        SETTINGS["language"] = text
        save_settings()
        InfoBar.info(
            title="Restart Required",
            content="Please restart the application to apply language changes.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )

    def toggle_restart(self, checked):
        from config import save_settings
        SETTINGS["auto_restart"] = checked
        save_settings()

    def toggle_animation(self, checked):
        """Toggle background animation"""
        from config import save_settings
        SETTINGS["animated_bg"] = checked
        save_settings()
        if hasattr(self.window(), 'toggle_animation'):
            self.window().toggle_animation(checked)

    def change_transparency(self, text):
        """Change window transparency effect"""
        from config import save_settings
        SETTINGS["transparency"] = text
        save_settings()
        if hasattr(self.window(), 'set_transparency'):
            self.window().set_transparency(text)

class AboutPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AboutPage")
        self.setStyleSheet("""
            AboutPage { background: transparent; }
            CardWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.titleLabel = TitleLabel(tr("about").upper(), self)
        _apply_bowlby_font(self.titleLabel)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)

        self.card = CardWidget(self)
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        logo = ImageLabel(os.path.join(BASE_DIR, "FontUltraInstaller.ico")) if os.path.exists("FontUltraInstaller.ico") else None
        if logo:
            logo.setFixedSize(64, 64)
            layout.addWidget(logo, 0, Qt.AlignCenter)

        layout.addWidget(SubtitleLabel(tr("window_title"), self), 0, Qt.AlignCenter)
        layout.addWidget(BodyLabel(tr("version"), self), 0, Qt.AlignCenter)
        layout.addWidget(BodyLabel(tr("credits"), self), 0, Qt.AlignCenter)
        layout.addWidget(CaptionLabel(tr("about_desc"), self), 0, Qt.AlignCenter)

        self.vBoxLayout.addWidget(self.card)
