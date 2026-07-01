# Lecciones formatting upgrade (v2) spec

Date: 2026-07-01
File: `veo-y-digo-source.html` (all changes here; re-bake into `pebble-app.html`). Bump `PEBBLE_BUILD` to 14.

From Gabby's on-device feedback: the lesson content renders poorly. Five fixes, applied to ALL lessons (generator prompt + renderer + lesson list), plus auto-regeneration of old cached lessons.

## New LessonObject shape (v2)

```
{
  "teach": "1-2 sentence plain-English intro to the rule",
  "tips": ["short tip, one idea", "another tip"],          // 0-4 items, each shown on its own line
  "patternTable": {
    "headers": ["Pronombre", "Forma"],                     // 2 or 3 short column headers
    "rows": [["yo","soy"], ["tú","eres"], ["él/ella","es"]]// each row same length as headers
  },
  "examples": [
    { "es": "Yo soy alta.", "en": "I am tall.", "highlight": "soy", "label": "ser" }
  ],
  "practice": [ { "q":"", "options":[], "answer":"", "why":"" } ],
  "quiz":     [ { "q":"", "options":[], "answer":"", "why":"" } ],
  "_v": 2
}
```

Field notes:
- `tips`: each is a single short sentence, shown as its own bullet line. Use for "remember: ...", exceptions, gotchas. May be empty.
- `patternTable`: a real table. For conjugations, headers `["Pronombre","Forma"]` and one row per person. For contrast topics (ser vs estar, por vs para), headers can be `["Uso","Ejemplo"]` or `["","Ser","Estar"]` (2 or 3 columns). Every row length must equal headers length.
- `examples[].highlight`: the EXACT substring of `es` that is the point of the example (must appear verbatim in `es`). `examples[].label`: a very short tag naming what it demonstrates (e.g. `ser`, `estar`, `pretérito`, `objeto directo`). Both required on every example.
- `_v`: literal 2. Marks the new shape for the regeneration check.

## 1. Generator prompt (`leccGenerate`)

Replace the prompt so it requests the shape above. Requirements to state in the prompt:
- Return ONLY valid JSON, no markdown, matching the exact shape (show it).
- `teach`: 1-2 sentences. Put any "remember" notes, exceptions, or gotchas as separate `tips` entries, NOT in `teach`.
- `patternTable`: a real table with 2 or 3 short headers and rows; for a conjugation give one row per pronoun (yo, tú, él/ella/usted, nosotros, vosotros, ellos/ustedes) with the conjugated form; for a contrast topic give a comparison table. Every row length equals headers length.
- 2 or 3 `examples`; on each, `highlight` must be an exact substring of `es`, and `label` names the point (for ser vs estar, label each example `ser` or `estar`).
- 6 `practice` items, 4 `quiz` items, each `{q, options[4], answer (exactly one option), why}`.
- Do not include `_v` from the model; the code sets `_v: 2` after parsing.
- Keep it tight for a 10-minute lesson.

After parsing, before caching, the code sets `lesson._v = 2`.

## 2. Shape guard (`leccGenerate`, keep it before the cache write)

```
if (!lesson || typeof lesson.teach !== 'string' || !Array.isArray(lesson.practice) || !Array.isArray(lesson.quiz) || !lesson.quiz.length || !Array.isArray(lesson.examples)) throw new Error('bad-lesson');
lesson._v = 2;
```
(patternTable and tips are optional at the guard level; the renderer tolerates their absence.)

## 3. Auto-regenerate old cached lessons (`openLeccion`)

Where openLeccion reads the cached lesson, treat a cached lesson without `_v === 2` as stale:
```
let lesson = (window.__esLessons[topicId] && window.__esLessons[topicId].lesson) || null;
if (lesson && lesson._v !== 2) lesson = null;   // old shape: force regenerate into the new format
```
Everything after (no-key branch, generate, error branch) stays as is.

## 4. Lesson list English (`LECCIONES` constant + `renderLecciones`)

Add an `en` field to every topic in `LECCIONES`. Use exactly these English labels:

Fundamentos: pronunciacion "Pronunciation & stress"; genero "Noun gender & articles"; concordancia "Adjective agreement"; pronombres "Subject pronouns"; ser-estar "The two verbs for to be"; preguntas "Question words"; negacion "Negation".
Presente: presente-reg "Regular present tense"; cambio-radical "Stem-changing verbs"; irregulares "Common irregular verbs"; reflexivos "Reflexive verbs"; progresivo "Present progressive (-ing)"; gustar "Gustar and similar verbs (to like)".
Pronombres y conectores: od "Direct object pronouns"; oi "Indirect object pronouns"; dobles "Double object pronouns"; posesivos "Possessives & demonstratives"; por-para "Por vs para (for)"; preposiciones "Common prepositions".
Pasado: preterito "Preterite (completed past)"; imperfecto "Imperfect (ongoing past)"; pret-vs-imp "Preterite vs imperfect"; pres-perfecto "Present perfect (have done)".
Futuro y modos: ir-a "Going to (near future)"; futuro "Simple future (will)"; condicional "Conditional (would)"; imperativo "Commands"; subjuntivo "Present subjunctive"; subj-imp "Imperfect subjunctive"; si-clausulas "If / conditional clauses".
Pulido: se-pasivo "Passive & impersonal se"; relativos "Relative clauses"; comparativos "Comparatives & superlatives"; conectores "Discourse connectors".

In `renderLecciones`, render the English as a small muted line inside each `.lecc-row` under the Spanish label, for example:
```
html += '<button class="lecc-row" onclick="openLeccion(\''+t.id+'\')"><span class="lecc-mark">'+mark+'</span> <span class="lecc-label">'+t.label+'</span><span class="lecc-en-sm">'+(t.en||'')+'</span></button>';
```
(`lecc-label` block, `lecc-en-sm` smaller muted below it.)

## 5. Lesson view render (`renderLeccionView`)

Render in this order: back button, title, teach intro, tips list, pattern table, examples, practice, mini-quiz, Terminar. Replace the teach/pattern/examples portions:

```
// intro
html += '<p class="lecc-teach">'+esc(lesson.teach)+'</p>';
// tips, each on its own line
if (Array.isArray(lesson.tips) && lesson.tips.length) {
  html += '<ul class="lecc-tips">' + lesson.tips.map(t => '<li>'+esc(t)+'</li>').join('') + '</ul>';
}
// pattern table (fallback to old string pattern if no table)
if (lesson.patternTable && Array.isArray(lesson.patternTable.rows) && lesson.patternTable.rows.length) {
  const pt = lesson.patternTable;
  let t = '<table class="lecc-table">';
  if (Array.isArray(pt.headers) && pt.headers.length) t += '<thead><tr>' + pt.headers.map(h => '<th>'+esc(h)+'</th>').join('') + '</tr></thead>';
  t += '<tbody>' + pt.rows.map(r => '<tr>' + (Array.isArray(r) ? r : [r]).map(c => '<td>'+esc(c)+'</td>').join('') + '</tr>').join('') + '</tbody></table>';
  html += t;
} else if (typeof lesson.pattern === 'string' && lesson.pattern) {
  html += '<pre class="lecc-pattern">'+esc(lesson.pattern)+'</pre>';
}
// examples: highlight the target word, label the sentence
html += '<div class="lecc-examples">' + (lesson.examples||[]).map((ex,i) => {
  let esHtml = esc(ex.es);
  if (ex.highlight) {
    const h = esc(ex.highlight);
    if (esHtml.indexOf(h) !== -1) esHtml = esHtml.replace(h, '<span class="lecc-hl">'+h+'</span>');
  }
  const tag = ex.label ? '<span class="lecc-tag">'+esc(ex.label)+'</span>' : '';
  return '<div class="lecc-ex"><div class="lecc-ex-line"><span class="lecc-es">'+esHtml+'</span> '+tag+'</div>'
       + '<div class="lecc-ex-tools"><button class="lecc-mini" onclick="leccHear('+i+')">oír</button> <button class="lecc-mini" onclick="leccSaveEx('+i+')">guardar</button></div>'
       + '<span class="lecc-en">'+esc(ex.en)+'</span></div>';
}).join('') + '</div>';
```
The practice and mini-quiz rendering below this is unchanged. `esc`, `leccHear`, `leccSaveEx` already exist. The `.replace(h, ...)` replaces only the first occurrence, which is correct for a single highlighted word.

## 6. CSS (add to the lecc style block)

```
.lecc-tips { margin:8px 0 8px 18px; padding:0; }
.lecc-tips li { margin:4px 0; font-size:0.9rem; color:var(--ink); line-height:1.4; }
.lecc-table { width:100%; border-collapse:collapse; margin:10px 0; font-size:0.9rem; }
.lecc-table th { text-align:left; font-family:'DM Mono',monospace; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--olive); border-bottom:2px solid rgba(42,33,24,0.15); padding:6px 8px; }
.lecc-table td { padding:6px 8px; border-bottom:1px solid rgba(42,33,24,0.08); color:var(--ink); }
.lecc-table tr td:first-child { font-weight:600; color:var(--terracotta); white-space:nowrap; }
.lecc-hl { background:#fbe7c6; color:var(--terracotta-dk,#9a3f22); border-radius:4px; padding:0 3px; font-weight:700; }
.lecc-tag { display:inline-block; font-family:'DM Mono',monospace; font-size:0.66rem; text-transform:uppercase; letter-spacing:0.06em; background:var(--olive); color:var(--paper); border-radius:999px; padding:2px 8px; vertical-align:middle; }
.lecc-ex-line { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.lecc-ex-tools { margin-top:4px; }
.lecc-label { }
.lecc-en-sm { display:block; font-size:0.76rem; color:var(--olive); margin-top:2px; }
```
(Reuse existing `--terracotta`, `--olive`, `--paper`, `--ink` vars. If `--terracotta-dk` is not defined, `#9a3f22` is the fallback in the value above.)

## Verify
- `python3 scratchpad/checkblock.py veo-y-digo-source.html "function renderLeccionView"` -> JS SYNTAX OK
- `python3 scratchpad/rebake.py "patternTable"` -> re-bake OK marker-present
- grep confirm: `_v` set in leccGenerate; `lesson._v !== 2` regen check in openLeccion; `en:` present on LECCIONES topics; `.lecc-table` and `.lecc-hl` in the style block; `PEBBLE_BUILD = 14`.

## Out of scope
The chat "teach me X" (`teachSpanish`, React side) is a separate lighter path; not changed here.

## No em dashes anywhere. UI copy Spanish, accented. No emojis.
