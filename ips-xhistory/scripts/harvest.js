/* ips-xhistory API harvester — inject with javascript_tool into any logged-in x.com tab.
   Replays X's own GraphQL timeline endpoint with cursor pagination.
   ~100 items per request, no UI throttling. Read-only. */
(function () {
  window.__G = window.__G || { items: new Map(), pages: 0, cursor: null };

  // The public web-client bearer is a build constant; the CSRF token is the ct0 cookie.
  window.__H = {
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'x-csrf-token': (document.cookie.match(/ct0=([^;]+)/) || [])[1],
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
    'content-type': 'application/json'
  };

  /* Only top-level timeline entries. A naive recursive search for __typename==='Tweet'
     also picks up quoted and retweeted posts nested inside, which are arbitrarily old
     and will wreck any date-based stop condition. */
  window.__parse = function (j) {
    var out = [], cursor = null;
    (function walk(o) {
      if (!o || typeof o !== 'object') return;
      if (Array.isArray(o)) { for (var i = 0; i < o.length; i++) walk(o[i]); return; }
      if (typeof o.entryId === 'string') {
        if (o.entryId.indexOf('tweet-') === 0) {
          var res = (((o.content || {}).itemContent || {}).tweet_results || {}).result;
          if (res) out.push(res.tweet || res);
        } else if (o.entryId.indexOf('cursor-bottom') === 0) {
          var v = (o.content || {}).value || (((o.content || {}).itemContent || {}).value);
          if (v) cursor = v;
        }
      }
      for (var k in o) { try { walk(o[k]); } catch (e) {} }
    })(j);
    return { tweets: out, cursor: cursor };
  };

  window.__extract = function (t, source) {
    var lg = t.legacy || {};
    var u = ((t.core || {}).user_results || {}).result || {};
    var uc = u.core || {}, ul = u.legacy || {};
    var note = ((t.note_tweet || {}).note_tweet_results || {}).result;   // long-form: full text
    var urls = ((lg.entities || {}).urls || []).map(function (x) {
      return { href: x.expanded_url, text: x.display_url };              // already un-shortened
    });
    var media = ((lg.extended_entities || lg.entities || {}).media) || [];
    return {
      id: t.rest_id, source: source,
      url: 'https://x.com/' + (uc.screen_name || ul.screen_name) + '/status/' + t.rest_id,
      handle: '@' + (uc.screen_name || ul.screen_name || '?'),
      name: uc.name || ul.name || '',
      posted_at: lg.created_at ? new Date(lg.created_at).toISOString() : null,
      text: (note && note.text) || lg.full_text || '',
      truncated: false, links: urls, has_media: media.length > 0,
      order: window.__G.items.size
    };
  };

  window.__harvest = async function (tmplUrl, source, maxPages) {
    var cursor = window.__G.cursor || null, added = 0, stop = '', last = null;
    for (var p = 0; p < maxPages; p++) {
      var u = new URL(tmplUrl);
      var v = JSON.parse(u.searchParams.get('variables'));
      if (cursor) v.cursor = cursor; else delete v.cursor;
      v.count = 100;
      u.searchParams.set('variables', JSON.stringify(v));
      var r = await fetch(u.toString(), { credentials: 'include', headers: window.__H });
      if (r.status !== 200) { stop = 'http' + r.status; break; }
      var pr = window.__parse(await r.json());
      for (var i = 0; i < pr.tweets.length; i++) {
        var rec = window.__extract(pr.tweets[i], source);
        if (!rec.posted_at) continue;
        last = rec.posted_at;
        var key = source + ':' + rec.id;
        if (!window.__G.items.has(key)) { window.__G.items.set(key, rec); added++; }
      }
      window.__G.pages++;
      if (!pr.tweets.length) { stop = 'empty'; break; }
      if (!pr.cursor || pr.cursor === cursor) { stop = 'no-cursor'; break; }
      cursor = pr.cursor; window.__G.cursor = cursor;
    }
    return { added: added, total: window.__G.items.size, pages: window.__G.pages, lastOnPage: last, stop: stop || 'page-cap' };
  };

  window.__gCopy = async function () {
    var N = new RegExp('[\\u0080-\\uFFFF]', 'g');
    var s = JSON.stringify(Array.from(window.__G.items.values()))
      .replace(N, function (c) { return '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4); });
    await navigator.clipboard.writeText(s);
    return { items: window.__G.items.size, bytes: s.length };
  };

  return 'ready';
})();
