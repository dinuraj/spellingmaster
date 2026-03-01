# Prompt 01 — Project Setup & Database Models

> **How to use:** Paste this entire prompt into GitHub Copilot Chat (`Ctrl+Shift+I`) and send it.  
> Copilot will generate the files listed below. Accept each file into your workspace.

---

## Your Task

Generate the initial project scaffold for a Flask application called **Spelling Master**.

### 1. `requirements.txt`
Include the following dependencies (pin versions):
- `flask>=3.0`
- `flask-sqlalchemy>=3.1`
- `flask-wtf>=1.2`        ← for CSRF protection on forms
- `wtforms>=3.1`
- `python-dotenv>=1.0`

### 2. `app.py` — Flask Application Factory
- Use the **application factory** pattern (`create_app()` function).
- Load config from a `.env` file using `python-dotenv` (`SECRET_KEY`, `DATABASE_URL`).
- Default `DATABASE_URL` to `sqlite:///instance/spelling.db` if not set.
- Register blueprints `admin_bp` (prefix `/admin`) and `quiz_bp` (prefix `/quiz`).
- Create all database tables on first run using `db.create_all()` inside an `app.context`.
- Add a root route `/` that redirects to `home.html`.

### 3. `models.py` — SQLAlchemy Models

Create **three models**:

#### `WordList`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String(100) | Unique, not null — e.g. "Week 3 Words" |
| `description` | String(255) | Optional description for the teacher |
| `created_at` | DateTime | Auto-set to `utcnow` |

Relationship: one `WordList` has many `Word` objects (cascade delete).

#### `Word`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `word` | String(100) | The spelling word (stored lowercase) |
| `hint` | String(255) | Optional sentence using the word |
| `list_id` | Integer | Foreign key → `WordList.id` |

Add a `__repr__` method to both models.

#### `QuizResult`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer | Primary key |
| `list_id` | Integer | FK → `WordList.id` |
| `total_words` | Integer | |
| `correct_count` | Integer | |
| `missed_words` | Text | JSON string — list of words the student got wrong |
| `completed_at` | DateTime | Auto-set to `utcnow` |

Add a helper property `score_percent` that returns `(correct_count / total_words) * 100`.

### 4. `routes/__init__.py`
Empty file with a module docstring.

### 5. `.env.example`
```
SECRET_KEY=change-me-to-a-random-string
DATABASE_URL=sqlite:///instance/spelling.db
```

### 6. `.gitignore`
Ignore: `__pycache__/`, `*.pyc`, `.env`, `instance/`, `.venv/`, `*.db`

---

## Acceptance Criteria
- `python app.py` starts the dev server without errors.
- `instance/spelling.db` is created automatically with all three tables.
- No hardcoded secrets — everything comes from `.env`.
