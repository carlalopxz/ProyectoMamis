import os
import streamlit as st
from pathlib import Path
import indexer

# Configuración general de la página
st.set_page_config(
    page_title="Biblioteca Tribu | Buscador de Familias",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (amigable, cálido, móvil-first)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header principal */
    .hero-container {
        background: linear-gradient(135deg, #FFF6EC 0%, #F5F0FF 50%, #ECF6F1 100%);
        padding: 2rem 1.5rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        border: 1px solid #EFE6FD;
        text-align: center;
        box-shadow: 0 4px 20px rgba(108, 71, 166, 0.04);
    }
    .hero-title {
        color: #382B47;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        color: #6C5D81;
        font-size: 1.05rem;
        max-width: 720px;
        margin: 0 auto;
    }

    /* Tarjetas de resultados */
    .result-card {
        background-color: #FFFFFF;
        border: 1px solid #E8E5EE;
        border-radius: 18px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .doc-title {
        font-weight: 600;
        color: #2D233C;
        font-size: 1.05rem;
    }
    .badge-cat {
        background-color: #F1EDFC;
        color: #5D3799;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-type {
        background-color: #EAF7EE;
        color: #226E40;
        padding: 0.2rem 0.65rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .snippet-text {
        color: #484153;
        font-size: 0.96rem;
        line-height: 1.6;
        margin-top: 0.5rem;
    }
    mark.highlight {
        background-color: #FFE699;
        color: #3B2A00;
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Tarjetas del explorador de categorías */
    .cat-box {
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.05);
        height: 100%;
    }
    .cat-box h4 {
        margin: 0 0 0.4rem 0;
        font-weight: 700;
    }
    .cat-box p {
        font-size: 0.88rem;
        margin-bottom: 0;
        line-height: 1.45;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- CONTROL DE ACCESO PRIVADO (PIN) -----------------
CLAVE_GRUPO = "familias2025"
try:
    if hasattr(st, "secrets") and "GRUPO_PIN" in st.secrets:
        CLAVE_GRUPO = st.secrets["GRUPO_PIN"]
    elif "GRUPO_PIN" in os.environ:
        CLAVE_GRUPO = os.environ["GRUPO_PIN"]
except Exception:
    pass

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def check_login():
    clave_ingresada = st.session_state.get("pin_input", "")
    if clave_ingresada == CLAVE_GRUPO:
        st.session_state["autenticado"] = True
    else:
        st.error("Clave incorrecta. Consulta al administrador del grupo.")

if not st.session_state["autenticado"]:
    st.markdown("""
    <div style="max-width: 450px; margin: 4rem auto; text-align: center; background: #FFF9F5; padding: 2.5rem; border-radius: 24px; border: 1px solid #FFE6D6; box-shadow: 0 8px 24px rgba(0,0,0,0.04);">
        <h1 style="font-size: 2.8rem; margin-bottom: 0.3rem;">🍼</h1>
        <h2 style="color: #3C2B20; margin-bottom: 0.4rem; font-weight: 700;">Biblioteca Tribu</h2>
        <p style="color: #7A6658; font-size: 0.95rem; margin-bottom: 1.5rem;">
            Espacio privado de libros, recetas, guías de salud y recomendaciones para nuestra comunidad.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.text_input("Clave de acceso del grupo:", type="password", key="pin_input", on_change=check_login)
        st.button("Entrar a la biblioteca", type="primary", use_container_width=True, on_click=check_login)
        st.caption("🔒 *Acceso exclusivo para integrantes de la Tribu.*")
    st.stop()


# ----------------- INICIALIZACIÓN -----------------
if "db_initialized" not in st.session_state:
    indexer.init_db()
    stats_check = indexer.get_stats()
    if stats_check["total_files"] == 0:
        with st.spinner("Preparando biblioteca por primera vez..."):
            indexer.index_all_documents()
    st.session_state["db_initialized"] = True


# ----------------- SIDEBAR (BIBLIOTECA Y SUBIDA) -----------------
with st.sidebar:
    st.markdown("### 📚 Biblioteca Tribu")
    
    stats = indexer.get_stats()
    c_m1, c_m2 = st.columns(2)
    c_m1.metric("Libros y Archivos", stats["total_files"])
    c_m2.metric("Páginas / Secciones", stats["total_chunks"])
    
    st.markdown("---")
    
    # Botón para reindexar archivos locales
    if st.button("🔄 Actualizar / Reindexar Biblioteca", use_container_width=True):
        with st.spinner("Escaneando libros y notas..."):
            sync_stats = indexer.index_all_documents()
            st.success(f"Listo: {sync_stats['indexed_files']} archivos actualizados ({sync_stats['indexed_chunks']} fragmentos).")
            st.rerun()

    st.markdown("---")
    
    # Subida de nuevos archivos desde la web
    st.markdown("#### 📤 Agregar Nuevo Documento")
    st.caption("Sube un PDF, EPUB o archivo .txt de WhatsApp.")
    
    uploaded_file = st.file_uploader(
        "Seleccionar archivo",
        type=["pdf", "epub", "txt"],
        help="Formatos admitidos: .pdf, .epub, .txt"
    )
    
    cat_destino = st.selectbox(
        "Categoría donde guardarlo:",
        options=list(indexer.CATEGORIES.keys()),
        format_func=lambda k: indexer.CATEGORIES[k]
    )
    
    if uploaded_file is not None:
        if st.button("💾 Guardar e Indexar", type="primary", use_container_width=True):
            save_folder = indexer.DOCS_DIR / cat_destino
            save_folder.mkdir(parents=True, exist_ok=True)
            target_path = save_folder / uploaded_file.name
            
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            with st.spinner("Indexando nuevo documento..."):
                sync_stats = indexer.index_all_documents()
                st.success(f"¡'{uploaded_file.name}' guardado con éxito!")
                st.rerun()

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()


# ----------------- CONTENIDO PRINCIPAL -----------------

# Portada / Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🍼 Biblioteca Tribu</div>
    <div class="hero-subtitle">
        Buscador inteligente de libros, recetas, guías de sueño, protocolos APLV, primeros auxilios y recomendaciones comunitarias.
    </div>
</div>
""", unsafe_allow_html=True)

# Barra de Búsqueda y Filtro
col_search, col_cat = st.columns([2.5, 1.3])

with col_search:
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

    query = st.text_input(
        "¿Qué información o receta necesitas?",
        value=st.session_state["search_query"],
        placeholder="Ej: recetas calabaza, regresión 4 meses, RCP, leche APLV, odontopediatra...",
        key="main_search_input"
    )

with col_cat:
    cat_options = {"todas": "🌟 Todas las categorías"}
    cat_options.update(indexer.CATEGORIES)
    selected_category = st.selectbox(
        "Filtrar por categoría:",
        options=list(cat_options.keys()),
        format_func=lambda k: cat_options[k]
    )

# Sugerencias rápidas (Chips)
st.caption("💡 Sugerencias rápidas de búsqueda:")
chips_cols = st.columns(6)
chips_data = [
    ("🥑 Calabaza / Zapallo", "calabaza"),
    ("😴 Regresión de sueño", "regresion"),
    ("🥛 APLV / Alergias", "aplv"),
    ("🚑 RCP / Urgencias", "rcp"),
    ("🤱 Lactancia materna", "lactancia"),
    ("🩺 Pediatra", "pediatra")
]

for col, (label, term) in zip(chips_cols, chips_data):
    if col.button(label, use_container_width=True):
        st.session_state["search_query"] = term
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- RESULTADOS DE BÚSQUEDA -----------------
active_query = query.strip() or st.session_state.get("search_query", "").strip()

if active_query:
    results = indexer.search_documents(active_query, category_filter=selected_category)
    
    if results:
        st.markdown(f"#### 🔎 Encontramos **{len(results)}** coincidencia(s) para *'{active_query}'*:")
        
        for idx, item in enumerate(results):
            cat_display = indexer.CATEGORIES.get(item['category'], item['category'].title())
            file_abs_path = indexer.BASE_DIR / item['file_path']
            
            with st.container():
                st.markdown(f"""
                <div class="result-card">
                    <div class="card-header">
                        <div>
                            <span class="badge-type">{item['file_type']}</span>
                            <span class="doc-title">&nbsp; {item['filename']}</span>
                            <span style="color: #7B708A; font-size: 0.85rem;"> • {item['section']}</span>
                        </div>
                        <span class="badge-cat">{cat_display}</span>
                    </div>
                    <div class="snippet-text">
                        "{item['snippet_match']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_exp, col_down = st.columns([4.2, 1.1])
                with col_exp:
                    with st.expander(f"📖 Leer contexto completo ({item['section']})"):
                        st.write(item["content"])
                
                with col_down:
                    if file_abs_path.exists():
                        with open(file_abs_path, "rb") as f:
                            st.download_button(
                                label="📥 Descargar",
                                data=f.read(),
                                file_name=item["filename"],
                                mime="application/octet-stream",
                                key=f"down_{idx}_{item['id']}",
                                use_container_width=True
                            )
                st.markdown("<hr style='border: none; border-top: 1px dashed #E2DDF0; margin: 0.6rem 0 1rem 0;'>", unsafe_allow_html=True)
    else:
        st.warning(f"No encontramos resultados para '{active_query}'.")
        st.info("💡 **Consejo:** Prueba con una palabra más general (ej: *calabaza*, *rutinas*, *fiebre*, *pecho*) o selecciona '🌟 Todas las categorías'.")
else:
    # Vista de inicio con categorías temáticas
    st.markdown("### 📚 Explora la Biblioteca por Categorías")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="cat-box" style="background: #F4FAF5; border-color: #D3ECD9;">
            <h4 style="color: #246B3C;">🥑 Alimentación y Recetas</h4>
            <p style="color: #43634C;">
                BLW, BLISS, cortes seguros, papillas nutritivas, galletitas, muffins y libros de Sabrina Critzmann, Melisa Jurozdicki y más.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="cat-box" style="background: #F3F8FC; border-color: #CFE3F7;">
            <h4 style="color: #1F5A8E;">🤱 Lactancia Materna</h4>
            <p style="color: #435E77;">
                Manejo, conservación y banco de leche materna, aumento de producción y destete respetuoso.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="cat-box" style="background: #F8F5FE; border-color: #E2D7FB;">
            <h4 style="color: #552FA3;">😴 Sueño y Descanso</h4>
            <p style="color: #584A7A;">
                Guías de MiniBabySalud, regresiones de sueño, colecho seguro (UNICEF), planes de 7 días y libros de Rosa Jové.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="cat-box" style="background: #FFF5F5; border-color: #FDDDDD;">
            <h4 style="color: #A32F2F;">🚑 RCP, Urgencias y Salud</h4>
            <p style="color: #794C4C;">
                Cuadernillos de RCP pediátrico (Mater Dei y MinSalud), prevención de asfixia con frutos secos, sanitización y botiquín.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="cat-box" style="background: #FEFAF2; border-color: #F8E8C8;">
            <h4 style="color: #8C590E;">🥛 Alergias y APLV</h4>
            <p style="color: #6C5535;">
                Protocolos APLV, listados de alimentos aptos, introducción de alérgenos y formularios OSDE y Swiss Medical.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="cat-box" style="background: #FAF7F2; border-color: #ECE5D8;">
            <h4 style="color: #665039;">🌱 Crianza y Contactos</h4>
            <p style="color: #655B50;">
                Bésame Mucho (Carlos González), Hoy No Es Siempre, datos de pediatras y productos probados por familias.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👆 Escribe cualquier duda en el buscador arriba o toca una de las sugerencias para ver fragmentos de los libros.")
