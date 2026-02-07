import pytest
from unittest.mock import MagicMock, patch
from blim import BlimEditor  # This imports your class

@patch('blim.build')
def test_save_post_success(mock_build):
    # 1. SETUP
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_posts = mock_service.posts.return_value
    
    # Ensure execute() returns a dictionary
    mock_posts.insert.return_value.execute.return_value = {'id': '12345'}
    mock_posts.update.return_value.execute.return_value = {'id': '12345'}

    # 2. INITIALIZE & FORCE STATE
    editor = BlimEditor()
    editor.is_offline = False  # Force online
    editor.service = mock_service # Force the mock service into the editor
    
    editor.body_field.text = "This is a **test** post."
    editor.title_field.text = "Test Title"
    editor.blog_id = "123"
    editor.current_post_id = None 
    
    # 3. ACTION
    editor.save_post()

    # 4. ASSERTIONS
    # We check if the 'insert' method on our mock was called
    assert mock_posts.insert.called, "The code never called the insert method!"
    assert "Saved" in editor.last_spell_report

@patch('blim.build')
def test_save_post_failure(mock_build):
    editor = BlimEditor()
    editor.is_offline = False
    
    # 1. Create a "grumpy" service
    bad_service = MagicMock()
    # We define 'bad_posts' here so we can use it in assertions later
    bad_posts = bad_service.posts.return_value
    
    # Tell the service to raise an error when .execute() is called
    bad_posts.insert.return_value.execute.side_effect = Exception("API Down")
    bad_posts.update.return_value.execute.side_effect = Exception("API Down")
    
    # 2. Assign the grumpy service to the editor
    editor.service = bad_service
    
    # 3. Run your actual method
    editor.save_post()

    # 4. ASSERTIONS (Corrected for the failure case)
    # We check 'bad_posts' (the variable we defined above)
    was_called = bad_posts.insert.called or bad_posts.update.called
    assert was_called, "The Blogger API was never even attempted!"
    
    # We check for "Save Error" because we EXPECTED a failure here
    assert "Save Error" in editor.last_spell_report
