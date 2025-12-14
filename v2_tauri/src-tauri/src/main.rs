// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod font_ops;
mod system;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            font_ops::validate_font,
            font_ops::analyze_font,
            system::is_admin,
            system::get_installed_fonts,
            system::install_font
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
