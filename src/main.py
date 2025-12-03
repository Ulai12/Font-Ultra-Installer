import sys
import os

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsOpacityEffect
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    Theme, setTheme, setThemeColor, isDarkTheme
)

from config import tr, BASE_DIR, SETTINGS
from core import is_admin, run_as_admin
from ui import (
    HomePage, LibraryPage, GoogleFontsPage, SettingsPage, AboutPage,
    GlyphInspectorPage, TypewriterPage, VersusComparerPage, SplashScreen
)
# from ui.pairing import FontPairingPage

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        if not is_admin():
            run_as_admin()
            sys.exit()

        self.setWindowTitle(tr("window_title"))
        self.resize(1000, 600)

        # Set window icon
        logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Center window on screen
        self.moveToCenter()

        # --- Liquid Glass Background ---
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Opacity effect for animation
        self.bg_opacity = QGraphicsOpacityEffect()
        self.bg_label.setGraphicsEffect(self.bg_opacity)
        self.bg_opacity.setOpacity(1.0)

        # Load initial background
        self.update_background()

        # Animation setup
        if SETTINGS["animated_bg"]:
            self.anim_timer = QTimer(self)
            self.anim_timer.timeout.connect(self.animate_background)
            self.anim_timer.start(3000)  # Animate every 3 seconds
            self.anim_timer.start(3000)  # Animate every 3 seconds
            self.anim_value = 0

        # Load custom fonts FIRST
        self.load_custom_fonts()

        # Apply initial transparency settings
        self.set_transparency(SETTINGS.get("transparency", "Mica"))

        # Create and setup splash screen as overlay widget
        self.splash = SplashScreen(self)
        self.splash.setGeometry(self.geometry())
        self.splash.raise_()
        self.splash.start_animation()

        # Set System Accent Color BEFORE creating interfaces
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            value, _ = winreg.QueryValueEx(key, "AccentColor")
            r = value & 0xFF
            g = (value >> 8) & 0xFF
            b = (value >> 16) & 0xFF
            accent_color = f"#{r:02x}{g:02x}{b:02x}"
            setThemeColor(accent_color)
        except Exception:
            pass

        self.update_glass_style()

        # NOW create interfaces AFTER fonts are loaded and stylesheet is applied
        self.homeInterface = HomePage(self)
        self.libraryInterface = LibraryPage(self)
        self.googleFontsInterface = GoogleFontsPage(self)
        self.inspectorInterface = GlyphInspectorPage(self)
        self.typewriterInterface = TypewriterPage(self)
        self.comparerInterface = VersusComparerPage(self)
        # self.pairingInterface = FontPairingPage(self)
        self.settingsInterface = SettingsPage(self)
        self.aboutInterface = AboutPage(self)

        self.addSubInterface(self.homeInterface, FIF.HOME, tr("home"))
        self.addSubInterface(self.libraryInterface, FIF.LIBRARY, tr("library"))
        self.addSubInterface(self.googleFontsInterface, FIF.SHOPPING_CART, tr("store"))
        self.addSubInterface(self.inspectorInterface, FIF.SEARCH, tr("inspector"))
        self.addSubInterface(self.typewriterInterface, FIF.EDIT, tr("type writer"))
        self.addSubInterface(self.comparerInterface, FIF.VIEW, tr("versus"))
        # self.addSubInterface(self.pairingInterface, FIF.PALETTE, tr("pairing"))

        self.addSubInterface(self.settingsInterface, FIF.SETTING, tr("settings"), NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.aboutInterface, FIF.INFO, tr("about"), NavigationItemPosition.BOTTOM)

        # Show main window
        self.show()

        # Start splash animation after window is shown
        QTimer.singleShot(100, self.splash.start_animation)
        QTimer.singleShot(2500, self.splash.finish)

    def load_custom_fonts(self):
        """Charger toutes les polices personnalisées depuis assets"""
        self.fonts = {
            "Title": "Segoe UI",
            "Subtitle": "Segoe UI",
            "Body": "Segoe UI",
            "Mono": "Consolas"
        }

        assets_dir = os.path.join(BASE_DIR, "assets")

        def find_font_path(filename):
            for root, dirs, files in os.walk(assets_dir):
                if filename in files:
                    return os.path.join(root, filename)
            return None

        # Map font types to filenames
        font_files = {
            "Title": "BowlbyOneSC-Regular.ttf",
            "Subtitle": "AvenirLTStd-Black.otf",
            "Body": "AvenirLTStd-Roman.otf",
            "Mono": "Inconsolata-Regular.ttf"
        }

        for key, filename in font_files.items():
            path = find_font_path(filename)
            if path and os.path.exists(path):
                font_id = QFontDatabase.addApplicationFont(path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.fonts[key] = families[0]
                        print(f"Police {key} chargée: {families[0]} depuis {path}")
            else:
                print(f"Fichier de police non trouvé: {filename}")

    def update_background(self):
        """Mettre à jour l'image de fond en fonction du thème"""
        is_dark = isDarkTheme()
        bg_file = "liquid_bg_dark.png" if is_dark else "liquid_bg_light.png"
        bg_path = os.path.join(BASE_DIR, "assets", bg_file)

        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            self.bg_label.setPixmap(pixmap)

    def animate_background(self):
        """Smooth opacity animation for liquid effect"""
        self.anim_value = (self.anim_value + 1) % 2

        anim = QPropertyAnimation(self.bg_opacity, b"opacity")
        anim.setDuration(2000)
        anim.setStartValue(1.0 if self.anim_value == 0 else 0.95)
        anim.setEndValue(0.95 if self.anim_value == 0 else 1.0)
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.start()

        # Store animation to prevent garbage collection
        self.current_anim = anim

    def toggle_animation(self, enabled):
        """Enable or disable background animation"""
        SETTINGS["animated_bg"] = enabled
        if enabled:
            if not hasattr(self, 'anim_timer'):
                self.anim_timer = QTimer(self)
                self.anim_timer.timeout.connect(self.animate_background)
                self.anim_value = 0
            self.anim_timer.start(3000)
        else:
            if hasattr(self, 'anim_timer'):
                self.anim_timer.stop()
            self.bg_opacity.setOpacity(1.0)

    def show_message(self, title, content, duration=2000):
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.info(title, content, duration=duration, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def show_success(self, content):
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(tr("success_title"), content, duration=2000, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def show_error(self, content):
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.error("Error", content, duration=3000, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def moveToCenter(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def set_transparency(self, mode):
        """Set window transparency effect"""

        if mode == "Mica":
            if sys.getwindowsversion().build >= 22000:
                self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
                self.bg_label.hide()
                self.setStyleSheet("MainWindow { background: transparent; }")
            else:
                print("Mica effect is only available on Windows 11. Falling back to Aero.")
                self.set_transparency("Aero")
                return
        elif mode == "Acrylic":
            self.windowEffect.setAcrylicEffect(self.winId(), "101010" if isDarkTheme() else "F2F2F2")
            self.bg_label.hide()
            self.setStyleSheet("MainWindow { background: transparent; }")
        elif mode == "Aero":
            self.windowEffect.setAeroEffect(self.winId())
            self.bg_label.hide()
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setStyleSheet("MainWindow { background: transparent; }")
        else:
            # None - Restore Liquid Glass
            self.windowEffect.removeBackgroundEffect(self.winId())
            self.bg_label.show()
            self.update_background()
            # Reset stylesheet to default if needed, or just let bg_label cover it
            self.setStyleSheet("")
            self.update_glass_style()

    def update_glass_style(self):
        # Dynamic Glass Stylesheet
        is_dark = isDarkTheme()

        # Custom Colors
        dark_base = "#0d0c07"
        light_base = "#fffce1"

        if is_dark:
            text_color = light_base
            nav_bg = "rgba(13, 12, 7, 0.85)"
            popup_bg = "rgba(13, 12, 7, 0.95)"
            combo_bg = "rgba(255, 255, 255, 0.05)"
            combo_border = "rgba(255, 255, 255, 0.1)"
            item_hover = "rgba(255, 255, 255, 0.1)"
            nav_border = "rgba(255, 255, 255, 0.05)"
        else:
            text_color = dark_base
            nav_bg = "rgba(255, 252, 225, 0.85)"
            popup_bg = "rgba(255, 252, 225, 0.95)"
            combo_bg = "rgba(255, 255, 255, 0.5)"
            combo_border = "rgba(0, 0, 0, 0.1)"
            item_hover = "rgba(0, 0, 0, 0.05)"
            nav_border = "rgba(0, 0, 0, 0.05)"

        glass_style = f"""
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}

            /* Title Font - Bowlby One SC */
            TitleLabel {{
                font-family: "{self.fonts['Title']}";
                font-size: 36px;
                font-weight: 900;
                letter-spacing: 1px;
            }}

            /* Subtitle Font - Avenir */
            SubtitleLabel, StrongBodyLabel {{
                font-family: "{self.fonts['Subtitle']}";
                font-weight: bold;
            }}

            /* Body Font - Avenir */
            BodyLabel, CaptionLabel, QLabel, QPushButton, QLineEdit {{
                font-family: "{self.fonts['Body']}";
            }}

            NavigationInterface, NavigationWidget {{
                background-color: {nav_bg};
                border: none;
            }}

            /* ComboBox Glass Effect */
            QComboBox {{
                background-color: {combo_bg};
                border: 1px solid {combo_border};
                border-radius: 6px;
                padding: 4px 10px;
                color: {text_color};
            }}
            QComboBox:hover {{
                background-color: {item_hover};
                border: 1px solid {combo_border};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                background: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {popup_bg};
                border: 1px solid {combo_border};
                border-radius: 8px;
                padding: 4px;
                outline: none;
                color: {text_color};
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px;
                border-radius: 4px;
                color: {text_color};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {item_hover};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {item_hover};
            }}
        """
        self.setStyleSheet(glass_style)

if __name__ == '__main__':
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
