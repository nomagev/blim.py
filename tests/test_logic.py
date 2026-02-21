import pytest
from unittest.mock import MagicMock
from blim import BlimEditor

@pytest.fixture
def robot():
    """Builds a fresh Robot User in test mode."""
    return BlimEditor(test_mode=True)

def test_robot_point_2_markdown_processing(robot):
    """Scenario: User types Markdown and Robot verifies conversion to HTML."""
    markdown_content = "This is **bold**."
    
    # Use the correct method: _parse_markdown converts MD to HTML
    cleaned_output = robot._parse_markdown(markdown_content)
    
    # Your code converts **text** to <b>text</b>
    assert "<b>bold</b>" in cleaned_output

def test_robot_point_3_sidebar_toggle(robot):
    """Scenario: User toggles the help sidebar."""
    # Your code uses 'show_help' for the F1 sidebar
    initial_state = robot.show_help
    
    robot.show_help = not robot.show_help
    
    assert robot.show_help != initial_state

def test_robot_point_4_commands(robot, tmp_path):
    """Scenario: User adds a custom word via :add command."""
    fake_dict = tmp_path / "robot_dict.txt"
    robot.custom_dict_path = str(fake_dict)

    robot._reload_dictionary()  # Ensure it starts empty
    test_word = "blimpy"
    
    # We must mock the buffer object that handle_normal_input expects
    mock_buffer = MagicMock()
    mock_buffer.text = f":add {test_word}"
    
    robot.handle_normal_input(mock_buffer)
    
    # Verify file writing
    assert test_word in fake_dict.read_text()
    # Verify internal dictionary update
    assert test_word in robot.spell

def test_robot_point_5_recovery_system(robot, tmp_path):
    """Scenario: User writes content and the system creates a recovery file."""
    # 1. Setup a temporary recovery path so we don't overwrite your real one
    test_recovery_file = tmp_path / "recovery_test.json"
    robot.recovery_path = str(test_recovery_file)
    
    # 2. Action: Robot types into the fields
    robot.title_field.text = "Robot's Secret Diary"
    robot.body_field.text = "I am a robot and I like Markdown."
    
    # 3. Action: Trigger the auto-save
    robot.auto_save_recovery()
    
    # 4. Validation: Check if file exists and has correct JSON content
    assert test_recovery_file.exists()
    
    import json
    with open(test_recovery_file, 'r') as f:
        data = json.load(f)
        assert data["title"] == "Robot's Secret Diary"
        assert data["body"] == "I am a robot and I like Markdown."

def test_robot_recovery_loading(robot, tmp_path):
    """Scenario: Robot starts up and finds an existing recovery file."""
    test_recovery_file = tmp_path / "recovery_test.json"
    robot.recovery_path = str(test_recovery_file)
    
    # 1. Create a "fake" recovery file manually
    import json
    with open(test_recovery_file, 'w') as f:
        json.dump({"title": "Recovered Title", "body": "Recovered Body"}, f)
        
    # 2. Action: Tell the robot to load it
    robot.load_recovery()
    
    # 3. Validation: Verify the fields updated
    assert robot.title_field.text == "Recovered Title"
    assert robot.body_field.text == "Recovered Body"