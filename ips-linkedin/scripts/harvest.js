/**
 * ips-linkedin — inject this into a logged-in LinkedIn tab.
 *
 * Defines: __LI, __imgUrls, __toMd, __grabFrame, __harvestPosts, __stash.
 * See SKILL.md for the procedure and references/dead-ends.md for what not to try.
 */

window.__LI = window.__LI || {posts: new Map(), arts: {}};

/** csrf token lives in the JSESSIONID cookie, quotes and all. */
const __hdrs = () => ({
  accept: 'application/vnd.linkedin.normalized+json+2.1',
  'csrf-token': (document.cookie.match(/JSESSIONID="?([^";]+)/) || [])[1] || '',
});

/**
 * Every image URL under a node. LinkedIn stores them as
 * {rootUrl, artifacts:[{width, fileIdentifyingUrlPathSegment}]} — widest wins.
 * Swap the sort for a mid-width pick if the destination is a git repo.
 */
window.__imgUrls = (node) => {
  const out = [];
  const walk = (n) => {
    if (!n || typeof n !== 'object') return;
    if (Array.isArray(n)) return n.forEach(walk);
    if (n.rootUrl && Array.isArray(n.artifacts)) {
      const best = n.artifacts.slice().sort((a, b) => (b.width || 0) - (a.width || 0))[0];
      if (best?.fileIdentifyingUrlPathSegment) out.push(n.rootUrl + best.fileIdentifyingUrlPathSegment);
      return;
    }
    for (const v of Object.values(n)) walk(v);
  };
  walk(node);
  return [...new Set(out)];
};

/** An activity id carries its creation time in the top 41 bits. */
window.__urnDate = (id) => new Date(Number(BigInt(id) >> 22n)).toISOString();

/** Paginate the feed on paginationToken. `start` is a no-op — see dead-ends. */
window.__harvestPosts = async (profileUrn, queryId, selfName, {pageSize = 50, maxPages = 40} = {}) => {
  if (!selfName) throw new Error('__harvestPosts needs the account holder\'s display name to tell originals from reposts');
  const enc = encodeURIComponent(profileUrn);
  const get = async (token) => {
    const vars = token
      ? `(count:${pageSize},start:0,profileUrn:${enc},paginationToken:${encodeURIComponent(token)})`
      : `(count:${pageSize},start:0,profileUrn:${enc})`;
    const r = await fetch(
      `/voyager/api/graphql?includeWebMetadata=true&variables=${vars}&queryId=${queryId}`,
      {headers: __hdrs(), credentials: 'include'},
    );
    return r.json();
  };

  let token = null;
  let stop = 'page-cap';
  const rounds = [];

  for (let i = 0; i < maxPages; i++) {
    const j = await get(token);
    const ups = (j.included || []).filter((o) => o.$type === 'com.linkedin.voyager.dash.feed.Update');
    let added = 0;
    for (const u of ups) {
      const eu = u.entityUrn || '';
      const id = (eu.match(/urn:li:activity:(\d+)/) || [])[1];
      if (!id || window.__LI.posts.has(id)) continue;
      const art = u.content?.articleComponent || null;
      const headerText = u.header?.text?.text || null;
      const actorName = u.actor?.name?.text || null;
      window.__LI.posts.set(id, {
        activityId: id,
        actorName,
        headerText,
        // Authored by the account holder. Two things that look like they would
        // work and do not: `entityUrn` says MEMBER_SHARES on reposts too, and
        // the reshare reference is `*resharedUpdate` — the plain key is
        // `undefined`, so `!u.resharedUpdate` passes every repost through.
        // See references/dead-ends.md.
        isOriginal: actorName === selfName && !headerText && !u['*resharedUpdate'],
        text: u.commentary?.text?.text || '',
        articleTitle: art?.title?.text || art?.title || null,
        articleUrl: art?.navigationContext?.actionTarget || null,
        images: window.__imgUrls(u.content || {}),
      });
      added++;
    }
    rounds.push({page: i, updates: ups.length, added, total: window.__LI.posts.size});
    const next = j?.data?.data?.feedDashProfileUpdatesByMemberShareFeed?.metadata?.paginationToken;
    if (ups.length === 0) { stop = 'empty-page'; break; }
    if (!next) { stop = 'no-token'; break; }
    if (added === 0) { stop = 'no-new'; break; }
    token = next;
    await new Promise((r) => setTimeout(r, 600));
  }

  const all = [...window.__LI.posts.values()];
  const rejected = all.filter((p) => !p.isOriginal);
  return {
    stop, rounds,
    activities: all.length,
    original: all.filter((p) => p.isOriginal && p.text.trim()).length,
    rejected: rejected.length,
    // Report the split: a silent filter that drops a third of the corpus is
    // indistinguishable from one that drops nothing.
    rejectedActors: [...new Set(rejected.map((p) => p.actorName).filter((n) => n && n !== selfName))],
  };
};

/** Article DOM -> Markdown. Keeps headings, lists, links, emphasis, code, images. */
window.__toMd = (root) => {
  const flat = (t) => t.replace(/\s+/g, ' ');
  const inline = (n) => {
    let s = '';
    for (const c of n.childNodes) {
      if (c.nodeType === 3) { s += flat(c.nodeValue); continue; }
      if (c.nodeType !== 1) continue;
      const t = c.tagName.toLowerCase();
      if (t === 'a' && c.href) s += `[${inline(c).trim()}](${c.href})`;
      else if (t === 'strong' || t === 'b') s += `**${inline(c).trim()}**`;
      else if (t === 'em' || t === 'i') s += `*${inline(c).trim()}*`;
      else if (t === 'code') s += '`' + inline(c).trim() + '`';
      else if (t === 'br') s += '\n';
      else s += inline(c);
    }
    return s;
  };
  const out = [];
  const walk = (el) => {
    for (const c of el.children) {
      const t = c.tagName.toLowerCase();
      if (/^h[1-6]$/.test(t)) out.push('#'.repeat(Math.min(6, Math.max(2, +t[1]))) + ' ' + inline(c).trim());
      else if (t === 'p') { const s = inline(c).trim(); if (s) out.push(s); }
      else if (t === 'ul' || t === 'ol') {
        [...c.children].forEach((li, i) => { const s = inline(li).trim(); if (s) out.push((t === 'ol' ? `${i + 1}. ` : '- ') + s); });
        out.push('');
      } else if (t === 'blockquote') { const s = inline(c).trim(); if (s) out.push('> ' + s); }
      else if (t === 'pre') out.push('```\n' + c.innerText.trim() + '\n```');
      else if (t === 'figure' || t === 'img') {
        const img = t === 'img' ? c : c.querySelector('img');
        if (img?.src) out.push(`![${(img.alt || '').replace(/[[\]]/g, '')}](${img.src})`);
      } else if (c.children.length) walk(c);
      else { const s = inline(c).trim(); if (s) out.push(s); }
    }
  };
  walk(root);
  return out.filter((l, i, a) => !(l === '' && a[i - 1] === '')).join('\n\n').replace(/\n{3,}/g, '\n\n').trim();
};

/**
 * Render one Pulse article in a same-origin hidden iframe and convert it.
 * fetch() returns an empty SPA shell — see dead-ends.
 */
window.__grabFrame = (url) => new Promise((resolve) => {
  const f = document.createElement('iframe');
  f.style.cssText = 'position:fixed;left:-9999px;width:1200px;height:2000px';
  f.src = url;
  let done = false;
  const finish = (r) => { if (done) return; done = true; f.remove(); resolve(r); };
  f.onload = () => {
    let tries = 0;
    const t = setInterval(() => {
      tries++;
      try {
        const d = f.contentDocument;
        const body = d?.querySelector('.reader-article-content');
        if (body && body.innerText.trim().length > 200) {
          clearInterval(t);
          finish({
            url, ok: true,
            title: d.querySelector('h1')?.innerText?.trim() || null,
            // Pulse renders no datetime attribute; this is a display string.
            date: d.querySelector('time')?.getAttribute('datetime') || d.querySelector('time')?.innerText?.trim() || null,
            cover: d.querySelector('.reader-article-content img, figure img')?.src || null,
            md: window.__toMd(body),
          });
        }
        if (tries > 28) { clearInterval(t); finish({url, ok: false, reason: 'timeout-render'}); }
      } catch (e) { clearInterval(t); finish({url, ok: false, reason: 'cross-origin:' + e.message}); }
    }, 500);
  };
  f.onerror = () => finish({url, ok: false, reason: 'iframe-error'});
  document.body.appendChild(f);
});

/**
 * Stash a payload for the receiver. window.name survives cross-origin
 * navigation; the clipboard and a localhost POST both fail here.
 */
window.__stash = (rows) => {
  window.name = JSON.stringify(rows).replace(
    /[-￿]/g,
    (c) => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'),
  );
  return {stashed: window.name.length, rows: rows.length};
};
