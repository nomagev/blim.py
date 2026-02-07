# Blim.py
# Copyright (C) 2026 Nomagev

from email.mime import text
import os, sys, time, json, re, asyncio
from prompt_toolkit import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, ConditionalContainer, DynamicContainer
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import TextArea, Label
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.html import HtmlLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.application import get_app

from spellchecker import SpellChecker
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from assets import BANNER, HELP_TEXT, TRANSLATIONS

blim_style = Style.from_dict({
    'status-warn': 'bg:#ff0000 #ffffff bold', 
    'prompt-normal': '#00ff00 bold',
    'spell-error': 'fg:#ffaa00 bold',
    'status-bar': 'bg:#222222 #00ff00',
    'help-text': 'fg:#00ff00 bg:#000000', 
    'body': 'fg:#00ff00 bg:#000000',
    'reverse-header': 'reverse bold',
})

class BlimEditor:
    def __init__(self):
        self._load_paths()
        self._load_config()
        
        # --- State ---
        self.is_offline = False
        self.current_post_id = None
        self.post_status = "NEW"
        self.last_saved_content = ""
        self.is_warning_mode = False
        self.pending_action = None 
        self.show_help = False
        self.show_browser = False
        self.pending_delete = False
        self.browser_index = 0
        self.posts_list = []
        self.start_time = time.time()
        self.last_spell_report = f"Ready ({self.lang.upper()})"
        self.sprint_active = False
        self.sprint_time_left = 0
        self.ghost_mode_enabled = False 
        self.last_interaction_time = time.time()
        self.ghost_timeout = 3 

        self.spell = SpellChecker(language=self.lang)
        self.service = self.authenticate()
        
        # --- UI Fields ---
        self._init_ui_components()

        # --- GHOST MODE WAKE-UP ---
        def wake_up(buffer):
            self.last_interaction_time = time.time()

        self.body_field.buffer.on_text_changed += wake_up

        self._init_layout()
        self.kb = KeyBindings()
        self.setup_bindings()

        if os.path.exists(self.recovery_path):
            self.last_spell_report = "RECOVERY FILE FOUND! Type :restore"

    def _load_paths(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_path, 'config.json')
        self.secrets_path = os.path.join(self.base_path, 'client_secrets.json')
        self.token_path = os.path.join(self.base_path, 'token.json')
        self.recovery_path = os.path.join(self.base_path, '.recovery_blim.tmp')

    def _load_config(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump({"blog_id": "YOUR_ID", "word_goal": 500, "language": "es"}, f)
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.blog_id = str(config.get("blog_id")).strip()
            self.word_goal = config.get("word_goal", 500)
            self.lang = config.get("language", "es")

    def _init_ui_components(self):
        # Added focus_on_click=True to restore mouse support per field
        self.title_field = TextArea(height=1, prompt='Title: ', multiline=False, focus_on_click=True)
        self.tags_field = TextArea(height=1, prompt='Tags:  ', multiline=False, focus_on_click=True)
        self.body_field = TextArea(scrollbar=True, line_numbers=True, lexer=PygmentsLexer(HtmlLexer), wrap_lines=True, focus_on_click=True)
        self.command_field = TextArea(height=1, prompt='Enter Command: ', style='class:prompt-normal', multiline=False, accept_handler=self.handle_normal_input, focus_on_click=True)
        self.warning_field = TextArea(height=1, prompt='UNSAVED! Proceed? (y/n): ', style='class:status-warn', multiline=False, accept_handler=self.handle_warning_input)
        help_content = HELP_TEXT.get(self.lang, HELP_TEXT["en"]).strip()
        self.help_field = TextArea(text=help_content, read_only=True, style='class:help-text')
        self.browser_field = TextArea(text="Fetching posts...", read_only=True, style='class:help-text')

    def _init_layout(self):
        # 1. We define the "Normal" bars
        self.header_bar = VSplit([Window(), Label(text=" BLIM.PY | DISTRACTION-FREE WRITER ", style="class:reverse-header"), Window()], height=1)
        self.status_bar_view = VSplit([Window(), Label(text=self.get_status_text, style='class:status-bar'), Window()], height=1)
        self.command_view = VSplit([Window(), self.command_field, Window()], height=1)
        self.warning_view = VSplit([Window(), self.warning_field, Window()], height=1)

        # 2. These "Dynamic" versions check the timer 10 times a second
        # If is_ui_visible() is False, they return an empty Window (vanishing effect)
        self.header_row = DynamicContainer(lambda: self.header_bar if self.is_ui_visible() else Window(height=1))
        self.status_row = DynamicContainer(lambda: self.status_bar_view if self.is_ui_visible() else Window(height=1))
        
        # 3. Metadata logic (Titles/Tags) - also vanishes but keeps space
        self.metadata_row = DynamicContainer(lambda: HSplit([self.title_field, self.tags_field, Window(height=1, char='-')]) if self.is_ui_visible() else Window(height=3))

        # 4. The Main Writing area
        self.main_stack = HSplit([
            ConditionalContainer(content=HSplit([self.metadata_row, self.body_field]), filter=Condition(lambda: not self.show_help and not self.show_browser)),
            ConditionalContainer(content=self.help_field, filter=Condition(lambda: self.show_help)),
            ConditionalContainer(content=self.browser_field, filter=Condition(lambda: self.show_browser)),
        ], width=80)

        # 5. THE MASTER ASSEMBLY
        # This is the vertical stack of the whole app
        self.container = HSplit([
            self.header_row,                                     # Top Bar
            VSplit([Window(), self.main_stack, Window()]),       # Writing Area
            DynamicContainer(lambda: self.warning_view if self.is_warning_mode else self.command_view), # Command Bar
            self.status_row                                      # Bottom Bar
        ])

    def is_ui_visible(self):
        # 1. If Ghost Mode is OFF, show UI
        if not self.ghost_mode_enabled:
            return True
        
        # 2. If we are NOT in the body, show UI 
        try:
            app = get_app()
            if app.layout.current_buffer != self.body_field.buffer:
                return True
        except:
            return True

        # 3. Only hide if the timer has expired (3 seconds)
        return (time.time() - self.last_interaction_time) < self.ghost_timeout
    
    def authenticate(self):
        from google.auth.exceptions import TransportError
        creds = None
        self.is_offline = False 
        try:
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.secrets_path, ['https://www.googleapis.com/auth/blogger'])
                    creds = flow.run_local_server(port=0)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            return build('blogger', 'v3', credentials=creds)
        except (TransportError, Exception):
            self.is_offline = True
            self.last_spell_report = "⚠️ OFFLINE MODE: Google unreachable."
            return None

    def get_status_text(self):
        from assets import TRANSLATIONS
        t = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]) # Fallback to English
        
        dirty = "*" if self.is_dirty() else ""
        words, read_min = self.calculate_stats()
        
        # Using the dictionary for "DONE" and "Words/Palabras"
        goal_label = t["done"] if words >= self.word_goal else f"{words}/{self.word_goal}"
        
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        
        sprint_label = f" | {t['sprint']}: {divmod(self.sprint_time_left, 60)[0]:02d}:{divmod(self.sprint_time_left, 60)[1]:02d}" if self.sprint_active else ""
        
        return f" [{self.post_status}]{dirty} | {goal_label} | {t['read']}: {read_min}m{sprint_label} | {mins:02d}:{secs:02d} | {self.last_spell_report} "

    def is_dirty(self): return self.body_field.text.strip() != self.last_saved_content.strip()

    def handle_normal_input(self, buffer):
        user_input = buffer.text.strip().lower()
        if not user_input:
            get_app().layout.focus(self.body_field)
            return
        if user_input == ':new': self.start_new_post()
        elif user_input in [':q', ':exit']:
            if not self.is_dirty(): get_app().exit()
            else:
                self.is_warning_mode = True
                self.pending_action = "quit"
                get_app().layout.focus(self.warning_field)
        elif user_input == ':help':
            self.show_help, self.show_browser = True, False
        elif user_input == ':restore': self.load_recovery()
        elif user_input.startswith(':sprint'):
            parts = user_input.split()
            self.start_sprint(parts[1] if len(parts) > 1 else 25)
        elif user_input.isdigit(): 
            self.fetch_and_load(user_input)
            get_app().layout.focus(self.body_field)
        buffer.text = ""

    def handle_warning_input(self, buffer):
        choice = buffer.text.strip().lower()
        if choice == 'y':
            if self.pending_action == "quit": get_app().exit()
            else: self._force_clear_all(); self.is_warning_mode = False
        else:
            self.is_warning_mode = False
            get_app().layout.focus(self.body_field)
        buffer.text = ""

    def start_new_post(self):
        if self.is_dirty():
            self.is_warning_mode, self.pending_action = True, "new"
            get_app().layout.focus(self.warning_field)
        else: self._force_clear_all()

    def _force_clear_all(self):
        self.current_post_id, self.post_status = None, "NEW"
        self.title_field.text = self.tags_field.text = self.body_field.text = self.last_saved_content = ""
        get_app().layout.focus(self.title_field)

    def fetch_recent_posts(self):
        if self.is_offline or not self.service:
            return
        try:
            # We explicitly ask for BOTH Live and Draft posts
            posts_data = self.service.posts().list(
                blogId=self.blog_id, 
                maxResults=20, 
                status=['LIVE', 'DRAFT'], # Ensure 'DRAFT' is included here
                view='AUTHOR'
            ).execute()
            
            items = posts_data.get('items', [])
            self.posts_list = [{'id': p['id'], 'title': p.get('title', '(Untitled)'), 'status': p.get('status', 'DRAFT')} for p in items]
            self.render_browser()
        except Exception as e:
            self.browser_field.text = f"Fetch Error: {str(e)[:20]}"

    def render_browser(self):
        width = 76
        lines = [" ╔" + "═"*(width-2) + "╗", " ║  POST BROWSER" + " "*(width-17) + "║", " ╠" + "═"*(width-2) + "╣"]
        for i, post in enumerate(self.posts_list):
            prefix = " › " if i == self.browser_index else "   "
            lines.append(f" ║ {prefix}[{post['status'][0]}] {post['title'][:55]}".ljust(width) + "║")
        while len(lines) < 18: lines.append(" ║".ljust(width) + "║")
        lines.append(" ╚" + "═"*(width-2) + "╝")
        self.browser_field.text = "\n".join(lines)

    def fetch_and_load(self, post_id):
        try:
            post = self.service.posts().get(blogId=self.blog_id, postId=post_id, view='AUTHOR').execute()
            self.current_post_id, self.post_status = post['id'], post.get('status', 'LIVE')
            self.title_field.text = post.get('title', '')
            self.tags_field.text = ", ".join(post.get('labels', []))
            self.body_field.text = self.last_saved_content = self.clean_html_for_editor(post.get('content', ''))
        except: self.last_spell_report = "Load Error"

    def calculate_stats(self):
        text = self.body_field.text.strip()
        word_count = len(text.split()) if text else 0
        # 225 wpm is the standard for adult reading
        reading_time = max(1, round(word_count / 225)) 
        return word_count, reading_time
    
    def run_spellcheck(self):
        text = self.body_field.text.strip()
        if not text:
            self.last_spell_report = "Empty document"
            return

        # Clean text of basic punctuation for better accuracy
        words = re.findall(r'\w+', text.lower())
        misspelled = self.spell.unknown(words)
        
        if not misspelled:
            self.last_spell_report = f"✅ No errors ({self.lang.upper()})"
        else:
            # Show the first 3 misspelled words to keep the status bar clean
            count = len(misspelled)
            sample = ", ".join(list(misspelled)[:3])
            self.last_spell_report = f"❌ {count} errors: {sample}..."

    def clean_html_for_editor(self, html):
        # 1. Block-level handling (Headers and breaks)
        text = re.sub(r'<(p|div|h1|h2|h3|h4|h5|h6)[^>]*>', '', html)
        text = re.sub(r'</(p|div|h1|h2|h3|h4|h5|h6)>', '\n\n', text)
        text = re.sub(r'<br[^>]*>', '\n', text)

        # 2. Translate Bold and Italic
        text = re.sub(r'<(b|strong)>(.*?)</\1>', r'**\2**', text)
        text = re.sub(r'<(i|em)>(.*?)</\1>', r'*\2*', text)

        # 2.5 Translate Links: <a href="URL">TEXT</a> -> [TEXT](URL)
        # This regex captures the href value and the link text separately
        text = re.sub(r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)

        # 3. Final strip (Removes remaining tags but preserves images as per your original)
        return re.sub(r'<(?!img|/img)[^>]+>', '', text).strip()

    def save_post(self, is_draft=True):
        if self.is_offline or not self.service:
            self.last_spell_report = "SAVE FAILED: Offline"
            return False # Early exit if we can't save

        # 1. Start with the raw text from the body
        md = self.body_field.text

        # 2. LIGHTWEIGHT MARKDOWN PARSING (Regex)
        html = md
        # Headers (### Title -> <h3>Title</h3>)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.M)
        
        # Bold (**text**) and Italics (*text*)
        html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
        
        # Links ([text](url) -> <a href="url">text</a>)
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        # 3. Paragraph Handling
        # Convert double newlines to <p> tags and single newlines to <br />
        content_html = f"<p>{html.replace('\n\n', '</p><p>').replace('\n', '<br />')}</p>"

        # 4. Blogger API Upload
        labels_list = [t.strip() for t in self.tags_field.text.split(',') if t.strip()]
        body = {"title": self.title_field.text, "content": content_html, "labels": labels_list}
        
        try:
            if self.current_post_id:
                self.service.posts().update(blogId=self.blog_id, postId=self.current_post_id, body=body).execute()
                if not is_draft:
                    self.service.posts().publish(blogId=self.blog_id, postId=self.current_post_id).execute()
            else:
                res = self.service.posts().insert(blogId=self.blog_id, body=body, isDraft=is_draft).execute()
                self.current_post_id = res['id']
            
            self.last_saved_content = self.body_field.text
            self.post_status = "DRAFT" if is_draft else "LIVE"
            self.last_spell_report = "Saved with Markdown!"
        except Exception as e:
            self.last_spell_report = f"Save Error: {str(e)[:20]}"
            return False # Return False if saving failed

    def setup_bindings(self):
        @self.kb.add('f1')
        def _(event): self.show_help = not self.show_help; self.show_browser = False
        @self.kb.add('c-l')
        def _(event): self.show_browser = not self.show_browser; self.show_help = False; self.fetch_recent_posts()
        @self.kb.add('tab')
        def _(event): event.app.layout.focus_next()
        @self.kb.add('s-tab')
        def _(event): event.app.layout.focus_previous()
        @self.kb.add('c-d')
        def _(event): self.run_spellcheck()
        @self.kb.add('c-g')
        def _(event): event.app.layout.focus(self.command_field)
        @self.kb.add('c-s')
        def _(event): self.save_post(is_draft=True)
        @self.kb.add('c-p')
        def _(event): self.save_post(is_draft=False)
        @self.kb.add('c-t')
        def _(event): 
            self.ghost_mode_enabled = not self.ghost_mode_enabled
            self.last_spell_report = f"Ghost Mode: {'ON' if self.ghost_mode_enabled else 'OFF'}"
        @self.kb.add('c-b')
        def _(event):
            buffer = self.body_field.buffer
            if buffer.selection_state:
                start, end = buffer.document.selection_range()
                # .strip() removes the trailing newline that causes the jump
                selected_text = buffer.document.text[start:end].strip()
                new_text = buffer.document.text[:start] + f"**{selected_text}**" + buffer.document.text[end:]
                buffer.text = new_text
                buffer.cursor_position = start + len(selected_text) + 4
                buffer.exit_selection()
            else:
                buffer.insert_text("****")
                buffer.cursor_left(count=2)

        @self.kb.add('c-k')
        def _(event):
            buffer = self.body_field.buffer
            if buffer.selection_state:
                start, end = buffer.document.selection_range()
                selected_text = buffer.document.text[start:end].strip()
                new_text = buffer.document.text[:start] + f"*{selected_text}*" + buffer.document.text[end:]
                buffer.text = new_text
                buffer.cursor_position = start + len(selected_text) + 2
                buffer.exit_selection()
            else:
                buffer.insert_text("**")
                buffer.cursor_left(count=1)
        @self.kb.add('up', filter=Condition(lambda: self.show_browser))
        def _(event): self.browser_index = max(0, self.browser_index - 1); self.render_browser()
        @self.kb.add('down', filter=Condition(lambda: self.show_browser))
        def _(event): self.browser_index = min(len(self.posts_list)-1, self.browser_index + 1); self.render_browser()
        @self.kb.add('enter', filter=Condition(lambda: self.show_browser))
        def _(event): 
            if self.posts_list: self.fetch_and_load(self.posts_list[self.browser_index]['id']); self.show_browser = False; get_app().layout.focus(self.body_field)

    def start_sprint(self, mins):
        self.sprint_time_left = int(mins) * 60
        self.sprint_active = True
        # Capture starting word count
        text = self.body_field.text.strip()
        self.sprint_start_words = len(text.split()) if text else 0
        self.last_spell_report = f"🚀 Sprint Started! Goal: {mins}m"
    
    def update_sprint(self):
            if self.sprint_active and self.sprint_time_left > 0:
                self.sprint_time_left -= 1
                if self.sprint_time_left <= 0:
                    self.sprint_active = False
                    # Calculate Results
                    current_words = len(self.body_field.text.split())
                    total_written = current_words - self.sprint_start_words
                    # Ensure we don't show negative numbers if they deleted text
                    net_gain = max(0, total_written)
                    self.last_spell_report = f"★ DONE! +{net_gain} words ★"

    def get_reading_time(self):
        text = self.body_field.text.strip()
        if not text:
            return 0
        word_count = len(text.split())
        # Average reading speed is ~225 WPM
        minutes = word_count / 225
        return round(minutes) if minutes >= 1 else "< 1"
    def auto_save_recovery(self):
        try:
            with open(self.recovery_path, 'w') as f: json.dump({"title": self.title_field.text, "body": self.body_field.text}, f)
        except: pass
    def load_recovery(self):
        try:
            with open(self.recovery_path, 'r') as f:
                d = json.load(f)
                self.title_field.text, self.body_field.text = d['title'], d['body']
        except: pass

def show_loading():
    print("\033[H\033[J", end="") 
    print(BANNER)
    time.sleep(1.2)

async def main():
    editor = BlimEditor()
    app = Application(
        layout=Layout(editor.container, focused_element=editor.body_field), 
        key_bindings=editor.kb, 
        full_screen=True, 
        style=blim_style, 
        editing_mode=EditingMode.EMACS,
        mouse_support=True # Fixed mouse support for all terminals
        )
    async def refresh():
        ticks = 0
        while True:
            await asyncio.sleep(0.1) 
            app.invalidate()  # THIS IS THE CRITICAL LINE
            ticks += 1
            if ticks % 10 == 0: 
                editor.update_sprint()
            if ticks >= 600: 
                editor.auto_save_recovery()
                ticks = 0
    
    app.create_background_task(refresh())
    await app.run_async()

if __name__ == "__main__":
    show_loading()
    try: asyncio.run(main())
    except (KeyboardInterrupt, EOFError): pass