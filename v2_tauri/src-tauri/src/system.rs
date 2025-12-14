use std::path::PathBuf;
use std::process::Command;
use std::fs;

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

#[tauri::command]
pub fn is_admin() -> bool {
    let mut cmd = Command::new("net");
    cmd.arg("session");

    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);

    match cmd.output() {
        Ok(out) => out.status.success(),
        Err(_) => false,
    }
}

#[tauri::command]
pub fn get_installed_fonts() -> Vec<String> {
    let font_dir = PathBuf::from(std::env::var("WINDIR").unwrap_or("C:\\Windows".to_string())).join("Fonts");
    let mut fonts = Vec::new();

    if let Ok(entries) = fs::read_dir(font_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if let Some(ext) = path.extension() {
                let ext_str = ext.to_string_lossy().to_lowercase();
                if ext_str == "ttf" || ext_str == "otf" || ext_str == "ttc" {
                    if let Some(name) = path.file_name() {
                        fonts.push(name.to_string_lossy().to_string());
                    }
                }
            }
        }
    }
    fonts
}

// Stub for install/uninstall - calling the PowerShell script would go here
#[tauri::command]
pub fn install_font(path: String) -> Result<String, String> {
    // Logic to call SystemOps.ps1
    // For safety in this demo, we return a success message without modifying registry
    // Implementation would be: Command::new("powershell")...

    Ok(format!("Mock Install Success: {}", path))
}
