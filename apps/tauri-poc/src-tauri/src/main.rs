#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    if let Err(error) = apexbot_tauri_poc::run() {
        eprintln!("failed to start apexbot feed PoC: {error}");
        std::process::exit(1);
    }
}
