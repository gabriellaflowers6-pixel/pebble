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
waterCount: { 'YYYY-MM-DD': number }
dailyPlan: { date, plan }
notebook: { saves[], dailyPick{date,quote,quoteAuthor,funFact,rec} }
pageNotes: { pageName: "note text" }
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
- System prompt injects: profile, context (knowledge base), todos, events, meals, skincare, study, workouts, career, journal (last 5 entries), stickies, page notes, existing daily plan
- **Time-of-day awareness**: current time injected, AI adjusts tone (morning=energizing, evening=wind-down, night=reflective)
- **Smart reminders**: AI sees what hasn't been done today (workout, skincare, journal, study) and can gently nudge
- AI can emit `<actions>` blocks to modify app data and `<memory>` blocks to suggest saving personal facts
- **Voice input**: mic button on chat bar using Web Speech API (`webkitSpeechRecognition`). Tap to listen, transcribes to input field. Only shows if browser supports it.
- **Layer 2 Tool Use** — Claude's native `tools` parameter with tool-use loop:
  - `get_weather` — Open-Meteo API (temp, UV, rain, forecast). Free, no key, CORS OK
  - `define_word` — Free Dictionary API. No key, CORS OK
  - `get_time` — World Time API (timezone lookup). No key, CORS OK
  - `get_quote` — ZenQuotes API (random quote). No key, CORS OK
  - Tool-use loop in `sendMessage()`: Claude requests tool → `executeToolCall()` fetches data → result sent back → Claude responds with real data. Max 5 loops.
- **Stickies in prompt**: AI sees all stickies and naturally references them when relevant
- **Per-page AI notes**: `UPDATE_PAGE_NOTE` action lets AI save short tips/suggestions per room page. `PageNote` component renders collapsible "pebble's notes ✦" on each page.

### Gist Sync + Brain File
- **Auto-save** debounced 3s to GitHub Gist (settings excluded for security)
- **Two files saved**: `pebble.json` (full app data) + `pebble-brain.md` (clean markdown summary for Claude Project)
- `generateBrainMd(data)` — standalone function that builds a readable markdown brain file with: About Me, Knowledge Base, Stickies, Active Todos, Skincare, Study, Career, Fitness, Recent Journal, AI Notes
- **Claude Project integration**: Gabby has a "Pebble" project on claude.ai (laptop). She pastes `pebble-brain.md` into the project's Files so Claude on laptop knows the same things as Pebble on phone
- **LOAD_DATA** preserves local settings via `{ ...merged, settings: { ...merged.settings, ...state.settings } }`
- Manual "push now" / "pull now" buttons in Settings

### Theme System
- **22 built-in themes** in `THEMES` object
- **CSS_DEFAULTS** — 30+ CSS variables reset before each theme switch
- **Extra vars cleanup**: `extraVarsRef` tracks element-override vars from playground themes, removes them on theme switch
- **Playground export** (`pushToApp()`) exports ALL vars + cloud image data (`cloudImg: { src, opacity, target }`)
- **Cloud images**: `applyTheme()` applies cloud overlays to phone-frame bg and/or cards. Card overlays use CSS `::after` with `--card-cloud-img` and `--card-cloud-opacity` vars
- CSS classes use vars: `.checkbox` uses `--checkbox-shape` + `--stroke-width`, `.page-title` uses `--heading-size`, `.dot` uses `--stroke-width`

### Navigation System (3 styles, switchable in Settings)
- **`navStyle` setting**: `'jar'` (default) | `'tabs'` | `'pebbles'`
- **MarbleJar** — fullscreen overlay with SVG jar + labeled marbles. Header shows jar icon button.
- **TabNav** — horizontal scrollable manila folder tabs with drop shadow divider
- **PebbleNav** — horizontal scrollable labeled circles with drop shadow divider
- **PageDots** (vertical indicator) only shows in jar mode
- **Header** has subtle drop shadow for visual separation in all modes

### Jar Icon System
- **9 icon options** in Settings, all transparent PNGs in `images/`
- Icon picker only shows when nav style is 'jar'

### Haptic Feedback
- `navigator.vibrate?.(10)` on key interactions: dot toggles, checkbox toggles, nav buttons, mood selectors, theme swatches, water tracker, send button

### Settings Panel (top to bottom)
1. **Theme dropdown** — compact, tap to expand/collapse
2. **Navigation** — 3 buttons: jar / tabs / pebbles
3. **Jar icon** — 9 image picker (only when nav = jar)
4. **Account** — name (input), diet (tappable toggle), skin type (input)
5. **My knowledge base** — textarea showing `[key] value` entries
6. **Sync & AI** — Claude API key, Gist ID/token, push/pull, OneSignal
7. **Open on phone** — QR code
8. **Data** — export/import, reset

### Rooms (page order — updated 2026-03-14)
1. **Stream (Home)** — greeting, today's dots, water tracker (0/8 glasses with +/- and progress bar), mood trends (7-day colored dots), daily plan ("plan my day" AI-generated schedule), task/calorie stats, streak badge
2. **Planner** — todos, priority dots, filter tabs, weekly calendar, events
3. **Kitchen** — calorie progress bar, meal cards, grocery list
4. **Gym** — workout logging, streak tracking, recent sessions
5. **Self-Care** — AM/PM skincare routines, numbered steps
6. **Study** — course progress bars, session logging
7. **Tracker** — monthly dot grid for 5 categories, cloud painting bg
8. **Career** — goal, skills, job applications, experience log
9. **Journal** — full-page lined paper (cream bg, blue ruled lines, red margin), swipe left/right to flip between days, today editable, previous read-only, page counter, mood pills
10. **Notebook (Picks)** — daily quote (from books + McKenna/Watts/Doctor Who), fun fact, recommendation (leans toward literary fiction), saved picks
11. **Build** — custom segment builder
12. **Stickies** — colored sticky notes, add/edit/delete
13+. **Custom Segments** — dynamic pages from `data.segments[]`

### Daily Plan Feature
- "plan my day" button on Stream page
- AI generates personalized daily schedule using Haiku (fast)
- Based on: todos, events, meals, skincare, workouts, stickies, journal mood, knowledge base
- Saves to `data.dailyPlan { date, plan }`, regenerates daily
- Collapsible with "regenerate" button

### Daily Picks (Notebook)
- Auto-generates on mount when API key present and pick is stale
- **Quote**: rotates between Terence McKenna, Alan Watts, Doctor Who, and Gabby's favorite books (Song of Achilles, Circe, Babel, Life of Pi, Martyr!)
- **Fun fact**: weird/delightful facts about science, history, mythology, space, animals
- **Recommendation**: movie/book/podcast/recipe, leans toward literary fiction matching Gabby's taste
- Heart button to save picks

### Chat UX
- **Close chat**: tap-outside backdrop (fixed positioning) + pull-down handle bar at top of overlay
- Chat overlay: blurred bg, last 10 messages, "thinking..." indicator
- Swipe right on chat bar area to toggle

### Multi-Step Planning (Layer 3 — basic)
- User asks AI to plan something ("help me prep for my interview", "plan my Sunday")
- AI breaks into 5-8 actionable steps, emits `<plan>{"title":"...","steps":["..."]}</plan>` block
- `ADD_PLAN`, `TOGGLE_PLAN_STEP`, `DELETE_PLAN` reducer actions
- Plans show as persistent checklist cards on Stream page with progress bars
- AI sees active plans + progress in system prompt, can reference them in future chats
- Haptic feedback on step toggles

### Auto-Reconnect (URL Hash Sync)
- Gist ID, token, and API key encoded in URL hash fragment: `#g=...&t=...&k=...`
- `getHashCreds()` reads keys from hash on init — overrides localStorage (most reliable source)
- `updateHashCreds()` keeps hash in sync whenever settings change
- **"📎 copy sync link"** button in Settings copies the full URL with keys baked in
- Bookmark that URL on phone → even if Safari wipes localStorage, opening the bookmark auto-loads keys and pulls data from Gist
- Hash fragment never sent to servers (stays client-side only)

### Pebble Nav Glass Marbles
- `PEBBLE_COLORS` array: 12 unique colors matching pebble-jar.html marble gradients
- Each room gets its own color: teal (stream), lavender (planner), sage (kitchen), coral (gym), rose (selfcare), indigo (study), orange (tracker), steel (career), amber (journal), lime (picks), terracotta (build), mint (stickies)
- Radial gradient + specular highlights for transparent glass marble look
- Active marble has glow shadow

### GitHub Pages Deployment
- **Live URL:** `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html`
- **Repo:** `https://github.com/gabriellaflowers6-pixel/pebble`
- Push: `cd "/Users/gabriellakalvaitis-flowers/Desktop/my projects/pebble" && git add pebble-app.html && git commit -m "update" && git push`

---

## Pebble AI Vision — Three Layers

1. **Knowledge Base** (DONE) — keyed memory, system prompt injection, memory tray, Gist brain sync, per-page AI notes
2. **Tool Use** (DONE) — 4 browser-native tools (weather, dictionary, timezone, quotes). Time-of-day context. Smart reminders. Voice input.
3. **Agent Mode** (STARTED) — multi-step planning with persistent checklists. AI breaks goals into steps, user checks them off over time. Future: Netlify Functions for recipe search, web search, nutrition lookup, calendar OAuth, gym booking.

## Gabby's Preferences
- **Books**: Song of Achilles, Circe, Babel (R.F. Kuang), Life of Pi, Martyr! (Kaveh Akbar)
- **Reading list**: There Is No Antimemetics Division
- **Taste**: literary fiction, mythological retellings, philosophical/existential themes, lyrical prose
- **Quotes**: Terence McKenna, Alan Watts, Doctor Who, plus quotes from favorite books
- **Daily picks**: quote + fun fact + book-leaning recommendation

## Not Yet Built (future sessions)

### Next up (Gabby approved)
- [ ] Onboarding flow — 3-step welcome: name → theme → Gist sync setup
- [ ] Search — search across todos, journal, stickies, notes, grocery, everything
- [ ] Swipe to delete — swipe left on todos/grocery/stickies to delete (native mobile feel)
- [ ] Streak calendar — GitHub-style heatmap on tracker page showing streaks over months
- [ ] Night mode shortcut — long-press "pebble" header to toggle midnight mode
- [ ] Grocery auto-clear — "clear completed" button when all items are checked

### Backlog
- [ ] Export to PDF — weekly plan, journal, meal plan as printable PDF
- [ ] Chat pinning — pin important AI responses so they don't scroll away
- [ ] Weekly review — AI summarizes the week every Sunday
- [ ] Grocery from meals — AI suggests missing grocery items based on meal plan
- [ ] Planner: monthly calendar view
- [ ] Kitchen: AI meal suggestions
- [ ] Stats room: year-at-a-glance dot grid view
- [ ] Tier 2 tools (need Netlify proxy): recipe search, web search, nutrition lookup
- [ ] Layer 3 advanced: calendar OAuth, email, gym booking, full autonomous agent tasks
