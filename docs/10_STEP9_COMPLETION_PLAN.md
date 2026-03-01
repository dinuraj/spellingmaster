# Step 9 Completion Plan — Prompt 08 (Polish, Seed Data & Testing)

Date: 2026-03-01

This plan completes **Step 9** from [QUICK_START.md](./QUICK_START.md):
- Source prompt: [08_POLISH_AND_TESTING.md](./08_POLISH_AND_TESTING.md)
- Goal artifacts: `seed_data.py`, `README.md`, error handling pages/logic, and `TESTING_CHECKLIST.md`

---

## 1) Step 9 Scope (Required)

From `08_POLISH_AND_TESTING.md`, Step 9 requires:

1. **Seed script** (`seed_data.py`) with 3 predefined lists and idempotent behavior.
2. **Error handling layer**:
   - 404 and 500 handlers in `app.py`
   - Friendly templates in `templates/errors/404.html` and `templates/errors/500.html`
3. **Quiz route guards** in `routes/quiz.py`:
   - Redirect to quiz index with flash when session quiz is missing
4. **Admin input sanitization** in `routes/admin.py`:
   - `word.strip().lower()`
   - Reject non alphabet/hyphen words
5. **README cleanup** (`README.md`) with required sections and accurate setup/run instructions.
6. **Manual testing checklist** (`TESTING_CHECKLIST.md`) covering setup, admin, quiz, results, edge cases.

---

## 2) Current Status vs Step 9

### Already implemented
- `seed_data.py` exists, creates required 3 lists, and is idempotent by checking existing data.
- 404/500 handlers exist in `app.py`.
- Error templates exist at `templates/errors/404.html` and `templates/errors/500.html`.
- Admin sanitization is implemented (`strip().lower()` + regex validation in `routes/admin.py`).
- `TESTING_CHECKLIST.md` is present and closely matches Step 9 requirements.

### Gaps to complete
1. **README mismatch**
   - Current `README.md` still reflects mixed/legacy monorepo notes (React/Express + Flask notes).
   - Needs to be rewritten to the Step 9-required sections and copy-paste setup flow.

2. **Quiz guard consistency**
   - `routes/quiz.py` has guard coverage in `play` and part of other routes, but not fully aligned with Prompt 08 wording for *every quiz route where needed*.
   - `results` and `check` behavior should be normalized to the same guard/redirect policy (except JSON endpoints where API error is intentional).

3. **Step 9 acceptance verification not fully codified**
   - No focused test pass proving Prompt 08 acceptance criteria end-to-end for this branch.

---

## 3) Execution Plan (Ordered)

## Phase A — Documentation finalization (High priority)
1. Rewrite `README.md` to match Prompt 08 required sections exactly:
   - Features, Requirements, Installation, Running the App, Loading Sample Data,
     Adding Your Own Word Lists, How the Quiz Works, Offline Mode (Canvas),
     Browser Compatibility, Project Structure.
2. Ensure setup commands reflect **this repository’s real structure** and are runnable on macOS/Windows.
3. Remove conflicting legacy statements that refer to different stacks unless explicitly marked as optional/legacy.

**Definition of done**: README reads as a single-source guide for current app setup and execution.

---

## Phase B — Backend guard alignment (High priority)
1. Audit all routes under `routes/quiz.py`:
   - `start_quiz`, `play`, `check`, `results`, `reset`, `recognize_handwriting`.
2. Apply consistent guard behavior:
   - Page routes (`play`, `results`) should flash + redirect to `quiz_bp.index` when no active quiz data.
   - API routes (`check`, `recognize_handwriting`) should return JSON errors where UI expects API responses.
3. Preserve existing UX flow (don’t break JS handlers that expect JSON).

**Definition of done**: No route throws session-related errors; behavior is predictable and user-friendly.

---

## Phase C — Validation & acceptance checks (High priority)
1. Run seed script:
   - `python seed_data.py`
   - confirm success message and no duplicate insertions on re-run.
2. Run targeted test suite first (fast signal), then broader tests:
   - quiz/admin route tests
   - model/basic tests
3. Perform manual checklist items from `TESTING_CHECKLIST.md` (especially edge cases):
   - `/quiz/play` without session
   - 404 page rendering
   - full quiz to results
4. Confirm Step 9 acceptance criteria from Prompt 08 are all satisfied.

**Definition of done**: Step 9 can be marked complete with passing automated/manual evidence.

---

## 4) Suggested Command Checklist (macOS)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py
pytest -q
python app.py
```

Then manually verify browser flows using `TESTING_CHECKLIST.md`.

---

## 5) Deliverables for “Step 9 Complete”

- Updated `README.md` aligned to Prompt 08
- Guard-aligned `routes/quiz.py` behavior
- Verified `seed_data.py` idempotency and output
- Confirmed error templates and handlers
- Completed/updated `TESTING_CHECKLIST.md` run evidence

---

## 6) Optional hardening after Step 9 (not required)

- Add/expand automated tests for session-guard edge cases.
- Add CI workflow to run `pytest` on each push.
- Add a short troubleshooting section in README for TTS/OCR/browser caveats.
