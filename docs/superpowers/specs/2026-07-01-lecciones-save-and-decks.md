# Lecciones: save (heart) + per-lesson flashcards spec

Date: 2026-07-01
Files: `veo-y-digo-source.html` (Lecciones UI, re-bake) + `pebble-app.html` (React data layer + message handlers, no re-bake for React parts). Bump `PEBBLE_BUILD` to 15.

Two additions on top of the v2 lesson formatting. Both reuse the existing React<->iframe postMessage bridge and the esFlash deck reducer.

## Feature A: Heart a lesson to save it (Guardadas)

**Data:** the React `data.esLessons[topicId]` entry gains a `saved` boolean.

**Reducer (pebble-app.html):** new action
```
case 'ES_LESSON_SAVE': {
  const cur = state.esLessons[action.topicId] || { status:'new', lesson:null, score:null };
  return { ...state, esLessons: { ...state.esLessons, [action.topicId]: { ...cur, saved: !!action.saved } } };
}
```
The existing `ES_LESSON_CACHE` / `ES_LESSON_PROGRESS` reducers already spread `...cur`, so they preserve `saved`. Confirm they do (they use `const cur = state.esLessons[topicId] || {...}; return {...cur, <field>}`), so `saved` survives a later cache/progress update.

**Message (iframe -> React):** `{ type:'esLessonSave', topicId, saved }`. Add to the `EspanolPage` message listener:
```
else if (d.type === 'esLessonSave') dispatch({ type:'ES_LESSON_SAVE', topicId: d.topicId, saved: d.saved });
```
`saved` flows back to the iframe through the existing `esLessonsData` post (no new outbound message needed).

**Iframe UI (veo-y-digo-source.html):**
- `leccIsSaved(id)` -> `!!(window.__esLessons[id] && window.__esLessons[id].saved)`.
- `leccToggleSave(id)`: compute `next = !leccIsSaved(id)`; set `window.__esLessons[id] = window.__esLessons[id] || {status:'new',lesson:null,score:null}; window.__esLessons[id].saved = next;` then `window.parent.postMessage({type:'esLessonSave', topicId:id, saved:next}, '*')`; re-render the current view (if in lesson view, re-render its header; simplest is to re-run renderLeccionView; on the list, renderLecciones).
- In `renderLeccionView`, add a heart button in the header next to the back button:
  `'<button class="lecc-heart'+(leccIsSaved(topic.id)?' on':'')+'" onclick="leccToggleSave(\''+topic.id+'\')" aria-label="guardar">'+(leccIsSaved(topic.id)?'♥':'♡')+'</button>'`
  (filled heart U+2665 when saved, outline U+2661 when not).
- In `renderLecciones`, before the phased list, render a **Guardadas** section listing saved topics (only if any):
```
const saved = [];
LECCIONES.forEach(g => g.topics.forEach(t => { if (leccIsSaved(t.id)) saved.push(t); }));
if (saved.length) {
  html += '<div class="lecc-phase">Guardadas</div>';
  saved.forEach(t => {
    html += '<button class="lecc-row" onclick="openLeccion(\''+t.id+'\')"><span class="lecc-mark">♥</span> <span class="lecc-label">'+t.label+'</span><span class="lecc-en-sm">'+(t.en||'')+'</span></button>';
  });
}
// then the existing phased checklist follows
```

## Feature B: Per-lesson flashcard deck

**Message (iframe -> React):** `{ type:'esMakeDeck', id, label, cards:[{es,en,kind}] }`. Add to the `EspanolPage` listener:
```
else if (d.type === 'esMakeDeck' && d.id && Array.isArray(d.cards)) {
  dispatch({ type:'ES_FLASH_NEW_SET', id: d.id, label: d.label || d.id, date: new Date().toISOString().slice(0,10), themed: true });
  d.cards.forEach(c => { if (c && c.es) dispatch({ type:'ES_FLASH_ADD_CARD', setId: d.id, card: { kind: c.kind || 'sentence', es: c.es, en: c.en || '' } }); });
}
```
`ES_FLASH_NEW_SET` is idempotent (no-op if the deck id exists) and `ES_FLASH_ADD_CARD` dedups by `convoCardKey`, so re-tapping the button is safe (no duplicate deck, no duplicate cards).

**Iframe UI (veo-y-digo-source.html):** in `renderLeccionView`, add a button below the examples (or near Terminar):
`'<button class="mode" onclick="leccMakeDeck()">Hacer tarjetas de esta leccion</button>'`
and:
```
function leccMakeDeck(){
  if (!leccState) return;
  const topic = leccState.topic, lesson = leccState.lesson;
  const cards = [];
  (lesson.examples||[]).forEach(ex => {
    if (ex.es) cards.push({ es: ex.es, en: ex.en || '', kind:'sentence' });
    if (ex.highlight) cards.push({ es: ex.highlight, en: ex.label ? (ex.label) : (ex.en || ''), kind:'word' });
  });
  if (!cards.length) return;
  try { window.parent.postMessage({ type:'esMakeDeck', id:'leccion-'+topic.id, label:'Leccion: '+topic.label, cards: cards }, '*'); } catch(e){}
  const btnHost = document.getElementById('leccView');
  const tag = document.createElement('p'); tag.className='lecc-loading'; tag.textContent = 'Tarjetas creadas: "Leccion: '+topic.label+'" (revisa Tarjetas).';
  if (btnHost) btnHost.appendChild(tag);
}
```
Card content: each example gives a sentence card (es front, en back) and, when it has a `highlight`, a word card (the highlighted word front; back = its label if present, else the example english). Deck id `leccion-<topicId>`, label `Leccion: <topic.label>` (plain "Leccion", no accent inside a JS string label is fine; keep it ASCII-safe here to avoid any encoding surprises in the deck label). Themed so it survives the esFlash merge migration and shows in Tarjetas.

## CSS (add to lecc block)
```
.lecc-heart { background:none; border:none; cursor:pointer; font-size:1.3rem; line-height:1; color:var(--terracotta); padding:2px 6px; }
.lecc-heart.on { color:var(--berry,#b23a48); }
```
(Place the heart in the header row; the header currently holds the back button, so wrap them in a flex row if needed, or float the heart right.)

## Preserve
All v2 formatting (table, highlighted examples, tips, list english), the done-status guard on reopen, the view-reset in renderLecciones, the `_v!==2` regeneration, leccHear/leccSaveEx, practice/quiz/leccFinishQuiz. Do not clobber.

## Verify
- `python3 scratchpad/checkblock.py veo-y-digo-source.html "function leccMakeDeck"` -> JS SYNTAX OK
- `node scratchpad/checkbabel.js pebble-app.html "function EspanolPage"` -> BABEL SYNTAX OK (React handlers added)
- `node scratchpad/checkbabel.js pebble-app.html "ES_LESSON_SAVE"` -> BABEL SYNTAX OK
- `python3 scratchpad/rebake.py "function leccMakeDeck"` -> re-bake OK marker-present
- grep: `esLessonSave` + `esMakeDeck` handlers in pebble-app.html; `ES_LESSON_SAVE` reducer; `leccToggleSave` + `leccMakeDeck` + `lecc-heart` in veo source; `PEBBLE_BUILD = 15`.

## No em dashes. Spanish copy accented in UI text (deck labels kept ASCII-safe). No emojis (hearts are Unicode glyphs U+2665/U+2661, intentional UI, not decoration).
