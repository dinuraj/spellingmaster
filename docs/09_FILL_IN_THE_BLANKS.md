# Prompt 09 — Fill-in-the-Blank Quiz

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 08.

---

## Your Task

Add a new quiz type — **Fill in the Blanks** — alongside the existing spelling quiz. This includes a data import mechanism, backend routes, paged quiz UI, results page, and navigation integration.

---

## Data Source

Two JSON files contain the question bank:

- `data/fill_questions_june_july_aug_sept.json` (158 words)
- `data/fill_questions_oct_nov_dec_jan_feb.json` (200 words)

### JSON structure (both files):
```json
{
  "items": [
    {
      "word": "estimate",
      "suitable": true,
      "questions": [
        { "question": "We can easily _____ the math answer by rounding first.", "answer": "estimate" },
        { "question": "To make a quick guess without counting is to _____.", "answer": "estimate" },
        { "question": "The teacher asked us to _____ how many jellybeans were in the jar.", "answer": "estimate" }
      ]
    }
  ]
}
```

Each word has **3 question variants**. When building a quiz, pick **one question per word at random** so the student sees a different sentence each time they retake the quiz.

---

## Database — Existing Models (no changes needed)

The following models already exist in `models.py`:

### `FillQuestion`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `word` | String(100) | Indexed |
| `question` | String(1000) | Sentence with `_____` blank |
| `answer` | String(100) | The target word |
| `month` | String(20) | Optional metadata |
| `subject` | String(50) | Optional metadata |
| `source_file` | String(200) | Original filename |

### `FillQuizAttempt`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `created_at` | DateTime | Auto-set |
| `completed_at` | DateTime | Set on finish |
| `total_questions` | Integer | |
| `correct_count` | Integer | |
| `question_ids` | Text | JSON list of `FillQuestion.id` in quiz order |
| `results` | Text | JSON list of per-question results |

---

## 1. Data Import — Admin UI Button

### Route: `POST /admin/import-fill-questions`
Already exists in `routes/fillgen.py`. Modify it to:
- **Remove the debug-mode guard** so it works from the admin panel.
- Import all rows from both JSON files into the `FillQuestion` table.
- Skip duplicates (match on `word` + `question` text).
- Flash a success message: "✅ Imported {count} fill questions ({skipped} duplicates skipped)."
- Redirect back to `/admin/`.

### Admin UI
Add an "Import Fill Questions" card/button to `templates/admin/manage_lists.html`:
```
┌──────────────────────────────────────┐
│  📝 Fill-in-the-Blank Questions       │
│                                      │
│  {count} questions in database        │
│                                      │
│  [Import from JSON Files]            │
│  [Manage Questions →]                │
└──────────────────────────────────────┘
```
- The Import button is a POST form (with CSRF token) to `/admin/import-fill-questions`.
- "Manage Questions" links to the existing `/admin/fillquestions` page.

---

## 2. Fill Quiz Routes — `routes/fillquiz.py`

### `GET /fillquiz/` — Quiz launcher page
Render `templates/fillquiz/index.html`.

Template variables:
| Variable | Type | Description |
|---|---|---|
| `total_words` | int | Count of distinct words in `FillQuestion` |
| `total_questions` | int | Total rows in `FillQuestion` |
| `recent_attempts` | list | Last 5 `FillQuizAttempt` rows |

### `POST /fillquiz/start` — Start a quiz
Accept form field `size` (values: `15`, `30`, `50`, `all`).

Logic:
1. Query all distinct words from `FillQuestion`.
2. If `size == 'all'`, use all words; otherwise cap at the requested number.
3. Shuffle the word list.
4. For each word, pick one random `FillQuestion` row.
5. Create a `FillQuizAttempt` record with `question_ids` = JSON list of selected question IDs.
6. Store `attempt_id` in session.
7. Redirect to `/fillquiz/play?page=1`.

### `GET /fillquiz/play?page=N` — Render one page of 5 questions
Guard: if no `attempt_id` in session, flash warning and redirect to `/fillquiz/`.

Template variables:
| Variable | Type | Description |
|---|---|---|
| `attempt_id` | int | |
| `page` | int | Current page (1-based) |
| `total_pages` | int | `ceil(total_questions / 5)` |
| `questions` | list[dict] | 5 items: `{id, number, question}` |
| `answers` | dict | Previously submitted answers for this attempt (from session) |
| `progress_pct` | int | `(page / total_pages) * 100` |

### `POST /fillquiz/play` — Submit a page of answers and advance
Accept form fields: `answer_{question_id}` for each question on the page.
1. Save answers into `session['fill_answers']` dict (key = question_id, value = answer string).
2. Determine direction from submit button (`next`, `prev`, or `finish`).
3. If `next` → redirect to `/fillquiz/play?page=N+1`.
4. If `prev` → redirect to `/fillquiz/play?page=N-1`.
5. If `finish` → redirect to `/fillquiz/finish`.

### `POST /fillquiz/finish` — Score and save results
1. Read `session['fill_answers']`.
2. For each question in the attempt, compare answer (case-insensitive, stripped).
3. Build results JSON: `[{question_id, word, question, answer, submitted, correct}]`.
4. Update `FillQuizAttempt`: set `completed_at`, `correct_count`, `results`.
5. Clear session quiz data.
6. Redirect to `/fillquiz/results?attempt_id=X`.

### `GET /fillquiz/results?attempt_id=X` — Results page
Template variables:
| Variable | Type | Description |
|---|---|---|
| `attempt` | FillQuizAttempt | The attempt record |
| `results` | list[dict] | Per-question result objects |
| `correct_count` | int | |
| `total` | int | |
| `score_percent` | float | |
| `stars` | int | 3 if ≥90%, 2 if ≥70%, else 1 |
| `message` | str | Personalised feedback |

---

## 3. Templates

### `templates/fillquiz/index.html`
Extends `base.html`. Title: "Fill in the Blanks 📝".

```
┌──────────────────────────────────────────────┐
│  Fill in the Blanks 📝                        │
│                                              │
│  {total_words} words available               │
│                                              │
│  How many questions?                         │
│  [ 15 ▼ | 30 | 50 | All ]                   │
│                                              │
│          [🚀 Start Quiz]                     │
│                                              │
│  ── Recent Attempts ──                       │
│  | Date | Score | ... |                      │
└──────────────────────────────────────────────┘
```

- Size selector: radio buttons or button group (15 / 30 / 50 / All).
- Start Quiz: POST form to `/fillquiz/start` with hidden `size` field.
- Recent attempts table: date, score fraction, percentage — link to results page.
- If no questions in DB: show friendly message "No fill questions imported yet" with link to admin.

### `templates/fillquiz/play.html`
Extends `base.html`. Title: "Fill Quiz — Page {{ page }} of {{ total_pages }}".

```
┌──────────────────────────────────────────────┐
│  Progress: [████████░░░░] Page 2 of 8        │
├──────────────────────────────────────────────┤
│                                              │
│  6. We can easily _____ the math answer      │
│     by rounding first.                       │
│     [ answer input          ]                │
│                                              │
│  7. The middle part of an insect's body,     │
│     where the legs are attached, is the ____ │
│     [ answer input          ]                │
│                                              │
│  ... (5 questions per page)                  │
│                                              │
│  [← Previous]              [Next →]          │
│                    — or —                    │
│              [✅ Finish Quiz]                 │
│         (only on last page)                  │
└──────────────────────────────────────────────┘
```

- Each question is a styled card with the sentence and a text input.
- Question number is global (not per-page): `(page-1)*5 + index + 1`.
- Inputs pre-filled with any previously saved answers from session.
- Disable autocorrect and spellcheck on inputs: `autocomplete="off" autocorrect="off" spellcheck="false"`.
- Previous button hidden on page 1.
- Finish button shown only on last page; Next shown on all other pages.
- All navigation via form POST (answers submitted with each page change).

### `templates/fillquiz/results.html`
Extends `base.html`. Title: "Fill Quiz Results 🏆".

Reuse the same visual pattern as the spelling quiz results page:

#### Score card (centered)
```
┌──────────────────────────────┐
│  ⭐⭐⭐   (or fewer stars)    │
│     28 / 30                  │
│   93% Correct                │
│  "Fantastic work!"           │
└──────────────────────────────┘
```
- Stars: ⭐ for filled, ☆ for empty (3rem font size).
- Score fraction in 4rem font.
- Message in coloured bubble (gold/green/blue per star count).
- Confetti animation if `stars == 3` (reuse CSS from spelling quiz results).

#### Review section
Two side-by-side columns:

**✅ Correct answers** — green list of words.

**❌ Words to practice** — red list, each showing:
- The word in bold
- The sentence (question)
- What the student typed
- The correct answer
- 🔊 "Hear it" button using `speakSingleWord()` from `speech.js`

#### Action buttons
- **Try Again** — POST form to `/fillquiz/start` with same size
- **Choose Different Size** — link to `/fillquiz/`
- **Practice Missed Words** (only if wrong answers exist) — POST to `/fillquiz/start` with `missed_only=true`

---

## 4. JavaScript — `static/js/fillquiz.js`

Keep JavaScript minimal (server-rendered form flow). Only add:

```javascript
/**
 * Auto-focus the first empty input on page load.
 */
document.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('.fill-answer-input');
  for (const inp of inputs) {
    if (!inp.value.trim()) { inp.focus(); break; }
  }
});
```

- Add green border class on filled inputs (CSS: `.fill-answer-input:not(:placeholder-shown)`).
- Confetti on results page (reuse existing confetti CSS from spelling quiz).

---

## 5. Navigation Integration

### `templates/base.html`
Add a nav link:
```html
<a href="/fillquiz/">Fill Quiz</a>
```

### `templates/home.html`
Add a new section below the word list cards:
```html
<section class="fill-quiz-section">
  <div class="card">
    <h2>📝 Fill in the Blanks</h2>
    <p class="muted">Practice spelling by filling in missing words in sentences.</p>
    <p class="badge">{{ fill_word_count }} words available</p>
    <a href="/fillquiz/" class="btn btn-primary">Start Fill Quiz</a>
  </div>
</section>
```
Update the `quiz_bp.index` route to also pass `fill_word_count` to the template.

---

## 6. CSS — Add to `static/css/style.css`

```css
/* Fill quiz — question cards */
.fill-question-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.fill-question-card .question-number {
  font-weight: 800;
  color: var(--blue);
  margin-right: 8px;
}
.fill-question-card .question-text {
  font-size: 1.15rem;
  line-height: 1.6;
  margin-bottom: 12px;
}
.fill-answer-input {
  font-family: 'Nunito', sans-serif;
  font-size: 1.3rem;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  width: 100%;
  max-width: 320px;
  transition: border-color 0.2s;
}
.fill-answer-input:focus {
  border-color: var(--blue);
  outline: none;
  box-shadow: 0 0 0 3px rgba(33,150,243,0.15);
}
.fill-answer-input:not(:placeholder-shown) {
  border-color: var(--green);
}

/* Fill quiz — size selector */
.size-selector { display: flex; gap: 12px; margin: 16px 0; flex-wrap: wrap; }
.size-selector label {
  padding: 10px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.2s;
}
.size-selector input[type="radio"] { display: none; }
.size-selector input[type="radio"]:checked + span {
  background: var(--blue);
  color: white;
  border-color: var(--blue);
}

/* Fill quiz — pager */
.fill-pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  gap: 12px;
}
```

---

## Acceptance Criteria

- [ ] Admin can import fill questions from JSON via a single button click; duplicates are skipped.
- [ ] Fill quiz launcher shows word count and size options (15 / 30 / 50 / All).
- [ ] Starting a quiz picks one random question per word.
- [ ] Quiz pages display 5 questions each with progress bar and page navigation.
- [ ] Answers are preserved when navigating between pages (Previous / Next).
- [ ] Finishing the quiz scores answers case-insensitively and saves a `FillQuizAttempt`.
- [ ] Results page shows score card with stars, personalised message, and correct/wrong review.
- [ ] "Practice Missed Words" only quizzes on words the student got wrong.
- [ ] Fill quiz is accessible from the home page and nav bar.
- [ ] All pages match the kid-friendly theme (Nunito, rounded cards, gold/green/blue palette).
- [ ] CSRF tokens are included on all POST forms. 

