# Prompt 05 — Quiz Screen UI

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 04.

---

## Your Task

Generate `templates/quiz/quiz.html` — the main quiz screen students interact with.

---

## `templates/quiz/quiz.html`

Extends `base.html`. Title: "Spelling Quiz 🎯". Add `{% block extra_head %}` to load `quiz.js`, `speech.js`, `canvas.js`.

### Layout (full-screen, centered, playful)

```
┌──────────────────────────────────────────┐
│  Progress Bar  [████████░░░░]  4 / 10    │
├──────────────────────────────────────────┤
│                                          │
│     Word 4 of 10                         │
│                                          │
│   [🔊 Hear the Word]  [🔊 Hear Again]    │
│                                          │
│   ┌────────────────────────────────┐    │
│   │  Type your answer here...      │    │
│   └────────────────────────────────┘    │
│                                          │
│         [✅  Check My Spelling]          │
│                                          │
│   ─── or ───                             │
│   [✏️  Write Instead]  (toggle canvas)  │
│                                          │
│   [feedback zone — hidden until checked] │
└──────────────────────────────────────────┘
```

### Template variables (passed from Flask route):
- `current_index` — 0-based int
- `total_words` — int
- `word` — the current word string (used ONLY in JavaScript data, never displayed in HTML — the student must not see it!)
- `hint` — optional hint sentence

> ⚠️ **Important:** The word must be stored in a JavaScript variable, **not** visible anywhere in the HTML. Pass it via a hidden `<span>` with `id="current-word"` and `data-word="{{ word }}"`, but ensure it is hidden with `display:none`.

### HTML sections to create:

#### 1. Progress bar
```html
<div class="progress-container">
  <div class="progress-bar" style="width: {{ progress_pct }}%"></div>
</div>
<p class="progress-label">Word {{ current_index + 1 }} of {{ total_words }}</p>
```
`progress_pct` = `(current_index / total_words) * 100` — compute this in the route.

#### 2. Audio controls
```html
<div class="audio-controls">
  <button class="btn btn-primary btn-lg" onclick="speakWord()" id="btn-speak">
    🔊 Hear the Word
  </button>
  <button class="btn btn-secondary" onclick="speakWord()" id="btn-repeat" style="display:none">
    🔊 Hear Again
  </button>
</div>
```
After the first `speakWord()` call, JS should hide the first button and show the repeat button.

#### 3. Hint (optional)
```html
{% if hint %}
<div class="hint-box">
  <span class="hint-label">Hint:</span> {{ hint }}
</div>
{% endif %}
```

#### 4. Answer input
```html
<div class="answer-section" id="type-section">
  <input type="text" id="answer-input" class="spelling-input"
         placeholder="Type your spelling here..."
         autocomplete="off" autocorrect="off" spellcheck="false"
         autofocus />
  <button class="btn btn-success btn-lg" onclick="submitAnswer()">
    ✅ Check My Spelling
  </button>
</div>
```
- Pressing **Enter** in the input should also trigger `submitAnswer()`.
- Disable autocorrect and spellcheck to avoid giving hints.

#### 5. Canvas toggle
```html
<div class="mode-toggle">
  <span>— or —</span>
  <button class="btn btn-secondary" onclick="toggleCanvas()" id="btn-canvas">
    ✏️ Write Instead
  </button>
</div>

<div class="canvas-section" id="canvas-section" style="display:none">
  <canvas id="handwriting-canvas" width="500" height="200"></canvas>
  <div class="canvas-controls">
    <button onclick="clearCanvas()">🗑️ Clear</button>
    <button onclick="submitCanvas()">✅ Submit Writing</button>
  </div>
  <p class="canvas-hint">Write the word on the canvas, then press Submit Writing.</p>
</div>
```

#### 6. Feedback zone
```html
<div class="feedback-zone" id="feedback" style="display:none">
  <div id="feedback-icon" class="feedback-icon"></div>
  <p id="feedback-msg" class="feedback-msg"></p>
  <p id="correct-word-reveal" class="correct-reveal" style="display:none"></p>
  <button class="btn btn-primary btn-lg" onclick="nextWord()" id="btn-next">
    Next Word →
  </button>
</div>
```

#### 7. Hidden data
```html
<span id="current-word" data-word="{{ word }}" style="display:none"></span>
<span id="quiz-data"
      data-total="{{ total_words }}"
      data-index="{{ current_index }}"
      style="display:none"></span>
```

---

## CSS classes to add to `style.css` for this page:

```css
/* Progress */
.progress-container { background: #eee; border-radius: 50px; height: 16px; margin: 20px 0; }
.progress-bar { background: var(--green); border-radius: 50px; height: 100%; transition: width 0.5s ease; }

/* Spelling input — large and inviting */
.spelling-input {
  font-family: 'Nunito', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  text-align: center;
  border: 3px solid var(--blue);
  border-radius: var(--radius);
  padding: 16px 24px;
  width: 100%;
  max-width: 480px;
  outline: none;
  transition: border-color 0.2s;
}
.spelling-input:focus { border-color: var(--gold); box-shadow: 0 0 0 4px rgba(255,215,0,0.3); }

/* Feedback */
.feedback-zone { text-align: center; margin-top: 24px; }
.feedback-icon { font-size: 4rem; }
.feedback-msg { font-size: 1.4rem; font-weight: 700; }
.correct-reveal { color: var(--coral); font-size: 1.2rem; }

/* Hint box */
.hint-box { background: #FFF9C4; border-left: 4px solid var(--gold); padding: 12px 16px; border-radius: 8px; font-style: italic; }

/* Canvas */
#handwriting-canvas { border: 3px dashed var(--blue); border-radius: var(--radius); background: white; touch-action: none; }
```

---

## Acceptance Criteria
- The word is **never** visible as plain text in the rendered HTML — only in a `data-*` attribute.
- Enter key submits the answer.
- Feedback zone animates in (use `.animate-bounce` or `.animate-shake` from `style.css`).
- Canvas section toggles smoothly.
- All buttons are large enough for a child's fingers (min 48 px tall).
