# Prompt 02 — Backend Routes (Admin CRUD + Quiz Logic)

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 01 is complete and files are in your workspace.

---

## Your Task

Generate two Flask Blueprint files inside the `routes/` folder.

---

## `routes/admin.py` — Word List Management

Register as blueprint `admin_bp` with url_prefix `/admin`.

### Routes to implement:

| Method | URL | Description |
|---|---|---|
| GET | `/admin/` | List all `WordList` rows; render `admin/manage_lists.html` |
| GET/POST | `/admin/list/new` | Create a new `WordList`; redirect to manage page on success |
| GET/POST | `/admin/list/<int:list_id>/edit` | Edit list name/description; also show its words |
| POST | `/admin/list/<int:list_id>/delete` | Delete list (cascade deletes words); redirect to manage page |
| POST | `/admin/list/<int:list_id>/word/add` | Add a single `Word` to a list (JSON body: `{word, hint}`) |
| POST | `/admin/word/<int:word_id>/delete` | Delete a single word; return JSON `{success: true}` |
| POST | `/admin/list/<int:list_id>/bulk` | Accept a textarea of words (one per line, optional hint after `|`) and bulk-insert them |

**Bulk import format example:**
```
beautiful|She wore a beautiful dress.
because
friend|He is my best friend.
```

### Validation rules (raise `flash` error if violated):
- Word list name must be 2–100 characters.
- Each word must be 1–50 alphabetic characters (strip extra whitespace).
- Hint is optional; max 200 characters.
- Duplicate words within the same list should be silently skipped (no crash).

---

## `routes/quiz.py` — Quiz Session Logic

Register as blueprint `quiz_bp` with url_prefix `/quiz`.

Use Flask `session` to track quiz state:
```python
session["quiz"] = {
    "list_id": int,
    "words": [str, ...],      # shuffled list of words
    "current_index": int,     # 0-based pointer
    "correct": [str, ...],    # words answered correctly
    "wrong": [str, ...]       # words answered incorrectly
}
```

### Routes to implement:

| Method | URL | Description |
|---|---|---|
| GET | `/quiz/` | Show word-list selector (render `home.html`) |
| POST | `/quiz/start` | Body: `{list_id}`. Load words, shuffle, store in session, redirect to `/quiz/play` |
| GET | `/quiz/play` | Render `quiz/quiz.html`; pass current word index, total count, current word |
| POST | `/quiz/check` | Body: `{answer}`. Compare answer (strip + lowercase) to current word. Increment index. Return JSON: `{correct: bool, correct_word: str, next_available: bool}` |
| GET | `/quiz/results` | Render `quiz/results.html` with final stats; save a `QuizResult` row to DB |
| POST | `/quiz/reset` | Clear `session["quiz"]`; redirect to `/quiz/` |

### `/quiz/check` logic (detailed):
```
1. Get answer from request JSON (strip whitespace, lowercase).
2. Get current word from session (lowercase for comparison).
3. If answer == word → append to session["quiz"]["correct"].
4. Else → append to session["quiz"]["wrong"].
5. Increment session["quiz"]["current_index"].
6. If current_index >= len(words) → set next_available = False.
7. Return JSON response.
```

### `/quiz/results` logic:
- Calculate `score_percent`.
- Determine star rating: ≥90% = 3 stars, ≥70% = 2 stars, else 1 star.
- Determine feedback message (see table below).
- Save `QuizResult` to DB.
- Pass all data to template.

| Score | Message |
|---|---|
| 100% | "Amazing! You're a Spelling Superstar! 🌟" |
| 90–99% | "Fantastic work! Almost perfect!" |
| 70–89% | "Great job! Keep practicing those tricky words." |
| 50–69% | "Good effort! Review the words you missed and try again." |
| < 50% | "Keep going! Practice makes perfect. You've got this! 💪" |

---

## Acceptance Criteria
- All routes return the correct HTTP status codes (200, 302, 400 as appropriate).
- No route crashes if the session is empty — redirect to `/quiz/` gracefully.
- All DB writes are inside `try/except db.session.rollback()` blocks.
- Every function has a Python docstring.
