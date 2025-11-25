import os
import sys
import json
import locale

# --- Constants ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, 'bin')
FONT_TOOL = os.path.join(BIN_DIR, 'font_tool.exe')
SYSTEM_OPS = os.path.join(BIN_DIR, 'SystemOps.ps1')

# --- Settings ---
SETTINGS = {
    "theme": "System",
    "auto_restart": False,
    "language": "System",
    "animated_bg": True
}

# --- Translations ---
LOCALES_DIR = os.path.join(BASE_DIR, "locales")
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

# Settings file path
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

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
