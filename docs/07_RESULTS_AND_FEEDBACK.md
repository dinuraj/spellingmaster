# Prompt 07 — Results Page & End-of-Quiz Feedback

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 06.

---

## Your Task

Generate `templates/quiz/results.html` — the celebratory end-of-quiz screen shown to the student.

---

## `templates/quiz/results.html`

Extends `base.html`. Title: "Quiz Results 🏆".

### Template variables (passed from route):
| Variable | Type | Description |
|---|---|---|
| `correct_count` | int | Number of words spelled correctly |
| `total_words` | int | Total words in the quiz |
| `score_percent` | float | `(correct_count / total_words) * 100` |
| `stars` | int | 1, 2, or 3 |
| `message` | str | Personalised feedback message |
| `wrong_words` | list[str] | Words the student got wrong |
| `correct_words` | list[str] | Words the student got right |
| `list_name` | str | Name of the word list that was tested |

---

## Page Layout

### 1. Confetti animation (CSS only)
At the top of the `{% block content %}`, if `stars == 3`, add a `<div class="confetti-container">` with 20 `<span class="confetti-piece">` elements. Animate them with a CSS `@keyframes fall` animation using random `animation-delay` and `left` values via inline styles (generate these in the Jinja2 template with a loop and `loop.index`).

```css
@keyframes fall {
  0%   { transform: translateY(-10px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
}
.confetti-piece {
  position: fixed; top: -20px;
  width: 10px; height: 10px; border-radius: 2px;
  animation: fall 3s ease-in forwards;
}
/* Assign alternating colors using nth-child */
```

### 2. Score card (centered, large)
```
┌──────────────────────────────┐
│  ⭐⭐⭐   (or fewer stars)    │
│                              │
│     8 / 10                   │
│   80% Correct                │
│                              │
│  "Great job! Keep practicing │
│   those tricky words."       │
└──────────────────────────────┘
```

Star display: loop `{% for i in range(3) %}` — filled star ⭐ if `i < stars`, else empty star ☆. Make stars large (font-size 3rem).

Score fraction: display as `{{ correct_count }} / {{ total_words }}` in a very large font (4rem).

Percentage: display below, smaller.

Message: display in a coloured bubble matching the star count (gold for 3 stars, green for 2, blue for 1).

### 3. Review section
Split into two side-by-side columns on desktop, stacked on mobile:

**Left — ✅ Words You Got Right:**
- Green checkmark list of `correct_words`.
- If empty: "None this time — keep going!"

**Right — ❌ Words to Practice:**
- Red X list of `wrong_words`.
- For each missed word: show the word in bold and a button "🔊 Hear it" that calls `speakSingleWord('{{ word }}')` (a function in `speech.js`).
- If empty: "🎯 Perfect score — no words to review!"

### 4. Action buttons
Three buttons in a row:
- **Try Again** — POST form to `/quiz/start` with hidden `list_id` (re-shuffles the same list)
- **Choose Different List** — link to `/`
- **Practice Missed Words** (only show if `wrong_words` is not empty) — POST form to `/quiz/start` with a hidden input `missed_only=true` and `list_id`; the route should detect this and only quiz on missed words

> Note: the "Practice Missed Words" feature requires a small addition to `routes/quiz.py`: if `missed_only=true` and session contains `wrong_words`, load only those words.

### 5. History / Previous attempts (optional stretch)
A collapsed `<details>` element: "📊 View Past Attempts" — inside, a table of the last 5 `QuizResult` rows for this list (queried in the route).

---

## CSS to add to `style.css`:

```css
/* Results page */
.score-card {
  text-align: center;
  padding: 40px;
  border-radius: 24px;
  background: linear-gradient(135deg, #fff9c4, #ffffff);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  margin: 32px auto;
  max-width: 480px;
}
.score-fraction { font-size: 4rem; font-weight: 800; color: var(--text); line-height: 1; }
.score-stars    { font-size: 3rem; letter-spacing: 8px; margin: 16px 0; }
.score-message  { font-size: 1.2rem; font-weight: 700; padding: 12px 20px; border-radius: 50px; display: inline-block; }
.message-gold   { background: var(--gold); color: #333; }
.message-green  { background: var(--green); color: white; }
.message-blue   { background: var(--blue); color: white; }

/* Review columns */
.review-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 32px 0;
}
@media (max-width: 600px) { .review-grid { grid-template-columns: 1fr; } }

.review-col { background: var(--card-bg); border-radius: var(--radius); padding: 20px; }
.review-col h3 { margin-top: 0; }
.word-item { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f0f0f0; }
```

---

## Add `speakSingleWord(word)` to `speech.js`
```javascript
/**
 * Speaks a single arbitrary word (used on results page).
 * @param {string} word - The word to speak aloud.
 */
function speakSingleWord(word) {
  const utter = new SpeechSynthesisUtterance(word);
  utter.rate = 0.85;
  utter.pitch = 1.1;
  speechSynthesis.cancel();
  speechSynthesis.speak(utter);
}
```

---

## Acceptance Criteria
- Confetti shows only on a perfect or 3-star score.
- Stars render correctly for all score ranges.
- Missed words are listed with a working "Hear it" button.
- "Practice Missed Words" button only appears when there are missed words.
- Results are saved to the `QuizResult` table in the database.
