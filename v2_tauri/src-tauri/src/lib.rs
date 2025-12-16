// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
mod font_ops;
mod system;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            font_ops::validate_font,
            font_ops::analyze_font,
            system::is_admin,
            system::get_installed_fonts,
            system::install_font,
            system::download_font,
            font_ops::get_font_chars
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
