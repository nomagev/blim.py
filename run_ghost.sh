#!/bin/bash

# --- 1. ENVIRONMENT CHECK ---
echo "👻 Blim.py Ghost Suite: Checking Environment..."

# Activate venv if it exists
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated."
    fi
fi

# --- 2. THE SMART CHECK ---
GHOST_FILE="tests/ghost_test.py"

if [ -f "$GHOST_FILE" ]; then
    echo "📄 $GHOST_FILE already exists. Keeping your current version."
else
    echo "✨ $GHOST_FILE not found. Creating the default Self-Documenting Ghost..."
    mkdir -p tests
    cat << 'EOF' > "$GHOST_FILE"
import asyncio
import time
from prompt_toolkit.application import Application
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.layout import Layout
from prompt_toolkit.enums import EditingMode
from blim import BlimEditor, blim_style

async def run_ghost_session():
    with create_pipe_input() as cp:
        editor = BlimEditor(test_mode=True)
        app = Application(
            layout=Layout(editor.container, focused_element=editor.body_field),
            key_bindings=editor.kb,
            full_screen=True, 
            style=blim_style,
            input=cp,
            editing_mode=EditingMode.EMACS,
        )

        async def type_log(message):
            app.layout.focus(editor.body_field)
            editor.body_field.text += f"\n\n> {message.upper()}\n"
            app.invalidate()
            await asyncio.sleep(1.5)

        async def ghost_actions():
            try:
                await asyncio.sleep(2) 
                editor.body_field.text = "--- BLIM GHOST PROTOCOL START ---"

                await type_log("Toggling Ghost Mode (Ctrl+T)...")
                cp.send_text("\x14") 
                await asyncio.sleep(2)
                
                await type_log("Disabling Ghost Mode to show Title/Tags...")
                cp.send_text("\x14") 
                await asyncio.sleep(1)

                await type_log("Changing UI language to Spanish ('es')...")
                editor.lang = "es"
                editor.apply_language("es")
                app.invalidate()
                await asyncio.sleep(2)

                await type_log("Changing UI language back to English ('en')...")
                editor.lang = "en"
                editor.apply_language("en")
                app.invalidate()

                await type_log("Opening the Help Sidebar (F1)...")
                editor.show_help = True
                app.invalidate()
                await asyncio.sleep(2)
                editor.show_help = False
                app.invalidate()

                await type_log("Focusing Title field...")
                app.layout.focus(editor.title_field)
                cp.send_text("\x15GHOST TITLE VERIFIED")
                await asyncio.sleep(1)

                await type_log("Focusing Tags field...")
                app.layout.focus(editor.tags_field)
                cp.send_text("\x15robot, testing, automation")
                await asyncio.sleep(1)

                await type_log("Returning to body for Markdown check...")
                app.layout.focus(editor.body_field)
                cp.send_text("\n\nTesting **Bold** conversion...")
                await asyncio.sleep(1)
                
                html = editor._parse_markdown(editor.body_field.text)
                editor.last_spell_report = "MD OK" if "<b>" in html else "MD FAIL"
                app.invalidate()
                
                await type_log("Ghost test complete. Powering down.")
                await asyncio.sleep(2)
            finally:
                app.exit()

        await asyncio.gather(app.run_async(), ghost_actions())

if __name__ == "__main__":
    asyncio.run(run_ghost_session())
EOF
fi

# --- 3. LAUNCH ---
echo "🚀 Launching Ghost Test..."
python3 "$GHOST_FILE"