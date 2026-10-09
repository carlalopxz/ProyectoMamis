# 🍼 Rincón de la Tribu - Directorio de Recomendaciones y Biblioteca Digital

Una aplicación web privada y fácil de usar diseñada para que un grupo cerrado de madres y padres pueda:
1. **Consultar y compartir recomendaciones** de profesionales de la salud (pediatras, odontopediatras, osteópatas), productos esenciales para madres y bebés (sillas de comer, aspiradores nasales, cremas) y consejos/tips prácticos de crianza.
2. **Buscar por palabras clave** (por ejemplo: `silla de comer`, `pediatra`, `frenillo`, `calendula`) con enlaces directos al producto, consultorio, WhatsApp o web.
3. **Explorar y buscar en libros y guías en PDF y EPUB** (recetas BLW, protocolos APLV, sueño infantil, primeros auxilios/RCP).

---

## 🔑 Claves de Acceso y Permisos

* **Clave de Acceso del Grupo (Familias):** `familias2025`
  * Permite consultar todas las recomendaciones y libros.
  * Permite compartir nuevas recomendaciones comunitarias.
  * *Por seguridad de la comunidad, las recomendaciones cargadas no pueden ser editadas ni borradas por otras personas.*
* **Clave de Administradora (Carla):** `admin2025`
  * Te permite ingresar directamente con rol de Administradora o activarlo desde la barra lateral.
  * Como administradora tienes botones exclusivos para **✏️ Editar** y **🗑️ Eliminar** cualquier recomendación cargada en el sistema.
  * Puedes personalizar estas claves usando las variables de entorno o secrets `GRUPO_PIN` y `ADMIN_PIN`.

---

## 🌟 Cómo funciona la Sección de Recomendaciones

1. **Búsqueda por palabras clave:**
   * Escribe cualquier término en el buscador (ej: `silla de comer`).
   * El sistema filtra al instante buscando en títulos, descripciones, palabras clave asociadas y datos de contacto, ignorando mayúsculas y acentos.
   * También puedes pulsar en las sugerencias rápidas (chips) como *🪑 Silla de comer*, *🩺 Pediatra*, *🦷 Odontopediatra*, etc.
2. **Filtros por categoría:**
   * 🩺 **Profesionales de la Salud** (médicas, puericultoras, terapeutas).
   * 🧸 **Productos para Mamás y Bebés** (artículos de puericultura, sillas, cochecitos).
   * 💡 **Consejos y Tips** (pautas de sueño, deglución, banco de leche).
3. **Enlaces directos:**
   * Cada tarjeta incluye botones como **🛒 Ver Producto / Link** o **📞 Contactar al Profesional** que llevan directamente a la tienda, WhatsApp o red social correspondiente.
4. **Carga y Edición:**
   * Cualquier mamá puede hacer clic en **➕ Compartir Dato** para sumar un dato nuevo.
   * Una vez publicado, queda bloqueado para los usuarios comunes con el aviso *"Recomendación comunitaria (Solo editable por la administradora)"*.
   * Cuando activas el **Modo Administradora**, aparecen los botones **✏️ Editar** y **🗑️ Eliminar** en cada publicación para corregir enlaces, textos o dar de baja publicaciones.

---

## 🚀 Cómo iniciar la aplicación en tu computadora

1. Abre una terminal de PowerShell en esta carpeta.
2. Activa el entorno virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Ejecuta la aplicación:
   ```powershell
   streamlit run app.py
   ```
4. Se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## 📂 Cómo agregar nuevos libros o documentos a la biblioteca

### Opción 1: Desde la propia página web (Más fácil)
1. Inicia sesión en la web.
2. En la barra lateral izquierda, ve a **"📤 Subir Documento a Biblioteca"**.
3. Arrastra tu PDF, EPUB o archivo `.txt`.
4. Selecciona la categoría (*Recetas*, *Sueño*, *Salud y Seguridad*, *Lactancia*, etc.) y pulsa **"Guardar e Indexar"**.

### Opción 2: Copiando los archivos en las carpetas
Copia tus archivos directamente en las subcarpetas dentro de `documentos/` y pulsa **"🔄 Reindexar Archivos Locales"** en la barra lateral.

---

## 🌐 Cómo compartirlo por internet con tu grupo cerrado (Gratis)

1. Sube los archivos a un repositorio de [GitHub](https://github.com).
2. Entra a [Streamlit Community Cloud](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
3. Haz clic en **"Create App"**, selecciona tu repositorio y el archivo `app.py`.
4. En **Advanced Settings > Secrets**, puedes configurar las claves privadas:
   ```toml
   GRUPO_PIN = "familias2025"
   ADMIN_PIN = "admin2025"
   ```
5. ¡Listo! Te dará un enlace (ej: `https://rincon-tribu.streamlit.app`) para compartir con el grupo.
