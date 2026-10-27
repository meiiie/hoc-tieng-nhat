'use strict';
(function (root) {
  const Content = {};

  Content.audioURL = function (word, kind, voice) {
    const url = word.audio?.[voice]?.[kind] || `audio/${word.page}/${voice}/${kind}/${word.num}.mp3`;
    if (!/^audio\/(?:generated\/(?:gb|us)\/[a-f0-9]{24}|p\d+\/(?:gb|us)\/(?:w|ex)\/\d+)\.mp3$/.test(url)) {
      throw new Error('Invalid audio path');
    }
    return url;
  };

  Content.cloze = function (word) {
    const { ex, cloze } = word;
    if (!ex || !cloze || ex.slice(cloze.start, cloze.end) !== cloze.text) return null;
    return { before: ex.slice(0, cloze.start), ans: cloze.text, after: ex.slice(cloze.end) };
  };

  Content.downloadAudio = async function (words, voice, cache, progress, fetcher = fetch) {
    const urls = [...new Set(words.flatMap(w => ['w', 'ex'].map(k => Content.audioURL(w, k, voice))))];
    const result = { total: urls.length, saved: 0, failed: [] };
    let next = 0;
    async function worker() {
      while (next < urls.length) {
        const url = urls[next++];
        try {
          const cached = await cache.match(url);
          if (!cached || cached.status !== 200) {
            const response = await fetcher(url, { signal: AbortSignal.timeout(30000) });
            if (response.status !== 200) throw new Error(`HTTP ${response.status}`);
            await cache.put(url, response);
          }
          result.saved++;
        } catch (error) {
          result.failed.push({ url, error: String(error.message || error) });
        }
        progress?.(result);
      }
    }
    await Promise.all(Array.from({ length: Math.min(4, urls.length) }, worker));
    return result;
  };
  root.Content = Content;
  if (typeof module !== 'undefined') module.exports = Content;
})(globalThis);
