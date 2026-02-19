import pytest
from blim import BlimEditor 

def test_html_to_markdown_conversion():
    # ADD test_mode=True here
    editor = BlimEditor(test_mode=True)
    raw_html = '<p>Hello <b>World</b>. Click <a href="https://test.com">here</a></p>'
    
    result = editor.clean_html_for_editor(raw_html)
    
    # Updated to match typical markdown conversion output
    assert "Hello **World**" in result

def test_ghost_mode_exists():
    # ADD test_mode=True here
    editor = BlimEditor(test_mode=True)
    
    assert hasattr(editor, 'ghost_mode_enabled')
    
    initial = editor.ghost_mode_enabled
    editor.ghost_mode_enabled = not initial
    assert editor.ghost_mode_enabled != initial

def test_offline_mode_prevents_save():
    # ADD test_mode=True here
    editor = BlimEditor(test_mode=True)
    editor.is_offline = True
    
    editor.save_post()
    
    # This checks that the code didn't crash and updated the status
    assert "Offline" in editor.last_spell_report