# Spelling Master — Project Overview & Copilot Guidance

## Purpose
Build a Python web application called **Spelling Master** for 3rd-grade students (ages 8–9) to practice and test their spelling skills. A teacher or parent can load word lists into the app; the app then dictates each word aloud, the student types the spelling, and the app scores and gives feedback at the end.

---

## Technology Stack
| Layer | Choice |
|---|---|
| Backend | Python 3.11+, Flask |
| Database | SQLite via SQLAlchemy ORM |
| Frontend | Jinja2 templates + plain HTML/CSS/JS (no heavy frameworks) |
| Text-to-Speech | Web Speech API (browser-native, works offline) |
| Offline Handwriting | HTML5 Canvas (draw with mouse or touch stylus) |
| OCR (optional stretch) | Tesseract.js (client-side JS library) |

---

## Project Folder Structure
```
spelling_master/
│
├── app.py                  # Flask app factory & route registration
├── models.py               # SQLAlchemy models
├── routes/
│   ├── __init__.py
│   ├── admin.py            # Word-list management (CRUD)
│   └── quiz.py             # Quiz session logic
│
├── static/
│   ├── css/
│   │   └── style.css       # Kid-friendly styles
│   ├── js/
│   │   ├── speech.js       # Web Speech API wrapper
│   │   ├── canvas.js       # Offline handwriting canvas
│   │   └── quiz.js         # Quiz flow controller
│   └── sounds/
│       ├── correct.mp3     # Positive chime
│       └── wrong.mp3       # Gentle "try again" sound
│
├── templates/
│   ├── base.html           # Base layout with nav
│   ├── home.html           # Landing / word-list selector
│   ├── admin/
│   │   ├── manage_lists.html
│   │   └── edit_list.html
│   └── quiz/
│       ├── quiz.html       # Main quiz screen
│       └── results.html    # End-of-quiz feedback
│
├── instance/
│   └── spelling.db         # SQLite database (auto-created)
│
├── requirements.txt
└── README.md
```

---

## Core Features (must implement)
1. **Word Database Management** — Add / edit / delete word lists and individual words with optional hint sentences.
2. **Audio Dictation** — Each word is spoken aloud using the browser's Speech Synthesis API; the student can replay it.
3. **Keyboard Input Mode** — Student types the spelling; on submit the app checks it (case-insensitive).
4. **Offline Canvas Mode** — Toggle to a drawing canvas so the student can write by hand using a mouse or stylus.
5. **Live Scoring** — Track correct/incorrect per word during the quiz session.
6. **End-of-Quiz Feedback** — Show score, star rating, personalised message, and a review of missed words.

---

## Kid-Friendly UI Rules (apply everywhere)
- Bright, cheerful color palette — primary: `#FFD700` (gold), `#4CAF50` (green), `#2196F3` (blue), accents: `#FF6B6B` (coral).
- Rounded corners (`border-radius: 16px` minimum), large tap targets (≥ 48 px).
- Font: **Nunito** (Google Fonts) — friendly and very readable.
- Font size: body 18 px, headings 28–36 px, quiz word prompt 48 px.
- Animated feedback: bounce on correct, gentle shake on incorrect.
- No distracting ads or external links on the quiz screen.
- Progress bar showing how many words remain.
- Every interactive element has a clear hover/focus state.

---

## How the Files in This Folder Are Organised
Each numbered file is a **Copilot Chat prompt**. Open the file, copy its content into the Copilot Chat panel in VSCode (`Ctrl+Shift+I`), and run them **in order**:

| File | What Copilot will generate |
|---|---|
| `01_SETUP_AND_MODELS.md` | Project scaffold, `requirements.txt`, `models.py` |
| `02_BACKEND_ROUTES.md` | Flask routes for admin CRUD and quiz logic |
| `03_BASE_TEMPLATES.md` | `base.html`, `home.html`, global CSS |
| `04_ADMIN_UI.md` | Word-list management pages |
| `05_QUIZ_UI.md` | Quiz screen HTML + JS |
| `06_SPEECH_AND_CANVAS.md` | `speech.js` and `canvas.js` |
| `07_RESULTS_AND_FEEDBACK.md` | Results page with scoring logic |
| `08_POLISH_AND_TESTING.md` | Error handling, seed data, manual test checklist |

---

## Coding Conventions for Copilot
- Use **type hints** on all Python functions.
- Every Flask route returns JSON for API endpoints or renders a template — never mix.
- Keep JavaScript in separate `.js` files; do **not** inline `<script>` blocks longer than 5 lines.
- Add a docstring to every Python function and a JSDoc comment to every JS function.
- Use `flask.flash()` for user-facing success/error messages.
- All database writes must be wrapped in `try/except` with a rollback on error.
