# 🚀 Quick Start — Using These Prompts with GitHub Copilot

## Step-by-Step Instructions

### Before you begin
1. Open **VSCode** with the **GitHub Copilot** and **GitHub Copilot Chat** extensions installed.
2. Create an empty project folder: `mkdir spelling_master && cd spelling_master`
3. Open it in VSCode: `code .`
4. Open Copilot Chat: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)

---

## Running the Prompts in Order

| Step | File to Open | What Gets Generated | Est. Time |
|---|---|---|---|
| 1 | `00_PROJECT_OVERVIEW.md` | Read this first — no Copilot action | 2 min |
| 2 | `01_SETUP_AND_MODELS.md` | `app.py`, `models.py`, `requirements.txt` | 5 min |
| 3 | `02_BACKEND_ROUTES.md` | `routes/admin.py`, `routes/quiz.py` | 8 min |
| 4 | `03_BASE_TEMPLATES.md` | `base.html`, `home.html`, `style.css` | 6 min |
| 5 | `04_ADMIN_UI.md` | `manage_lists.html`, `edit_list.html` | 5 min |
| 6 | `05_QUIZ_UI.md` | `quiz.html` | 5 min |
| 7 | `06_SPEECH_AND_CANVAS.md` | `speech.js`, `canvas.js`, `quiz.js` | 8 min |
| 8 | `07_RESULTS_AND_FEEDBACK.md` | `results.html` | 5 min |
| 9 | `08_POLISH_AND_TESTING.md` | `seed_data.py`, `README.md`, error pages | 5 min |

**Total estimated time: ~50 minutes**

---

## How to Use Each Prompt File

1. Open the `.md` file in this folder.
2. Select all text (`Ctrl+A`).
3. Copy (`Ctrl+C`).
4. Click into the **Copilot Chat** panel.
5. Paste (`Ctrl+V`) and press **Enter**.
6. Review the generated code carefully.
7. Use **"Insert into New File"** or **"Apply to Workspace"** for each generated file.
8. After each prompt, **run the app** (`python app.py`) to check for errors before proceeding.

---

## Tips for Getting Better Results

- **Be in context:** Before pasting a prompt, open the relevant existing file in the editor. Copilot will use it as context.
- **Accept incrementally:** Accept one function or class at a time — don't accept everything at once.
- **Iterate:** If a generated file isn't quite right, ask Copilot in chat: *"The `/quiz/check` route doesn't handle empty input — please add validation."*
- **Use inline Copilot too:** Inside a `.py` or `.js` file, press `Ctrl+Enter` to see Copilot completions after typing a function signature.
- **Reference files:** In Copilot Chat, type `#` to reference a specific file, e.g. `#models.py — add a method to WordList that returns words in random order`.

---

## First Test After Setup

After completing prompts 1–2, run:
```bash
pip install -r requirements.txt
python app.py
```
You should see:
```
 * Running on http://127.0.0.1:5000
```
Visit `http://localhost:5000` — you should see the home page (possibly empty, no word lists yet).

After prompt 8, run:
```bash
python seed_data.py
```
Refresh the home page — you should see 3 word list cards ready to quiz!

---

## Common Issues & Fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` |
| `No such table: word_list` | Make sure `db.create_all()` is in `app.py`; delete `spelling.db` and restart |
| Speech doesn't work | Use Chrome or Edge; check browser permissions for audio |
| Canvas doesn't draw on tablet | Ensure `touch-action: none` is on the `<canvas>` element |
| Copilot generates wrong file structure | Paste `00_PROJECT_OVERVIEW.md` first to set context, then re-run the failing prompt |

---

## Final Project Checklist

Before considering the app complete, verify:
- [ ] All 8 prompts have been run and files created
- [ ] `python seed_data.py` runs without errors
- [ ] A full quiz can be completed start-to-finish in keyboard mode
- [ ] A full quiz can be completed in canvas mode
- [ ] Results page shows correctly with stars and missed words
- [ ] A teacher can add a new word list through the admin interface
- [ ] The app works with the browser offline (after first load)
