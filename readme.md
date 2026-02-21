# BLIM.PY

![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)
![Version: 1.7.5](https://img.shields.io/badge/Version-1.7.5-green)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-yellow)
[![Python Tests](https://github.com/nomagev/blim.py/actions/workflows/python-test.yml/badge.svg)](https://github.com/nomagev/blim.py/actions/workflows/python-test.yml)

### Distraction-Free Writer for Google Blogger

BLIM.PY is a terminal-based, minimalist writing environment designed for authors who want to publish to Google Blogger without the distractions of a web browser. It features a centered UI, real-time word counting, and a post management system.

<img title="Blim.py on Cool Retro Term" alt="Blim.py ASCII art" src="/img/blimpy-on-CRT.png">

## New & Improved Features
- **Multi-Language Support**: Full UI and spellcheck support for English (`:eng`) and Spanish (`:spa`).
- **Word Sprints**: Set a timer for focused writing sessions using `:sprint NN`.
- **Reading Time Estimation**: Real-time calculation of how long your post will take to read.
- **Local Recovery**: Automatic background saving to `.recovery_blim.tmp` to prevent data loss.
- **Ghost Mode**: Hide the entire UI while typing (`Ctrl+T`) to focus purely on the words.
- **Markdown Support**: Headers (#), Bold (**), Italics (*), Links, Lists, and Blockquotes.
- **Smart HTML Parser**: Generates clean, Blogger-ready HTML without paragraph nesting bugs.
- **Post Browser**: Manage Live and Draft posts with a dedicated menu (`Ctrl+O`).
- **Distraction-Free UI**: Centered text area with a clean, high-contrast interface.
- **Blogger Integration**: Fetch, edit, publish, or delete posts directly via the Google Blogger API.
- **Spellcheck**: Real-time spellchecking for multiple languages (ES/EN).

## Keyboard Shortcuts
- `F1`: Toggle Help Menu.
- `Ctrl + O`: Open Post Browser / Fetch Posts
- `Ctrl + S`: Save as Draft
- `Ctrl + P`: Publish Live
- `Ctrl + T`: Toggle Ghost Mode
- `Ctrl + B`: Bold Selection
- `Ctrl + K`: Italic Selection
- `Ctrl + L`: Create Unordered List
- `Ctrl + Q`: Create Blockquote
- `Ctrl + D`: Run Spellcheck
- `TAB`: Switch focus (Title / Body / Commands)

## Requirements
- Python 3.10+
- Google Cloud Project with Blogger API enabled
- `client_secrets.json` in the root directory

## Installation
1. Clone the repository.
   ```bash
   git clone [https://github.com/youruser/blim.py.git](https://github.com/youruser/blim.py.git)
   cd blim.py
2. Install dependencies:
   ```bash
   pip install prompt_toolkit pyspellchecker google-api-python-client google-auth-oauthlib markdown
3. Place your client_secrets.json (from [Google Cloud Console](https://console.cloud.google.com/)) in the root folder.

   To use Blim, you must configure a project in the Google Cloud Console:

   **Enable API**: Search for and enable the **Blogger API v3**.

   OAuth Consent Screen:

   Set User Type to **External**.

   Add the scope: `.../auth/blogger`.

      Important: Set Publishing Status to Production to prevent 7-day token expiration.

   **Credentials**: Create an **OAuth 2.0 Client ID** (Type: Desktop App) and download the JSON as `client_secrets.json`.

4. Run the App:
   ```bash
   chmod +x run.sh
   ./run.sh
##  Security & Privacy
This repository includes a `.gitignore` file to ensure that your `client_secrets.json`, `token.json`, and `config.json` are never uploaded to GitHub. 

**Never share these files.** They contain your private blog access and Google API credentials.

## License
**License:** This project is licensed under the **GNU General Public License v2.0.** You are free to share and change this software as long as the source code remains open.