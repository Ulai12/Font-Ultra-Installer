# Rust Font Tool

This Rust binary replaces the previous C++ and Java components for font validation and metadata extraction.

## Building

1. Install Rust from https://rustup.rs/
2. Run the build script:
   ```powershell
   .\build.ps1
   ```

The compiled binary will be placed in `bin/font_tool.exe`.

## Usage

```bash
# Validate a font
font_tool.exe validate path/to/font.ttf

# Analyze and get metadata (JSON output)
font_tool.exe analyze path/to/font.ttf
```

## Dependencies

- `ttf-parser` - Fast and safe TrueType/OpenType parser
- `serde` + `serde_json` - JSON serialization
