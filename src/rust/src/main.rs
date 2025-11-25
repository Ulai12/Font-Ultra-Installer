use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::process;
use ttf_parser::{Face, name_id};

#[derive(Serialize, Deserialize)]
struct FontMetadata {
    name: String,
    family: String,
    style: String,
    version: String,
    format: String,
}

fn validate_font(path: &str) -> Result<(), String> {
    let data = fs::read(path).map_err(|e| format!("Failed to read file: {}", e))?;
    
    // Try to parse as font
    Face::parse(&data, 0).map_err(|e| format!("Invalid font: {:?}", e))?;
    
    Ok(())
}

fn analyze_font(path: &str) -> Result<FontMetadata, String> {
    let data = fs::read(path).map_err(|e| format!("Failed to read file: {}", e))?;
    
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
    let format = if path.ends_with(".ttf") {
        "TrueType"
    } else if path.ends_with(".otf") {
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

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 3 {
        eprintln!("Usage: font_tool <command> <path>");
        eprintln!("Commands:");
        eprintln!("  validate <path>  - Validate font file");
        eprintln!("  analyze <path>   - Analyze font and output JSON metadata");
        process::exit(1);
    }
    
    let command = &args[1];
    let path = &args[2];
    
    match command.as_str() {
        "validate" => {
            match validate_font(path) {
                Ok(_) => {
                    process::exit(0);
                }
                Err(e) => {
                    eprintln!("Validation failed: {}", e);
                    process::exit(1);
                }
            }
        }
        "analyze" => {
            match analyze_font(path) {
                Ok(metadata) => {
                    let json = serde_json::to_string(&metadata).unwrap();
                    println!("{}", json);
                    process::exit(0);
                }
                Err(e) => {
                    eprintln!("{{\"name\": \"Error\", \"error\": \"{}\"}}", e);
                    process::exit(1);
                }
            }
        }
        _ => {
            eprintln!("Unknown command: {}", command);
            eprintln!("Valid commands: validate, analyze");
            process::exit(1);
        }
    }
}
