# BLIM.PY

![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)
![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-green)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-yellow)
[![Python Tests](https://github.com/nomagev/blim.py/actions/workflows/python-test.yml/badge.svg)](https://github.com/nomagev/blim.py/actions/workflows/python-test.yml)

### Distraction-Free Writer for Google Blogger

BLIM.PY is a terminal-based, minimalist writing environment designed for authors who want to publish to Google Blogger without the distractions of a web browser. It features a centered UI, real-time word counting, and a post management system.

## Features
- **Distraction-Free UI**: Centered text area with a clean, high-contrast interface.
- **Blogger Integration**: Fetch, edit, publish, or delete posts directly via the Google Blogger API.
- **Post Browser**: A dedicated menu (`Ctrl+L`) to manage Live and Draft posts.
- **Spellcheck**: Real-time spellchecking for multiple languages (ES/EN/FR).
- **Lightweight Assets**: Static text and banners stored externally for a cleaner codebase.

## Requirements
- Python 3.10+
- Google Cloud Project with Blogger API enabled
- `client_secrets.json` in the root directory

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install prompt_toolkit pyspellchecker google-api-python-client google-auth-oauthlib

##  Security & Privacy
This repository includes a `.gitignore` file to ensure that your `client_secrets.json`, `token.json`, and `config.json` are never uploaded to GitHub. 

**Never share these files.** They contain your private blog access and Google API credentials.
