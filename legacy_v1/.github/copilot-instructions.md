# Ultra Font Installer - AI Agent Instructions

## Project Overview

Ultra Font Installer is a **hybrid Python/Rust/PowerShell application** for managing system fonts on Windows. The UI uses PySide6 with Fluent Widgets (modern glassmorphism design), while performance-critical operations use Rust for font validation and metadata extraction.

**Architecture:**

- **Frontend**: `src/main.py` - PySide6 FluentWindow with 8 navigation pages
- **Configuration**: `src/config.py` - Settings, localization (FR/EN), and constants
- **Core Logic**: `src/core.py` - Font operations, workers (QThread), system integration
- **UI Components**: `src/ui/` - Individual pages, reusable components, inspectors
- **Backend**: `src/rust/` - Font validation & metadata extraction (Cargo project)
- **System**: `bin/SystemOps.ps1` - PowerShell registry operations for font installation

## Key Architectural Patterns

### 1. Worker Threads (QThread-Based)

All I/O operations run asynchronously in dedicated workers to prevent UI blocking:

- `AnalyzeWorker` - Scans fonts, validates, checks install status, generates previews
- `InstallWorker` - Installs multiple fonts with progress tracking
- `DownloadWorker` - Fetches fonts from URLs
- `LoadLibraryWorker` - Enumerates system fonts
- `GoogleFontsWorker` - Loads predefined Google Fonts list

**Pattern**: Emit signals (e.g., `font_analyzed`, `progress`) to communicate results back to UI.

### 2. Localization System

- Translations in `locales/{en.json, fr.json}`
- Use `tr(key)` function from `config.py` for all UI text
- Auto-detects system language; falls back to English
- **Critical**: Every new text string must be added to both JSON files AND called via `tr()`

### 3. Settings Management

- Stored in `settings.json` at workspace root
- Loaded on startup via `load_settings()`
- Modified at runtime via `SETTINGS` dict
- Saved explicitly with `save_settings()`
- Current keys: `theme`, `auto_restart`, `language`, `animated_bg`

### 4. Rust Integration

- `font_tool.exe` (binary in `bin/`) validates and analyzes fonts
- Called via subprocess: `[FONT_TOOL, "validate"|"analyze", file_path]`
- Returns JSON on stdout for analysis; exit code 0 = valid
- **Fallback**: If binary missing, app uses basic `.ttf/.otf` extension validation
- To rebuild: `cd src/rust && .\build.ps1` (requires Rust toolchain)

### 5. Font Installation Flow

```
User selects fonts → AnalyzeWorker (validate, get metadata, preview)
→ InstallWorker (copies to C:\Windows\Fonts, calls PowerShell)
→ SystemOps.ps1 (registers in registry via "runas" elevation)
→ Optional: restart_explorer() if auto_restart enabled
```

## Development Conventions

### File Organization

- **Pages**: `src/ui/pages.py` - Home, Library, GoogleFonts, Settings, About, Inspector, Typewriter, Versus
- **Components**: `src/ui/components.py` - FontCard, LibraryCard, GoogleFontCard (drag/drop, context menus)
- **Utilities**: Grouping logic in separate modules (inspector.py, preview.py, comparer.py, typewriter.py, pairing.py)

### UI/UX Patterns

- **Glass Theme**: Transparent widgets with `rgba()` colors, blur effects in stylesheets
- **CardWidget** for content containers with hover states
- **InfoBar** for toast notifications (success/error/info)
- **ScrollArea + QVBoxLayout** for dynamic font lists
- **Dark Mode Aware**: `isDarkTheme()` returns bool; stylesheets change colors conditionally

### Error Handling

- Workers emit partial data even on errors (e.g., `{'error': 'message', 'valid': False}`)
- UI gracefully degrades (e.g., no preview if PIL fails)
- Subprocess errors caught silently; logged to stdout only
- **No try/except suppression without reason** - add comments explaining degraded behavior

### Rust/Cargo Workflow

- Edit `src/rust/src/main.rs` for new font analysis features
- Add dependencies to `src/rust/Cargo.toml`
- Build with `.\build.ps1` → outputs `bin/font_tool.exe`
- Test with `font_tool validate C:\path\to\font.ttf`

## Testing & Debugging

- **Test script**: `test_fonts.py` - Manual testing utilities
- **Development launcher**: `start.bat` - Auto-installs dependencies, runs app
- **Admin requirement**: App enforces admin mode; forces re-run with elevation if needed
- **HiDPI scaling**: Explicitly disabled to avoid scaling issues on high-DPI displays

## Common Tasks

### Adding a New UI Page

1. Create class in `src/ui/pages.py` inheriting from `QFrame`
2. Add to `MainWindow.__init__()` with `self.addSubInterface()`
3. Add translation keys to `locales/*.json`
4. Import and wire workers for async operations

### Adding a New Setting

1. Add key/value to `SETTINGS` dict in `config.py`
2. Add UI control in `SettingsPage`
3. Ensure `save_settings()` called after changes
4. Add to translation files if user-facing

### Adding Localization

1. Add key to both `locales/en.json` and `locales/fr.json`
2. Use `tr("key")` in Python code
3. Rebuild translation cache: modify `config.py` to force `load_translations()`

### Debugging Font Operations

- Check `FONT_TOOL` path in `config.py` and verify binary exists
- Test validation: `python -c "from core import validate_font; print(validate_font('path'))"`
- Inspect workers with print statements in `run()` method
- Use InfoBar to show errors: `self.parent().show_error("message")`

## Do's and Don'ts

✅ **DO:**

- Use `tr()` for all user-facing text
- Run I/O in worker threads (never block main thread)
- Emit signals from workers; connect to UI slots
- Check `os.path.exists()` before file operations
- Use `creationflags=subprocess.CREATE_NO_WINDOW` for subprocesses

❌ **DON'T:**

- Hardcode text strings (no translation)
- Call subprocess without `CREATE_NO_WINDOW`
- Access `SETTINGS` without importing from `config`
- Modify workers after `start()` called
- Assume Rust binary exists (always provide fallback)

## Key File References

| File                   | Purpose                                        |
| ---------------------- | ---------------------------------------------- |
| `src/main.py`          | Entry point, MainWindow, theme/animation logic |
| `src/config.py`        | Settings, translations, constants, paths       |
| `src/core.py`          | Font validation, workers, system operations    |
| `src/ui/pages.py`      | All UI pages and page logic                    |
| `src/ui/components.py` | Reusable FontCard, LibraryCard, GoogleFontCard |
| `src/rust/src/main.rs` | Font metadata extraction (ttf-parser)          |
| `bin/SystemOps.ps1`    | Registry operations for font installation      |
| `locales/*.json`       | English and French translations                |
