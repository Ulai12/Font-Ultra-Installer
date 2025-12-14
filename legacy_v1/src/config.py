import os
import sys
import json
import locale

# --- Gestion des ressources PyInstaller ---
# Quand l'application est compilée avec PyInstaller, les ressources sont
# extraites dans un répertoire temporaire stocké dans sys._MEIPASS.
# Cette fonction permet de récupérer le bon chemin selon le contexte d'exécution.

def get_resource_base_dir():
    """
    Récupère le répertoire de base des ressources.

    En mode développement : retourne le répertoire parent du dossier src/
    En mode PyInstaller (.exe) : retourne sys._MEIPASS où les ressources sont extraites

    Returns:
        str: Chemin absolu vers le répertoire contenant les ressources (assets, locales, bin)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Mode PyInstaller : les ressources sont dans _MEIPASS
        return sys._MEIPASS
    else:
        # Mode développement : chemin relatif classique
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource(*path_parts):
    """
    Récupère le chemin absolu vers une ressource.

    Cette fonction gère automatiquement la différence entre :
    - Mode développement : ressources dans le répertoire du projet
    - Mode PyInstaller : ressources extraites dans sys._MEIPASS

    Args:
        *path_parts: Parties du chemin relatif (ex: 'assets', 'logo.png')

    Returns:
        str: Chemin absolu vers la ressource

    Exemple:
        get_resource('assets', 'logo.png')  -> 'C:/temp/_MEI123/assets/logo.png' (en .exe)
        get_resource('locales', 'fr.json')  -> 'D:/ULTRA FONT INSTALLER/locales/fr.json' (dev)
    """
    base = get_resource_base_dir()
    return os.path.join(base, *path_parts)

# --- Constants ---
# BASE_DIR pour les ressources (assets, locales, bin) - utilise _MEIPASS si frozen
BASE_DIR = get_resource_base_dir()

# Répertoire de l'application (pour les fichiers de configuration comme settings.json)
# Ce répertoire reste le répertoire d'exécution, pas _MEIPASS
if getattr(sys, 'frozen', False):
    # En mode .exe, utiliser le répertoire où se trouve l'exécutable
    APP_DIR = os.path.dirname(sys.executable)
else:
    # En mode développement, utiliser le répertoire du projet
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = get_resource('bin')
FONT_TOOL = get_resource('bin', 'font_tool.exe')
SYSTEM_OPS = get_resource('bin', 'SystemOps.ps1')
BOWLBY_FONT_PATH = get_resource('assets', 'Fonts', 'Bowlby_One_SC', 'BowlbyOneSC-Regular.ttf')

# --- Settings ---
SETTINGS = {
    "theme": "System",
    "auto_restart": False,
    "language": "System",
    "animated_bg": True,
    "transparency": "Mica"
}

# --- Translations ---
# Les traductions sont des ressources empaquetées avec l'application
LOCALES_DIR = get_resource("locales")
TRANSLATIONS = {}

def load_translations():
    """Load translations from JSON files"""
    global TRANSLATIONS
    for lang in ["fr", "en"]:
        locale_file = os.path.join(LOCALES_DIR, f"{lang}.json")
        if os.path.exists(locale_file):
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    TRANSLATIONS[lang] = json.load(f)
            except Exception as e:
                print(f"Failed to load {lang} translations: {e}")
                TRANSLATIONS[lang] = {}
        else:
            TRANSLATIONS[lang] = {}

# Load translations on module import
load_translations()

GOOGLE_FONTS = [
    {"family": "Roboto", "url": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"},
    {"family": "Open Sans", "url": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf"},
    {"family": "Lato", "url": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf"},
    {"family": "Montserrat", "url": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf"},
    {"family": "Oswald", "url": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Regular.ttf"},
    {"family": "Raleway", "url": "https://github.com/google/fonts/raw/main/ofl/raleway/Raleway-Regular.ttf"},
    {"family": "Poppins", "url": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"},
    {"family": "Nunito", "url": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito-Regular.ttf"},
    {"family": "Ubuntu", "url": "https://github.com/google/fonts/raw/main/ufl/ubuntu/Ubuntu-Regular.ttf"},
    {"family": "Playfair Display", "url": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf"},
]

def tr(key):
    """Translate a key based on current language setting"""
    lang = SETTINGS.get("language", "System")
    if lang == "System":
        sys_lang = locale.getdefaultlocale()[0]
        lang = "fr" if sys_lang and sys_lang.startswith("fr") else "en"

    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# Chemin du fichier de paramètres - utilise APP_DIR pour être à côté de l'exécutable
# (et non dans _MEIPASS qui est temporaire et supprimé après exécution)
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

def save_settings():
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(SETTINGS, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save settings: {e}")

def load_settings():
    """Load settings from JSON file"""
    global SETTINGS
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                SETTINGS.update(loaded)
    except Exception as e:
        print(f"Failed to load settings: {e}")

# Load settings on module import
load_settings()
