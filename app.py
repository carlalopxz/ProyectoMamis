import os
from datetime import datetime
from pathlib import Path
import streamlit as st

import indexer
import recommendations

# Configuración general de la página
st.set_page_config(
    page_title="Tribu Mamis | Recomendaciones y Biblioteca",
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
        max-width: 760px;
        margin: 0 auto;
    }

    /* Tarjetas de resultados y recomendaciones */
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
        font-weight: 700;
        color: #2D233C;
        font-size: 1.1rem;
    }
    .badge-cat {
        padding: 0.28rem 0.85rem;
        border-radius: 20px;
        font-size: 0.82rem;
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

    /* Banner admin */
    .admin-banner {
        background: #FFF9DB;
        border: 1px solid #F59F00;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- CONTROL DE ACCESO PRIVADO (PIN & ADMIN) -----------------
CLAVE_GRUPO = "familias2025"
CLAVE_ADMIN = "admin2025"

try:
    if hasattr(st, "secrets"):
        if "GRUPO_PIN" in st.secrets:
            CLAVE_GRUPO = str(st.secrets["GRUPO_PIN"])
        if "ADMIN_PIN" in st.secrets:
            CLAVE_ADMIN = str(st.secrets["ADMIN_PIN"])
    if "GRUPO_PIN" in os.environ:
        CLAVE_GRUPO = os.environ["GRUPO_PIN"]
    if "ADMIN_PIN" in os.environ:
        CLAVE_ADMIN = os.environ["ADMIN_PIN"]
except Exception:
    pass

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "es_admin" not in st.session_state:
    st.session_state["es_admin"] = False

def check_login():
    clave_ingresada = st.session_state.get("pin_input", "").strip()
    if clave_ingresada == CLAVE_ADMIN:
        st.session_state["autenticado"] = True
        st.session_state["es_admin"] = True
    elif clave_ingresada == CLAVE_GRUPO:
        st.session_state["autenticado"] = True
        st.session_state["es_admin"] = False
    else:
        st.error("Clave incorrecta. Consulta al administrador del grupo.")

if not st.session_state["autenticado"]:
    st.markdown("""
    <div style="max-width: 480px; margin: 4rem auto; text-align: center; background: #FFF9F5; padding: 2.5rem; border-radius: 24px; border: 1px solid #FFE6D6; box-shadow: 0 8px 24px rgba(0,0,0,0.04);">
        <h1 style="font-size: 2.8rem; margin-bottom: 0.3rem;">🍼</h1>
        <h2 style="color: #3C2B20; margin-bottom: 0.4rem; font-weight: 700;">Rincón de la Tribu</h2>
        <p style="color: #7A6658; font-size: 0.95rem; margin-bottom: 1.5rem;">
            Espacio privado para familias: recomendaciones de profesionales de la salud, productos para bebés, tips de crianza y biblioteca digital.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.text_input("Clave de acceso del grupo o administradora:", type="password", key="pin_input", on_change=check_login)
        st.button("Entrar al espacio", type="primary", use_container_width=True, on_click=check_login)
        st.caption("🔒 *Acceso exclusivo para integrantes de la comunidad.*")
    st.stop()


# ----------------- INICIALIZACIÓN DE BASES DE DATOS -----------------
if "db_initialized" not in st.session_state:
    try:
        recommendations.init_recom_db()
        indexer.init_db()
        stats_check = indexer.get_stats()
        if stats_check["total_files"] == 0:
            with st.spinner("Preparando e indexando biblioteca por primera vez..."):
                indexer.index_all_documents()
    except Exception as e:
        with st.spinner("Reconstruyendo bases de datos..."):
            recommendations.init_recom_db()
            indexer.init_db()
            indexer.index_all_documents()
    st.session_state["db_initialized"] = True


# ----------------- DIÁLOGOS MODALES (EDITAR / BORRAR / AGREGAR) -----------------
@st.dialog("✏️ Editar Recomendación (Modo Administradora)", width="large")
def modal_editar_recomendacion(rec_id: int):
    rec = recommendations.get_recommendation_by_id(rec_id)
    if not rec:
        st.error("No se encontró la recomendación solicitada.")
        return

    cat_keys = list(recommendations.RECOM_CATEGORIES.keys())
    cat_idx = cat_keys.index(rec["category"]) if rec["category"] in cat_keys else 0

    with st.form(key=f"form_edit_{rec_id}"):
        new_cat = st.selectbox(
            "Categoría:",
            options=cat_keys,
            index=cat_idx,
            format_func=lambda k: recommendations.RECOM_CATEGORIES[k]["label"]
        )
        new_title = st.text_input("Título o Nombre:", value=rec["title"])
        new_desc = st.text_area("Descripción / Por qué se recomienda:", value=rec["description"], height=140)
        new_link = st.text_input("Enlace / Link (opcional):", value=rec["link"] or "", placeholder="https://...")
        new_contact = st.text_input("Datos de Contacto / Dirección / Teléfono (opcional):", value=rec["contact_info"] or "", placeholder="Palermo • WhatsApp: 11-5555-1234")
        new_keywords = st.text_input("Palabras clave de búsqueda (separadas por coma):", value=rec["keywords"] or "", placeholder="silla de comer, postura, blw")
        new_author = st.text_input("Recomendado por:", value=rec["author_name"])

        c_sub1, c_sub2 = st.columns([1, 1])
        with c_sub1:
            guardar = st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True)
        with c_sub2:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

        if cancelar:
            st.rerun()

        if guardar:
            if not new_title.strip() or not new_desc.strip():
                st.error("El título y la descripción son obligatorios.")
            else:
                recommendations.update_recommendation(
                    rec_id=rec_id,
                    category=new_cat,
                    title=new_title,
                    description=new_desc,
                    link=new_link,
                    contact_info=new_contact,
                    keywords=new_keywords,
                    author_name=new_author
                )
                st.success("¡Recomendación actualizada correctamente!")
                st.rerun()

@st.dialog("🗑️ Confirmar Eliminación")
def modal_eliminar_recomendacion(rec_id: int, title: str):
    st.warning(f"¿Estás segura de que deseas eliminar permanentemente esta recomendación?\n\n**'{title}'**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sí, Eliminar", type="primary", use_container_width=True):
            recommendations.delete_recommendation(rec_id)
            st.success("Recomendación eliminada con éxito.")
            st.rerun()
    with c2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("➕ Compartir Nueva Recomendación con la Tribu", width="large")
def modal_nueva_recomendacion(is_admin: bool = False):
    default_author = "Carla (Administradora)" if is_admin else ""
    with st.form(key="form_nueva_recom"):
        st.markdown("Comparte un profesional de confianza, un producto que te salvó o un tip que toda mamá debería saber.")
        
        new_cat = st.selectbox(
            "Tipo de recomendación:",
            options=list(recommendations.RECOM_CATEGORIES.keys()),
            format_func=lambda k: recommendations.RECOM_CATEGORIES[k]["label"]
        )
        new_title = st.text_input(
            "Título o Nombre:",
            placeholder="Ej: Silla de Comer Evolutiva / Dra. Mariana Gómez (Pediatra) / Tip de sueño..."
        )
        new_desc = st.text_area(
            "¿Por qué lo recomiendas? (Tu experiencia o consejo):",
            placeholder="Cuenta por qué te sirvió, cómo te ayudó, cómo usarlo, etc...",
            height=130
        )
        new_link = st.text_input(
            "Enlace al Producto, Instagram o Sitio Web (opcional):",
            placeholder="https://mercadolibre.com.ar/... o https://wa.me/..."
        )
        new_contact = st.text_input(
            "Datos de Contacto / Consultorio / Teléfono (opcional):",
            placeholder="Ej: Consultorio en Palermo • WhatsApp: 11-5555-1234"
        )
        new_keywords = st.text_input(
            "Palabras clave para que otras mamás lo encuentren (separadas por coma):",
            placeholder="Ej: silla de comer, madera, postura, blw, 90 grados"
        )
        new_author = st.text_input(
            "Tu Nombre o Apodo:",
            value=default_author,
            placeholder="Ej: Mamá Paula"
        )

        st.caption("🔒 *Aviso: Para resguardar la seguridad y veracidad comunitaria, una vez cargada, solo la administradora puede editar o eliminar esta recomendación.*")

        c1, c2 = st.columns([1, 1])
        with c1:
            publicar = st.form_submit_button("🚀 Publicar Recomendación", type="primary", use_container_width=True)
        with c2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

        if cancel:
            st.rerun()

        if publicar:
            if not new_title.strip() or not new_desc.strip():
                st.error("Por favor completa al menos el título y la descripción.")
            else:
                author_final = new_author.strip() if new_author.strip() else ("Carla (Administradora)" if is_admin else "Familia de la Tribu")
                recommendations.add_recommendation(
                    category=new_cat,
                    title=new_title,
                    description=new_desc,
                    link=new_link,
                    contact_info=new_contact,
                    keywords=new_keywords,
                    author_name=author_final,
                    is_admin=is_admin
                )
                st.success("¡Muchas gracias! Tu recomendación fue publicada para toda la Tribu.")
                st.rerun()


# ----------------- SIDEBAR (PANEL DE CONTROL) -----------------
with st.sidebar:
    st.markdown("### 🍼 Rincón de la Tribu")

    # Módulo de Estado de Administradora
    if st.session_state.get("es_admin", False):
        st.markdown("""
        <div style="background: #FFF9DB; border: 1px solid #FFE066; border-radius: 12px; padding: 0.75rem 0.9rem; margin-bottom: 0.8rem;">
            <b style="color: #8F5B00; font-size: 0.95rem;">👑 Modo Administradora Activo</b><br>
            <span style="font-size: 0.82rem; color: #6E5000;">
                Hola Carla, tienes permisos para <b>editar</b> y <b>eliminar</b> cualquier recomendación.
            </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔒 Salir de Modo Administradora", use_container_width=True):
            st.session_state["es_admin"] = False
            st.rerun()
    else:
        with st.expander("👑 ¿Eres la Administradora?"):
            admin_code = st.text_input("Clave de Administradora:", type="password", key="side_admin_pin")
            if st.button("Activar Modo Admin", use_container_width=True):
                if admin_code.strip() == CLAVE_ADMIN:
                    st.session_state["es_admin"] = True
                    st.success("¡Modo Administradora activado!")
                    st.rerun()
                else:
                    st.error("Clave de administradora incorrecta.")

    st.markdown("---")
    
    # Resumen de Recomendaciones
    recom_counts = recommendations.get_recom_stats()
    st.markdown("#### 🌟 Recomendaciones Cargadas")
    cr1, cr2 = st.columns(2)
    cr1.metric("Total Datos", recom_counts["total"])
    cr2.metric("Profesionales", recom_counts["by_category"].get("profesional", 0))
    cr3, cr4 = st.columns(2)
    cr3.metric("Productos", recom_counts["by_category"].get("producto", 0))
    cr4.metric("Tips y Consejos", recom_counts["by_category"].get("tip", 0))

    st.markdown("---")

    # Resumen de Biblioteca Documental
    st.markdown("#### 📚 Biblioteca Digital")
    stats = indexer.get_stats()
    cm1, cm2 = st.columns(2)
    cm1.metric("Archivos", stats["total_files"])
    cm2.metric("Páginas / Notas", stats["total_chunks"])

    if st.button("🔄 Reindexar Archivos Locales", use_container_width=True):
        with st.spinner("Escaneando libros y notas..."):
            sync_stats = indexer.index_all_documents()
            st.success(f"Listo: {sync_stats['indexed_files']} archivos actualizados ({sync_stats['indexed_chunks']} fragmentos).")
            st.rerun()

    st.markdown("---")

    # Subida de archivos desde la web
    with st.expander("📤 Subir Documento a Biblioteca"):
        st.caption("Formatos: .pdf, .epub, .txt")
        uploaded_file = st.file_uploader("Seleccionar archivo", type=["pdf", "epub", "txt"])
        cat_destino = st.selectbox(
            "Categoría de destino:",
            options=list(indexer.CATEGORIES.keys()),
            format_func=lambda k: indexer.CATEGORIES[k]
        )
        if uploaded_file is not None:
            if st.button("💾 Guardar e Indexar Documento", type="primary", use_container_width=True):
                save_folder = indexer.DOCS_DIR / cat_destino
                save_folder.mkdir(parents=True, exist_ok=True)
                target_path = save_folder / uploaded_file.name
                with open(target_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner("Indexando nuevo documento..."):
                    indexer.index_all_documents()
                    st.success(f"¡'{uploaded_file.name}' guardado e indexado!")
                    st.rerun()

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["es_admin"] = False
        st.rerun()


# ----------------- CONTENIDO PRINCIPAL -----------------

# Portada / Banner Superior
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🍼 Rincón de Familias y Bebés</div>
    <div class="hero-subtitle">
        Buscador integrado de recomendaciones comunitarias (pediatras, productos probados, tips) y biblioteca de libros de alimentación, sueño y salud.
    </div>
</div>
""", unsafe_allow_html=True)

# Pestañas principales
tab_recomendaciones, tab_biblioteca = st.tabs([
    "🌟 Directorio de Recomendaciones (Profesionales, Productos y Tips)",
    "📚 Biblioteca de Libros y Guías (PDF / EPUB)"
])


# =========================================================================
# SECCIÓN 1: RECOMENDACIONES DE LA COMUNIDAD (PROFESIONALES, PRODUCTOS, TIPS)
# =========================================================================
with tab_recomendaciones:
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h3 style="color: #2D233C; margin-bottom: 0.2rem; font-weight: 700;">
            🌟 Recomendaciones de la Tribu
        </h3>
        <p style="color: #6C5D81; font-size: 0.95rem; margin-bottom: 0;">
            Consulta datos de boca en boca de mamás y papás. Busca por palabras clave (ej: <b>silla de comer</b>, <b>odontopediatra</b>, <b>aspirador nasal</b>) y accede directo a enlaces o contactos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    def set_recom_search(term: str):
        st.session_state["recom_search_input"] = term

    # Inicializar estado de búsqueda de recomendaciones si no existe
    if "recom_search_input" not in st.session_state:
        st.session_state["recom_search_input"] = ""

    # Barra de búsqueda y filtros
    col_r_search, col_r_cat, col_r_btn = st.columns([2.5, 1.4, 1.3])

    with col_r_search:
        recom_search_text = st.text_input(
            "Buscar por palabra clave:",
            key="recom_search_input",
            placeholder="Ej: silla de comer, odontopediatra, caléndula, osteópata, frenillo, blw..."
        )

    with col_r_cat:
        cat_choices = {
            "todas": "🌟 Todas las categorías",
            "profesional": "🩺 Profesionales de la Salud",
            "producto": "🧸 Productos para Mamás y Bebés",
            "tip": "💡 Consejos y Tips"
        }
        selected_recom_cat = st.selectbox(
            "Filtrar por categoría:",
            options=list(cat_choices.keys()),
            format_func=lambda k: cat_choices[k],
            key="select_recom_cat"
        )

    with col_r_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Compartir Dato", type="primary", use_container_width=True):
            modal_nueva_recomendacion(is_admin=st.session_state.get("es_admin", False))

    # Chips de búsqueda rápida sugeridos
    st.caption("💡 Sugerencias rápidas por palabras clave:")
    r_chips = [
        ("🪑 Silla de comer", "silla de comer"),
        ("🩺 Pediatra", "pediatra"),
        ("🦷 Odontopediatra", "odontopediatra"),
        ("👃 Aspirador nasal", "aspirador nasal"),
        ("🧴 Caléndula pañal", "calendula"),
        ("🦴 Osteópata", "osteopata"),
        ("🤱 Leche materna", "leche materna"),
        ("🥑 Consejos BLW", "blw")
    ]
    r_chip_cols = st.columns(len(r_chips))
    for col_c, (chip_lbl, chip_val) in zip(r_chip_cols, r_chips):
        col_c.button(
            chip_lbl,
            key=f"rec_chip_{chip_val}",
            use_container_width=True,
            on_click=set_recom_search,
            args=(chip_val,)
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Consulta y presentación de resultados
    recom_results = recommendations.search_recommendations(
        query=recom_search_text,
        category_filter=selected_recom_cat
    )

    # Mensaje de resultados
    if not recom_results:
        if recom_search_text.strip():
            st.warning(f"No encontramos recomendaciones que coincidan con '{recom_search_text.strip()}'.")
            st.info("💡 **Consejo:** Prueba con otra palabra o haz clic en **➕ Compartir Dato** para agregar una recomendación.")
        else:
            st.info("✨ **Aún no hay recomendaciones cargadas en la Tribu.**\n\nSé la primera en compartir un profesional de la salud de confianza, un producto útil para mamás y bebés o un tip de crianza haciendo clic en el botón **➕ Compartir Dato** arriba a la derecha.")
    else:
        if recom_search_text.strip():
            st.markdown(f"#### 🔎 Encontramos **{len(recom_results)}** recomendación(es) para *'{recom_search_text.strip()}'*:")
        else:
            st.markdown(f"#### 📋 Todas las recomendaciones disponibles ({len(recom_results)}):")

        for item in recom_results:
            cat_key = item.get("category", "tip")
            cat_info = recommendations.RECOM_CATEGORIES.get(cat_key, recommendations.RECOM_CATEGORIES["tip"])

            # Fecha formateada
            raw_date = item.get("created_at", "")
            date_display = ""
            if raw_date:
                try:
                    dt = datetime.strptime(str(raw_date).split(".")[0], "%Y-%m-%d %H:%M:%S")
                    date_display = dt.strftime("%d/%m/%Y")
                except Exception:
                    date_display = ""

            admin_badge = (
                '<span style="background-color: #FFF3C4; color: #8F5B00; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; margin-left: 0.5rem; border: 1px solid #FFE066;">👑 Administradora</span>'
                if item.get("is_admin_entry") else ""
            )

            # Tags de palabras clave
            keywords_raw = item.get("keywords") or ""
            kw_tags = [k.strip() for k in keywords_raw.split(",") if k.strip()]
            keywords_badges = "".join([
                f'<span style="background-color: #F1EDFC; color: #5D3799; padding: 0.2rem 0.55rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-right: 0.35rem; display: inline-block; margin-top: 0.3rem;">#{k}</span>'
                for k in kw_tags
            ])

            # Info de contacto
            contact_html = (
                f'<div style="background: #F9F8FD; border-left: 3px solid #7B5EA7; padding: 0.45rem 0.8rem; border-radius: 8px; font-size: 0.88rem; color: #3C2B54; margin: 0.65rem 0;">'
                f'📍 <b>Contacto / Ubicación:</b> {item["contact_info"]}'
                f'</div>'
            ) if item.get("contact_info") else ""

            keywords_html = (
                f'<div style="margin-top: 0.4rem;">{keywords_badges}</div>'
            ) if keywords_badges else ""

            card_html = (
                f'<div class="result-card" style="border-left: 5px solid {cat_info["border"]};">'
                f'<div class="card-header">'
                f'<div>'
                f'<span class="badge-cat" style="background-color: {cat_info["color"]}; color: {cat_info["text_color"]};">{cat_info["label"]}</span>'
                f'<span class="doc-title" style="margin-left: 0.5rem;">{item["title"]}</span>'
                f'{admin_badge}'
                f'</div>'
                f'<div style="font-size: 0.82rem; color: #7B708A;">'
                f'👤 <b>{item.get("author_name", "Familia")}</b>{f" • {date_display}" if date_display else ""}'
                f'</div>'
                f'</div>'
                f'<div class="snippet-text" style="font-size: 0.98rem; line-height: 1.6; margin-bottom: 0.5rem;">'
                f'{item["description"]}'
                f'</div>'
                f'{contact_html}'
                f'{keywords_html}'
                f'</div>'
            )

            with st.container():
                st.markdown(card_html, unsafe_allow_html=True)

                col_btn_link, col_btn_admin = st.columns([3.5, 2.5])

                with col_btn_link:
                    if item.get("link"):
                        cleaned_link = recommendations.clean_url(item["link"])
                        if cleaned_link:
                            st.link_button(cat_info["action_text"], cleaned_link, use_container_width=False)

                with col_btn_admin:
                    if st.session_state.get("es_admin", False):
                        col_e, col_d = st.columns(2)
                        with col_e:
                            if st.button("✏️ Editar", key=f"btn_edit_rec_{item['id']}", use_container_width=True):
                                modal_editar_recomendacion(item["id"])
                        with col_d:
                            if st.button("🗑️ Eliminar", key=f"btn_del_rec_{item['id']}", use_container_width=True):
                                modal_eliminar_recomendacion(item["id"], item["title"])
                    else:
                        st.caption("🔒 *Recomendación comunitaria (Solo editable por la administradora)*")

                st.markdown("<hr style='border: none; border-top: 1px dashed #E2DDF0; margin: 0.4rem 0 1rem 0;'>", unsafe_allow_html=True)


# =========================================================================
# SECCIÓN 2: BIBLIOTECA DIGITAL DE DOCUMENTOS (PDF, EPUB, NOTAS)
# =========================================================================
with tab_biblioteca:
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h3 style="color: #2D233C; margin-bottom: 0.2rem; font-weight: 700;">
            📚 Biblioteca de Libros y Archivos
        </h3>
        <p style="color: #6C5D81; font-size: 0.95rem; margin-bottom: 0;">
            Buscador inteligente en libros de nutrición, recetas, guías de sueño, protocolos APLV, primeros auxilios y notas comunitarias.
        </p>
    </div>
    """, unsafe_allow_html=True)

    def set_doc_search(term: str):
        st.session_state["doc_search_input"] = term

    if "doc_search_input" not in st.session_state:
        st.session_state["doc_search_input"] = ""

    col_search, col_cat = st.columns([2.5, 1.3])

    with col_search:
        doc_query = st.text_input(
            "¿Qué tema o receta buscas en los libros?",
            key="doc_search_input",
            placeholder="Ej: recetas calabaza, regresión 4 meses, RCP, leche APLV, odontopediatra..."
        )

    with col_cat:
        cat_options = {"todas": "🌟 Todas las categorías"}
        cat_options.update(indexer.CATEGORIES)
        selected_category = st.selectbox(
            "Filtrar categoría documental:",
            options=list(cat_options.keys()),
            format_func=lambda k: cat_options[k],
            key="select_doc_cat"
        )

    # Sugerencias rápidas documentales
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
        col.button(
            label,
            key=f"chip_doc_{term}",
            use_container_width=True,
            on_click=set_doc_search,
            args=(term,)
        )

    st.markdown("<br>", unsafe_allow_html=True)

    active_doc_query = doc_query.strip()

    # Si hay una búsqueda activa, avisar si también hay coincidencias en recomendaciones comunitarias
    if active_doc_query:
        matching_recoms = recommendations.search_recommendations(active_doc_query)
        if matching_recoms:
            st.info(f"💡 **Dato de la comunidad:** Encontramos **{len(matching_recoms)}** dato(s) en la sección **🌟 Directorio de Recomendaciones** relacionados con *'{active_doc_query}'* (ej: {matching_recoms[0]['title']}). Puedes consultarlos en la primera pestaña.")

        results = indexer.search_documents(active_doc_query, category_filter=selected_category)
        
        if results:
            st.markdown(f"#### 🔎 Encontramos **{len(results)}** página(s) o fragmento(s) para *'{active_doc_query}'*:")
            
            for idx, item in enumerate(results):
                cat_display = indexer.CATEGORIES.get(item['category'], item['category'].title())
                clean_rel = item['file_path'].replace("\\", "/")
                file_abs_path = indexer.BASE_DIR / clean_rel
                
                if not file_abs_path.exists():
                    candidate = indexer.DOCS_DIR / item['category'] / item['filename']
                    if candidate.exists():
                        file_abs_path = candidate
                    else:
                        matches = list(indexer.DOCS_DIR.rglob(item['filename']))
                        if matches:
                            file_abs_path = matches[0]
                
                with st.container():
                    doc_card_html = (
                        f'<div class="result-card">'
                        f'<div class="card-header">'
                        f'<div>'
                        f'<span class="badge-type">{item["file_type"]}</span>'
                        f'<span class="doc-title">&nbsp; {item["filename"]}</span>'
                        f'<span style="color: #7B708A; font-size: 0.85rem;"> • {item["section"]}</span>'
                        f'</div>'
                        f'<span class="badge-cat" style="background-color: #F1EDFC; color: #5D3799;">{cat_display}</span>'
                        f'</div>'
                        f'<div class="snippet-text">'
                        f'"{item["snippet_match"]}"'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(doc_card_html, unsafe_allow_html=True)
                    
                    col_exp, col_down = st.columns([4.2, 1.2])
                    with col_exp:
                        with st.expander(f"📖 Leer contexto completo ({item['section']})"):
                            st.write(item["content"])
                    
                    with col_down:
                        if file_abs_path.exists():
                            with open(file_abs_path, "rb") as f:
                                file_bytes = f.read()

                            mime_type = "application/octet-stream"
                            fn_lower = item["filename"].lower()
                            if fn_lower.endswith(".pdf"):
                                mime_type = "application/pdf"
                            elif fn_lower.endswith(".epub"):
                                mime_type = "application/epub+zip"
                            elif fn_lower.endswith(".txt"):
                                mime_type = "text/plain; charset=utf-8"

                            st.download_button(
                                label="📥 Descargar",
                                data=file_bytes,
                                file_name=item["filename"],
                                mime=mime_type,
                                key=f"down_{idx}_{item['id']}",
                                use_container_width=True
                            )
                        else:
                            st.caption("📄 *Ver texto*")
                    st.markdown("<hr style='border: none; border-top: 1px dashed #E2DDF0; margin: 0.6rem 0 1rem 0;'>", unsafe_allow_html=True)
        else:
            st.warning(f"No encontramos resultados en libros o archivos para '{active_doc_query}'.")
            st.info("💡 **Consejo:** Prueba con una palabra más general (ej: *calabaza*, *rutinas*, *fiebre*, *pecho*) o revisa la pestaña de Recomendaciones de la Tribu.")
    else:
        # Vista de inicio con categorías temáticas
        st.markdown("### 📚 Explora la Biblioteca por Categorías")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="cat-box" style="background: #F4FAF5; border-color: #D3ECD9;">
                <h4 style="color: #246B3C;">🥑 Alimentación y Recetas</h4>
                <p style="color: #43634C;">
                    BLW, BLISS, cortes seguros, papillas nutritivas, galletitas, muffins y libros de Sabrina Critzmann y Melisa Jurozdicki.
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
                    Cuadernillos de RCP pediátrico, prevención de asfixia con frutos secos, sanitización y botiquín familiar.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="cat-box" style="background: #FEFAF2; border-color: #F8E8C8;">
                <h4 style="color: #8C590E;">🥛 Alergias y APLV</h4>
                <p style="color: #6C5535;">
                    Protocolos APLV, listados de alimentos aptos, introducción de alérgenos y formularios médicos.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="cat-box" style="background: #FAF7F2; border-color: #ECE5D8;">
                <h4 style="color: #665039;">🌱 Crianza Respetuosa</h4>
                <p style="color: #655B50;">
                    Bésame Mucho (Carlos González), Hoy No Es Siempre y material de acompañamiento respetuoso.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("👆 Escribe cualquier duda en el buscador arriba o toca una de las sugerencias para ver fragmentos de los libros.")
