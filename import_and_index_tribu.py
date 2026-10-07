import os
import shutil
import unicodedata
from pathlib import Path
import indexer

SOURCE_DIR = Path("G:/Mi unidad/Biblioteca Tribu")
TARGET_DIR = indexer.DOCS_DIR

def normalize(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

def determine_category(filename: str) -> str:
    n = normalize(filename)
    if 'aplv' in n or 'medicamentosa' in n or 'alergen' in n:
        return 'aplv'
    elif 'lactancia' in n or 'leche materna' in n or ('teta' in n and 'sueno' not in n):
        return 'lactancia'
    elif 'sueno' in n or 'dormir' in n or 'colecho' in n or 'rutinas' in n or 'regresion' in n or 'minibabysalud' in n:
        return 'sueno'
    elif 'rcp' in n or 'urgencia' in n or 'masaje' in n or 'peligroso' in n or 'intoxicacion' in n or 'sanitizac' in n:
        return 'salud_seguridad'
    elif any(k in n for k in ['receta', 'recetario', 'comida', 'alimento', 'blw', 'bliss', 'galletita', 'muffin', 'papilla', 'quinoa', 'prebiotico', 'comer y criar', 'nutricion', 'plato', 'alimentacion']):
        return 'recetas'
    elif 'besame mucho' in n or 'hoy no es siempre' in n:
        return 'crianza'
    else:
        return 'general'

def run_import():
    print(f"=== Escaneando documentos en: {SOURCE_DIR} ===")
    if not SOURCE_DIR.exists():
        print(f"ERROR: No se encuentra la ruta {SOURCE_DIR}")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for cat in indexer.CATEGORIES.keys():
        (TARGET_DIR / cat).mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0

    for src_file in SOURCE_DIR.iterdir():
        if not src_file.is_file():
            continue
        
        # Ignorar archivos del sistema
        if src_file.name.lower() in ["desktop.ini", ".ds_store", "thumbs.db"]:
            continue

        category = determine_category(src_file.name)
        target_name = src_file.name

        # Normalizar archivos EPUB que vienen sin extensión
        if target_name.lower().endswith(" epub"):
            target_name = target_name[:-5] + ".epub"
        elif target_name.lower().endswith(" - epub"):
            target_name = target_name[:-7] + ".epub"

        dest_file = TARGET_DIR / category / target_name

        # Copiar si no existe o si cambió el tamaño
        if not dest_file.exists() or dest_file.stat().st_size != src_file.stat().st_size:
            print(f"[{category.upper()}] Copiando: {src_file.name} -> {target_name}")
            try:
                shutil.copy2(src_file, dest_file)
                copied += 1
            except Exception as e:
                print(f"Error copiando {src_file.name}: {e}")
        else:
            skipped += 1

    print(f"\nResumen de importación: {copied} archivos copiados, {skipped} ya existían.")
    print("=== Iniciando indexación en la base de datos... ===")
    stats = indexer.index_all_documents()
    print(f"=== Indexación completada: {stats['indexed_files']} archivos procesados, {stats['indexed_chunks']} fragmentos/páginas indexadas ===")

if __name__ == "__main__":
    run_import()
