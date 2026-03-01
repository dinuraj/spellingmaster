# Prompt 06 — Speech Synthesis & Handwriting Canvas (JavaScript)

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 05.

---

## Your Task

Generate two JavaScript files: `static/js/speech.js` and `static/js/canvas.js`.

---

## `static/js/speech.js`

Implements text-to-speech using the **Web Speech API** (`SpeechSynthesis`), which is built into all modern browsers and works **completely offline**.

### Requirements:

```javascript
/**
 * speech.js — Web Speech API wrapper for Spelling Master
 * Uses browser-native SpeechSynthesis (no internet required).
 */
```

#### `initSpeech()`
- Called once on page load.
- Check if `window.speechSynthesis` exists; if not, show a visible warning banner: "⚠️ Your browser doesn't support text-to-speech. Please use Chrome or Edge."
- Pre-load available voices with `speechSynthesis.getVoices()`.
- On some browsers, voices load asynchronously — attach `speechSynthesis.onvoiceschanged` to capture them.

#### `speakWord()`
- Read the word from `document.getElementById('current-word').dataset.word`.
- Create a `SpeechSynthesisUtterance`.
- **Voice selection:** prefer a voice with `lang === 'en-US'`; fall back to any English voice, then any voice.
- Set `rate: 0.85` (slightly slower for children), `pitch: 1.1` (slightly higher, friendlier), `volume: 1`.
- Call `speechSynthesis.cancel()` first to stop any running speech.
- Speak the word **twice** with a 1.5-second pause between repetitions (use `setTimeout`).
- After first call: hide `#btn-speak`, show `#btn-repeat`.

#### `speakFeedback(isCorrect)`
- If `isCorrect`: speak "Correct! Well done!"
- If not: speak "Not quite. The correct spelling is ..." then spell out the word letter by letter with pauses.

#### `spellOutWord(word)`
- Helper: speak each letter individually with 400 ms gaps.
- Example: "b... e... a... u... t... i... f... u... l"

---

## `static/js/canvas.js`

Implements the offline handwriting canvas using **HTML5 Canvas** and mouse/touch events. The student draws their answer; the teacher/parent confirms it visually.

> Note: Full OCR (automatic reading of handwriting) is complex. For now, implement a **manual confirmation flow**: the student draws, presses "Submit Writing", and the app reveals the correct spelling so a parent/teacher can look and confirm, then manually marks it correct or incorrect.

### Requirements:

```javascript
/**
 * canvas.js — Offline handwriting canvas for Spelling Master
 * Supports mouse and touch input for tablets/styluses.
 */
```

#### State variables
```javascript
let isDrawing = false;
let lastX = 0;
let lastY = 0;
const STROKE_COLOR = '#1a1a2e';
const STROKE_WIDTH = 4;
```

#### `initCanvas()`
- Get the `<canvas id="handwriting-canvas">` element.
- Set up event listeners for:
  - Mouse: `mousedown`, `mousemove`, `mouseup`, `mouseleave`
  - Touch: `touchstart`, `touchmove`, `touchend`
- Set `canvas.style.cursor = 'crosshair'`.
- Draw a faint baseline guide: a dashed horizontal line at 75% of canvas height.

#### `startDrawing(e)`
- Set `isDrawing = true`.
- Get coordinates (handle both mouse and touch events).
- `ctx.beginPath(); ctx.moveTo(x, y)`.

#### `draw(e)`
- If not drawing, return.
- Get coordinates; `ctx.lineTo(x, y); ctx.stroke()`.
- Set `ctx.strokeStyle`, `ctx.lineWidth`, `ctx.lineCap = 'round'`, `ctx.lineJoin = 'round'`.

#### `stopDrawing()`
- Set `isDrawing = false`.

#### `clearCanvas()`
- `ctx.clearRect(...)` the full canvas.
- Redraw the baseline guide.

#### `toggleCanvas()`
- Toggle visibility of `#canvas-section` and `#type-section`.
- If showing canvas: call `initCanvas()` if not already initialised.
- Update button text of `#btn-canvas` to "⌨️ Type Instead" / "✏️ Write Instead".

#### `submitCanvas()`
- Hide the canvas section.
- Show the `#feedback` zone with these contents:
  - `#feedback-icon` = "✍️"
  - `#feedback-msg` = "Show your writing to a grown-up to check!"
  - Reveal a "Mark Correct ✅" and "Mark Wrong ❌" button pair.
- Clicking **Mark Correct** → calls `recordResult(true)` (defined in `quiz.js`).
- Clicking **Mark Wrong** → calls `recordResult(false)`.

#### Helper: `getCoords(e)`
- Returns `{x, y}` from either a mouse event or a touch event (use `e.touches[0]`).
- Subtract canvas bounding rect to get relative coords.

---

## `static/js/quiz.js`

A short coordinator script that ties speech and canvas together with the quiz flow.

### Functions:

#### `submitAnswer()`
```javascript
async function submitAnswer() {
  const answer = document.getElementById('answer-input').value.trim();
  if (!answer) { /* shake the input and return */ }

  const response = await fetch('/quiz/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ answer })
  });
  const data = await response.json();
  showFeedback(data.correct, data.correct_word, data.next_available);
}
```

#### `showFeedback(isCorrect, correctWord, hasNext)`
- Disable the answer input and submit button.
- If correct: show ✅ icon, green "Correct! 🎉", call `speakFeedback(true)`.
- If wrong: show ❌ icon, red "Not quite!", reveal correct word in `#correct-word-reveal`, call `speakFeedback(false)`.
- Apply `.animate-bounce` or `.animate-shake` CSS class to `#feedback`.
- Show `#btn-next` if `hasNext`, otherwise change it to "See My Results 🏆" and set `onclick="goToResults()"`.

#### `recordResult(isCorrect)`
- Called from canvas manual marking.
- POST to `/quiz/check` with `{answer: isCorrect ? correctWord : ''}`.
- Then call `showFeedback(...)`.

#### `nextWord()`
- Reload the page to get the next word: `window.location.reload()`.

#### `goToResults()`
- `window.location.href = '/quiz/results'`.

#### Page init
```javascript
document.addEventListener('DOMContentLoaded', () => {
  initSpeech();
  // Auto-speak the word after a 1-second delay
  setTimeout(speakWord, 1000);
  // Enter key submits
  document.getElementById('answer-input')
    .addEventListener('keypress', e => { if (e.key === 'Enter') submitAnswer(); });
});
```

---

## Acceptance Criteria
- Speech works in Chrome, Edge, and Firefox (desktop + mobile).
- Canvas draws smoothly with a mouse and with a finger/stylus on a touchscreen.
- After canvas submission, parent/teacher can mark correct/incorrect.
- No external JS libraries — only vanilla JavaScript.
- All functions have JSDoc comments.
