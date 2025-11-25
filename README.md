# Ultra Font Installer (Rust Edition)

This application uses a hybrid architecture:
- **Python**: GUI (PySide6 + Fluent Widgets) and Orchestration
- **Rust**: Font Validation & Metadata Extraction (High Performance & Safe)
- **PowerShell**: System Registration

## Requirements
- Python 3.x
- Rust (for building the font tool, optional - prebuilt binary included)

## Installation & Running
1. Run `start.bat`
2. It will automatically install required dependencies: `PySide6`, `PySide6-Fluent-Widgets`, `packaging`, `pillow`.

## Building Rust Component (Optional)
If you want to rebuild the Rust binary:

```powershell
cd src/rust
.\build.ps1
```

This requires Rust to be installed: https://rustup.rs/

## Troubleshooting
- **Rust Binary Missing**: If `font_tool.exe` is missing, the app will use basic file extension validation.
- **Python Errors**: Make sure all dependencies are installed via `pip install PySide6 PySide6-Fluent-Widgets packaging pillow`.

## Development Guidelines
- **Stability**: Ensure that each modification does not cause conflicts with the rest of the code.
- **Localization**: Ensure that every newly added text is included in the translation logic.
- **Quality Control**: Verify and fix problems and errors.
