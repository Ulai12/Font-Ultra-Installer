use serde::{Deserialize, Serialize};
use std::fs;
use ttf_parser::{name_id, Face};

#[derive(Serialize, Deserialize)]
pub struct FontMetadata {
    pub name: String,
    pub family: String,
    pub style: String,
    pub version: String,
    pub format: String,
}

#[tauri::command]
pub fn validate_font(path: String) -> Result<bool, String> {
    let data = fs::read(&path).map_err(|e| format!("Failed to read file: {}", e))?;
    // Try to parse as font
    match Face::parse(&data, 0) {
        Ok(_) => Ok(true),
        Err(_) => Ok(false), // Return false if invalid, don't error
    }
}

#[tauri::command]
pub fn analyze_font(path: String) -> Result<FontMetadata, String> {
    let data = fs::read(&path).map_err(|e| format!("Failed to read file: {}", e))?;

    let face = Face::parse(&data, 0).map_err(|e| format!("Invalid font: {:?}", e))?;

    // Extract metadata
    let family = face
        .names()
        .into_iter()
        .find(|name| name.name_id == name_id::FAMILY)
        .and_then(|name| name.to_string())
        .unwrap_or_else(|| "Unknown".to_string());

    let style = face
        .names()
        .into_iter()
        .find(|name| name.name_id == name_id::SUBFAMILY)
        .and_then(|name| name.to_string())
        .unwrap_or_else(|| "Regular".to_string());

    let version = face
        .names()
        .into_iter()
        .find(|name| name.name_id == name_id::VERSION)
        .and_then(|name| name.to_string())
        .unwrap_or_else(|| "1.0".to_string());

    let full_name = face
        .names()
        .into_iter()
        .find(|name| name.name_id == name_id::FULL_NAME)
        .and_then(|name| name.to_string())
        .unwrap_or_else(|| family.clone());

    // Determine format
    let format = if path.to_lowercase().ends_with(".ttf") {
        "TrueType"
    } else if path.to_lowercase().ends_with(".otf") {
        "OpenType"
    } else {
        "Unknown"
    };

    Ok(FontMetadata {
        name: full_name,
        family,
        style,
        version,
        format: format.to_string(),
    })
}

#[tauri::command]
pub fn get_font_chars(path: String) -> Result<Vec<u32>, String> {
    let data = fs::read(&path).map_err(|e| format!("Failed to read file: {}", e))?;
    let face = Face::parse(&data, 0).map_err(|e| format!("Invalid font: {:?}", e))?;

    let mut chars = Vec::new();

    // Find a Unicode cmap subtable
    if let Some(table) = face.tables().cmap {
        for subtable in table.subtables {
            if subtable.is_unicode() {
                subtable.codepoints(|c| {
                    chars.push(c);
                });
                break; // Use the first valid unicode subtable
            }
        }
    }

    // Sort to be nice
    chars.sort();
    chars.dedup();

    Ok(chars)
}
