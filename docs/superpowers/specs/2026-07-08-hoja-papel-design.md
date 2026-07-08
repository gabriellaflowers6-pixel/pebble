# Hoja de Trabajo — "Modo papel" (paper worksheet mode)

Date: 2026-07-08. Approved direction from Gabby: add as a SECOND mode (keep the existing one-at-a-time drill), fill blanks by tapping choices, and allow AI-generated extra questions on explicit tap.

## What it is

A paper-style worksheet view per category in the Veo app's Hoja de Trabajo section. One scrollable page that looks like a school worksheet:

1. **Word key at the top.** A compact explanation of the words being drilled, e.g. for the Tu category: `tú = you (subject) · te = you (object) · tu = your · ti = after prepositions`. Content comes from the category's existing `desc` plus a condensed version of `wsRefs[catId]` where available. Always visible while working, so she can glance up like on a real worksheet.
2. **Numbered question list.** ALL of the category's `exercises` rendered at once as numbered fill-in-the-blank sentences (`1. ___ llamo mañana. (I'll call you tomorrow)`).
3. **Tap to fill.** Tapping a blank opens the question's small option chips inline under that sentence (tú/te/tu/ti). Picking one fills the blank: green if right; red with the correct word shown if wrong. Each answered question gets a small `¿por qué?` toggle reusing the exercise's existing `why` text.
4. **Score line.** At the bottom: `8 / 10 correctas` once all blanks are filled, plus a `Repetir` button that clears the sheet.
5. **✦ Más preguntas (AI).** Button at the bottom. On explicit tap only, calls Claude (claude-sonnet-4-6, same headers as `leccGenerate`) asking for ~6 NEW exercises for this category in the exact `wsCategories` exercise JSON shape ({before, blank, after, english, options, answer, why}), avoiding duplicates of the ones on the sheet. Generated questions are appended to the sheet under a "Preguntas nuevas" divider.

## Persistence (credit rule)

Generated questions are cached, never regenerated automatically:

- Veo posts `{type:'wsExtra', catId, exercises}` to the parent; Pebble stores them in `data.wsExtra[catId]` (new reducer case `WS_EXTRA_ADD`) in localStorage.
- `EspanolPage` posts the whole `wsExtra` map into the iframe on load (same pattern as `esLessonsData`); Veo merges them into the paper sheet for that category.
- Tapping "Más preguntas" again generates ANOTHER batch (explicit tap = explicit spend) and appends; no auto-regen anywhere.

## Entry point

On the category picker (`wsCategoryList`), each category row gets a second small button: `📄 hoja` next to the existing drill entry. Existing drill flow untouched.

## Error handling

- No API key / API error on Más preguntas: inline message under the button ("No se pudo generar. Revisa tu clave o intenta de nuevo."), sheet unaffected.
- Response shape guard before caching (array, each item has blank/options/answer), mirroring leccGenerate's guard so garbage never poisons the cache.

## Testing

No test framework: syntax gates (checkblock/checkbabel), rebake round-trip, headless render of the paper sheet at 375px, on-device check by Gabby (fill a sheet, generate extras, reload and confirm extras persist).

## Out of scope

Typed-answer input, worksheet PDF export, changes to the existing drill mode, other categories' content.
