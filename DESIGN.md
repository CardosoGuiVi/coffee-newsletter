# Coado — Design System

Visual identity and UI guidelines for the Coado coffee newsletter project.

---

## Brand

**Name:** Coado

**Tagline:** O melhor do café, filtrado pra você

**Tone:** Warm, refined, editorial. Specialty coffee culture without pretension.

**Language:** Portuguese (PT-BR) for all copy and UI. English for code and documentation.

---

## Color Palette

All colors are defined as CSS custom properties in `apps/web/styles/index.css`.

| Token | Hex | Usage |
|---|---|---|
| `--cream-50` | `#F7F3ED` | Page background |
| `--cream-100` | `#EFE9E1` | Intro block background, subtle surfaces |
| `--cream-200` | `#E9E2D6` | Dividers, separators |
| `--cream-300` | `#D4C6AE` | Borders, pill outlines, muted dividers |
| `--coffee-300` | `#C87941` | Accent bar (left border on callout blocks), decorative elements |
| `--coffee-500` | `#8B5E3C` | Secondary text, labels, source tags, links |
| `--coffee-700` | `#6F3F1E` | Primary accent, buttons, active borders, decorative SVG fills |
| `--coffee-900` | `#2B1F17` | Body text, headlines |

### Usage Rules

- **Background:** always `--cream-50`
- **Body text:** always `--coffee-900`
- **Primary interactive elements** (buttons, focus rings, active states): `--coffee-700`
- **Hover on interactive elements:** `--coffee-900`
- **Muted/secondary text:** `--coffee-500`
- **Borders and outlines:** `--cream-300`

---

## Typography

```css
--font-display: 'Fraunces', Georgia, serif;
--font-body:    'Inter', -apple-system, sans-serif;
```

| Role | Font | Weight | Notes |
|---|---|---|---|
| Headlines / hero | Fraunces | 400 | Optical size variable, italic available |
| Display numbers (stats) | Fraunces | 300 | `font-variant-numeric: tabular-nums` |
| Body copy | Inter | 400 | `line-height: 1.75` |
| Labels / buttons | Inter | 500 | |
| Eyebrow / tags | Inter | 500 | `letter-spacing: 0.22em`, uppercase |

**Google Fonts import:**
```
Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300;1,9..144,400
Inter:wght@400;500
```

> **Email fallback:** Email clients do not support web fonts. Use `Georgia, serif` for display and `Arial, sans-serif` for body in all email templates.

---

## Logo

- File: `apps/web/images/logo-dark.svg`
- Rendered as `<img>` tag, `height: 50px`, `width: auto`
- Wrapped in `.logo-link` with `opacity: 0.7` on hover
- Dark variant only (`logo-dark.svg`) — designed for the cream background

---

## Textures & Decorative Elements

### Grain overlay

Applied via `body::before` pseudo-element. SVG fractal noise pattern at `opacity: 0.03`, fixed position, `pointer-events: none`, `z-index: 0`. Creates subtle paper-like texture without affecting readability.

```css
background-image: url("data:image/svg+xml,...fractalNoise baseFrequency='0.85' numOctaves='4'...");
background-size: 160px;
```

### Coffee drop shapes

Two decorative SVG teardrop/drop shapes, fixed-positioned, `opacity: 0.04`, `fill: #6F3F1E` (`--coffee-700`):

- `.deco-1` — top-right, `width: 300px`, slight offset outside viewport
- `.deco-2` — bottom-left, `width: 240px`, `rotate(18deg)`

Both are `pointer-events: none`, `z-index: 0`, `aria-hidden="true"`.

---

## UI Components

### Form row

Inline email input + submit button inside a single bordered container.

```
.form-row
  border: 1.5px solid --cream-300
  border-radius: 10px
  background: #ffffff
  overflow: hidden

:focus-within
  border-color: --coffee-700
  box-shadow: 0 0 0 3px rgba(111, 63, 30, 0.09)
```

- Input: `padding: 0.875rem 1rem`, transparent background, placeholder color `--cream-300`
- Button: `background: --coffee-700`, `color: --cream-50`, hover → `--coffee-900`
- On mobile (`max-width: 480px`): stacks vertically, input gets `border-bottom: 1px solid --cream-200`

### Pills / Tags

```
padding: 0.3rem 0.8rem
border: 1px solid --cream-300
border-radius: 999px
font-size: 0.72rem
letter-spacing: 0.09em
color: --coffee-500
```

### Stats

```
font-family: --font-display (Fraunces)
font-weight: 300
font-size: 2.25rem
letter-spacing: -0.04em
color: --coffee-900
font-variant-numeric: tabular-nums
```

Label below each stat: `0.69rem`, `letter-spacing: 0.14em`, uppercase, `--coffee-500`.
Separator between stats: `1px solid --cream-200`, `height: 30px`.

---

## Animation

Easing function used throughout:

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
```

| Keyframe | From | To | Usage |
|---|---|---|---|
| `fadeUp` | `opacity:0; translateY(14px)` | `opacity:1; translateY(0)` | All hero elements, form, categories, stats |
| `fadeDown` | `opacity:0; translateY(-10px)` | `opacity:1; translateY(0)` | Hero rule (vertical line above label) |

Hero elements stagger with increasing `animation-delay`:

| Element | Delay |
|---|---|
| `.hero-rule` | 0s |
| `.hero-label` | 0.1s |
| `.hero-headline` | 0.2s |
| `.hero-sub` | 0.3s |
| `.subscribe-form` | 0.4s |
| `.categories` | 0.55s |
| `.stats-section` | 0.65s |

All animations use `animation-fill-mode: both`.

---

## Email Templates

Email templates live in `packages/newsletter/templates/`.

### Constraints

- No external fonts — use `Georgia, serif` and `Arial, sans-serif` only
- Layout via `<table>` only (no flexbox, no grid)

### Color mapping (email)

| Role | Value |
|---|---|
| Background | `#F7F3ED` |
| Surface (intro block) | `#EFE9E1` |
| Item card background | `#FFFFFF` |
| Item card border | `#EFE9E1` |
| Accent bar | `#C87941` |
| Primary text | `#2B1F17` |
| Secondary text / links | `#8B5E3C` |
| Muted text (footer) | `#D4C6AE` |

### Templates

| File | Purpose | Key variables |
|---|---|---|
| `newsletter.html` | Weekly digest | `week_label`, `intro`, `items`, `closing`, `unsubscribe_url` |
| `newsletter_item.html` | Single article block | `title`, `summary`, `source`, `url` |
| `welcome.html` | Sent on signup | `name` (optional, defaults to `'amante de café'`), `unsubscribe_url` |

### List-Unsubscribe

To enable the native Gmail unsubscribe button, include these headers in every Resend send call:

```python
"headers": {
    "List-Unsubscribe": f"<{unsubscribe_url}>",
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
}
```

The `unsubscribe_url` must accept POST requests (RFC 8058). Gmail renders the native button after a few sends from a domain with valid DKIM/DMARC.

---

## Layout

Page uses CSS Grid with four rows:

```css
.page {
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  /* header / hero / stats / footer */
}
```

All content above `z-index: 1`. Decorative and texture layers at `z-index: 0`.

---

## Responsive Breakpoints

| Breakpoint | Changes |
|---|---|
| `max-width: 480px` | Form stacks vertically, reduced padding, smaller stats numbers (`1.875rem`) |
| `max-width: 360px` | Hero headline forced to `2.4rem` |