# Prompt 08 — Polish, Seed Data & Testing Checklist

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **last**, after all other prompts are complete.

---

## Your Task

Generate three things: a seed data script, an error handling layer, and a manual testing checklist document.

---

## 1. `seed_data.py` — Sample Word Lists

A standalone script that populates the database with sample data for testing.  
Run with: `python seed_data.py`

### Script requirements:
- Import `app` and `db` from `app.py`, use `app.app_context()`.
- Check if data already exists before inserting (idempotent — safe to run multiple times).
- Create **3 word lists**:

#### List 1: "Grade 3 — Common Words" (15 words)
```
because, friend, beautiful, different, really, school, through, thought, people, always,
every, together, sometimes, something, would
```
Add a simple hint sentence for each word.

#### List 2: "Grade 3 — Animals & Nature" (10 words)
```
butterfly, ocean, forest, creature, habitat, migrate, season, weather, mountain, valley
```

#### List 3: "Sight Words — Set A" (8 words)
```
again, carry, early, enough, group, often, until, usually
```

Print a success message when done: "✅ Seed data loaded successfully!"

---

## 2. Error Handling & Edge Cases

Add the following improvements to the existing code:

### `app.py` additions:
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
```

### `templates/errors/404.html`
- Friendly message: "Oops! We couldn't find that page 🔍"
- Big cartoon magnifying glass emoji.
- "Go Home" button.

### `templates/errors/500.html`
- Friendly message: "Something went wrong on our end 🛠️"
- "Go Home" button.
- Do NOT show technical error details.

### `routes/quiz.py` guards:
Add these guards to every quiz route:
```python
if 'quiz' not in session or not session['quiz'].get('words'):
    flash('Please select a word list to start a quiz.', 'warning')
    return redirect(url_for('quiz_bp.index'))
```

### `routes/admin.py` — input sanitisation:
- Strip all word inputs: `word.strip().lower()`
- Reject words containing non-alphabetic characters (allow only `a-z` and hyphens for hyphenated words).

---

## 3. `README.md` — Setup & Run Instructions

Generate a clean README with these sections:

### Sections:
```markdown
# Spelling Master 🎓

A spelling practice web app for 3rd-grade students.

## Features
## Requirements
## Installation
## Running the App
## Loading Sample Data
## Adding Your Own Word Lists
## How the Quiz Works
## Offline Mode (Canvas)
## Browser Compatibility
## Project Structure
```

**Installation steps:**
```bash
git clone <repo>
cd spelling_master
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```
Open browser to `http://localhost:5000`

**Browser compatibility table:**
| Browser | Speech (TTS) | Canvas | Recommended |
|---|---|---|---|
| Chrome (desktop) | ✅ | ✅ | ⭐ Best |
| Edge | ✅ | ✅ | ⭐ Best |
| Firefox | ✅ | ✅ | ✅ Good |
| Safari | ✅ | ✅ | ✅ Good |
| Chrome (Android) | ✅ | ✅ | ✅ Good |
| Samsung Internet | ✅ | ✅ | ✅ Good |

---

## 4. `TESTING_CHECKLIST.md` — Manual Test Checklist

Generate a markdown checklist for manually verifying the app works.

```markdown
# Manual Testing Checklist

## Setup
- [ ] App starts without errors (`python app.py`)
- [ ] Database is created at `instance/spelling.db`
- [ ] Seed data loads (`python seed_data.py`)
- [ ] Home page shows 3 word list cards

## Admin — Word List Management
- [ ] Can create a new word list
- [ ] Can edit word list name and description
- [ ] Can add a single word with hint
- [ ] Can bulk import words using the textarea
- [ ] Can delete a word (without page reload)
- [ ] Can delete an entire list
- [ ] Deleting a list also deletes its words
- [ ] Duplicate words in bulk import are silently skipped

## Quiz — Keyboard Mode
- [ ] Selecting a word list starts the quiz
- [ ] Word is spoken aloud automatically after 1 second
- [ ] "Hear Again" button replays the word
- [ ] Correct answer shows green feedback and ✅
- [ ] Wrong answer shows red feedback and the correct spelling
- [ ] Progress bar advances correctly
- [ ] "Next Word" button loads the next word
- [ ] Final word shows "See My Results" button
- [ ] Enter key submits the answer

## Quiz — Canvas Mode
- [ ] Toggle to canvas mode hides the text input
- [ ] Can draw with mouse
- [ ] Can draw with touch/stylus (on tablet)
- [ ] Clear button wipes the canvas
- [ ] Submit Writing shows the correct word for comparison
- [ ] Mark Correct / Mark Wrong buttons work correctly

## Results Page
- [ ] Score fraction displays correctly (e.g. 8/10)
- [ ] Stars display correctly (3/2/1 based on score)
- [ ] Personalised message matches the score range
- [ ] Correct words list is accurate
- [ ] Missed words list is accurate
- [ ] "Hear it" button speaks missed words
- [ ] Quiz result is saved to database
- [ ] "Try Again" starts a new quiz with the same list
- [ ] "Practice Missed Words" only quizzes on wrong words
- [ ] Confetti shows on perfect score

## Edge Cases
- [ ] Visiting `/quiz/play` with no active session redirects to home
- [ ] Empty word list shows a friendly message and no "Start Quiz" button
- [ ] 404 page shows a friendly error
- [ ] App works offline (no internet) after initial page load
```

---

## Acceptance Criteria
- `python seed_data.py` runs without errors and creates 3 word lists.
- 404 and 500 error pages render without crashing.
- README contains accurate, copy-pasteable setup instructions.
- Testing checklist covers all major user flows.
