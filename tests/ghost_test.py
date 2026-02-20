import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            """Types a message into the body field as a running log."""
            app.layout.focus(editor.body_field)
            # Add a visual separator
            editor.body_field.text += f"\n\n> {message.upper()}\n"
            app.invalidate()
            await asyncio.sleep(1.5)

        async def ghost_actions():
            try:
                await asyncio.sleep(2) 
                editor.body_field.text = "--- BLIM GHOST PROTOCOL START ---"

                # --- 1. GHOST MODE ---
                await type_log("Toggling Ghost Mode (Ctrl+T)...")
                cp.send_text("\x14") 
                await asyncio.sleep(2)
                
                await type_log("Disabling Ghost Mode to show Title/Tags...")
                cp.send_text("\x14") 
                await asyncio.sleep(1)

                # --- 2. LANGUAGE ---
                await type_log("Changing UI language to Spanish ('es')...")
                editor.lang = "es"
                editor.apply_language("es")
                app.invalidate()
                await asyncio.sleep(2)

                await type_log("Changing UI language back to English ('en')...")
                editor.lang = "en"
                editor.apply_language("en")
                app.invalidate()

                # --- 3. F1 HELP ---
                await type_log("Opening the Help Sidebar (F1)...")
                editor.show_help = True
                app.invalidate()
                await asyncio.sleep(2)
                editor.show_help = False
                app.invalidate()

                # --- 4. TITLE & TAGS ---
                await type_log("Moving focus to Title field...")
                app.layout.focus(editor.title_field)
                cp.send_text("\x15GHOST TITLE VERIFIED")
                await asyncio.sleep(1)

                await type_log("Moving focus to Tags field...")
                app.layout.focus(editor.tags_field)
                cp.send_text("\x15robot, testing, automation")
                await asyncio.sleep(1)

                # --- 5. MARKDOWN ---
                await type_log("Returning to body to test Markdown rendering...")
                app.layout.focus(editor.body_field)
                cp.send_text("\n\nTesting **Bold** and *Italic*...")
                await asyncio.sleep(1)
                
                html = editor._parse_markdown(editor.body_field.text)
                if "<b>" in html:
                    await type_log("Markdown Verification: SUCCESS")
                else:
                    await type_log("Markdown Verification: FAILED")
                
                await type_log("Ghost test complete. Exiting in 3 seconds...")
                await asyncio.sleep(3)
                
            finally:
                app.exit()

        await asyncio.gather(app.run_async(), ghost_actions())

if __name__ == "__main__":
    asyncio.run(run_ghost_session())