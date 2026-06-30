# Pebble — Interface Design System
# Mock Direction: Vintage Letterpress

## Identity

**App:** Pebble — single-file React lifestyle app, phone frame 375×812px
**Stack:** React 18 + Babel Standalone + Tailwind CDN, single HTML file
**Mock:** Pebble Mock 1 — Vintage Letterpress direction
**Vibe:** Circus poster / 1920s–30s print advertising. Heavy borders, ornamental type, cream + burgundy + near-black.

---

## Color Tokens (Vintage Letterpress)

```
--bg:            #FFF5ED    warm ivory cream
--surface:       #FFFAF5    near-white
--primary:       #8B2332    deep burgundy / maroon
--primary-light: rgba(139,35,50,0.08)
--accent:        #D4A0A0    dusty rose
--accent-light:  rgba(212,160,160,0.12)
--dark:          #1A1A1A    near-black
--muted:         #8A7A6A    warm gray-brown
--danger:        #8B2332
--card-bg:       rgba(255,250,245,0.95)
--card-border:   rgba(26,26,26,0.30)
--card-shadow:   rgba(139,35,50,0.06)
```

---

## Typography

```
--font-display: 'Playfair Display', serif   → headlines, titles
--font-body:    'Libre Baskerville', serif  → body text
--font-mono:    'DM Mono', monospace        → data, tracking numbers
```

**Display rules:**
- Page titles: font-weight 900, uppercase, letter-spacing 5px, font-size 18px
- Prefix with ✦ ornament character
- Solid 4px burgundy underline bar (::after)
- Never use system fonts (Inter, Roboto, etc)

**Type scale:**
- Page title: 18px / 900 weight
- Section label: 12px / uppercase / tracked
- Body: 14px / regular
- Small label: 10–11px
- Ornamental footer: 10px / Libre Baskerville

---

## Spacing

```
Base unit: 4px
Scale: 4, 8, 12, 16, 20, 24, 32
```

Page padding: 20px horizontal, 16px top
Card padding: 16px horizontal, 12px vertical (standard) / 12px horizontal, 10px vertical (compact)
Section gap: 8–12px
Element gap: 4–8px

---

## Depth Strategy

**Primary: Border-based (heavy)**

Cards use bold visible borders — no reliance on shadows for depth.

```
Card:     2.5px solid #1A1A1A (outer) + 1px solid rgba(139,35,50,0.3) inset (inner, 3px offset)
Section:  1px solid rgba(139,35,50,0.2) hairline rules
No blur:  backdrop-filter: none — crisp, opaque surfaces
```

Shadow use is minimal and only for print-style offset effects:
- Offset shadow when needed: `3px 3px 0 #1A1A1A` (not diffuse)

---

## Shapes

```
--card-radius:    0px    sharp corners everywhere
--card-border-w:  2px
Checkboxes:       square (border-radius: 0 !important)
Dots/indicators:  square
Buttons:          square or minimal radius (2–4px max)
```

---

## Ornamental Language

These are the visual signatures of this theme — use them consistently:

| Element | Treatment |
|---|---|
| Page title prefix | `✦ ` character |
| Section divider | `— ✦ —` centered, 10px, burgundy 30% opacity |
| Cards | Double-frame: outer 2.5px black + inner 1px burgundy offset |
| Underlines | Solid 4px block underline, not decorative underline |
| Rules | 1px horizontal lines between sections |

---

## Card Pattern

```css
.glass-card {
  background: rgba(255,250,245,0.95);
  border: 2.5px solid #1A1A1A;
  border-radius: 0;
  box-shadow: none;
  position: relative;
}
.glass-card::before {
  content: '';
  position: absolute;
  inset: 3px;
  border: 1px solid rgba(139,35,50,0.3);
  pointer-events: none;
}
```

---

## Pages (6 swipe pages)

1. **Home** — greeting, streak badge, today dots, quick stats, swipe hint
2. **Tasks** — checkbox list, priority dots, add hint
3. **Meals** — calorie bar, 3 meal cards (breakfast/lunch/dinner)
4. **Workout** — workout card, streak, exercise list
5. **Tracker** — monthly dot grid (5 categories)
6. **Picks** — daily quote card, recommendation card

---

## What to Avoid

- Rounded corners (no rounded-xl, rounded-2xl on cards)
- Backdrop blur / glassmorphism
- Gradient backgrounds (cloud sky = none)
- Soft box shadows (diffuse glow)
- Sans-serif fonts for display text
- Generic Inter/Roboto/system fonts
- Lower-case page titles
- Colorful backgrounds — stay on cream/ivory
