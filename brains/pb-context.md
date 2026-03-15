# Pebble App — Context File for Chat Continuity

## What is Pebble?
A single-file React lifestyle/productivity app (`pebble-app.html`) with a phone-frame UI (375x812). Built with React 18 + Babel Standalone + Tailwind CDN. All code lives in one HTML file.

## File Locations
- **Main app:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/pebble-app.html`
- **Playground:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/pebble-playground.html`
- **Images:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/images/` (cloud 1-6, jar icons as PNGs, ref images, screenshots)
- **Vintage Typography images:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/Vintage Typography/` (source images for jar icons, reference art)
- **Brain/Context (this file):** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/brains/pb-context.md`
- **Pebble Brain (user data for Claude Project):** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/brains/pebble-brain.md`
- **PRD:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/Pebble-PRD.docx`
- **Jar preview:** `/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble/pebble-jar.html`

## Architecture

### State Management
- **DataContext + useReducer** — all data in `DEFAULT_DATA` object
- **localStorage persistence** — saves on every state change, loads on mount
- **Credentials backup** — `pebble-credentials` localStorage key backs up `settings` + `profile` to survive mobile purges and Gist pulls
- **DataProvider** wraps the app: `<ThemeProvider><DataProvider><App /></DataProvider></ThemeProvider>`

### Data Schema (DEFAULT_DATA)
```
profile: { name, vegan, skinType, context: {} }   ← context is keyed object (see Memory System)
planner: { events, todos[{id,text,priority,done}], notes[] }
journal: { entries[{date,body,mood}] }
kitchen: { mealPlan{breakfast,lunch,dinner}, calorieLog{...}, target, grocery[{text,done}] }
gym: { workoutPlan[{name,exercises}], sessions[{date,workout,notes}] }
selfCare: { skincare{morning[],evening[]}, routines[] }
study: { courses[{name,status,progress}], sessions[], goals[] }
career: { role, targetDate, skills[{name,progress}], applications[{company,role,date,status}], experiences[] }
segments: [ { id, name, features[], entries[], checks[], note, bars[], dots{} } ]
dots: { category: { 'YYYY-MM-DD': true } }
notebook: { saves[], dailyPick{date,quote,quoteAuthor,rec} }
settings: { gistId, gistToken, apiKey, oneSignalAppId, oneSignalRestKey, jarIcon, navStyle }
chat: { messages[{role,content,time}] }
stickies: [{id, text, color, createdAt}]
memory: { pending[] }
```

### Memory System (profile.context — keyed object)
- `profile.context` is a **keyed object**, not a flat string: `{ "skincare:cleanser": "CeraVe", "allergy:food": "beets" }`
- **UPDATE_CONTEXT action** requires `key` + `fact` — same key overwrites old value (no duplicates)
- **Memory tray**: after each chat, Claude emits `<memory>` blocks → user reviews → save dispatches UPDATE_CONTEXT
- **Migration**: old string format auto-migrates to keyed object via `migrateContext()` on load
- System prompt injects context as: `- [key] value` per entry
- Editable in Settings → "my knowledge base" textarea (renders as `[key] value` lines)
- **Profile backup**: credentials backup now includes full `profile` data (name, vegan, skinType, context) to survive localStorage purges

### Chat System + AI (Layer 1 + Layer 2)
- **ChatBar** sends messages to Claude API (`claude-sonnet-4-6`) with `anthropic-dangerous-direct-browser-access` header
- System prompt injects: profile, context (knowledge base), todos, events, meals, skincare, study, workouts, career, journal (last 5 entries), stickies
- AI can emit `<actions>` blocks to modify app data and `<memory>` blocks to suggest saving personal facts
- **Layer 2 Tool Use** — Claude's native `tools` parameter with tool-use loop:
  - `get_weather` — Open-Meteo API (temp, UV, rain, forecast). Free, no key, CORS OK
  - `define_word` — Free Dictionary API. No key, CORS OK
  - `get_time` — World Time API (timezone lookup). No key, CORS OK
  - `get_quote` — ZenQuotes API (random quote). No key, CORS OK
  - Tool-use loop in `sendMessage()`: Claude requests tool → `executeToolCall()` fetches data → result sent back → Claude responds with real data. Max 5 loops.
- **Stickies in prompt**: AI sees all stickies and naturally references them when relevant

### Gist Sync + Brain File
- **Auto-save** debounced 3s to GitHub Gist (settings excluded for security)
- **Two files saved**: `pebble.json` (full app data) + `pebble-brain.md` (clean markdown summary for Claude Project)
- `generateBrainMd(data)` — standalone function that builds a readable markdown brain file with: About Me, Knowledge Base, Stickies, Active Todos, Skincare, Study, Career, Fitness, Recent Journal
- **Claude Project integration**: Gabby has a "Pebble" project on claude.ai (laptop). She pastes `pebble-brain.md` into the project's Files so Claude on laptop knows the same things as Pebble on phone
- **LOAD_DATA** preserves local settings via `{ ...merged, settings: { ...merged.settings, ...state.settings } }`
- Manual "push now" / "pull now" buttons in Settings

### Theme System
- **22 built-in themes** in `THEMES` object
- **CSS_DEFAULTS** — 30+ CSS variables reset before each theme switch, including:
  - Colors: `--bg`, `--surface`, `--primary`, `--primary-light`, `--accent`, `--accent-light`, `--dark`, `--muted`, `--danger`, `--card-bg`, `--card-border`, `--card-shadow`
  - Fonts: `--font-display`, `--font-body`, `--font-mono`
  - Typography sizes: `--brand-size`, `--heading-size`, `--body-size`, `--label-size`, `--stat-size`, `--icon-size`
  - Shapes: `--border-radius`, `--card-radius`, `--card-border-w`, `--checkbox-shape`, `--btn-fill`, `--btn-fill-done`
  - Strokes: `--stroke-width`, `--icon-stroke`
  - Spacing: `--card-padding`, `--spacing`
  - Other: `--cloud-sky`, `--sky-height`, `--tab-active-bg`
- **Extra vars cleanup**: `extraVarsRef` tracks element-override vars from playground themes, removes them on theme switch
- **Playground export** (`pushToApp()`) now exports ALL vars: colors, fonts, sizes, shapes, strokes, spacing, element overrides
- CSS classes use vars: `.checkbox` uses `--checkbox-shape` + `--stroke-width`, `.page-title` uses `--heading-size`, `.dot` uses `--stroke-width`

### Navigation System (3 styles, switchable in Settings)
- **`navStyle` setting**: `'jar'` (default) | `'tabs'` | `'pebbles'`
- **MarbleJar** — original fullscreen overlay with SVG jar + labeled marbles. Only shows when `navStyle === 'jar'`. Header shows jar icon button.
- **TabNav** — horizontal scrollable manila folder tabs below header. Active tab has card-bg, pops up with no bottom border.
- **PebbleNav** — horizontal scrollable row of labeled circular pebbles below header. Active pebble filled with primary color.
- All nav styles auto-scroll to keep active page visible
- **PageDots** (vertical indicator) only shows in jar mode

### Jar Icon System
- **9 icon options** in Settings, all transparent PNGs in `images/`:
  - `pebble-logo.png` (bunny silhouette — default), `icon-bunny-stars.png`, `icon-sun.png`, `icon-moon-bunny.png`, `icon-flower-oval.png`, `icon-rose.png`, `icon-tulip-stamp.png`, `icon-plant.png`, `icon-chicken.png`
- Backgrounds removed + cropped via Python Pillow
- Header uses `data.settings.jarIcon` with `mix-blend-mode: multiply`
- Icon picker only shows in Settings when nav style is 'jar'

### Settings Panel (top to bottom)
1. **Theme dropdown** — compact: shows current theme name + color dots, tap to expand scrollable list, tap theme to select + collapse. Custom playground themes in separate section.
2. **Navigation** — 3 buttons: jar / tabs / pebbles
3. **Jar icon** — 9 image picker (only visible when nav = jar)
4. **Account** — name (editable input), diet (tappable toggle: vegan/no preference), skin type (editable input)
5. **My knowledge base** — textarea showing `[key] value` entries, editable
6. **Sync & AI** — Claude API key, Gist ID, Gist token, push/pull buttons, OneSignal fields
7. **Open on phone** — QR code auto-generated from current URL
8. **Data** — export/import, reset

### Rooms (12 static + dynamic custom segments)
1. **Stream (Home)** — greeting, today's dots, task/calorie stats, streak badge
2. **Planner** — todos with toggle/add/delete, priority dots, filter tabs
3. **Journal** — daily textarea with auto-save, mood selector, previous entries
4. **Kitchen** — calorie progress bar, meal cards, grocery list
5. **Gym** — workout logging, streak tracking, recent sessions
6. **Self-Care** — AM/PM skincare routines, numbered steps
7. **Study** — course progress bars, session logging
8. **Tracker** — monthly dot grid for 5 categories, cloud painting bg
9. **Career** — goal, skills, job applications, experience log
10. **Notebook (Picks)** — daily quote + recommendation, saved picks
11. **Build** — custom segment builder
12. **Stickies** — colored sticky notes, add/edit/delete
13+. **Custom Segments** — dynamic pages from `data.segments[]`

### GitHub Pages Deployment
- **Live URL:** `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html`
- **Repo:** `https://github.com/gabriellaflowers6-pixel/pebble`
- Push: `cd "/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble" && git add pebble-app.html && git commit -m "update" && git push`

---

## Pebble AI Vision — Three Layers

1. **Knowledge Base** (DONE) — `profile.context` keyed memory, system prompt injection, memory tray, Gist brain sync
2. **Tool Use** (DONE — basic) — 4 browser-native tools via Claude's `tools` API parameter (weather, dictionary, timezone, quotes). No backend needed.
3. **Agent Mode** (future) — multi-step autonomous tasks, user approves before execution. Would need Netlify Functions for: recipe search, web search, nutrition lookup, calendar OAuth, gym booking.

## Session 2026-03-14: What Was Built

### Memory System Overhaul
- `profile.context` changed from flat string → keyed object
- UPDATE_CONTEXT now requires `key` + `fact`, same key = overwrite
- `migrateContext()` auto-converts old string format on load/Gist pull
- System prompt tells AI to use descriptive keys like `skincare:cleanser`
- Settings knowledge base textarea renders `[key] value` format

### Theme Sync Fix
- Playground `pushToApp()` now exports ALL CSS vars (was only exporting colors/fonts)
- `CSS_DEFAULTS` expanded with 13 new vars (sizes, shapes, strokes, spacing)
- CSS classes updated to use vars (`.checkbox`, `.page-title`, `.dot`, `.theme-swatch`)
- `extraVarsRef` tracks/cleans element-override vars on theme switch
- Fixed `--card-border-width` → `--card-border-w` naming mismatch

### Navigation System
- 3 switchable nav styles: jar, tabs, pebbles
- TabNav: manila folder tabs, scrollable, active tab pops up
- PebbleNav: labeled circles in a row, scrollable
- Header hides jar button when not in jar mode
- Settings picker with icons

### Jar Icon System
- 9 transparent PNG icons from Vintage Typography folder
- Backgrounds removed + cropped via Python Pillow
- Selectable in Settings, persists in `settings.jarIcon`

### Profile Persistence Fix
- Credentials backup now includes full `profile` (was only `settings`)
- Prevents vegan/skinType/context from being lost on mobile purges or Gist pulls
- Diet toggle made tappable, skin type made editable in Settings

### AI Context Expansion
- Journal entries (last 5) now injected into system prompt
- Stickies injected into system prompt with instruction to reference naturally
- Brain file (`pebble-brain.md`) auto-generated on every Gist sync

### Layer 2: Tool Use
- `PEBBLE_TOOLS` array with 4 tool definitions
- `executeToolCall()` function handles each tool
- `sendMessage()` now uses a while loop for multi-turn tool calls
- Tools: get_weather (Open-Meteo), define_word (Free Dictionary), get_time (World Time), get_quote (ZenQuotes)
