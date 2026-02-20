# Blim.py
# Copyright (C) 2026 Nomagev
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os, sys, time, json, re, asyncio
from prompt_toolkit import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, ConditionalContainer, DynamicContainer
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import TextArea, Label
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style
from prompt_toolkit.application import get_app

from spellchecker import SpellChecker
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import TransportError

from core.assets import get_banner, HELP_TEXT, TRANSLATIONS

# --- Style Definition ---
blim_style = Style.from_dict({
    # Markdown Styles
    'md.header': 'bold cyan',
    'md.bold': 'bold yellow',
    'md.italic': 'italic green',
    'md.code': 'bg:#333333 #ffffff',
    'md.link': 'underline blue',
    'md.quote': 'magenta',
    'md.strike': 'fg:#888888',
    
    # UI elements
    'status-warn': 'bg:#ff0000 #ffffff bold',
    'status-bar': 'bg:#222222 #00ff00',
    'status-goal': 'bg:#ffd700 #000000 bold',
    'status-dirty': '#ff0000',
    'prompt-normal': '#00ff00 bold',
    'spell-error': 'ansigray underline', 
    'help-text': 'fg:#00ff00 bg:#000000', 
    'body': 'fg:#00ff00 bg:#000000',
    'reverse-header': 'reverse bold',
})

# The dedicated Ghost Mode style
ghost_style = Style.from_dict({
    **dict(blim_style.style_rules),
    # Black out scrollbars
    'scrollbar': 'fg:#000000 bg:#000000',
    'scrollbar.button': 'fg:#000000 bg:#000000',
    'scrollbar.background': 'fg:#000000 bg:#000000',
    'scrollbar.arrow': 'fg:#000000 bg:#000000',
    # Black out line numbers
    'line-number': 'fg:#000000 bg:#000000',
    'line-number.current': 'fg:#000000 bg:#000000',
})

# --- Lexer for Spell Checking plus markdown highlighting ---
class BlimLexer(Lexer):
    def __init__(self, editor):
        self.editor = editor
        self.md_rules = [
            (r'\*\*.*?\*\*', 'class:md.bold'),
            (r'(?<!\*)\*[^*].*?[^*]\*(?!\*)', 'class:md.italic'),
            (r'~~.*?~~', 'class:md.strike'),      
            (r'\[.*?\]\(.*?\)', 'class:md.link'), 
            (r'`.*?`', 'class:md.code'),
        ]

    def lex_document(self, document: Document):
        def get_line(lineno):
            line_text = document.lines[lineno]
            line_start_index = document.translate_row_col_to_index(lineno, 0)
            
            if line_text.startswith('#'): return [('class:md.header', line_text)]
            if line_text.startswith('>'): return [('class:md.quote', line_text)]

            formatted_line = []
            last_pos = 0
            matches = []
            for pattern, style in self.md_rules:
                for m in re.finditer(pattern, line_text):
                    matches.append((m.start(), m.end(), style))
            matches.sort()

            for start, end, style in matches:
                if start > last_pos:
                    self._add_spellchecked_text(formatted_line, line_text[last_pos:start], 
                                               line_start_index + last_pos, document.cursor_position)
                formatted_line.append((style, line_text[start:end]))
                last_pos = end

            if last_pos < len(line_text):
                self._add_spellchecked_text(formatted_line, line_text[last_pos:], 
                                           line_start_index + last_pos, document.cursor_position)
            return formatted_line
        return get_line

    def _add_spellchecked_text(self, fragments, text, start_index, cursor_pos):
        last_pos = 0
        for match in re.finditer(r'\w+', text):
            word = match.group()
            word_start = start_index + match.start()
            word_end = start_index + match.end()
            
            if match.start() > last_pos:
                fragments.append(('', text[last_pos:match.start()]))
            
            is_unknown = word.lower() not in self.editor.spell
            is_being_typed = word_start <= cursor_pos <= word_end

            if self.editor.show_spelling_errors and is_unknown and not is_being_typed:
                fragments.append(('class:spell-error', word))
            else:
                fragments.append(('', word))
            
            last_pos = match.end()

        if last_pos < len(text):
            fragments.append(('', text[last_pos:]))

# --- Main Editor Class ---
class BlimEditor:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode 
        self._load_paths()
        self._load_config()
        
        # State
        self.current_post_id = None
        self.post_status = "NEW"
        self.last_saved_content = ""
        self.is_warning_mode = False
        self.pending_action = None 
        self.show_help = False
        self.show_browser = False
        self.browser_index = 0
        self.start_time = time.time()

        # Dictionary & Spell Checker
        self.show_spelling_errors = False  
        self._reload_dictionary()
        if self.test_mode:
            os.makedirs(os.path.dirname(self.custom_dict_path), exist_ok=True)
            if not os.path.exists(self.custom_dict_path):
                with open(self.custom_dict_path, 'w', encoding='utf-8') as f:
                    f.write("")

        if os.path.exists(self.custom_dict_path):
            self.spell.word_frequency.load_text_file(self.custom_dict_path)
        self.last_spell_report = self._t("ready").format(lang=self.lang.upper())
        
        # Sprint & Ghost Mode
        self.sprint_active = False
        self.sprint_time_left = 0
        self.sprint_start_words = 0
        self.ghost_mode_enabled = False 
        
        # Reading Speed
        self.reading_speed = 225

        # Services
        self._reload_dictionary()
        self.service = self.authenticate()
        
        # UI & Layout 
        self._init_ui_components()
        self._init_layout()
        
        # Input Handling
        self.kb = KeyBindings()
        self.setup_bindings()
        
        # Final Setup
        self.apply_language(self.lang)
        if os.path.exists(self.recovery_path):
            self.last_spell_report = self._t("recovery_found")

    def _load_paths(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(self.base_path, 'config')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        self.config_path = os.path.join(config_dir, 'config.json')
        self.secrets_path = os.path.join(config_dir, 'client_secrets.json')
        self.token_path = os.path.join(config_dir, 'token.json')
        self.recovery_path = os.path.join(config_dir, '.blim_recovery.json') 
        self.custom_dict_path = os.path.join(config_dir, 'custom_dictionary.txt')

    def _load_config(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump({"blog_id": "YOUR_ID", "word_goal": 500, "language": "es"}, f)
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.blog_id = str(config.get("blog_id")).strip()
            self.word_goal = config.get("word_goal", 500)
            self.lang = config.get("language", "es")

    def _t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])["ui"][key]

    def _reload_dictionary(self):
        self.spell = SpellChecker(language=self.lang)
        if os.path.exists(self.custom_dict_path):
            self.spell.word_frequency.load_text_file(self.custom_dict_path)

    def _init_ui_components(self):
        # UI Fields
        self.header_label = Label(text=lambda: self._t("header"), style='class:reverse-header')

        self.title_field = TextArea(height=1, prompt=lambda: self._t("title"), multiline=False, lexer=BlimLexer(self), focus_on_click=True)
        self.tags_field = TextArea(height=1, prompt=lambda: self._t("tags"), multiline=False, focus_on_click=True)
        
        self.body_field = TextArea(
            text="",
            scrollbar=True,
            line_numbers=True,
            lexer=BlimLexer(self),
            wrap_lines=True, 
            focus_on_click=True,
        )
        self.body_field.window.soft_wrap = True
        self.body_buffer = self.body_field.buffer  

        self.command_field = TextArea(
            height=1, 
            prompt=lambda: f"👻 {self._t('command')}" if self.ghost_mode_enabled else self._t("command"), 
            style='class:prompt-normal', 
            multiline=False, 
            accept_handler=self.handle_normal_input, 
            focus_on_click=True
        )
        self.warning_field = TextArea(height=1, prompt=lambda: self._t("warning_prompt"), style='class:status-warn', multiline=False, accept_handler=self.handle_warning_input, focus_on_click=True)
        
        # Static Text Areas
        self.help_field = TextArea(read_only=True, style='class:help-text')
        self.browser_field = TextArea(read_only=True, style='class:help-text')

    def _init_layout(self):
        # Rows
        self.header_bar = VSplit([
            Label(text=" v1.4.0 ", style='class:reverse-header'), 
            self.header_label, 
            Label(text=f" [F1] {self._t('help_btn')} ", style='class:reverse-header') 
        ], height=1)
        
        status_bar_view = VSplit([Window(), Label(text=self.get_status_text, style='class:status-bar'), Window()], height=1)
        command_view = VSplit([Window(), self.command_field, Window()], height=1)
        warning_view = VSplit([Window(), self.warning_field, Window()], height=1)

        # Visibility Logic
        self.header_row = DynamicContainer(lambda: self.header_bar if self.is_ui_visible() else Window(height=1))
        self.status_row = DynamicContainer(lambda: status_bar_view if self.is_ui_visible() else Window(height=1))
        
        metadata_row = DynamicContainer(lambda: HSplit([
            self.title_field, 
            self.tags_field, 
            Window(height=1, char='-')
        ], width=80) if self.is_ui_visible() else Window(height=3))

        # Main Stack 
        main_stack = HSplit([
            ConditionalContainer(
                content=HSplit([
                    metadata_row, 
                    self.body_field  
                ]), 
                filter=Condition(lambda: not self.show_help and not self.show_browser)
            ),
            ConditionalContainer(content=self.help_field, filter=Condition(lambda: self.show_help)),
            ConditionalContainer(content=self.browser_field, filter=Condition(lambda: self.show_browser)),
        ], width=85) 

        # Container Assembly
        self.container = HSplit([
            # Header
            ConditionalContainer(
                content=self.header_row,
                filter=Condition(lambda: self.is_ui_visible())
            ),
            # Centered Editor
            VSplit([
                Window(), 
                main_stack, 
                Window(), 
            ]),
            # Command Bar
            DynamicContainer(lambda: warning_view if self.is_warning_mode else command_view),
            # Status Bar
            ConditionalContainer(
                content=self.status_row,
                filter=Condition(lambda: self.is_ui_visible())
            ),
        ])

    def is_ui_visible(self):
        if not self.ghost_mode_enabled:
            return True
        try:
            return not get_app().layout.has_focus(self.body_field)
        except:
            return True
    
    def authenticate(self):
        if self.test_mode:
            self.is_offline = True
            return None

        self.is_offline = False 
        try:
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.secrets_path, 
                        ['https://www.googleapis.com/auth/blogger']
                    )
                    creds = flow.run_local_server(port=0)
                
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                    
            return build('blogger', 'v3', credentials=creds)
        except (TransportError, Exception):
            self.is_offline = True
            self.last_spell_report = self._t("offline")
            return None

    def get_status_text(self):
        t = TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])['status']
        dirty = " *" if self.is_dirty() else ""
        word_count = len(self.body_buffer.text.split())
        result = []

        if word_count >= self.word_goal:
            result.append(('class:status-goal', f" ★ {t['words']}: {word_count}/{self.word_goal} ★ "))
        else:
            result.append(('', f" {t['words']}: {word_count}/{self.word_goal} "))
        
        result.append(('', " | "))

        read_min = max(1, round(word_count / self.reading_speed))
        result.append(('', f" {read_min} {t.get('read', 'read')} "))
        
        if self.sprint_active:
            remaining = max(0, self.sprint_time_left)
            s_mins, s_secs = divmod(int(remaining), 60)
            sprint_color = 'class:status-warn' if remaining < 60 else '' 
            
            result.append(('', " | 🚀 "))
            if remaining == 0:
                result.append(('class:status-goal', f" {t.get('done', 'DONE')}! "))
            else:
                result.append((sprint_color, f" {s_mins:02d}:{s_secs:02d} "))

        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        result.append(('', f" | {mins:02d}:{secs:02d} "))
        
        if dirty:
            result.append(('class:status-dirty', dirty))
            
        result.append(('', f" | {self.last_spell_report} "))
        
        return result

    def is_dirty(self): return self.body_buffer.text.strip() != self.last_saved_content.strip()

    def apply_language(self, lang_code):
        self.lang = lang_code
        t = TRANSLATIONS[self.lang]["ui"]

        if self.post_status in ["[NEW]", "[NUEVO]", "NEW"]:
            self.post_status = t["new_post"]

        if self.show_browser: self.render_browser()
        self.help_field.text = HELP_TEXT.get(self.lang, HELP_TEXT["en"]).strip()
        self._reload_dictionary()
        self.last_spell_report = t["lang_feedback"]
    
    def spell_check(self):
        get_app().invalidate()

    def handle_normal_input(self, buffer):
        cmd = buffer.text.strip().lower()
        if not cmd:
            get_app().layout.focus(self.body_field); return

        if cmd == ':new': self.start_new_post()
        elif cmd == ':spa': self.apply_language('es')
        elif cmd == ':eng': self.apply_language('en')
        elif cmd in [':q', ':exit']:
            if not self.is_dirty(): get_app().exit()
            else:
                self.is_warning_mode = True
                self.pending_action = "quit"
                get_app().layout.focus(self.warning_field)
        elif cmd == ':help': self.show_help, self.show_browser = True, False
        elif cmd == ':restore': self.load_recovery()
        elif cmd.startswith(':sprint'):
            parts = cmd.split()
            try:
                duration = int(parts[1]) if len(parts) > 1 else 25
                self.start_sprint(duration)
            except ValueError:
                self.start_sprint(25)
            get_app().layout.focus(self.body_field) 
        elif cmd.isdigit(): 
            self.fetch_and_load(cmd)
            get_app().layout.focus(self.body_field)
        elif cmd.startswith(':speed'):
            parts = cmd.split()
            if len(parts) > 1 and parts[1].isdigit():
                self.reading_speed = int(parts[1])
                self.last_spell_report = self._t("speed_set").format(speed=self.reading_speed)
        elif cmd.startswith(':add '):
            word_to_add = cmd.replace(':add ', '').strip().lower()
            if word_to_add:
                with open(self.custom_dict_path, 'a', encoding='utf-8') as f:
                    f.write(word_to_add + "\n")
                self.spell.word_frequency.load_words([word_to_add])
                self.last_spell_report = f"'{word_to_add}' {self._t('added_to_dict')}"
                self.spell_check() 

        buffer.text = ""

    def handle_warning_input(self, buffer):
        if buffer.text.strip().lower() == 'y':
            if self.pending_action == "quit": get_app().exit()
            else: self._force_clear_all(); self.is_warning_mode = False
        else:
            self.is_warning_mode = False
            get_app().layout.focus(self.body_field)
        buffer.text = ""

    def start_new_post(self):
        self.title_field.text = self.body_buffer.text = self.tags_field.text = ""
        self.post_status = TRANSLATIONS[self.lang]["ui"]["new_post"]
        self.current_post_id = None
        get_app().layout.focus(self.body_field)

    def _force_clear_all(self):
        self.start_new_post()
        self.last_saved_content = ""

    def fetch_recent_posts(self):
        if self.is_offline or not self.service: return
        try:
            posts_data = self.service.posts().list(blogId=self.blog_id, maxResults=20, status=['LIVE', 'DRAFT'], view='AUTHOR').execute()
            self.posts_list = [{'id': p['id'], 'title': p.get('title', '(Untitled)'), 'status': p.get('status', 'DRAFT')} for p in posts_data.get('items', [])]
            self.render_browser()
        except Exception as e:
            self.browser_field.text = f"Fetch Error: {str(e)[:20]}"

    def render_browser(self):
        t = TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])["ui"]
        width = 76
        
        lines = [t["fetching"], " ╔" + "═"*(width-2) + "╗", f" ║{t['browser_title'].center(width-2)}║", " ╠" + "═"*(width-2) + "╣"]
        
        for i, post in enumerate(self.posts_list[:12]):
            prefix = " › " if i == self.browser_index else "   "
            display_title = post['title'][:60].ljust(60)
            status_char = post['status'][0].upper()
            content = f" {prefix}[{status_char}] {display_title}".ljust(width-2)
            lines.append(f" ║{content}║")
            
        while len(lines) < 16: 
            lines.append(" ║" + " "*(width-2) + "║")
            
        lines.append(" ╚" + "═"*(width-2) + "╝")
        lines.append(t["browser_hint"].center(width)) 
        
        self.browser_field.text = "\n".join(lines)

    def fetch_and_load(self, post_id):
        try:
            post = self.service.posts().get(blogId=self.blog_id, postId=post_id, view='AUTHOR').execute()
            self.current_post_id, self.post_status = post['id'], post.get('status', 'LIVE')
            self.title_field.text = post.get('title', '')
            self.tags_field.text = ", ".join(post.get('labels', []))
            self.body_buffer.text = self.last_saved_content = self.clean_html_for_editor(post.get('content', ''))
        except: self.last_spell_report = self._t("load_error")

    def run_spellcheck(self):
        text = self.body_buffer.text.strip()
        if not text:
            self.last_spell_report = self._t("empty_doc")
            return
        words = re.findall(r'\w+', text.lower())
        misspelled = self.spell.unknown(words)
        
        if not misspelled:
            self.last_spell_report = self._t("no_errors").format(lang=self.lang.upper())
        else:
            err_list = ', '.join(list(misspelled)[:3])
            self.last_spell_report = self._t("errors_found").format(
            count=len(misspelled), 
            list=err_list
        )
    
    def clean_html_for_editor(self, html):
        text = re.sub(r'<(p|div|h[1-6])[^>]*>', '', html)
        text = re.sub(r'</(p|div|h[1-6])>', '\n\n', text)
        text = re.sub(r'<br[^>]*>', '\n', text)
        text = re.sub(r'<(b|strong)>(.*?)</\1>', r'**\2**', text)
        text = re.sub(r'<(i|em)>(.*?)</\1>', r'*\2*', text)
        text = re.sub(r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)
        return re.sub(r'<(?!img|/img)[^>]+>', '', text).strip()

    def _parse_markdown(self, md_text):
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', md_text, flags=re.M)
        html = re.sub(r'^---$', r'<hr />', html, flags=re.M)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.M)
        
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.M)
        html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html, flags=re.S)

        html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        processed_blocks = []
        for block in html.split('\n\n'):
            trimmed = block.strip()
            if not trimmed: continue
            if trimmed.startswith('<'):
                processed_blocks.append(trimmed.replace('\n', '') if '<li>' in trimmed else trimmed)
            else:
                processed_blocks.append(f"<p>{trimmed.replace(chr(10), '<br />')}</p>")
        return "".join(processed_blocks)

    def save_post(self, is_draft=True):
        if self.is_offline or not self.service:
            self.last_spell_report = self._t("save_fail")
            return False

        content_html = self._parse_markdown(self.body_buffer.text)
        labels = [t.strip() for t in self.tags_field.text.split(',') if t.strip()]
        body = {"title": self.title_field.text, "content": content_html, "labels": labels}
        
        try:
            if self.current_post_id:
                self.service.posts().update(blogId=self.blog_id, postId=self.current_post_id, body=body).execute()
                if not is_draft: self.service.posts().publish(blogId=self.blog_id, postId=self.current_post_id).execute()
            else:
                res = self.service.posts().insert(blogId=self.blog_id, body=body, isDraft=is_draft).execute()
                self.current_post_id = res['id']
            
            self.last_saved_content = self.body_buffer.text
            self.post_status = self._t("status_draft") if is_draft else self._t("status_live")
            self.last_spell_report = self._t("saved")
        except Exception as e:
            self.last_spell_report = self._t("save_error").format(error=str(e)[:20])

    def _wrap_selection(self, symbol, offset_len):
        buff = self.body_field.buffer
        if buff.selection_state:
            start, end = buff.document.selection_range()
            text = buff.document.text[start:end].strip()
            new_text = buff.document.text[:start] + f"{symbol}{text}{symbol}" + buff.document.text[end:]
            buff.text = new_text
            buff.cursor_position = start + len(text) + (len(symbol) * 2)
            buff.exit_selection()
        else:
            buff.insert_text(symbol * 2)
            buff.cursor_left(count=offset_len)

    def setup_bindings(self):
        kb = self.kb
        
        @kb.add('f1')
        def _(event): self.show_help = not self.show_help; self.show_browser = False
        
        @kb.add('c-o')
        def _(event):
            self.show_browser = not self.show_browser
            self.show_help = False
            if self.show_browser:
                self.fetch_recent_posts()
                get_app().layout.focus(self.browser_field)
            else:
                get_app().layout.focus(self.body_field)

        @kb.add('tab')
        def _(event): event.app.layout.focus_next()
        
        @kb.add('s-tab')
        def _(event): event.app.layout.focus_previous()

        @kb.add('c-d')
        def _(event):
            self.show_spelling_errors = not self.show_spelling_errors
            if self.show_spelling_errors:
                self.run_spellcheck() 
            else:
                self.last_spell_report = self._t("ready").format(lang=self.lang.upper())
            event.app.invalidate()
        
        @kb.add('c-g')
        def _(event): event.app.layout.focus(self.command_field)
        
        @kb.add('c-s')
        def _(event): self.save_post(is_draft=True)
        
        @kb.add('c-p')
        def _(event): self.save_post(is_draft=False)
        
        @kb.add('c-t')
        def _(event):
            self.ghost_mode_enabled = not self.ghost_mode_enabled
            
            # 1. Toggle the widget attributes
            self.body_field.scrollbar = not self.ghost_mode_enabled
            self.body_field.line_numbers = not self.ghost_mode_enabled
            
            # 2. Swap the global application style
            if self.ghost_mode_enabled:
                event.app.style = ghost_style
                
                # THE TRICK: Resetting focus forces the TextArea to 
                # recalculate its internal window widths and hide the gutter.
                event.app.layout.focus(self.command_field)
                event.app.layout.focus(self.body_field)
            else:
                event.app.style = blim_style
                # Force recalculation to bring the gutter back
                event.app.layout.focus(self.command_field)
                event.app.layout.focus(self.body_field)

            event.app.invalidate()
        
        # Markdown Formatting Hotkeys
        @kb.add('c-b')
        def _(event): self._wrap_selection("**", 2)
        
        @kb.add('c-k')
        def _(event): self._wrap_selection("*", 1)

        @kb.add('c-q')
        def _(event):
            buff = self.body_field.buffer
            if buff.selection_state:
                text = buff.copy_selection().text
                buff.insert_text(f"> {text}", overwrite=True)
            else:
                buff.insert_text("> ")

        @kb.add('c-l')
        def _(event):
            buff = self.body_field.buffer
            if buff.selection_state:
                start, end = buff.document.selection_range()
                lines = buff.document.text[start:end].splitlines()
                new_list = "\n".join([f"* {line.strip()}" for line in lines if line.strip()])
                buff.text = buff.document.text[:start] + new_list + buff.document.text[end:]
                buff.cursor_position = start + len(new_list)
                buff.exit_selection()
            else:
                buff.insert_text("* ")

        # Navigation
        @kb.add('up', filter=Condition(lambda: self.show_browser))
        def _(event): self.browser_index = max(0, self.browser_index - 1); self.render_browser()
        
        @kb.add('down', filter=Condition(lambda: self.show_browser))
        def _(event): self.browser_index = min(len(self.posts_list)-1, self.browser_index + 1); self.render_browser()
        
        @kb.add('enter', filter=Condition(lambda: self.show_browser))
        def _(event): 
            if self.posts_list: 
                self.fetch_and_load(self.posts_list[self.browser_index]['id'])
                self.show_browser = False
                get_app().layout.focus(self.body_field)

    def start_sprint(self, mins):
        self.sprint_time_left = int(mins) * 60
        self.sprint_active = True
        self.sprint_start_words = len(self.body_buffer.text.split())
        self.last_spell_report = self._t("sprint_start").format(mins=mins)
    
    def update_sprint(self):
        if self.sprint_active and self.sprint_time_left > 0:
            self.sprint_time_left -= 1
            if self.sprint_time_left <= 0:
                self.sprint_active = False
                gain = max(0, len(self.body_buffer.text.split()) - self.sprint_start_words)
                self.last_spell_report = self._t("sprint_done").format(gain=gain)

    def auto_save_recovery(self):
        try:
            with open(self.recovery_path, 'w') as f: json.dump({"title": self.title_field.text, "body": self.body_buffer.text}, f)
        except: pass

    def load_recovery(self):
        try:
            with open(self.recovery_path, 'r') as f:
                d = json.load(f)
                self.title_field.text, self.body_buffer.text = d['title'], d['body']
        except: pass

def show_loading():
    print("\033[H\033[J" + get_banner())
    time.sleep(1.3)

async def main():
    editor = BlimEditor()
    app = Application(
        layout=Layout(editor.container, focused_element=editor.body_field.buffer), 
        key_bindings=editor.kb, 
        full_screen=True, 
        style=blim_style, 
        editing_mode=EditingMode.EMACS,
        mouse_support=True
    )
    async def refresh():
        ticks = 0
        while True:
            await asyncio.sleep(0.1) 
            app.invalidate()
            ticks += 1
            if ticks % 10 == 0: editor.update_sprint()
            if ticks >= 600: editor.auto_save_recovery(); ticks = 0
    
    app.create_background_task(refresh())
    await app.run_async()

if __name__ == "__main__":
    show_loading()
    try: asyncio.run(main())
    except (KeyboardInterrupt, EOFError): pass