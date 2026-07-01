# Lecciones: no auto-regen + manual regenerate + custom topic input (BUILD 16)

Date: 2026-07-01
Files: `veo-y-digo-source.html` (Lecciones UI, re-bake) + `pebble-app.html` (React: ES_LESSON_CACHE stores an optional `label`; no other React change). Bump `PEBBLE_BUILD` to 16.

Driven by user feedback: re-generating an already-loaded lesson wastes API credits. Caching already works and persists; the only problem is a forced auto-regen. Also: let the user type a custom topic to learn.

## A. Remove the auto-regeneration (the credit waste)

In `openLeccion`, DELETE this line entirely:
```
if (lesson && lesson._v !== 2) lesson = null;   // old shape: force regenerate into the new format
```
Result: a cached lesson of ANY version is used as-is (never auto-regenerated). The renderLeccionView already has backward-compat fallbacks (old `pattern` string renders via `<pre>`; examples without `highlight`/`label` render plainly), so old-format cached lessons still display fine. Only a topic with NO cached lesson triggers generation. leccGenerate still sets `_v = 2` on new lessons (keep that).

## B. Manual "Regenerar" button (only spends a credit on explicit tap)

In `renderLeccionView`, add a small button in the header area (in the `.lecc-head` row, or right after it):
`'<button class="lecc-mini" onclick="leccRegen()">regenerar</button>'`

Add the function:
```
async function leccRegen(){
  if (!leccState) return;
  const topic = leccState.topic;
  if (!window.__claudeKey) return;   // no key: do nothing (the normal view already handles no-key generation)
  const view = document.getElementById('leccView');
  view.innerHTML = '<p class="lecc-loading">Regenerando lección…</p>';
  try {
    const lesson = await leccGenerate(topic);   // overwrites window.__esLessons + posts esLessonCache
    leccState = { topic, lesson, answers:{} };
    renderLeccionView();
  } catch(e) {
    view.innerHTML = '<p class="lecc-loading">No se pudo regenerar. Intenta de nuevo.</p><button class="mode" onclick="leccBackToList()">← volver</button>';
  }
}
```
This is the ONLY path that regenerates an existing lesson, and only on user tap.

## C. Custom topic input ("I wanna learn X")

**Lecciones screen UI:** in the `lecciones` screen markup (or injected by renderLecciones at the top, before Guardadas), add an input + button. Simplest is static markup in the screen `<section>`, above the `leccList`:
```
<div class="lecc-custom">
  <input id="leccCustomInput" type="text" placeholder="¿Qué quieres aprender? (ej: el subjuntivo con ojalá)" />
  <button class="mode" onclick="leccCreateCustom()">Crear lección</button>
</div>
```

**Custom-topic handling (veo source):**
```
window.__customTopics = window.__customTopics || {};
function leccSlug(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40); }
function leccCreateCustom(){
  const el = document.getElementById('leccCustomInput');
  const text = el ? (el.value||'').trim() : '';
  if (!text) return;
  const id = 'custom-' + (leccSlug(text) || 'tema');
  const topic = { id: id, label: text, en: '' };
  window.__customTopics[id] = topic;
  if (el) el.value = '';
  openLeccion(id);
}
```

**`leccTopicById` must also find custom topics.** Change it so after the LECCIONES search it falls back to `window.__customTopics`:
```
function leccTopicById(id){
  for (const g of LECCIONES) for (const t of g.topics) if (t.id === id) return t;
  return (window.__customTopics && window.__customTopics[id]) || null;
}
```

**Persist the custom topic label so it survives reload and is re-listable.** When leccGenerate caches a lesson, it should post the topic label too. Change the `esLessonCache` post in leccGenerate from `{ type:'esLessonCache', topicId: topic.id, lesson: lesson }` to also carry `label: topic.label`:
```
try { window.parent.postMessage({ type:'esLessonCache', topicId: topic.id, lesson: lesson, label: topic.label }, '*'); } catch(e){}
```

**React (pebble-app.html) ES_LESSON_CACHE:** store the optional label on the entry (spread-preserving), so custom topics survive reload:
```
case 'ES_LESSON_CACHE': {
  const cur = state.esLessons[action.topicId] || { status:'new', lesson:null, score:null };
  const next = { ...cur, lesson: action.lesson };
  if (action.label) next.label = action.label;
  return { ...state, esLessons: { ...state.esLessons, [action.topicId]: next } };
}
```
And in `EspanolPage`'s esLessonCache handler, pass the label through:
`if (d.type === 'esLessonCache') dispatch({ type: 'ES_LESSON_CACHE', topicId: d.topicId, lesson: d.lesson, label: d.label });`

**On applyEsLessons (iframe), rebuild `window.__customTopics` from cached custom entries** so openLeccion can find them after reload, and so renderLecciones can list them:
In `applyEsLessons(l)`, after `window.__esLessons = l;`, add:
```
window.__customTopics = window.__customTopics || {};
Object.keys(l||{}).forEach(function(id){ if (id.indexOf('custom-')===0 && l[id] && l[id].label) window.__customTopics[id] = { id:id, label:l[id].label, en:'' }; });
```

**renderLecciones: a "Mis lecciones" section** listing custom lessons (from window.__esLessons custom- ids that have a lesson), above the phased list (after Guardadas):
```
const mine = Object.keys(window.__esLessons||{}).filter(id => id.indexOf('custom-')===0 && window.__esLessons[id] && window.__esLessons[id].lesson);
if (mine.length) {
  html += '<div class="lecc-phase">Mis lecciones</div>';
  mine.forEach(id => {
    const lbl = (window.__esLessons[id].label) || (window.__customTopics[id] && window.__customTopics[id].label) || id;
    const st = leccStatus(id); const mark = st==='done'?'✓':(st==='in-progress'?'·':'');
    html += '<button class="lecc-row" onclick="openLeccion(\''+id+'\')"><span class="lecc-mark">'+mark+'</span> <span class="lecc-label">'+esc(lbl)+'</span></button>';
  });
}
```
(Use `esc` for the custom label since it is user-entered text. `esc` already exists.)

## CSS (add to lecc block)
```
.lecc-custom { margin:8px 0 14px; }
.lecc-custom input { width:100%; padding:10px 12px; border:1px solid rgba(42,33,24,0.15); border-radius:10px; font-size:0.9rem; margin-bottom:8px; background:var(--paper); color:var(--ink); }
```

## Preserve
All v2 formatting, heart-to-save/Guardadas, per-lesson decks, done-status guard, view-reset, practice/quiz/leccFinishQuiz/leccHear/leccSaveEx/leccMakeDeck. The `saved` flag and per-lesson-deck flows are unaffected. Do not clobber.

## Verify
- `python3 scratchpad/checkblock.py veo-y-digo-source.html "function leccCreateCustom"` -> JS SYNTAX OK
- `node scratchpad/checkbabel.js pebble-app.html "ES_LESSON_CACHE"` -> BABEL SYNTAX OK
- `python3 scratchpad/rebake.py "function leccCreateCustom"` -> re-bake OK marker-present
- grep: the `_v !== 2` line is GONE from openLeccion; `leccRegen`, `leccCreateCustom`, `leccTopicById` custom fallback, `__customTopics` rebuild in applyEsLessons, `esLessonCache` posts `label`, `Mis lecciones` in renderLecciones, ES_LESSON_CACHE stores `label`; `PEBBLE_BUILD = 16`.

## No em dashes. Spanish UI copy accented. No emojis (hearts already Unicode glyphs).
