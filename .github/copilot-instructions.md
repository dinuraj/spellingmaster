# Copilot Instructions — Spelling Master

> These instructions describe every aspect of the **Spelling Master** application so that
> GitHub Copilot (or any developer) can reproduce, maintain, and extend the project.

---

## 1  Project Purpose

**Spelling Master** is a kid-friendly web application for 3rd-grade students (ages 8–9).  
It provides two quiz modes:

| Mode | Description |
|---|---|
| **Spelling Quiz** | A word is spoken aloud via Web Speech API; the student types the spelling. Optional handwriting canvas + Tesseract OCR fallback. |
| **Fill-in-the-Blank Quiz** | A sentence is shown with a missing word (indicated by `_____`); the student types the missing word. |

Teachers / parents manage word lists and fill questions through an admin panel.

---

## 2  Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.12+ | All backend code |
| Framework | Flask 3.x (app factory) | Lightweight, Jinja2 templates |
| ORM / DB | Flask-SQLAlchemy + SQLite | DB file: `instance/spelling.db` |
| Forms / CSRF | Flask-WTF + WTForms | CSRF tokens on every mutating form |
| Frontend | Jinja2 templates + plain HTML / CSS / JS | No React, no heavy frameworks |
| Text-to-Speech | Web Speech API (browser-native) | `static/js/speech.js` |
| Handwriting | HTML5 Canvas | `static/js/canvas.js` |
| OCR (optional) | Pillow + pytesseract (server-side) | `/quiz/recognize` endpoint |
| Testing | pytest | In-memory SQLite, fixtures in `tests/conftest.py` |
| Package mgr | pip + `requirements.txt` | Virtual env at `.venv/` |

---

## 3  Project Structure

```
spellingmaster/
├── app.py                       # Flask application factory (create_app)
├── extensions.py                # Shared singletons: db (SQLAlchemy), csrf (CSRFProtect)
├── models.py                    # All SQLAlchemy models
├── seed_data.py                 # Seed sample word lists for development
├── import_words.py              # Import words from docs/words.json
├── requirements.txt             # Python dependencies
├── .gitignore
├── .env                         # Environment overrides (SECRET_KEY, DATABASE_URL)
│
├── routes/
│   ├── __init__.py              # Empty module docstring
│   ├── admin.py                 # admin_bp  → /admin/*   (CRUD word lists, fill questions)
│   ├── quiz.py                  # quiz_bp   → /quiz/*    (spelling quiz + OCR)
│   ├── fillgen.py               # fillgen_bp → /admin/*  (generate / import fill questions)
│   └── fillquiz.py              # fillquiz_bp → /fillquiz/* (fill-in-the-blank quiz)
│
├── templates/
│   ├── base.html                # Base layout: nav bar, flash messages, footer
│   ├── home.html                # Landing page (word lists + fill quiz card)
│   ├── admin/
│   │   ├── manage_lists.html    # Word list CRUD + fill questions import card
│   │   ├── edit_list.html       # Edit single list + add / bulk-import words
│   │   ├── fill_questions.html  # Paginated fill question browser
│   │   ├── edit_fill_question.html
│   │   └── bulk_edit_fill_questions.html
│   ├── quiz/
│   │   ├── quiz.html            # Active spelling quiz screen
│   │   └── results.html         # Spelling quiz results
│   ├── fillquiz/
│   │   ├── index.html           # Fill quiz launcher (size selector + recent attempts)
│   │   ├── play.html            # Paged fill quiz (5 questions per page)
│   │   └── results.html         # Fill quiz results (stars, confetti, review)
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/style.css            # Single stylesheet (kid-friendly theme)
│   ├── js/
│   │   ├── quiz.js              # Spelling quiz flow controller
│   │   ├── speech.js            # Web Speech API wrapper
│   │   ├── canvas.js            # Handwriting canvas
│   │   └── fillquiz.js          # Fill quiz: auto-focus + Enter navigation
│   ├── img/                     # Favicon, optional images
│   └── sounds/                  # correct.mp3, wrong.mp3
│
├── scripts/
│   ├── import_fill_questions.py # One-time JSON → DB import
│   ├── generate_fill_questions.py
│   ├── generate_llm_fill_questions.py
│   ├── generate_difficult_lists.py
│   ├── seed_and_migrate.py
│   └── ...
│
├── data/
│   ├── fill_questions_june_july_aug_sept.json   # 158 words × 3 questions
│   ├── fill_questions_oct_nov_dec_jan_feb.json   # 200 words × 3 questions
│   ├── fill_questions.json                       # Earlier candidate pool
│   └── ...
│
├── tests/
│   ├── conftest.py              # App + client fixtures (in-memory SQLite)
│   ├── test_basic.py
│   ├── test_models.py
│   ├── test_fillquiz_import_and_admin.py
│   ├── test_fillquiz_play_finish.py
│   └── test_routes_extended.py
│
├── docs/                         # Copilot Chat prompt files (00–09)
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_SETUP_AND_MODELS.md
│   ├── ...
│   └── 09_FILL_IN_THE_BLANKS.md
│
├── instance/                     # Auto-created; holds spelling.db (git-ignored)
└── .venv/                        # Virtual environment (git-ignored)
```

---

## 4  Application Factory (`app.py`)

```python
def create_app(test_config=None) -> Flask:
```

Key behaviours:
1. Loads `.env` via `python-dotenv`.
2. Sets `SECRET_KEY` (defaults to `'dev-secret'`).
3. Sets `SQLALCHEMY_DATABASE_URI` (defaults to `sqlite:///<instance>/spelling.db`).
4. Initialises `db` and `csrf` from `extensions.py`.
5. Registers four blueprints (see §5).
6. Root `/` redirects to `/quiz/` (the home page).
7. Calls `db.create_all()` inside the app context.
8. Registers custom 404 and 500 error handlers.

### Extensions (`extensions.py`)

```python
db = SQLAlchemy()      # Import as: from extensions import db
csrf = CSRFProtect()   # Import as: from extensions import csrf
```

These are initialised in the factory with `db.init_app(app)` / `csrf.init_app(app)`.  
**Never** create a second `SQLAlchemy()` or `CSRFProtect()` instance.

---

## 5  Blueprints & URL Map

| Blueprint | Variable | Prefix | File |
|---|---|---|---|
| Admin | `admin_bp` | `/admin` | `routes/admin.py` |
| Spelling Quiz | `quiz_bp` | `/quiz` | `routes/quiz.py` |
| Fill Generator | `fillgen_bp` | `/admin` | `routes/fillgen.py` |
| Fill Quiz | `fillquiz_bp` | `/fillquiz` | `routes/fillquiz.py` |

### 5.1  Admin Routes (`admin_bp` + `fillgen_bp`)

| Method | URL | Handler | Purpose |
|---|---|---|---|
| GET | `/admin/` | `admin_bp.index` | List all word lists + fill question import card |
| GET/POST | `/admin/list/new` | `admin_bp.create_list` | Create word list |
| GET/POST | `/admin/list/<id>/edit` | `admin_bp.edit_list` | Edit list + manage words |
| POST | `/admin/list/<id>/delete` | `admin_bp.delete_list` | Delete list |
| POST | `/admin/list/<id>/word/add` | `admin_bp.add_word` | Add single word (JSON/form) |
| POST | `/admin/word/<id>/delete` | `admin_bp.delete_word` | Delete word |
| POST | `/admin/list/<id>/bulk` | `admin_bp.bulk_import` | Bulk import words |
| GET | `/admin/fillquestions` | `admin_bp.list_fill_questions` | Paginated fill questions browser |
| GET/POST | `/admin/fillquestions/<id>/edit` | `admin_bp.edit_fill_question` | Edit one fill question |
| POST | `/admin/fillquestions/<id>/delete` | `admin_bp.delete_fill_question` | Delete fill question |
| GET/POST | `/admin/fillquestions/bulk_edit` | `admin_bp.bulk_edit_fill_questions` | Bulk edit (pipe-separated) |
| POST | `/admin/generate-fill-questions` | `fillgen_bp.generate_fill_questions` | Template-based generation (debug only) |
| POST | `/admin/import-fill-questions` | `fillgen_bp.import_fill_questions` | Import JSON files into DB |

### 5.2  Spelling Quiz Routes (`quiz_bp`)

| Method | URL | Handler | Purpose |
|---|---|---|---|
| GET | `/quiz/` | `quiz_bp.index` | Home page — word lists + fill quiz card |
| POST | `/quiz/start` | `quiz_bp.start_quiz` | Start spelling quiz (session-based) |
| GET | `/quiz/play` | `quiz_bp.play` | Show current word |
| POST | `/quiz/check` | `quiz_bp.check` | Check answer (JSON API) |
| POST | `/quiz/recognize` | `quiz_bp.recognize_handwriting` | OCR from canvas (Pillow + pytesseract) |
| GET | `/quiz/results` | `quiz_bp.results` | Show results + persist `QuizResult` |
| POST | `/quiz/reset` | `quiz_bp.reset` | Clear session |

### 5.3  Fill-in-the-Blank Quiz Routes (`fillquiz_bp`)

| Method | URL | Handler | Purpose |
|---|---|---|---|
| GET | `/fillquiz/` | `fillquiz_bp.index` | Launcher — word count, size selector, recent attempts |
| POST | `/fillquiz/start` | `fillquiz_bp.start_quiz` | Pick questions, create `FillQuizAttempt`, redirect to play |
| GET/POST | `/fillquiz/play` | `fillquiz_bp.play_page` | Paged quiz (5 per page), saves answers in session |
| GET/POST | `/fillquiz/finish` | `fillquiz_bp.finish_quiz` | Score, save results, redirect to results |
| GET | `/fillquiz/results` | `fillquiz_bp.results_page` | Score card, stars, review, confetti |

---

## 6  Database Models (`models.py`)

### 6.1  `WordList`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `name` | String(100) | Unique, not null |
| `description` | String(255) | Optional |
| `created_at` | DateTime | Default `utcnow` |

Relationship: `words` → `Word` (cascade `all, delete-orphan`, lazy `dynamic`).

### 6.2  `Word`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `word` | String(100) | Not null, stored lowercase |
| `hint` | String(255) | Optional example sentence |
| `list_id` | Integer | FK → `word_lists.id`, not null |

### 6.3  `QuizResult`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer | PK |
| `list_id` | Integer | FK → `word_lists.id` |
| `total_words` | Integer | |
| `correct_count` | Integer | |
| `missed_words` | Text | JSON string `["word1", "word2"]` |
| `completed_at` | DateTime | Default `utcnow` |

Property: `score_percent` → float.  
Method: `missed_list()` → `List[str]`.

### 6.4  `FillQuestion`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer | PK |
| `word` | String(100) | Not null, indexed |
| `question` | String(1000) | Sentence with `_____` blank |
| `answer` | String(100) | The correct word |
| `month` | String(20) | Optional (e.g. "June") |
| `subject` | String(50) | Optional (e.g. "ENGLISH") |
| `source_file` | String(200) | JSON filename it was imported from |

Method: `as_dict()` → `dict`.

### 6.5  `FillQuizAttempt`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer | PK |
| `created_at` | DateTime | Default `utcnow` |
| `completed_at` | DateTime | Set when finished |
| `total_questions` | Integer | |
| `correct_count` | Integer | |
| `question_ids` | Text | JSON list of `FillQuestion.id` in order |
| `results` | Text | JSON list of per-question result dicts |

---

## 7  Data Format

Fill question JSON files live in `data/` and share this structure:

```json
{
  "items": [
    {
      "word": "conversation",
      "suitable": true,
      "questions": [
        {
          "question": "During lunch they had a long _____ about their school project.",
          "answer": "conversation"
        },
        { "question": "...", "answer": "conversation" },
        { "question": "...", "answer": "conversation" }
      ]
    }
  ]
}
```

- Each **word** has exactly **3 questions**.
- The blank in the question is represented by `_____` (five underscores).
- The `answer` field always matches the `word`.
- The import endpoint picks one random question per word for each quiz attempt.

Word lists (`docs/words.json`) map month → subject → word list:

```json
{
  "June": {
    "ENGLISH": ["word1", "word2"],
    "SCIENCE": ["word3"]
  }
}
```

---

## 8  Fill Quiz Flow (Detailed)

1. **Launcher** (`GET /fillquiz/`): Shows word count, question count, radio buttons for quiz size (15 / 30 / 50 / All), and a table of the 5 most recent attempts.
2. **Start** (`POST /fillquiz/start`): Picks `N` random unique words, selects one random question per word, creates a `FillQuizAttempt` row, stores the attempt ID and an empty answers dict in `session`, redirects to page 1.
3. **Play** (`GET|POST /fillquiz/play?page=N`): Renders 5 question cards per page. Each card shows the question number, sentence text, and an input field. On POST, saves the current page's answers into `session['fill_answers']` (keyed by question ID), then redirects to `prev`, `next`, or `finish`.
4. **Finish** (`GET|POST /fillquiz/finish`): Iterates all question IDs, compares `session['fill_answers']` to the correct answer (case-insensitive), computes score, updates the `FillQuizAttempt` row, stores missed words in session for practice mode, clears quiz session keys, redirects to results.
5. **Results** (`GET /fillquiz/results?attempt_id=N`): Shows a score card (fraction, percentage, stars ⭐, motivational message), confetti animation for 3 stars, two-column review (correct words in green, wrong words in red with expected answer), and action buttons (Try Again, Choose Different Size, Practice Missed Words).

### Session Keys Used

| Key | Type | Lifetime |
|---|---|---|
| `fill_attempt_id` | int | Set on start, cleared on finish |
| `fill_answers` | dict `{ "qid": "answer" }` | Updated each page POST, cleared on finish |
| `fill_missed_words` | list of strings | Set on finish, consumed by start (missed_only) |

---

## 9  Spelling Quiz Flow

1. `POST /quiz/start` → picks words from the selected `WordList`, shuffles, stores in `session['quiz']`.
2. `GET /quiz/play` → shows current word (spoken via Web Speech API), student types answer.
3. `POST /quiz/check` → JSON API: compares answer (case-insensitive), returns `{correct, correct_word, next_available}`.
4. `POST /quiz/recognize` → accepts base64 canvas image, runs Pillow preprocessing + pytesseract OCR, returns `{recognized}`.
5. `GET /quiz/results` → score card + stars + review. Persists `QuizResult` row, clears session.

---

## 10  Frontend Conventions

### 10.1  Template Hierarchy

All templates extend `base.html`:
```html
{% extends 'base.html' %}
{% block title %}Page Title{% endblock %}
{% block content %}...{% endblock %}
```

`base.html` provides:
- Google Fonts link (Nunito)
- Favicon
- CSS link (`/static/css/style.css`)
- Sticky header with nav links: Home · Fill Quiz · Manage Words
- Flash message container (categories: `success`, `error`, `warning`)
- `<main class="container">{% block content %}{% endblock %}</main>`
- Footer

### 10.2  CSS Design System

**Single file:** `static/css/style.css` (~80 lines).

| Token | Value | Usage |
|---|---|---|
| `--gold` | `#FFD700` | Primary buttons, star rating |
| `--green` | `#4CAF50` | Success states, correct answers |
| `--blue` | `#2196F3` | Focus rings, question numbers |
| `--coral` | `#FF6B6B` | Errors, wrong answers |
| `--bg` | `#FFFDF0` | Page background (warm ivory) |
| `--card-bg` | `#FFFFFF` | Card surfaces |
| `--radius` | `16px` | Border radius for cards |
| `--shadow` | `0 4px 16px rgba(0,0,0,0.10)` | Card elevation |

Font: **Nunito** (400, 600, 700, 800 weights) loaded from Google Fonts.

Key classes:
- `.container` — max-width 960 px, centred
- `.card` — white rounded card with shadow
- `.btn`, `.btn-primary`, `.btn-success`, `.btn-danger`, `.btn-secondary`, `.btn-warning` — pill-shaped buttons
- `.btn-lg`, `.btn-sm` — size variants
- `.hero` — centred hero section with padding
- `.lists-grid` — CSS Grid, `repeat(auto-fit, minmax(240px, 1fr))`
- `.badge` — small rounded label
- `.progress-container` + `.progress-bar` — quiz progress indicator
- `.score-card` — gradient background results card
- `.score-stars`, `.score-fraction`, `.score-percent`, `.score-message` — results typography
- `.fill-question-card` — fill quiz question card
- `.fill-answer-input` — text input with blue focus ring
- `.size-selector` — radio button group styled as pill toggles
- `.fill-pager` — flex row for prev / next / finish navigation
- `.review-grid` — two-column grid for correct / wrong review
- `.confetti-piece` + `@keyframes fall` — confetti animation
- `.animate-bounce`, `.animate-shake` — micro-animations

Media query: at `≤ 600 px`, `.review-grid` collapses to single column and `.main-nav` is hidden.

### 10.3  JavaScript

All JS files are plain ES5/ES6 — **no build step, no bundlers, no npm for frontend**.

| File | Purpose |
|---|---|
| `quiz.js` | Spelling quiz: listen for answer submit, call `/quiz/check`, update UI |
| `speech.js` | Wrap `window.speechSynthesis` — `speakWord(word)` function |
| `canvas.js` | Handwriting canvas with touch/mouse events, export to base64 |
| `fillquiz.js` | Auto-focus first empty input, Enter key advances to next input |

### 10.4  CSRF Tokens

Every mutating `<form>` must include:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
```

For AJAX `POST` requests, include the token in the request body or as a header.

---

## 11  Testing

### 11.1  Test Setup

```bash
# From project root
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

### 11.2  Fixture Pattern (`tests/conftest.py`)

```python
@pytest.fixture(scope='session')
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
```

- Session-scoped app + in-memory SQLite.
- Function-scoped `client` for each test.
- Always import from the project root (`from app import create_app; from extensions import db`).

### 11.3  Test Conventions

- File naming: `tests/test_<module>.py`.
- Each test function: `test_<what_it_tests>`.
- Use `client.get()` / `client.post()` with `follow_redirects=True` when needed.
- Assert status codes and check for expected strings in `res.data`.
- For fill quiz tests: create `FillQuestion` rows in a `with app.app_context()` block before testing routes.
- CSRF token can be disabled in tests by setting `WTF_CSRF_ENABLED: False` in test config (or extract it from the form).

---

## 12  Development Workflow

### 12.1  First-Time Setup

```bash
cd spellingmaster
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py                      # starts dev server on http://127.0.0.1:5000
```

### 12.2  Seed Data

```bash
# Spelling word lists (3 sample lists)
python seed_data.py

# Fill questions (imports ~1071 questions / 347 words from JSON files)
PYTHONPATH=. python scripts/import_fill_questions.py
# Or use the admin UI: Admin → Import Fill Questions button
```

### 12.3  Database

- SQLite stored at `instance/spelling.db`.
- Tables are auto-created by `db.create_all()` on app startup.
- No migrations tool — schema changes require `db.drop_all() + db.create_all()` or manual `ALTER TABLE`.
- The `instance/` directory is git-ignored.

### 12.4  Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `'dev-secret'` | Flask session signing key |
| `DATABASE_URL` | `sqlite:///<instance>/spelling.db` | SQLAlchemy URI |
| `TESSERACT_CMD` | (auto-detected) | Path to Tesseract binary |

---

## 13  Coding Conventions

### 13.1  Python

- **PEP 8** style.
- Use `from __future__ import annotations` at the top of every Python file.
- Type hints on function signatures (`def create_app(test_config: dict | None = None) -> Flask:`).
- Module docstrings on every file.
- Imports: standard library → third-party → local (`from extensions import db`).
- Flash messages use categories: `'success'`, `'error'`, `'warning'`.
- All routes that modify data must use `POST` (not `GET`).
- Use `db.session.add()` + `db.session.commit()` with try/except + `db.session.rollback()`.
- Duplicate checks: query `filter_by()` before inserting.
- JSON fields stored as `db.Column(db.Text)` and serialised/deserialised with `json.dumps()` / `json.loads()`.

### 13.2  Templates (Jinja2)

- Every template extends `base.html`.
- Use `url_for()` for internal links in Python; in templates, hardcoded URL paths like `/admin/` are acceptable for nav links.
- Cards use `<div class="card">`.
- Forms use standard `<form method="post" action="...">` with CSRF tokens.
- Empty states: `<div class="empty-state">` with an emoji and a CTA button.
- Tables: `<table class="admin-table">`.

### 13.3  CSS

- Use CSS custom properties defined in `:root`.
- No CSS preprocessors — plain CSS only.
- Keep all styles in `static/css/style.css`.
- Use the existing colour palette; don't introduce new colours without updating `:root`.
- Prefer `border-radius: 50px` for buttons (pill shape), `var(--radius)` (16 px) for cards.

### 13.4  JavaScript

- Plain JS (no TypeScript, no JSX, no bundler).
- Each file wrapped in `document.addEventListener('DOMContentLoaded', ...)`.
- Use `fetch()` for AJAX; no jQuery.
- Include CSRF tokens in POST requests.

---

## 14  Scoring & Feedback System

Both quiz types use the same star / message logic:

| Score | Stars | Confetti |
|---|---|---|
| ≥ 90 % | ⭐⭐⭐ | Yes (fill quiz only) |
| ≥ 70 % | ⭐⭐ | No |
| < 70 % | ⭐ | No |

Messages:

| Range | Message |
|---|---|
| 100 % | "Amazing! You're a Spelling Superstar! 🌟" (or Fill-in-the-Blank Superstar) |
| 90–99 % | "Fantastic work! Almost perfect!" |
| 70–89 % | "Great job! Keep practicing those tricky words." |
| 50–69 % | "Good effort! Review the words you missed and try again." |
| < 50 % | "Keep going! Practice makes perfect. You've got this! 💪" |

Results pages show a two-column review grid: correct words (green) on the left, wrong words (red) on the right.

---

## 15  Adding New Features — Checklist

When adding a new feature to Spelling Master, follow this sequence:

1. **Model**: Add columns or new models in `models.py`. Use the existing `db` from `extensions.py`.
2. **Route**: Add a new blueprint or extend an existing one in `routes/`. Register in `app.py` if new.
3. **Template**: Create or modify templates in `templates/`. Extend `base.html`.
4. **CSS**: Add styles to `static/css/style.css`. Use existing CSS custom properties.
5. **JS** (if needed): Add a new file in `static/js/` or extend an existing one.
6. **Navigation**: Update `base.html` nav and/or `home.html` to link to the new feature.
7. **Admin**: If the feature needs admin management, add routes and templates under admin.
8. **Seed/Import**: Provide a script in `scripts/` or an admin endpoint to load data.
9. **Tests**: Add test file in `tests/`. Use the `app` and `client` fixtures from `conftest.py`.
10. **Docs**: Add a numbered markdown file in `docs/` describing the feature.

---

## 16  Common Patterns

### Creating a New Blueprint

```python
# routes/new_feature.py
from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import SomeModel

new_feature_bp = Blueprint('new_feature_bp', __name__)

@new_feature_bp.route('/')
def index():
    return render_template('new_feature/index.html')
```

Register in `app.py`:
```python
from routes.new_feature import new_feature_bp
app.register_blueprint(new_feature_bp, url_prefix='/new-feature')
```

### Adding a Template

```html
{% extends 'base.html' %}
{% block title %}New Feature{% endblock %}
{% block content %}
<section class="hero">
  <h1>New Feature 🎉</h1>
</section>
<section class="card">
  <!-- content here -->
</section>
{% endblock %}
```

### Writing a Test

```python
def test_new_feature_page(client, app):
    with app.app_context():
        # seed test data
        ...
    res = client.get('/new-feature/')
    assert res.status_code == 200
    assert b'New Feature' in res.data
```

### Import Script Pattern

```python
"""One-time import script."""
from app import create_app
from extensions import db
from models import SomeModel
import json
from pathlib import Path

app = create_app()
with app.app_context():
    # load data, insert rows, commit
    db.session.commit()
```

Run with: `PYTHONPATH=. python scripts/my_script.py`

---

## 17  Git & Deployment

- **Branch**: `main` (single branch workflow).
- **Commit style**: Descriptive subject line + bullet list of changes in body.
- **Git-ignored**: `.venv/`, `instance/`, `*.db`, `__pycache__/`, `.env`, `node_modules/`, `dist/`, `.DS_Store`, `.vscode/`.
- **No Docker** currently — runs directly via `python app.py`.
- **No CI/CD** pipeline yet — tests run locally with `pytest`.

---

## 18  Known Constraints & Design Decisions

1. **No migrations**: Schema changes are manual. If models change, delete `instance/spelling.db` and let `db.create_all()` recreate it, then re-import data.
2. **No authentication**: The app has no login system. The admin panel is openly accessible. Suitable only for local / classroom use.
3. **Session-based quizzes**: Quiz state is stored in Flask's signed cookie session. This limits quiz size (cookie max ~4 KB for answers). For very large quizzes, answers should be moved to the database.
4. **SQLite only**: No support for PostgreSQL or other backends, though switching is straightforward via `DATABASE_URL`.
5. **OCR is optional**: pytesseract requires system-level Tesseract install. The app works fine without OCR — students can type answers.
6. **No real-time features**: No WebSockets or SSE. Everything is request/response.
7. **Single CSS file**: All styles in one file for simplicity. No CSS modules, no Tailwind.

---

## 19  Prompt Docs Reference

The `docs/` folder contains step-by-step Copilot Chat prompts that were used to build the app:

| File | Topic |
|---|---|
| `00_PROJECT_OVERVIEW.md` | Architecture, stack, folder structure |
| `01_SETUP_AND_MODELS.md` | App factory, database models, `.env` |
| `02_BACKEND_ROUTES.md` | Admin + quiz route handlers |
| `03_BASE_TEMPLATES.md` | Base layout, home page, nav |
| `04_ADMIN_UI.md` | Word list management templates |
| `05_QUIZ_UI.md` | Quiz play + results templates |
| `06_SPEECH_AND_CANVAS.md` | Web Speech API, handwriting canvas |
| `07_RESULTS_AND_FEEDBACK.md` | Scoring, stars, review grid |
| `08_POLISH_AND_TESTING.md` | Seed data, error pages, README, testing |
| `09_FILL_IN_THE_BLANKS.md` | Fill-in-the-blank quiz feature |

Each doc follows the format of a self-contained Copilot Chat prompt with acceptance criteria.

---

## 20  Quick Reference Commands

```bash
# Start development server
source .venv/bin/activate
python app.py

# Run tests
PYTHONPATH=. pytest tests/ -v

# Seed word lists
python seed_data.py

# Import fill questions
PYTHONPATH=. python scripts/import_fill_questions.py

# Import words from docs/words.json
python import_words.py

# Check database contents
sqlite3 instance/spelling.db ".tables"
sqlite3 instance/spelling.db "SELECT COUNT(*) FROM fill_questions;"
sqlite3 instance/spelling.db "SELECT COUNT(DISTINCT word) FROM fill_questions;"
```
