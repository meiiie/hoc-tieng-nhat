'use strict';
(function(root) {
  const has = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  const wordId = cid => cid.replace(/~r$/, '');
  const started = (introductions, id) => has(introductions, id);
  const GROUP_SIZE = 25;
  const limit = value => value !== '' && value != null && Number.isInteger(+value) && +value >= 0 ? Math.min(+value, GROUP_SIZE) : GROUP_SIZE;

  function groups(ids) {
    if (new Set(ids).size !== ids.length) throw new Error('Duplicate word ID in study days');
    const ordered = [...ids].sort((a,b)=>a.localeCompare(b,'en',{numeric:true}));
    const result = [];
    for (let i=0; i<ordered.length; i+=GROUP_SIZE) {
      const number = result.length+1;
      result.push({id:'day'+String(number).padStart(2,'0'), number, wordIds:ordered.slice(i,i+GROUP_SIZE)});
    }
    return result;
  }

  function restoreDays(state) {
    const f = state.set.f;
    state.migrationV11 = {goal:state.user?.goal, filter:{...f}};
    const oldFilter = state.migrationV9?.filter || {};
    if (!has(f,'day')) f.day = has(oldFilter,'day') ? oldFilter.day : (f.cefr || f.star || f.task1 ? '' : 'day01');
    if (state.user) {
      const wasAutomatic = state.user.goal === '10' && state.migrationV9?.goal === 'all';
      state.user.goal = String(wasAutomatic ? GROUP_SIZE : limit(state.user.goal));
    }
    if (state.sess) {
      delete state.sess.review;
      if (state.sess._last === 'review') delete state.sess._last;
    }
    return state;
  }

  function orderIds(baseOrder, {star={}, ev={}}) {
    const met = id => ev[id]?.at(-1)?.[0] || 0;
    return baseOrder.map((id,rank)=>({id,rank,star:!!star[id],met:met(id)}))
      .sort((a,b)=>Number(b.star)-Number(a.star) || b.met-a.met || a.rank-b.rank)
      .map(row=>row.id);
  }

  function removeLessonScope(state) {
    if (state.set.lesson || state.set.f?.lesson) {
      state.migrationV10 = {lesson:state.set.lesson, filter:{...state.set.f}};
    }
    delete state.set.lesson;
    delete state.set.f.lesson;
    if (state.sess) {
      delete state.sess.review;
      if (state.sess._last === 'review') delete state.sess._last;
    }
    return state;
  }

  function usage(state, start, ids=null) {
    const day = state.studyDay;
    if (day?.start !== start) return {words:0, directions:0};
    const scope = ids && new Set(ids);
    return {words:day.words.filter(id=>!scope || scope.has(id)).length,
            directions:day.directions.filter(cid=>!scope || scope.has(wordId(cid))).length};
  }

  function record(state, card, now, start) {
    if (state.studyDay?.start !== start) state.studyDay = {start, words:[], directions:[]};
    const day = state.studyDay, id = card.w.id;
    if (!started(state.introductions, id)) {
      state.introductions[id] = now;
      day.words.push(id);
    } else if (!day.words.includes(id) && !day.directions.includes(card.cid)) {
      day.directions.push(card.cid);
    }
  }

  function migrate(state, start) {
    const filter = state.set.f || {};
    state.migrationV9 = {filter:{...filter}, goal:state.user?.goal, notice:!!state.user?.done};
    delete filter.day;
    delete filter.page;
    state.set.f = filter;
    if (state.user) state.user.goal = String(limit(state.user.goal));
    state.introductions = {};
    const first = {};
    for (const [time, cid, , kind] of state.revlog || []) {
      if (kind === 'new') first[cid] = Math.min(first[cid] ?? Infinity, time);
    }
    for (const [cid, card] of Object.entries(state.srs || {})) {
      if (card && card.state !== 'new' && !has(first, cid)) first[cid] = 0;
    }
    for (const [cid, time] of Object.entries(first)) {
      const id = wordId(cid);
      state.introductions[id] = Math.min(state.introductions[id] ?? Infinity, time);
    }
    state.studyDay = {start, words:[], directions:[]};
    for (const [id, time] of Object.entries(state.introductions)) {
      if (time >= start) state.studyDay.words.push(id);
    }
    for (const [time, cid, , kind] of state.revlog || []) {
      if (time >= start && kind === 'new' && !state.studyDay.words.includes(wordId(cid)) && !state.studyDay.directions.includes(cid)) {
        state.studyDay.directions.push(cid);
      }
    }
    if (state.sess) {
      delete state.sess.review;
      if (state.sess._last === 'review') delete state.sess._last;
    }
    return state;
  }

  function queue({cards, srs, introductions, usage, newIds, limit:cap, buried, now, dayEnd}) {
    const learning = [], review = [], directions = [], freshById = new Map();
    const selected = new Set(newIds);
    const hidden = card => buried[card.w.id] && buried[card.w.id] !== card.cid;
    for (const x of cards) {
      const c = srs[x.cid];
      if (c?.susp || hidden(x)) continue;
      if (c && c.state !== 'new') {
        if (c.state === 'review') { if (c.due <= now) review.push(x); }
        else learning.push(x);
        continue;
      }
      if (srs[x.w.id]?.susp || srs[x.w.id+'~r']?.susp) continue;
      if (started(introductions, x.w.id)) { if (selected.has(x.w.id)) directions.push(x); }
      else if (x.dir === 'en') freshById.set(x.w.id, x);
    }
    const byDue = (a,b) => srs[a.cid].due - srs[b.cid].due || a.cid.localeCompare(b.cid);
    learning.sort(byDue);
    review.sort(byDue);
    directions.sort((a,b) => introductions[a.w.id] - introductions[b.w.id] || a.cid.localeCompare(b.cid));
    const seen = new Set();
    const uniqueDirections = directions.filter(x => !seen.has(x.w.id) && seen.add(x.w.id));
    return {
      learning, review,
      fresh:newIds.map(id => freshById.get(id)).filter(Boolean).slice(0, Math.max(0, cap-usage.words)),
      directions:uniqueDirections.slice(0, Math.max(0, cap-usage.directions)),
      learningToday:learning.filter(x => srs[x.cid].due < dayEnd).length,
      due:cid => srs[cid].due
    };
  }

  function next(q, now, currentId, learnAhead=20*60e3) {
    const due = q.learning.find(x => q.due(x.cid) <= now);
    if (due) return due;
    if (q.review.length) return q.review.find(x => x.cid === currentId) || q.review[0];
    const fresh = [...q.directions, ...q.fresh];
    if (fresh.length) return fresh.find(x => x.cid === currentId) || fresh[0];
    return q.learning.find(x => q.due(x.cid) <= now+learnAhead) || null;
  }

  const api = {GROUP_SIZE, groups, restoreDays, started, limit, usage, record, migrate, removeLessonScope, orderIds, queue, next};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LearningPlan = api;
})(globalThis);
