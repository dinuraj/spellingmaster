# Prompt 03 — Base Templates & Global CSS

> **How to use:** Paste this entire prompt into GitHub Copilot Chat and send it.  
> Run **after** Prompt 02.

---

## Your Task

Generate the base HTML layout and global stylesheet for Spelling Master.

---

## `templates/base.html`

Create a Jinja2 base template with:

### `<head>` section:
- `charset="UTF-8"`, `viewport` for mobile.
- Title block: `{% block title %}Spelling Master{% endblock %}`.
- Google Fonts import: `Nunito` weights 400, 600, 700, 800.
- Link to `/static/css/style.css`.
- Extra head block: `{% block extra_head %}{% endblock %}`.

### `<body>` layout:
```
<body>
  <header>  ← always visible top bar
  <main>    ← page content block
  <footer>  ← simple copyright line
</body>
```

### Header contents:
- App logo/name: a yellow pencil emoji ✏️ followed by **Spelling Master** in large bold font.
- Nav links: **Home** (`/`), **Manage Words** (`/admin/`).
- On mobile (< 600 px) the nav collapses — use a simple CSS hamburger toggle, no JS framework.

### Flash messages:
Below the header, render flashed messages using Bootstrap-style alert divs with categories: `success` (green), `error` (red), `warning` (yellow). Use `{% with messages = get_flashed_messages(with_categories=true) %}`.

### Content block:
```html
<main class="container">
  {% block content %}{% endblock %}
</main>
```

### Footer:
`© 2025 Spelling Master — Made with ❤️ for young learners`

---

## `templates/home.html`

Extends `base.html`. Shows:
1. **Hero section** — big friendly heading "Ready to Spell? 🚀" and a short subtitle.
2. **Word List Cards** — loop over `word_lists` variable (passed from route). Each card shows:
   - List name (large)
   - Word count badge
   - "Start Quiz" button (POST form to `/quiz/start` with hidden `list_id`)
3. **Empty state** — if no word lists exist, show a friendly message and a link to `/admin/`.

---

## `static/css/style.css`

Write a complete stylesheet. Do **not** import Bootstrap — write custom CSS only.

### Color variables (define as CSS custom properties on `:root`):
```css
--gold:    #FFD700;
--green:   #4CAF50;
--blue:    #2196F3;
--coral:   #FF6B6B;
--purple:  #9C27B0;
--bg:      #FFFDF0;      /* warm off-white background */
--card-bg: #FFFFFF;
--text:    #2D2D2D;
--text-light: #666666;
--radius:  16px;
--shadow:  0 4px 16px rgba(0,0,0,0.10);
```

### Global rules:
- `font-family: 'Nunito', sans-serif` on `body`.
- `font-size: 18px` base; line-height 1.6.
- `background-color: var(--bg)`.
- Smooth `box-sizing: border-box` on `*`.

### `.container`:
- `max-width: 960px`, centered with `margin: 0 auto`, `padding: 0 20px`.

### Buttons (`.btn`):
- Base: `padding: 12px 28px`, `border-radius: 50px`, `font-size: 1.1rem`, `font-weight: 700`, `cursor: pointer`, `border: none`, `transition: transform 0.15s, box-shadow 0.15s`.
- Hover: `transform: translateY(-2px)`, deeper shadow.
- `.btn-primary` → gold background, dark text.
- `.btn-success` → green background, white text.
- `.btn-danger` → coral background, white text.
- `.btn-lg` → larger padding and font size for the main quiz button.

### Cards (`.card`):
- `background: var(--card-bg)`, `border-radius: var(--radius)`, `box-shadow: var(--shadow)`, `padding: 24px`.

### Header (`header.site-header`):
- Sticky, white background, subtle bottom border.
- Flexbox layout: logo on left, nav on right.

### Flash alerts (`.alert`):
- Rounded, padded, dismissible look.
- `.alert-success`, `.alert-error`, `.alert-warning` with matching colors.

### Animations:
```css
@keyframes bounce-in {
  0%   { transform: scale(0.8); opacity: 0; }
  60%  { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-8px); }
  40%, 80% { transform: translateX(8px); }
}

.animate-bounce { animation: bounce-in 0.4s ease forwards; }
.animate-shake  { animation: shake 0.4s ease; }
```

### Responsive:
- Single-column card layout on screens < 600 px.
- Larger font on the quiz word display (`.quiz-word`) — `font-size: clamp(2rem, 8vw, 4rem)`.

---

## Acceptance Criteria
- Pages render correctly at 375 px (mobile) and 1200 px (desktop).
- Flash messages appear and are color-coded.
- Home page shows a card for each word list.
- No external CSS libraries — only Google Fonts import is allowed.
