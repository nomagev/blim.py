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
from unittest import result
from prompt_toolkit import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, ConditionalContainer, DynamicContainer
from prompt_toolkit.layout.controls import FormattedTextControl
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

from assets import BANNER, HELP_TEXT, TRANSLATIONS

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
    'md.link': 'underline blue',
    
    # UI elements
    'status-warn': 'bg:#ff0000 #ffffff bold',
    'status-bar': 'bg:#222222 #00ff00',
    'status-goal': 'bg:#ffd700 #000000 bold',
    'status-dirty': '#ff0000',
    'prompt-normal': '#00ff00 bold',
    'spell-error': 'fg:#ffaa00 bold',
    'help-text': 'fg:#00ff00 bg:#000000', 
    'body': 'fg:#00ff00 bg:#000000',
    'reverse-header': 'reverse bold',
})
# --- Lexer for Spell Checking plus markdown highlighting ---
class BlimLexer(Lexer):
    def __init__(self, editor):
        self.editor = editor
        # Inline patterns (things that happen inside a sentence)
        self.md_rules = [
            (r'\*\*.*?\*\*', 'class:md.bold'),
            (r'(?<!\*)\*[^*].*?[^*]\*(?!\*)', 'class:md.italic'),
            (r'~~.*?~~', 'class:md.strike'),      # Strikethrough
            (r'\[.*?\]\(.*?\)', 'class:md.link'), # Links [text](url)
            (r'`.*?`', 'class:md.code'),
        ]

    def lex_document(self, document: Document):
        def get_line(lineno):
            line_text = document.lines[lineno]
            
            # 1. Check for Line-level Markdown (Headers and Quotes)
            if line_text.startswith('#'):
                return [('class:md.header', line_text)]
            if line_text.startswith('>'):
                return [('class:md.quote', line_text)]

            # 2. Process Inline Markdown and Spelling
            formatted_line = []
            last_pos = 0
            
            # Find all bold/italic/code matches in this line
            matches = []
            for pattern, style in self.md_rules:
                for m in re.finditer(pattern, line_text):
                    matches.append((m.start(), m.end(), style))
            
            # Sort matches so we process the line from left to right
            matches.sort()

            for start, end, style in matches:
                # If there is text BEFORE the markdown, spellcheck it
                if start > last_pos:
                    self._add_spellchecked_text(formatted_line, line_text[last_pos:start])
                
                # Add the Markdown part (the bold/italic/code block)
                formatted_line.append((style, line_text[start:end]))
                last_pos = end

            # Add any remaining text at the end of the line (and spellcheck it)
            if last_pos < len(line_text):
                self._add_spellchecked_text(formatted_line, line_text[last_pos:])

            return formatted_line
        return get_line

    def _add_spellchecked_text(self, formatted_line, text):
        """Helper to handle the spelling logic for plain text gaps."""
        words = re.split(r"([^\w']+)", text)
        for piece in words:
            style = ''
            if re.match(r"[\w']+", piece):
                is_known = self.editor.spell.known([piece.lower()]) if self.editor.spell else True
                if not is_known:
                    style = 'class:spell-error'
            formatted_line.append((style, piece))

# --- Main Editor Class ---
class BlimEditor:
    def __init__(self):
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
        self.posts_list = []
        self.start_time = time.time()
        self.last_spell_report = self._t("ready").format(lang=self.lang.upper())
        
        # Sprint & Ghost Mode
        self.sprint_active = False
        self.sprint_time_left = 0
        self.sprint_start_words = 0
        self.ghost_mode_enabled = False 
        self.last_interaction_time = time.time()
        self.ghost_timeout = 3
        
        # Reading Speed
        self.reading_speed = 225

        # Services
        self.spell = SpellChecker(language=self.lang)
        self.service = self.authenticate()
        
        # UI & Layout
        self._init_ui_components()
        self._init_layout()
        
        # Input Handling
        self.kb = KeyBindings()
        self.setup_bindings()
        
        # Wake up Ghost Mode on typing
        self.body_field.buffer.on_text_changed += lambda _: setattr(self, 'last_interaction_time', time.time())
        
        # Final Setup
        self.apply_language(self.lang)
        if os.path.exists(self.recovery_path):
            self.last_spell_report = self._t("recovery_found")

    def _load_paths(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_path, 'config.json')
        self.secrets_path = os.path.join(self.base_path, 'client_secrets.json')
        self.token_path = os.path.join(self.base_path, 'token.json')
        self.recovery_path = os.path.join(self.base_path, '.blim_recovery.json') # Updated to match .gitignore

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
        """Helper to get translation string safely."""
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])["ui"][key]

    def _init_ui_components(self):
        # UI Fields
        self.header_label = Label(text=lambda: self._t("header"), style='class:reverse-header')

        self.title_field = TextArea(height=1, prompt=lambda: self._t("title"), multiline=False, lexer=BlimLexer(self), focus_on_click=True)
        self.tags_field = TextArea(height=1, prompt=lambda: self._t("tags"), multiline=False, focus_on_click=True)
        self.body_field = TextArea(scrollbar=True, line_numbers=True, lexer=BlimLexer(self), wrap_lines=True, focus_on_click=True)
        
        self.command_field = TextArea(height=1, prompt=lambda: self._t("command"), style='class:prompt-normal', multiline=False, accept_handler=self.handle_normal_input, focus_on_click=True)
        self.warning_field = TextArea(height=1, prompt=lambda: self._t("warning_prompt"), style='class:status-warn', multiline=False, accept_handler=self.handle_warning_input, focus_on_click=True)
        
        # Static Text Areas
        self.help_field = TextArea(read_only=True, style='class:help-text')
        self.browser_field = TextArea(read_only=True, style='class:help-text')

    def _init_layout(self):
        # Rows
        self.header_bar = VSplit([
            Label(text=" v1.4.0 ", style='class:reverse-header'), 
            self.header_label, 
            Label(text=f" [F1] {self._t('help_btn')} ", style='class:reverse-header') # Translated
        ], height=1)
        
        status_bar_view = VSplit([Window(), Label(text=self.get_status_text, style='class:status-bar'), Window()], height=1)
        command_view = VSplit([Window(), self.command_field, Window()], height=1)
        warning_view = VSplit([Window(), self.warning_field, Window()], height=1)

        # Visibility Logic
        self.header_row = DynamicContainer(lambda: self.header_bar if self.is_ui_visible() else Window(height=1))
        self.status_row = DynamicContainer(lambda: status_bar_view if self.is_ui_visible() else Window(height=1))
        
        metadata_row = DynamicContainer(lambda: HSplit([self.title_field, self.tags_field, Window(height=1, char='-')]) 
                                        if self.is_ui_visible() else Window(height=3))

        # Main Stack
        main_stack = HSplit([
            ConditionalContainer(content=HSplit([metadata_row, self.body_field]), 
                               filter=Condition(lambda: not self.show_help and not self.show_browser)),
            ConditionalContainer(content=self.help_field, filter=Condition(lambda: self.show_help)),
            ConditionalContainer(content=self.browser_field, filter=Condition(lambda: self.show_browser)),
        ], width=80)

        # Master Container
        self.container = HSplit([
            self.header_row,
            VSplit([Window(), main_stack, Window()]),
            DynamicContainer(lambda: warning_view if self.is_warning_mode else command_view),
            self.status_row
        ])

    def is_ui_visible(self):
        if not self.ghost_mode_enabled: return True
        # If user is not typing in the body, show UI
        if not get_app().layout.has_focus(self.body_field): return True
        # Hide if timeout expired
        return (time.time() - self.last_interaction_time) < self.ghost_timeout
    
    def authenticate(self):
        self.is_offline = False 
        try:
            creds = None
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
            self.last_spell_report = self._t("offline")
            return None

    def get_status_text(self):
        # t already contains the translations for the current language
        t = TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])['status']
        dirty = " *" if self.is_dirty() else ""
        word_count = len(self.body_field.text.split())
        result = []

        # 1. Word Count / Goal
        if word_count >= self.word_goal:
            result.append(('class:status-goal', f" ★ {t['words']}: {word_count}/{self.word_goal} ★ "))
        else:
            result.append(('', f" {t['words']}: {word_count}/{self.word_goal} "))
        
        result.append(('', " | "))

        # 2. Reading Time (Corrected to use translated labels)
        read_min = max(1, round(word_count / self.reading_speed))
        # We assume t['read'] in assets.py is "min read" or "min lectura"
        result.append(('', f" {read_min} {t.get('read', 'read')} "))
        
        # 3. Sprint Timer
        if self.sprint_active:
            remaining = max(0, self.sprint_time_left)
            s_mins, s_secs = divmod(int(remaining), 60)
            sprint_color = 'class:status-warn' if remaining < 60 else '' 
            
            result.append(('', " | 🚀 "))
            if remaining == 0:
                # Use translated 'done' or 'listo'
                result.append(('class:status-goal', f" {t.get('done', 'DONE')}! "))
            else:
                result.append((sprint_color, f" {s_mins:02d}:{s_secs:02d} "))

        # 4. Global Timer & Dirty Flag
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        result.append(('', f" | {mins:02d}:{secs:02d} "))
        
        if dirty:
            result.append(('class:status-dirty', dirty))
            
        # 5. Spellcheck/Feedback
        result.append(('', f" | {self.last_spell_report} "))
        
        return result

    def is_dirty(self): return self.body_field.text.strip() != self.last_saved_content.strip()

    def apply_language(self, lang_code):
        self.lang = lang_code
        t = TRANSLATIONS[self.lang]["ui"]

        # Update Post Status Label if it's new
        if self.post_status in ["[NEW]", "[NUEVO]", "NEW"]:
            self.post_status = t["new_post"]

        # Force UI Updates
        # Note: TextArea prompts update automatically via lambda, but manual refresh ensures safety
        if self.show_browser: self.render_browser()
        self.help_field.text = HELP_TEXT.get(self.lang, HELP_TEXT["en"]).strip()
        self.spell = SpellChecker(language=self.lang)
        self.last_spell_report = t["lang_feedback"]
    
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
                # Default to 25 if no number provided or if conversion fails
                duration = int(parts[1]) if len(parts) > 1 else 25
                self.start_sprint(duration)
            except ValueError:
                self.start_sprint(25)
            get_app().layout.focus(self.body_field) # Refocus editor after starting
        elif cmd.isdigit(): 
            self.fetch_and_load(cmd)
            get_app().layout.focus(self.body_field)
        elif cmd.startswith(':speed'):
            parts = cmd.split()
            if len(parts) > 1 and parts[1].isdigit():
                self.reading_speed = int(parts[1])
                self.last_spell_report = self._t("speed_set").format(speed=self.reading_speed)

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
        self.title_field.text = self.body_field.text = self.tags_field.text = ""
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
        
        # 1. Header and Box Top
        lines = [t["fetching"], " ╔" + "═"*(width-2) + "╗", f" ║{t['browser_title'].center(width-2)}║", " ╠" + "═"*(width-2) + "╣"]
        
        # 2. Post List
        for i, post in enumerate(self.posts_list[:12]):
            prefix = " › " if i == self.browser_index else "   "
            display_title = post['title'][:60].ljust(60)
            status_char = post['status'][0].upper()
            content = f" {prefix}[{status_char}] {display_title}".ljust(width-2)
            lines.append(f" ║{content}║")
            
        # 3. Padding for consistent height
        while len(lines) < 16: # Adjusted to make room for hint
            lines.append(" ║" + " "*(width-2) + "║")
            
        # 4. Box Bottom and Instruction Hint
        lines.append(" ╚" + "═"*(width-2) + "╝")
        lines.append(t["browser_hint"].center(width)) # New instruction line
        
        self.browser_field.text = "\n".join(lines)

    def fetch_and_load(self, post_id):
        try:
            post = self.service.posts().get(blogId=self.blog_id, postId=post_id, view='AUTHOR').execute()
            self.current_post_id, self.post_status = post['id'], post.get('status', 'LIVE')
            self.title_field.text = post.get('title', '')
            self.tags_field.text = ", ".join(post.get('labels', []))
            self.body_field.text = self.last_saved_content = self.clean_html_for_editor(post.get('content', ''))
        except: self.last_spell_report = self._t("load_error")

    def run_spellcheck(self):
        text = self.body_field.text.strip()
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
        # 1. Basics
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', md_text, flags=re.M)
        html = re.sub(r'^---$', r'<hr />', html, flags=re.M)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.M)
        
        # 2. Lists
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.M)
        html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html, flags=re.S)

        # 3. Inline
        html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        # 4. Paragraphs
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

        content_html = self._parse_markdown(self.body_field.text)
        labels = [t.strip() for t in self.tags_field.text.split(',') if t.strip()]
        body = {"title": self.title_field.text, "content": content_html, "labels": labels}
        
        try:
            if self.current_post_id:
                self.service.posts().update(blogId=self.blog_id, postId=self.current_post_id, body=body).execute()
                if not is_draft: self.service.posts().publish(blogId=self.blog_id, postId=self.current_post_id).execute()
            else:
                res = self.service.posts().insert(blogId=self.blog_id, body=body, isDraft=is_draft).execute()
                self.current_post_id = res['id']
            
            self.last_saved_content = self.body_field.text
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
                # FOCUS THE LIST IMMEDIATELY
                get_app().layout.focus(self.browser_field)
            else:
                # FOCUS THE EDITOR WHEN CLOSING
                get_app().layout.focus(self.body_field)

        # @kb.add('c-o')
        # def _(event): self.show_browser = not self.show_browser; self.show_help = False; self.fetch_recent_posts()
        
        @kb.add('tab')
        def _(event): event.app.layout.focus_next()
        
        @kb.add('s-tab')
        def _(event): event.app.layout.focus_previous()
        
        @kb.add('c-d')
        def _(event): self.run_spellcheck()
        
        @kb.add('c-g')
        def _(event): event.app.layout.focus(self.command_field)
        
        @kb.add('c-s')
        def _(event): self.save_post(is_draft=True)
        
        @kb.add('c-p')
        def _(event): self.save_post(is_draft=False)
        
        @kb.add('c-t')
        def _(event): 
            self.ghost_mode_enabled = not self.ghost_mode_enabled
            msg_key = "ghost_on" if self.ghost_mode_enabled else "ghost_off"
            self.last_spell_report = self._t(msg_key)

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
                # Use the index to get the ID
                self.fetch_and_load(self.posts_list[self.browser_index]['id'])
                self.show_browser = False
                # Return to the main editor
                get_app().layout.focus(self.body_field)

    def start_sprint(self, mins):
        self.sprint_time_left = int(mins) * 60
        self.sprint_active = True
        self.sprint_start_words = len(self.body_field.text.split())
        self.last_spell_report = self._t("sprint_start").format(mins=mins)
    
    def update_sprint(self):
        if self.sprint_active and self.sprint_time_left > 0:
            self.sprint_time_left -= 1
            if self.sprint_time_left <= 0:
                self.sprint_active = False
                gain = max(0, len(self.body_field.text.split()) - self.sprint_start_words)
                self.last_spell_report = self._t("sprint_done").format(gain=gain)

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
    print("\033[H\033[J" + BANNER)
    time.sleep(1.2)

async def main():
    editor = BlimEditor()
    app = Application(
        layout=Layout(editor.container, focused_element=editor.body_field), 
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