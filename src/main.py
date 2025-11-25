import sys
import os

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsOpacityEffect
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    Theme, setTheme, setThemeColor, isDarkTheme
)

from config import tr, BASE_DIR, SETTINGS
from core import is_admin, run_as_admin
from ui.pages import HomePage, LibraryPage, GoogleFontsPage, SettingsPage, AboutPage
from ui.inspector import GlyphInspectorPage
from ui.typewriter import TypewriterPage
from ui.comparer import VersusComparerPage
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
            self.anim_value = 0

        # Global stylesheet for glass effects and scrollbars
        self.setStyleSheet("""
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

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
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            self.bg_label.setPixmap(pixmap)

        # Dynamic Glass Stylesheet
        text_color = "white" if is_dark else "black"
        combo_bg = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(255, 255, 255, 0.5)"
        combo_border = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)"
        popup_bg = "rgba(32, 32, 32, 0.95)" if is_dark else "rgba(240, 240, 240, 0.95)"
        item_hover = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.05)"
        nav_bg = "rgba(32, 32, 32, 0.8)" if is_dark else "rgba(240, 240, 240, 0.8)"
        nav_border = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(0, 0, 0, 0.05)"

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

            /* Navigation Menu Glass Effect */
            NavigationPanel {{
                background-color: {nav_bg};
                border-right: 1px solid {nav_border};
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):
            self.bg_label.setGeometry(0, 0, self.width(), self.height())

if __name__ == '__main__':
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
