import os
import sys
import json
import subprocess
import ctypes
import urllib.request
from PySide6.QtCore import QThread, Signal
from PIL import Image, ImageFont, ImageDraw, ImageQt
from qfluentwidgets import isDarkTheme

from config import BASE_DIR, BIN_DIR, FONT_TOOL, SYSTEM_OPS

# --- System Operations ---

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def validate_font(file_path):
    if not os.path.exists(FONT_TOOL):
        return file_path.lower().endswith(('.ttf', '.otf', '.woff'))
    try:
        result = subprocess.run([FONT_TOOL, "validate", file_path], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return result.returncode == 0
    except: return False

def analyze_font(file_path):
    if not os.path.exists(FONT_TOOL):
        return {"name": os.path.basename(file_path), "family": os.path.basename(file_path), "style": "Regular"}
    try:
        result = subprocess.run([FONT_TOOL, "analyze", file_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"name": os.path.basename(file_path), "error": "Analysis Error"}
    except Exception as e:
        return {"name": os.path.basename(file_path), "error": str(e)}

def is_font_installed(font_name):
    """Simple check if font file exists in Fonts directory"""
    try:
        fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        # Check various possible font file names
        base_name = font_name.replace(' ', '')
        possible_names = [
            font_name,
            f"{font_name}.ttf",
            f"{font_name}.otf",
            f"{base_name}.ttf",
            f"{base_name}.otf",
        ]
        
        for name in possible_names:
            if os.path.exists(os.path.join(fonts_dir, name)):
                return True
        return False
    except Exception as e:
        # If anything fails, assume not installed
        return False

def get_installed_fonts():
    fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    fonts = []
    try:
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith(('.ttf', '.otf', '.ttc')):
                fonts.append(os.path.join(fonts_dir, filename))
    except: pass
    return fonts

def install_font_system(file_path):
    success = False
    if os.path.exists(FONT_TOOL):
        try:
            res = subprocess.run([FONT_TOOL, "validate", file_path], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0: success = True
        except: pass
    
    font_name = os.path.basename(file_path)
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SYSTEM_OPS, "-Command", "register", "-FontPath", file_path, "-FontName", font_name]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if "SUCCESS" in res.stdout: success = True
    except: pass
    return success

def uninstall_font_system(file_name):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SYSTEM_OPS, "-Command", "unregister", "-FontPath", file_name]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return "SUCCESS" in res.stdout
    except: return False

def restart_explorer():
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SYSTEM_OPS, "-Command", "restart-explorer"]
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def create_preview_pixmap(file_path, text="Aa", size=(300, 64)):
    try:
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        try: font = ImageFont.truetype(file_path, 40)
        except: font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (size[0] - (bbox[2] - bbox[0])) / 2
        y = (size[1] - (bbox[3] - bbox[1])) / 2 - bbox[1]
        
        fill_color = (255, 255, 255, 255) if isDarkTheme() else (0, 0, 0, 255)
        draw.text((x, y), text, font=font, fill=fill_color) 
        
        return ImageQt.toqpixmap(image)
    except: return None

# --- Workers ---

class AnalyzeWorker(QThread):
    font_analyzed = Signal(object)  # Changed from dict to object for proper Python dict support

    def __init__(self, files):
        super().__init__()
        self.files = files


    def run(self):
        for file_path in self.files:
            try:
                # Validate file exists
                if not os.path.exists(file_path):
                    continue
                
                # Analyze font with error handling
                try:
                    data = analyze_font(file_path)
                except Exception as e:
                    data = {
                        'name': os.path.basename(file_path),
                        'family': os.path.basename(file_path).rsplit('.', 1)[0],
                        'style': 'Regular',
                        'error': str(e)
                    }
                
                data['path'] = file_path
                
                # Validate font
                try:
                    data['valid'] = validate_font(file_path)
                except Exception as e:
                    data['valid'] = False
                
                # Check if installed
                try:
                    data['installed'] = is_font_installed(data.get('family', os.path.basename(file_path)))
                except Exception as e:
                    data['installed'] = False
                
                data['metadata'] = data
                
                # Generate preview with error handling
                try:
                    data['preview_pixmap'] = create_preview_pixmap(file_path)
                except Exception as e:
                    data['preview_pixmap'] = None
                
                self.font_analyzed.emit(data)
                
            except Exception as e:
                # Emit error data if complete analysis fails
                error_data = {
                    'path': file_path,
                    'valid': False,
                    'installed': False,
                    'metadata': {
                        'name': os.path.basename(file_path),
                        'family': os.path.basename(file_path).rsplit('.', 1)[0] if '.' in os.path.basename(file_path) else os.path.basename(file_path),
                        'style': 'Unknown',
                        'error': str(e)
                    },
                    'error': str(e),
                    'preview_pixmap': None
                }
                self.font_analyzed.emit(error_data)

class InstallWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(int)
    item_updated = Signal(str, bool)

    def __init__(self, fonts):
        super().__init__()
        self.fonts = fonts

    def run(self):
        count = 0
        total = len(self.fonts)
        for i, font in enumerate(self.fonts):
            if not font['valid'] or font.get('installed', False):
                continue
            
            try:
                self.progress.emit(i, total, os.path.basename(font['path']))
                success = install_font_system(font['path'])
                self.item_updated.emit(font['path'], success)
                if success:
                    count += 1
            except Exception as e:
                self.item_updated.emit(font['path'], False)
                
        self.finished.emit(count)

class DownloadWorker(QThread):
    finished = Signal(str, str) # url, local_path

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            local_path = os.path.join(os.environ['TEMP'], self.filename)
            urllib.request.urlretrieve(self.url, local_path)
            self.finished.emit(self.url, local_path)
        except:
            self.finished.emit(self.url, "")

class LoadLibraryWorker(QThread):
    font_found = Signal(str)

    def run(self):
        fonts = get_installed_fonts()
        for font in fonts:
            self.font_found.emit(font)

class GoogleFontsWorker(QThread):
    font_found = Signal(dict)

    def run(self):
        from config import GOOGLE_FONTS
        for font in GOOGLE_FONTS:
            self.font_found.emit(font)
