use std::fs;
use std::path::PathBuf;
use std::process::Command;

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
    let font_dir =
        PathBuf::from(std::env::var("WINDIR").unwrap_or("C:\\Windows".to_string())).join("Fonts");
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

#[tauri::command]
pub fn install_font(app: tauri::AppHandle, path: String) -> Result<String, String> {
    use tauri::Manager;

    // 1. Analyze font to get the name
    let meta = crate::font_ops::analyze_font(path.clone())?;
    let font_name = meta.name;

    // 2. Resolve script path
    let script_path = app
        .path()
        .resolve(
            "scripts/SystemOps.ps1",
            tauri::path::BaseDirectory::Resource,
        )
        .map_err(|e| format!("Failed to resolve script path: {}", e))?;

    // 3. Prepare PowerShell command
    // We use Start-Process to ensure we can request Admin privileges (RunAs)
    // This will trigger a UAC prompt if the app is not already running as Admin.
    // Note: Capturing output from a 'RunAs' process is complex.
    // For this version, we assume success if the process launches.

    let ps_args = format!(
        "-NoProfile -ExecutionPolicy Bypass -File \"{}\" -Command register -FontPath \"{}\" -FontName \"{}\"",
        script_path.display(),
        path,
        font_name
    );

    let status = Command::new("powershell")
        .arg("Start-Process")
        .arg("powershell")
        .arg("-ArgumentList")
        .arg(format!("'{}'", ps_args))
        .arg("-Verb")
        .arg("RunAs")
        .arg("-WindowStyle")
        .arg("Hidden")
        .arg("-Wait")
        .status()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if status.success() {
        Ok(format!(
            "Installation successfully initiated for {}",
            font_name
        ))
    } else {
        Err("Installation failed or was cancelled".to_string())
    }
}

#[tauri::command]
pub async fn download_font(app: tauri::AppHandle, url: String, filename: String) -> Result<String, String> {
    use std::io::Write;
    use tauri::Manager;

    // Use app temp dir
    let temp_dir = app.path().temp_dir().map_err(|e| format!("Failed to get temp dir: {}", e))?;
    let dest_path = temp_dir.join(&filename);

    let response = reqwest::get(&url)
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("Download failed with status: {}", response.status()));
    }

    let bytes = response.bytes().await.map_err(|e| format!("Failed to get bytes: {}", e))?;

    let mut file = fs::File::create(&dest_path).map_err(|e| format!("Failed to create file: {}", e))?;
    file.write_all(&bytes).map_err(|e| format!("Failed to write file: {}", e))?;

    Ok(dest_path.to_string_lossy().to_string())
}
