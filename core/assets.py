# assets.py

import os

# Get the path to where banner.txt lives
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
BANNER_PATH = os.path.join(ASSETS_DIR, 'banner.txt')

def get_banner():
    try:
        with open(BANNER_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "BLIM.PY" # Fallback if file is missing

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
    [:speed NN]      › Set reading speed (words per minute)
    [:add WORD]      › Add WORD to custom dictionary
    [:addall]        › Add all underlined words to dictionary
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
    Strikethrough    › ~~Strikethrough~~

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
    [:speed NN]      › Establecer velocidad de lectura (palabras por minuto)
    [:add PALABRA]   › Agregar PALABRA al diccionario personalizado
    [:addall]        › Agregar todas las palabras subrayadas al diccionario
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
    Tachado          › ~~Tachado~~
────────────────────────────────────────────────────────────────────────
 [Presiona F1 para volver a escribir]
"""
}

# Version info

VERSION = "1.7.4"

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
            "browser_hint": "Press ENTER to load, Control+O to exit.",
            'sprint_start': "🚀 Sprint Started! Goal: {mins}m",
            'sprint_done': "★ DONE! +{gain} words ★",
            'ghost_on': "Ghost Mode: ON",
            'ghost_off': "Ghost Mode: OFF",
            'offline': "⚠️ OFFLINE MODE: Google unreachable.",
            'save_fail': "SAVE FAILED: Offline",
            'load_error': "Load Error",
            'empty_doc': "Empty document",
            'ready': "Ready ({lang})",
            'recovery_found': "RECOVERY FILE FOUND! Type :restore",
            'no_errors': "✅ No errors ({lang})",
            'errors_found': "❌ {count} errors: {list}...",
            'saved': "Saved with Markdown!",
            'save_error': "Save Error: {error}",
            'status_draft': "DRAFT",
            'status_live': "LIVE",
            'speed_set': "Reading speed: {speed} wpm",
            'help_btn': "Help",
            'added_to_dict': "Added '{word}' to dictionary.",
            'addall_success': "All {count} words added to dictionary.",
            'addall_none': "No words to add to dictionary.",
            'addall_no_spell': "Dictionary not active. Press Ctrl+D first",
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
            "read": "min Read",
            "sprint": "Sprint",
            "done": "DONE",
            "status": "STATUS",
        }
    },
    "es": {
        "ui": {
            "title": "Título: ",
            "tags": "Etiquetas: ",
            "command": "Introduce Comando: ",
            "new_post": "[NUEVO]",
            "lang_feedback": "Idioma: ESPAÑOL",
            "header": " BLIM.PY | EDITOR SIN DISTRACCIONES PARA BLOGGER",
            "title_prompt": "Título: ",
            "tags_prompt": "Etiquetas: ",
            "command_prompt": "Comando: ",
            "warning_prompt": "¡POST SIN GUARDAR! ¿Continuar? (y/n): ",
            "browser_title": "  NAVEGADOR DE ENTRADAS",
            "fetching": "Buscando entradas...",
            "browser_hint": "ENTER para cargar entrada, Control+O para salir.",
            'sprint_start': "🚀 ¡Sprint iniciado! Meta: {mins}m",
            'sprint_done': "★ ¡LISTO! +{gain} palabras ★",
            'ghost_on': "Modo Fantasma: ACTIVADO",
            'ghost_off': "Modo Fantasma: DESACTIVADO",
            'offline': "⚠️ MODO OFFLINE: Google inaccesible.",
            'save_fail': "ERROR AL GUARDAR: Offline",
            'load_error': "Error de carga",
            'empty_doc': "Documento vacío",
            'ready': "Listo ({lang})",
            'recovery_found': "¡ARCHIVO DE RECUPERACIÓN! Escribe :restore",
            'no_errors': "✅ Sin errores ({lang})",
            'errors_found': "❌ {count} errores: {list}...",
            'saved': "¡Guardado con Markdown!",
            'save_error': "Error al guardar: {error}",
            'status_draft': "BORRADOR",
            'status_live': "PUBLICADO",
            'speed_set': "Velocidad de lectura: {speed} ppm",
            'help_btn': "Ayuda",
            'added_to_dict': "'{word}' añadida al diccionario.",
            'addall_success': "Se agregaron {count} palabras al diccionario.",
            'addall_none': "No hay palabras que agregar al diccionario.",
            'addall_no_spell': "El diccionario no está activo. Presiona Ctrl+D primero.",
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
            "read": "Min Lectura",
            "sprint": "Sprint",
            "done": "LISTO",
            "status": "ESTADO",
        }
    }
}