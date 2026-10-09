import sqlite3
import unicodedata
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "recommendations.db"

# Categorías disponibles para las recomendaciones
RECOM_CATEGORIES = {
    "profesional": {
        "label": "🩺 Profesional de la Salud",
        "short": "Profesionales",
        "color": "#EBF3FE",
        "text_color": "#185ABC",
        "border": "#C2D9FC",
        "icon": "🩺",
        "action_text": "📞 Ver Contacto / Web"
    },
    "producto": {
        "label": "🧸 Producto para Mamás y Bebés",
        "short": "Productos",
        "color": "#FEF7E6",
        "text_color": "#B06000",
        "border": "#FCE3A6",
        "icon": "🧸",
        "action_text": "🛒 Ver Producto / Link"
    },
    "tip": {
        "label": "💡 Consejo o Tip de Crianza",
        "short": "Consejos y Tips",
        "color": "#EEF9F1",
        "text_color": "#137333",
        "border": "#C4EBD0",
        "icon": "💡",
        "action_text": "🔗 Más Información"
    }
}

def normalize_text(text: str) -> str:
    """Normaliza texto removiendo acentos y pasando a minúsculas."""
    if not text:
        return ""
    clean = unicodedata.normalize('NFD', text)
    return ''.join(c for c in clean if unicodedata.category(c) != 'Mn').lower()

def clean_url(url: Optional[str]) -> Optional[str]:
    """Asegura que las URLs comiencen con http:// o https:// para enlaces de Streamlit."""
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("wa.me") or url.startswith("mailto:")):
        if url.startswith("www."):
            return f"https://{url}"
        elif re.match(r"^\+?\d[\d\s\-]{6,}$", url):
            # Es un teléfono o celular
            digits = re.sub(r"[^\d]", "", url)
            return f"https://wa.me/{digits}"
        else:
            return f"https://{url}"
    elif url.startswith("wa.me"):
        return f"https://{url}"
    return url

def init_recom_db():
    """Inicializa la base de datos de recomendaciones y carga datos iniciales si está vacía."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                link TEXT,
                contact_info TEXT,
                keywords TEXT,
                author_name TEXT NOT NULL,
                is_admin_entry INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def seed_initial_recommendations(cursor: sqlite3.Cursor):
    """Inserta recomendaciones de ejemplo útiles y reales para la comunidad."""
    seeds = [
        (
            "producto",
            "Silla de Comer Evolutiva de Madera (Tipo Tripp Trapp)",
            "Permite que el bebé coma a la misma altura de la mesa familiar, integrándose a las comidas compartidas. Su apoyapiés regulable es fundamental para mantener la postura erguida de 90° recomendada por fonoaudiólogos y nutricionistas en alimentación complementaria / BLW, lo que brinda estabilidad y previene el riesgo de atragantamiento.",
            "https://listado.mercadolibre.com.ar/silla-de-comer-evolutiva-madera",
            "Disponibles en MercadoLibre y carpinterías Montessori",
            "silla de comer, postura, blw, alimentacion complementaria, trona, madera, mesa, apoyapies",
            "Carla (Administradora)",
            1
        ),
        (
            "profesional",
            "Dra. Mariana Gómez - Médica Pediatra y Puericultora",
            "Pediatra súper respetuosa y pro-lactancia materna exclusiva. Atiende presencial en consultorio en Palermo y también ofrece videollamadas para urgencias o dudas de sueño y alimentación. Muy dulce en el trato y cero intervencionista innecesariamente.",
            "https://wa.me/5491155551234",
            "Palermo (Av. Santa Fe 3200) • WhatsApp turnos: 11-5555-1234",
            "pediatra, lactancia, puericultura, palermo, videollamada, colicos, recien nacido, control pediatrico",
            "Mamá Paula",
            0
        ),
        (
            "profesional",
            "Dr. Lucas Rossi - Odontopediatra Especialista en Lactancia",
            "Especialista en odontopediatría para bebés desde los primeros meses, evaluación del frenillo lingual (anquiloglosia) y su impacto en el acople y dolor al amamantar. Cero traumático con los chicos, súper paciente.",
            "https://wa.me/5491144449876",
            "Belgrano, CABA • Teléfono consultorio: 11-4444-9876",
            "odontopediatra, frenillo lingual, dientes, boca, anquiloglosia, lactancia, belgrano, chupete",
            "Mamá Carla",
            0
        ),
        (
            "producto",
            "Aspirador Nasal por Succión tipo NoseFrida",
            "Mucho más higiénico y efectivo que las tradicionales peritas de goma. Imprescindible para descongestionar la naricita en invierno antes de que el bebé tome la teta o duerma. Cuenta con filtro higiénico y se lava fácilmente con agua tibia.",
            "https://www.google.com/search?q=aspirador+nasal+succion+nosefrida",
            "Farmacias y tiendas de bebés",
            "aspirador nasal, mocos, congestion, resfrio, nosefrida, succion, salud bebe",
            "Mamá Romi",
            0
        ),
        (
            "producto",
            "Crema de Caléndula Orgánica Weleda para Pañal",
            "Bálsamo calmante y regenerador para la zona del pañal. Previene y alivia paspaduras e irritaciones con extractos naturales de caléndula y óxido de zinc, sin perfumes químicos ni derivados del petróleo.",
            "https://www.weleda.com.ar/producto/c/crema-facial-de-calendula-para-bebe",
            "Farmacias y dietéticas",
            "crema calendula, paspaduras, dermatitis del panal, weleda, colita, piel sensible",
            "Mamá Valen",
            0
        ),
        (
            "profesional",
            "Lic. Andrea Torres - Osteópata Pediátrica",
            "Recomendada para bebés con plagiocefalia, tortícolis posicional o cólicos severos. Realiza maniobras muy suaves e indoloras que relajan las tensiones musculares posteriores al parto.",
            "https://instagram.com",
            "Recoleta, CABA • Atención con turno previo",
            "osteopata, reflujo, plagiocefalia, torticolis, colicos, recoleta, kinesiologia infantil",
            "Mamá Laura",
            0
        ),
        (
            "tip",
            "Postura Segura en la Silla de Comer (Regla del 90-90-90)",
            "Al iniciar alimentación complementaria (sea papillas o BLW), el bebé debe estar sentado en un ángulo de 90° en caderas, 90° en rodillas y tener los pies apoyados firmemente. Si la silla de comer no tiene apoyapiés regulable, puedes atar una toalla enrollada o un elástico resistente como soporte. El apoyo plantar activa los músculos abdominales necesarios para toser o hacer arcada de forma segura.",
            None,
            "Recomendación de guías de deglución infantil",
            "silla de comer, postura, regla 90 90, atragantamiento, blw, deglucion, arcada, seguridad",
            "Carla (Administradora)",
            1
        ),
        (
            "tip",
            "Conservación y Uso Correcto de la Leche Materna",
            "La leche materna congelada dura hasta 3 meses en el freezer hogareño. Para descongelarla, pásala a la heladera la noche previa o entibia la mamadera/vasito sumergiéndolo en agua caliente fuera del fuego (baño maría apagado). NUNCA uses microondas ni hiervas la leche, ya que destruye los anticuerpos y nutrientes clave.",
            None,
            "Basado en protocolos de lactancia de la SAP y UNICEF",
            "leche materna, conservacion, banco de leche, extraccion, freezer, microondas, lactancia",
            "Mamá Flor",
            0
        )
    ]

    cursor.executemany("""
        INSERT INTO recommendations 
        (category, title, description, link, contact_info, keywords, author_name, is_admin_entry)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, seeds)

def add_recommendation(
    category: str,
    title: str,
    description: str,
    link: Optional[str] = None,
    contact_info: Optional[str] = None,
    keywords: Optional[str] = None,
    author_name: str = "Familia de la Tribu",
    is_admin: bool = False
) -> int:
    """Inserta una nueva recomendación en la base de datos."""
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations 
            (category, title, description, link, contact_info, keywords, author_name, is_admin_entry, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """, (
            category.strip().lower(),
            title.strip(),
            description.strip(),
            clean_url(link),
            contact_info.strip() if contact_info else None,
            keywords.strip() if keywords else None,
            author_name.strip() if author_name else "Familia de la Tribu",
            1 if is_admin else 0
        ))
        conn.commit()
        return cursor.lastrowid

def update_recommendation(
    rec_id: int,
    category: str,
    title: str,
    description: str,
    link: Optional[str] = None,
    contact_info: Optional[str] = None,
    keywords: Optional[str] = None,
    author_name: Optional[str] = None
) -> bool:
    """Actualiza una recomendación existente (función para la Administradora)."""
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        fields = [
            ("category", category.strip().lower()),
            ("title", title.strip()),
            ("description", description.strip()),
            ("link", clean_url(link)),
            ("contact_info", contact_info.strip() if contact_info else None),
            ("keywords", keywords.strip() if keywords else None),
            ("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        if author_name:
            fields.append(("author_name", author_name.strip()))
        
        set_clause = ", ".join([f"{f[0]} = ?" for f in fields])
        params = [f[1] for f in fields]
        params.append(rec_id)
        
        cursor.execute(f"UPDATE recommendations SET {set_clause} WHERE id = ?;", params)
        conn.commit()
        return cursor.rowcount > 0

def delete_recommendation(rec_id: int) -> bool:
    """Elimina una recomendación de la base de datos (exclusivo Administradora)."""
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recommendations WHERE id = ?;", (rec_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_recommendation_by_id(rec_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una recomendación específica por su ID."""
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recommendations WHERE id = ?;", (rec_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def search_recommendations(
    query: str = "",
    category_filter: str = "todas"
) -> List[Dict[str, Any]]:
    """
    Busca recomendaciones por palabras clave (ej: 'silla de comer', 'pediatra', 'calendula').
    Busca de manera insensible a mayúsculas y acentos en título, descripción, palabras clave y contacto.
    """
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM recommendations"
        params = []
        if category_filter and category_filter != "todas":
            sql += " WHERE category = ?"
            params.append(category_filter)
        sql += " ORDER BY is_admin_entry DESC, id DESC;"
        
        cursor.execute(sql, params)
        rows = [dict(r) for r in cursor.fetchall()]

    if not query or not query.strip():
        return rows

    # Búsqueda semántica / por palabras clave con normalización de acentos
    q_norm = normalize_text(query.strip())
    # Extraer palabras clave de búsqueda (ignorando palabras muy cortas de 1 o 2 letras a menos que sea única)
    raw_tokens = [w for w in re.split(r"[^\w\d]+", q_norm) if w]
    meaningful_tokens = [t for t in raw_tokens if len(t) > 2] or raw_tokens

    scored_results = []
    for item in rows:
        title_norm = normalize_text(item.get("title") or "")
        desc_norm = normalize_text(item.get("description") or "")
        kw_norm = normalize_text(item.get("keywords") or "")
        contact_norm = normalize_text(item.get("contact_info") or "")
        cat_info = RECOM_CATEGORIES.get(item.get("category"), {})
        cat_norm = normalize_text(cat_info.get("label", "") + " " + cat_info.get("short", ""))
        full_text = f"{title_norm} {kw_norm} {desc_norm} {contact_norm} {cat_norm}"

        score = 0
        # Coincidencia de frase exacta
        if q_norm in title_norm:
            score += 100
        if q_norm in kw_norm:
            score += 80
        if q_norm in desc_norm:
            score += 40

        # Coincidencia por cada token/palabra clave
        tokens_found = 0
        for token in meaningful_tokens:
            if token in kw_norm:
                score += 35
                tokens_found += 1
            elif token in title_norm:
                score += 30
                tokens_found += 1
            elif token in desc_norm or token in contact_norm:
                score += 15
                tokens_found += 1
            elif token in full_text:
                score += 10
                tokens_found += 1

        # Si al menos un token importante o la frase entera coincide
        if score > 0 and (tokens_found >= 1 or q_norm in full_text):
            scored_results.append((score, item))

    # Ordenar por relevancia (puntuación más alta primero)
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored_results]

def get_recom_stats() -> Dict[str, Any]:
    """Retorna conteos de recomendaciones por categoría."""
    init_recom_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recommendations;")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT category, COUNT(*) FROM recommendations GROUP BY category;")
        by_cat = dict(cursor.fetchall())

    return {
        "total": total,
        "by_category": by_cat
    }
