# assets.py

BANNER = r"""
    ██████╗ ██╗     ██╗███╗   ███╗       ██████╗ ██╗   ██╗
    ██╔══██╗██║     ██║████╗ ████║       ██╔══██╗╚██╗ ██╔╝
    ██████╔╝██║     ██║██╔████╔██║       ██████╔╝ ╚████╔╝ 
    ██╔══██╗██║     ██║██║╚██╔╝██║       ██╔═══╝   ╚██╔╝  
    ██████╔╝███████╗██║██║ ╚═╝ ██║  ██╗  ██║        ██║   
    ╚═════╝ ╚══════╝╚═╝╚═╝     ╚═╝  ╚═╝  ╚═╝        ╚═╝    
        DISTRACTION FREE WRITING FOR GOOGLE BLOGGER V.1.0
"""

# Dictionary for multi-language Help
HELP_TEXT = {
    "en": """
╔══════════════════════════════════════════════════════════════════════╗
║  BLIM.PY │ COMMAND REFERENCE MANUAL                                  ║
╚══════════════════════════════════════════════════════════════════════╝

  ◆ NAVIGATION & INTERFACE
    ────────────────────────────────────────────────────────────────────
    [F1] or [:help]  › Toggle this Manual
    [TAB] / [S-TAB]  › Cycle focus (Title / Tags / Body)
    [Ctrl+G]         › Jump to Command Bar
    [Ctrl+O]         › Open Post Browser (Fetch Drafts & Live)
    [:eng] or [:spa] › Switch Language (English/Spanish)

  ◆ WRITING & PRODUCTIVITY
    ────────────────────────────────────────────────────────────────────
    [:sprint NN]     › Start a NN minute Word Sprint
    [:restore]       › Recover content from last crash/exit
    [:new]           › Clear screen for a fresh start
    [Ctrl+T]         › Toggle Ghost Mode (Hide UI while writing)
    [Ctrl+D]         › Run Spellcheck / Dictionary Check

  ◆ PUBLISHING & SAVING
    ────────────────────────────────────────────────────────────────────
    [Ctrl+S]         › Save as DRAFT (Uploads to Blogger)
    [Ctrl+P]         › PUBLISH LIVE (Public visibility)
    [Enter]          › (In Browser) Load selected post

  ◆ FORMATTING (MARKDOWN)
    ────────────────────────────────────────────────────────────────────
    [Ctrl+B]         › **Bold**
    [Ctrl+K]         › *Italic*
    [Control+L]      › Insert List Item
    [Control+Q]      › Blockquote 
    Headers          › # H1, ## H2, ### H3
    Links            › [Text](url)

────────────────────────────────────────────────────────────────────────
 [Press F1 to Resume Writing]
""",
    "es": """
╔══════════════════════════════════════════════════════════════════════╗
║  BLIM.PY │ MANUAL DE REFERENCIA                                      ║
╚══════════════════════════════════════════════════════════════════════╝

  ◆ NAVEGACIÓN E INTERFAZ
    ────────────────────────────────────────────────────────────────────
    [F1] o [:help]   › Activar este manual
    [TAB] / [S-TAB]  › Cambiar foco (Título / Etiquetas / Cuerpo)
    [Ctrl+G]         › Ir a Barra de Comandos
    [Ctrl+O]         › Abrir Navegador (Cargar Borradores/Publicados)
    [:eng] o [:spa]  › Selecciona idioma (Inglés/Español)

  ◆ ESCRITURA Y PRODUCTIVIDAD
    ────────────────────────────────────────────────────────────────────
    [:sprint NN]     › Iniciar Sprint de Escritura de NN minutos
    [:restore]       › Recuperar contenido tras error/salida
    [:new]           › Limpiar pantalla (Nueva entrada)
    [Ctrl+T]         › Modo Fantasma (Ocultar interfaz al escribir)
    [Ctrl+D]         › Verificar Ortografía (Diccionario)

  ◆ PUBLICACIÓN Y GUARDADO
    ────────────────────────────────────────────────────────────────────
    [Ctrl+S]         › Guardar BORRADOR (Sube a Blogger)
    [Ctrl+P]         › PUBLICAR (Visible al público)
    [Enter]          › (En Navegador) Cargar entrada seleccionada

  ◆ FORMATO (MARKDOWN)
    ────────────────────────────────────────────────────────────────────
    [Ctrl+B]         › **Negrita**
    [Ctrl+K]         › *Cursiva*
    [Control+L]      › Crear Elemento de Lista
    [Control+Q]      › Citar Bloque
    Encabezados      › # T1, ## T2, ### T3
    Enlaces          › [Texto](url)
────────────────────────────────────────────────────────────────────────
 [Presiona F1 para volver a escribir]
"""
}

# Dictionary for UI labels
TRANSLATIONS = {
    "en": {
        "ui": {
            "title": "Title: ",
            "tags": "Tags: ",
            "command": "Enter Command: ",
            "new_post": "[NEW]",
            "lang_feedback": "Language: ENGLISH",
            "header": " BLIM.PY | BLOGGER DISTRACTION-FREE EDITOR",
            "title_prompt": "Title: ",
            "tags_prompt": "Tags:  ",
            "command_prompt": "Enter Command: ",
            "warning_prompt": "POST UNSAVED! Proceed? (y/n): ",
            "browser_title": "  POST BROWSER",
            "fetching": "Fetching posts...",
        },
        "messages": {
            "offline": "⚠️ OFFLINE MODE: Google unreachable.",
            "recovery_found": "RECOVERY FILE FOUND! Type :restore",
            "no_errors": "✅ No errors",
            "errors_found": "❌ {count} errors: {sample}...",
            "save_success": "Saved with Markdown!",
            "save_fail": "SAVE FAILED: Offline",
            "empty_doc": "Empty document",
            "sprint_start": "🚀 Sprint Started! Goal: {mins}m",
            "sprint_done": "★ DONE! +{net_gain} words ★",
        },
        "status": {
            "words": "Words",
            "read": "Read",
            "sprint": "SPRINT",
            "done": "DONE",
            "status": "STATUS",
        }
    },
    "es": {
        "ui": {
            "title": "Título: ",
            "tags": "Etiquetas: ",
            "command": "Introduce Commando: ",
            "new_post": "[NUEVO]",
            "lang_feedback": "Idioma: ESPAÑOL",
            "header": " BLIM.PY | EDITOR SIN DISTRACCIONES PARA BLOGGER",
            "title_prompt": "Título: ",
            "tags_prompt": "Etiquetas: ",
            "command_prompt": "Comando: ",
            "warning_prompt": "¡POST SIN GUARDAR! ¿Continuar? (y/n): ",
            "browser_title": "  NAVEGADOR DE ENTRADAS",
            "fetching": "Buscando entradas...",
        },
        "messages": {
            "offline": "⚠️ MODO OFFLINE: Google inaccesible.",
            "recovery_found": "¡ARCHIVO DE RECUPERACIÓN! Escribe :restore",
            "no_errors": "✅ Sin errores",
            "errors_found": "❌ {count} errores: {sample}...",
            "save_success": "¡Guardado con Markdown!",
            "save_fail": "ERROR: Sin conexión",
            "empty_doc": "Documento vacío",
            "sprint_start": "🚀 ¡Sprint iniciado! Meta: {mins}m",
            "sprint_done": "★ ¡LISTO! +{net_gain} palabras ★",
        },
        "status": {
            "words": "Palabras",
            "read": "Lectura",
            "sprint": "SPRINT",
            "done": "LISTO",
            "status": "ESTADO",
        }
    }
}