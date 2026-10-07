import os
import re
import sqlite3
import shutil
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

import pymupdf
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documentos"
DB_PATH = BASE_DIR / "data" / "index.db"

# Categorías temáticas enriquecidas para la Tribu
CATEGORIES = {
    "recetas": "🥑 Alimentación y Recetas (BLW, AC)",
    "sueno": "😴 Sueño y Rutinas de Descanso",
    "lactancia": "🤱 Lactancia Materna",
    "salud_seguridad": "🚑 Primeros Auxilios, RCP y Salud",
    "aplv": "🥛 Alergias y APLV (Protocolos y Fórmulas)",
    "crianza": "🌱 Crianza Respetuosa y Desarrollo",
    "profesionales": "🩺 Profesionales y Contactos",
    "productos": "🧸 Productos Recomendados",
    "general": "📁 Información General"
}

def normalize_text(text: str) -> str:
    """Normaliza texto removiendo acentos para comparaciones."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def init_db():
    """Inicializa la base de datos y la tabla virtual de búsqueda FTS5."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES.keys():
        (DOCS_DIR / cat).mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Tabla principal de entradas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                category TEXT NOT NULL,
                section TEXT NOT NULL,
                content TEXT NOT NULL,
                mtime REAL NOT NULL
            );
        """)

        # Tabla virtual para búsqueda Full-Text (FTS5)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                filename,
                category,
                section,
                content,
                content='entries',
                content_rowid='id'
            );
        """)

        # Triggers para mantener FTS5 sincronizado
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
                INSERT INTO entries_fts(rowid, filename, category, section, content)
                VALUES (new.id, new.filename, new.category, new.section, new.content);
            END;
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
                INSERT INTO entries_fts(entries_fts, rowid, filename, category, section, content)
                VALUES('delete', old.id, old.filename, old.category, old.section, old.content);
            END;
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
                INSERT INTO entries_fts(entries_fts, rowid, filename, category, section, content)
                VALUES('delete', old.id, old.filename, old.category, old.section, old.content);
                INSERT INTO entries_fts(rowid, filename, category, section, content)
                VALUES (new.id, new.filename, new.category, new.section, new.content);
            END;
        """)
        conn.commit()


def extract_pdf_chunks(pdf_path: Path) -> List[Dict[str, str]]:
    """Extrae texto de un archivo PDF página por página de forma ultra rápida con PyMuPDF."""
    chunks = []
    try:
        doc = pymupdf.open(str(pdf_path))
        num_pages = len(doc)
        for page_num in range(num_pages):
            try:
                page = doc[page_num]
                text = page.get_text()
                if text and text.strip():
                    clean_text = " ".join(text.split())
                    if len(clean_text) > 25:
                        chunks.append({
                            "section": f"Pág. {page_num + 1}",
                            "content": clean_text
                        })
            except Exception:
                continue
    except Exception as e:
        print(f"Error procesando PDF {pdf_path.name}: {e}")
    return chunks


def extract_epub_chunks(epub_path: Path) -> List[Dict[str, str]]:
    """Extrae texto de un archivo EPUB sección por sección."""
    chunks = []
    try:
        book = epub.read_epub(str(epub_path))
        chap_num = 1
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            try:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                if text and len(text.strip()) > 50:
                    clean_text = " ".join(text.split())
                    chunks.append({
                        "section": f"Capítulo {chap_num}",
                        "content": clean_text
                    })
                    chap_num += 1
            except Exception:
                continue
    except Exception as e:
        print(f"Error procesando EPUB {epub_path.name}: {e}")
    return chunks


def extract_whatsapp_chunks(txt_path: Path) -> List[Dict[str, str]]:
    """Extrae mensajes o bloques de texto de un archivo exportado de WhatsApp."""
    chunks = []
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_block = []
        current_header = "Nota comunitaria"
        
        date_pattern = re.compile(r"^(\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}[, ]+\d{1,2}:\d{2}(?::\d{2})?\]?)\s*[-:]?\s*([^:]+)?:\s*(.*)$")

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if "Los mensajes y las llamadas están cifrados" in line_str or "<Multimedia omitido>" in line_str:
                continue

            match = date_pattern.match(line_str)
            if match:
                date_str, sender, msg = match.groups()
                if current_block and len(" ".join(current_block)) > 120:
                    chunks.append({
                        "section": current_header,
                        "content": " ".join(current_block)
                    })
                    current_block = []
                
                sender_display = (sender or "").strip()
                current_header = f"Nota ({sender_display})" if sender_display else "Nota de chat"
                if msg:
                    current_block.append(msg.strip())
            else:
                current_block.append(line_str)

        if current_block:
            chunks.append({
                "section": current_header,
                "content": " ".join(current_block)
            })
    except Exception as e:
        print(f"Error procesando WhatsApp {txt_path.name}: {e}")
    return chunks


def extract_generic_txt_chunks(txt_path: Path) -> List[Dict[str, str]]:
    """Extrae texto de archivos .txt genéricos dividiéndolos por párrafos."""
    chunks = []
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for idx, p in enumerate(paragraphs, 1):
            chunks.append({
                "section": f"Párrafo {idx}",
                "content": " ".join(p.split())
            })
    except Exception as e:
        print(f"Error procesando TXT {txt_path.name}: {e}")
    return chunks


def index_all_documents() -> Dict[str, int]:
    """Escanea el directorio de documentos e indexa los nuevos o modificados."""
    init_db()
    stats = {"indexed_files": 0, "indexed_chunks": 0, "skipped_files": 0}

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT file_path, MAX(mtime) FROM entries GROUP BY file_path")
        indexed_mtimes = {row[0]: row[1] for row in cursor.fetchall()}

        found_files = set()

        for category_folder in sorted(DOCS_DIR.iterdir()):
            if not category_folder.is_dir():
                continue
            
            category_key = category_folder.name.lower()
            if category_key not in CATEGORIES:
                category_key = "general"

            for file_path in sorted(category_folder.rglob("*")):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext not in [".pdf", ".epub", ".txt"]:
                        continue

                    rel_path = file_path.relative_to(BASE_DIR).as_posix()
                    found_files.add(rel_path)
                    current_mtime = file_path.stat().st_mtime

                    # Si no ha cambiado, omitir
                    if rel_path in indexed_mtimes and indexed_mtimes[rel_path] >= current_mtime:
                        stats["skipped_files"] += 1
                        continue

                    # Eliminar versión previa si cambió
                    if rel_path in indexed_mtimes:
                        cursor.execute("DELETE FROM entries WHERE file_path = ?", (rel_path,))

                    chunks = []
                    file_type = "Documento"

                    if ext == ".pdf":
                        file_type = "PDF"
                        chunks = extract_pdf_chunks(file_path)
                    elif ext == ".epub":
                        file_type = "EPUB"
                        chunks = extract_epub_chunks(file_path)
                    elif ext == ".txt":
                        file_type = "WhatsApp / Nota"
                        chunks = extract_whatsapp_chunks(file_path)
                        if not chunks:
                            chunks = extract_generic_txt_chunks(file_path)

                    if not chunks:
                        # Si es un PDF escaneado sin capa de texto, indexamos el título
                        clean_stem = file_path.stem.replace("_", " ").replace("-", " ")
                        chunks = [{
                            "section": "Documento (Escaneado/Imagen)",
                            "content": f"{clean_stem}. Archivo en formato imagen/escaneado disponible para consulta y descarga."
                        }]

                    for chunk in chunks:
                        cursor.execute("""
                            INSERT INTO entries (file_path, filename, file_type, category, section, content, mtime)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            rel_path,
                            file_path.name,
                            file_type,
                            category_key,
                            chunk["section"],
                            chunk["content"],
                            current_mtime
                        ))
                        stats["indexed_chunks"] += 1

                    stats["indexed_files"] += 1
                    conn.commit()

        # Limpiar entradas de archivos borrados
        cursor.execute("SELECT DISTINCT file_path FROM entries")
        for (stored_path,) in cursor.fetchall():
            if stored_path not in found_files:
                cursor.execute("DELETE FROM entries WHERE file_path = ?", (stored_path,))
        conn.commit()

    return stats


def sanitize_query(query: str) -> str:
    """Limpia la consulta y prepara tokens de búsqueda para SQLite FTS5."""
    clean = re.sub(r"[^\w\s]", " ", query, flags=re.UNICODE)
    tokens = clean.split()
    if not tokens:
        return ""
    fts_tokens = [f'"{token}"*' for token in tokens]
    return " AND ".join(fts_tokens)


def search_documents(query: str, category_filter: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Busca en el índice FTS5 y devuelve resultados con fragmentos resaltados."""
    init_db()
    results = []

    fts_q = sanitize_query(query)
    if not fts_q:
        return results

    sql = """
        SELECT 
            entries.id,
            entries.file_path,
            entries.filename,
            entries.file_type,
            entries.category,
            entries.section,
            entries.content,
            snippet(entries_fts, 3, '<mark class="highlight">', '</mark>', '...', 32) AS snippet_match,
            bm25(entries_fts) AS rank
        FROM entries_fts
        JOIN entries ON entries_fts.rowid = entries.id
        WHERE entries_fts MATCH ?
    """
    params = [fts_q]

    if category_filter and category_filter != "todas":
        sql += " AND entries.category = ?"
        params.append(category_filter)

    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            for row in cursor.fetchall():
                results.append(dict(row))
        except sqlite3.OperationalError as e:
            print(f"Error en consulta FTS5: {e}")

    return results


def get_stats() -> Dict[str, Any]:
    """Obtiene el resumen de documentos indexados por categoría."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT file_path), COUNT(id) FROM entries")
        total_files, total_chunks = cursor.fetchone()

        cursor.execute("SELECT category, COUNT(DISTINCT file_path) FROM entries GROUP BY category")
        categories_count = dict(cursor.fetchall())

    return {
        "total_files": total_files or 0,
        "total_chunks": total_chunks or 0,
        "by_category": categories_count
    }
