/* Tatoeba examples: stored surface blanks and conservative, offline ruby. */
(function(root){'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function cloze(w){const e=w.example,m=e?.match;if(!m||!Number.isInteger(m.start)||!Number.isInteger(m.end)||m.start<0||m.end<=m.start||e.text.slice(m.start,m.end)!==m.surface)return null;return {before:e.text.slice(0,m.start),ans:m.surface,after:e.text.slice(m.end)}}
const label=t=>t.machine?'bản dịch máy, cần kiểm tra':t.pivot?'dịch qua câu tiếng Anh':'bản dịch tiếng Việt trên Tatoeba';
const credit=s=>`<a href="https://tatoeba.org/sentences/show/${Number(s.id)}" target="_blank" rel="noopener">Tatoeba #${Number(s.id)} · ${esc(s.username)}</a>`;
function attribution(e){const t=e.translation;return `<details class="ja-source ja-example-source"><summary>Nguồn câu ví dụ · ${esc(label(t))}</summary><p>${credit(e)} · <a href="https://creativecommons.org/licenses/by/2.0/fr/" target="_blank" rel="noopener">CC BY 2.0 FR</a></p>${t.machine?`<p>Dịch bởi AI từ ${credit(t.from)} (tiếng Anh, CC BY 2.0 FR); chưa có người bản ngữ kiểm tra.</p>`:`<p>Tiếng Việt: ${credit(t)} · CC BY 2.0 FR.</p>${t.pivot?`<p>Qua ${credit(t.via)} (tiếng Anh, CC BY 2.0 FR).</p>`:''}`}</details>`}
function sentence(e,furigana=true){const ss=e.furigana;if(!furigana||!Array.isArray(ss)||ss.map(s=>s.base).join('')!==e.text||ss.some(s=>typeof s.base!=='string'||(s.ruby&&(!/^[\p{Script=Han}々〆〇]+$/u.test(s.base)||!/^[ぁ-ゖー]+$/.test(s.ruby)))))return esc(e.text);return ss.map(s=>s.ruby?`<ruby>${esc(s.base)}<rt>${esc(s.ruby)}</rt></ruby>`:esc(s.base)).join('')}
function render(e,furigana=true){if(!e)return '';return `<div class="ja-example"><p lang="ja" class="ja-example-text">${sentence(e,furigana)}</p><p lang="vi">${esc(e.translation.text)}</p><p class="muted ja-small">${esc(label(e.translation))}</p>${attribution(e)}</div>`}
const api={cloze,render,attribution,label,sentence};if(typeof module==='object'&&module.exports)module.exports=api;else root.JaExamples=api;
})(typeof globalThis!=='undefined'?globalThis:this);
