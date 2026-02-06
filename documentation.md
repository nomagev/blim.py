# Blim.py | Professional Blogger Terminal Editor

Blim.py is a distraction-free, terminal-based writing suite designed for bloggers who value speed, focus, and the efficiency of the command line.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.8+**
* **Google Cloud Project**: You must enable the Blogger API and download `client_secrets.json`.
* **Dependencies**:
  `pip install google-api-python-client google-auth-oauthlib prompt_toolkit pygments`

### First Run
1. Place your `client_secrets.json` in the root directory.
2. Run `python blim.py`.
3. Your browser will open for a one-time Google authentication.
4. A `token.json` will be created locally to keep you logged in.

---

## ⌨️ Interface & Navigation

Blim.py uses a **Hybrid TUI** (Text User Interface) that supports both keyboard and mouse.

| Action | Shortcut | Mouse |
| :--- | :--- | :--- |
| **Switch Focus** | `Ctrl + W` | Click into any field |
| **Command Bar** | `Ctrl + G` | Click bottom bar |
| **Open Browser** | `Ctrl + L` | Click "Post Browser" in Help |
| **Toggle Help** | `F1` | — |

---

## 🛠 Command Reference

Commands are entered in the **Command Bar** (bottom) starting with a colon `:`.

* `:new` — Resets the editor for a fresh post.
* `:sprint <mins>` — Starts a timed Word Sprint (e.g., `:sprint 25`).
* `:restore` — Recovers data from the local hidden buffer after a crash or accidental exit.
* `:q` — Exits the application safely.
* `:help` — Opens the visual manual.

---

## ✍️ Writing Features

### Word Sprint Mode
Designed for the Pomodoro technique. When active, a live timer appears in the status bar. 
> **Tip:** Use sprints to bypass "Writer's Block" by focusing on the clock rather than the content.

### Reading Speed
The status bar automatically calculates the "Minutes to Read" based on an average reading speed of **225 words per minute**. This helps you gauge if your post is too long or too short for your audience.

### Local Recovery
Blim.py automatically saves a background snapshot every 60 seconds to `.recovery_blim.tmp`. If the power goes out or the terminal hangs, your work is safe.

---

## 🌐 Blogger Integration

* **Drafts vs. Live**: Use `Ctrl + S` to save a private draft and `Ctrl + P` to publish live to your blog.
* **Browser**: The Post Browser allows you to fetch your last 50 posts. You can navigate with arrow keys, press `Enter` to load, or `Delete` to remove a post.

---

## ⚖️ License
This project is licensed under the **GPL 2.0 License**.