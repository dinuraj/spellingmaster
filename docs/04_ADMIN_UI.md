# Prompt 04 — Admin / Word Management UI

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 03.

---

## Your Task

Generate the two admin HTML templates for managing word lists and words.

---

## `templates/admin/manage_lists.html`

Extends `base.html`. Title: "Manage Word Lists".

### Layout (top to bottom):

#### 1. Page header row
- Heading: "📚 Word Lists"
- Button: "+ New Word List" (opens the inline creation form below or links to `/admin/list/new`)

#### 2. Create New List form
- Fields: **List Name** (text, required), **Description** (textarea, optional).
- Submit button: "Create List".
- POST to `/admin/list/new`.
- Show inline validation hint if name is blank.

#### 3. Existing lists table
For each `WordList` in `word_lists`:

| Column | Content |
|---|---|
| List Name | Bold, links to `/admin/list/<id>/edit` |
| Words | Count badge (e.g. "12 words") |
| Created | Formatted date |
| Actions | Edit button, Delete button (with JS confirm dialog) |

Delete button: small form with POST to `/admin/list/<id>/delete` and `onclick="return confirm('Delete this list and all its words?')"`.

#### 4. Empty state
If no lists: friendly illustration (use a large emoji like 📭) and text "No word lists yet — create your first one above!"

---

## `templates/admin/edit_list.html`

Extends `base.html`. Title: "Edit — {{ word_list.name }}".

### Layout:

#### 1. Breadcrumb
`Word Lists > {{ word_list.name }}`

#### 2. Edit list details form
- Name and Description fields pre-filled.
- POST to `/admin/list/<id>/edit`.
- Save button.

#### 3. Bulk Import section
- Textarea labelled "Paste words (one per line). Add a hint after `|` — e.g. `beautiful|She wore a beautiful dress.`"
- Submit button "Import Words".
- POST to `/admin/list/<id>/bulk`.
- Show a small help note explaining the format.

#### 4. Current words table
Show all words in the list:

| # | Word | Hint | Remove |
|---|---|---|---|
| 1 | beautiful | She wore a beautiful dress. | ✕ button |

- The ✕ button calls a small JS function that does a `fetch` POST to `/admin/word/<id>/delete` and removes the table row on success (no page reload).
- Show word count above the table: "{{ words|length }} words in this list".

#### 5. Add single word form
At the bottom:
- Two inline inputs: **Word** and **Hint (optional)**.
- "Add Word" button.
- POST to `/admin/list/<id>/word/add` via `fetch` (AJAX); prepend the new word to the table on success without reloading.

#### JavaScript for this page (inline `<script>` block, < 50 lines):
```javascript
// deleteWord(wordId, rowElement) — DELETE via fetch, remove row
// addWord(listId) — POST via fetch, prepend new row to table
```

---

## Styling notes (add to `style.css` or use `<style>` block)

- Admin table: alternating row colors (`#f9f9f9` / white), rounded table container.
- Delete buttons: small, coral, icon-only with tooltip.
- Textarea for bulk import: `font-family: monospace`, `min-height: 120px`.
- Breadcrumb: small, muted gray text.

---

## Acceptance Criteria
- Creating a new list and adding words works end-to-end.
- Bulk import correctly parses the `word|hint` format.
- Deleting a word removes it from the table instantly without page reload.
- All forms show appropriate flash messages on success/failure.
