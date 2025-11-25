# Build script for Rust font_tool

Write-Host "Building Rust font_tool..." -ForegroundColor Cyan

# Check if Rust is installed
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Rust is not installed!" -ForegroundColor Red
    Write-Host "Please install Rust from: https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}

# Build in release mode
cargo build --release

if ($LASTEXITCODE -eq 0) {
    # Copy binary to bin directory
    $binDir = "..\..\bin"
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Path $binDir | Out-Null
    }
    
    Copy-Item "target\release\font_tool.exe" "$binDir\font_tool.exe" -Force
    Write-Host "Success! Binary copied to bin/font_tool.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
