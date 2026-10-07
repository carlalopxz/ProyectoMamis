# 🍼 Rincón de Familias - Buscador de Recomendaciones

Una aplicación web privada y fácil de usar diseñada para que un grupo cerrado de madres y padres pueda buscar rápidamente recomendaciones sobre recetas, profesionales de la salud y productos para bebés a partir de archivos **PDF**, libros **EPUB** y chats exportados de **WhatsApp**.

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

## 🔒 Clave de Acceso del Grupo

* Por defecto, la clave de ingreso es: `familias2025`
* Puedes cambiarla definiendo la variable de entorno `GRUPO_PIN` o editando la variable `CLAVE_GRUPO` al principio de `app.py`.

---

## 📂 Cómo agregar tus propios documentos

Tienes dos formas muy sencillas:

### Opción 1: Desde la propia página web (Más fácil)
1. Inicia sesión en la web.
2. En la barra lateral izquierda, ve a la sección **"📤 Agregar Nuevo Archivo"**.
3. Arrastra tu PDF, EPUB o archivo `.txt` de WhatsApp.
4. Selecciona la categoría (*Recetas*, *Profesionales*, *Productos* o *General*) y pulsa **"Guardar e Indexar"**.

### Opción 2: Copiando los archivos en las carpetas
Copia tus archivos directamente en las carpetas de tu proyecto:
* `documentos/recetas/` (libros de cocina, guías de alimentación complementaria, BLW)
* `documentos/profesionales/` (pediatras, odontopediatras, puericultoras, osteópatas)
* `documentos/productos/` (cochecitos, cunas, aspiradores, juguetes)
* `documentos/general/` (cualquier otro archivo)

Luego, haz clic en el botón **"🔄 Actualizar / Reindexar Archivos"** en la barra lateral de la web.

---

## 🌐 Cómo compartirlo por internet con tu grupo cerrado (Gratis)

Para que las demás familias puedan entrar desde su celular mediante un enlace:

1. Crea un repositorio privado o público en tu cuenta de [GitHub](https://github.com).
2. Sube los archivos de este proyecto (`app.py`, `indexer.py`, `requirements.txt`, etc.).
3. Entra a [Streamlit Community Cloud](https://share.streamlit.io/) e inicia sesión con GitHub.
4. Haz clic en **"Create App"**, selecciona tu repositorio y el archivo `app.py`.
5. ¡Listo! Te dará un enlace (ej: `https://familias-datos.streamlit.app`) que puedes enviar por el grupo de WhatsApp junto con la clave de acceso.
