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
    [F1] o [:help]   › Alternar este manual
    [TAB] / [S-TAB]  › Cambiar foco (Título / Etiquetas / Cuerpo)
    [Ctrl+G]         › Ir a Barra de Comandos
    [Ctrl+O]         › Abrir Navegador (Cargar Borradores/Publicados)

  ◆ ESCRITURA Y PRODUCTIVIDAD
    ────────────────────────────────────────────────────────────────────
    [:sprint NN]     › Iniciar Sprint de NN minutos
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
        
        "words": "Words",
        "read": "Read",
        "sprint": "SPRINT",
        "done": "DONE",
        "status": "Status"
    },
    "es": {
        "words": "Palabras",
        "read": "Lectura",
        "sprint": "SPRINT",
        "done": "LISTO",
        "status": "Estado"
    }
}