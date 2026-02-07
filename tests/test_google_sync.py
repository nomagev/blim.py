import pytest
from unittest.mock import MagicMock, patch
from blim import BlimEditor  # This imports your class

@patch('blim.build') # We "patch" the Google API build function
def test_save_post_success(mock_build):
    # 1. Setup the Fake API
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_posts = mock_service.posts.return_value
    mock_insert = mock_posts.insert.return_value
    
    # We simulate what Blogger usually returns
    mock_insert.execute.return_value = {'id': '12345', 'title': 'Test Post'}

    # 2. Initialize your class
    editor = BlimEditor()
    
    # We fill the fields manually so the method has something to save
    editor.body_field.text = "This is a **test** post."
    editor.title_field.text = "Test Title"
    editor.tags_field.text = "test, blim"
    editor.blog_id = "123"
    
    # 3. Run your actual method
    editor.save_post()

    # 4. Assertions (Checking the "Side Effects" instead of return values)
    # This confirms the API was actually "hit" by your code
    assert mock_posts.insert.called
    
    # This confirms your code updated the status message in the UI
    assert "Saved" in editor.last_spell_report

@patch('blim.build')
def test_save_post_failure(mock_build):
    editor = BlimEditor()
    editor.is_offline = False
    
    # 1. Create a "grumpy" service
    bad_service = MagicMock()
    # Tell the service to raise an error when .execute() is called
    bad_service.posts.return_value.insert.return_value.execute.side_effect = Exception("API Down")
    bad_service.posts.return_value.update.return_value.execute.side_effect = Exception("API Down")
    
    # 2. Assign the grumpy service to the editor
    editor.service = bad_service
    
    # 3. Now run the save
    editor.save_post()

    # 4. NOW it will land in the 'except' block
    assert "Save Error" in editor.last_spell_report