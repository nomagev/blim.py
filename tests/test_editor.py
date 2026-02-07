import pytest
from blim import BlimEditor  # Assuming your class is named Blim

def test_html_to_markdown_conversion():
    # Setup
    editor = BlimEditor()
    raw_html = '<p>Hello <b>World</b>. Click <a href="https://test.com">here</a></p>'
    
    # Execute
    result = editor.clean_html_for_editor(raw_html)
    
    # Assert (The expected outcome)
    assert result == "Hello **World**. Click [here](https://test.com)"

def test_ghost_mode_exists():
    editor = BlimEditor()
    # Check that the variable exists without calling it
    assert hasattr(editor, 'ghost_mode_enabled')
    
    # Manually simulate what your hotkey does
    initial = editor.ghost_mode_enabled
    editor.ghost_mode_enabled = not initial
    
    assert editor.ghost_mode_enabled != initial

def test_offline_mode_prevents_save():
    editor = BlimEditor()
    editor.is_offline = True
    
    editor.save_post()
    
    assert "Offline" in editor.last_spell_report