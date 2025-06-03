import os
import sys
import subprocess
import json
import datetime
from typing import List, Dict, Optional

# =====================
# Configuración Global
# =====================
CONFIG_FILE = os.path.expanduser("~/.yt-dlp-gui-config.json")
DEFAULT_CONFIG = {
    "download_path": os.path.expanduser("~/Videos/yt-dlp"),
    "filename": "%(title)s.%(ext)s",
    "format": "mkv",
    "codec": "avc1",
    "proxy": None,
    "user_agent": None,
    "speed_limit": None,
    "default_subtitles": ["en", "es"]
}

config = DEFAULT_CONFIG.copy()

# =====================
# Funciones auxiliares
# =====================
def clear_screen():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_command(command: List[str], url: str = "") -> None:
    """Ejecuta o exporta un comando"""
    print("\n[Comando]:", ' '.join(command))
    
    print("\nOpciones:")
    print("1. Ejecutar ahora")
    print("2. Exportar a script .sh")
    print("3. Cancelar")
    
    choice = input("Elige una opción (1-3): ").strip()
    if choice == "1":
        subprocess.run(command, check=True)
    elif choice == "2":
        export_command_to_sh(command, url)

def export_command_to_sh(command: List[str], url: str) -> None:
    """Exporta el comando a un archivo .sh ejecutable"""
    default_name = f"yt-dlp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
    filename = input(f"\nNombre del archivo [{default_name}]: ").strip() or default_name
    
    try:
        with open(filename, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"# Comando generado para: {url}\n")
            f.write(' '.join(command) + "\n")
        
        os.chmod(filename, 0o755)
        print(f"✓ Script guardado como '{filename}'")
        print(f"Ejecutar con: ./{filename}")
    except Exception as e:
        print(f"✗ Error al exportar: {str(e)}")

def load_config() -> None:
    """Carga la configuración desde archivo"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config.update(json.load(f))
        print("\n✓ Configuración cargada")
    except FileNotFoundError:
        print("\n⚠ No se encontró configuración previa")
    except json.JSONDecodeError:
        print("\n✗ Error: Archivo de configuración corrupto")

def save_config() -> None:
    """Guarda la configuración actual"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("\n✓ Configuración guardada")
    except Exception as e:
        print(f"\n✗ Error al guardar: {str(e)}")

# =====================
# Funciones de descarga
# =====================
def get_video_formats(url: str) -> List[Dict]:
    """Obtiene formatos disponibles del video"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-formats", "--no-playlist", url],
            capture_output=True,
            text=True,
            check=True
        )
        return parse_formats(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error al obtener formatos: {e.stderr}")
        return []

def parse_formats(formats_text: str) -> List[Dict]:
    """Parsea la salida de yt-dlp --list-formats"""
    formats = []
    for line in formats_text.split('\n'):
        if 'video only' in line and 'mp4' in line:
            parts = [p for p in line.split(' ') if p]
            formats.append({
                'id': parts[0],
                'resolution': parts[2],
                'fps': parts[3],
                'codec': parts[-1]
            })
    return formats

def download_with_subtitles(url: str) -> None:
    """Descarga video con subtítulos configurados"""
    langs = ",".join(config['default_subtitles'])
    command = [
        "yt-dlp",
        "-f", f"bv*[vcodec~='{config['codec']}']+ba",
        "--embed-subs",
        "--sub-langs", langs,
        "--convert-subs", "srt",
        "-o", f"{config['download_path']}/{config['filename']}",
        url
    ]
    run_command(command, url)

# =====================
# Menús interactivos
# =====================
def menu_video_completo():
    clear_screen()
    url = input("\nURL del video: ").strip()
    
    print("\n1. Descarga estándar")
    print("2. Con subtítulos")
    print("3. Elegir calidad")
    print("4. Volver")
    
    choice = input("Opción (1-4): ").strip()
    if choice == "1":
        command = [
            "yt-dlp",
            "-f", f"bv*[vcodec~='{config['codec']}']+ba",
            "-o", f"{config['download_path']}/{config['filename']}",
            url
        ]
        run_command(command, url)
    elif choice == "2":
        download_with_subtitles(url)

# ... (otros menús similares) ...

def main():
    load_config()
    while True:
        clear_screen()
        print("=== YT-DLP GUI ===")
        print("1. Video completo")
        print("2. Solo video")
        print("3. Solo audio")
        print("4. Configuración")
        print("5. Salir")
        
        choice = input("Opción (1-5): ").strip()
        if choice == "1":
            menu_video_completo()
        elif choice == "5":
            save_config()
            sys.exit()

if __name__ == "__main__":
    main()