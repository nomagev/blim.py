import pytest
from unittest.mock import MagicMock, patch
from blim import BlimEditor  # This imports your class

@patch('blim.build')
def test_save_post_success(mock_build):
    # 1. SETUP THE FAKE API (Modified for reliability)
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    # We grab the 'posts' level
    mock_posts = mock_service.posts.return_value
    
    # We ensure both 'insert' and 'update' return a mock that has an 'execute' method
    mock_posts.insert.return_value.execute.return_value = {'id': '12345'}
    mock_posts.update.return_value.execute.return_value = {'id': '12345'}

    # 2. INITIALIZE YOUR CLASS
    editor = BlimEditor()
    editor.body_field.text = "This is a **test** post."
    editor.title_field.text = "Test Title"
    editor.tags_field.text = "test, blim"
    editor.blog_id = "123"
    editor.current_post_id = None # Force it to use 'insert'
    
    # 3. RUN YOUR ACTUAL METHOD
    editor.save_post()

    # 4. ASSERTIONS (Modified to check for either action)
    # We check the 'posts' mock to see if its children were called
    api_was_called = mock_posts.insert.called or mock_posts.update.called
    assert api_was_called, "Blogger API was never reached!"
    
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
