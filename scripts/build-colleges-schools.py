#!/usr/bin/env python3
"""Regenerate pages/academics/colleges-schools.html.

Sources
  briefs/colleges-schools-data.json   13 colleges / 203 programs (verbatim copy)
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Edit the JSON or the PAGE_CSS / PAGE_JS blocks below and re-run:
    python3 scripts/build-colleges-schools.py
Do not hand-edit the generated HTML - it is overwritten wholesale.
"""
import json, html, re, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

# Repo root = parent of this script's directory, so the generator is portable.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
DATA = os.path.join(REPO, 'briefs/colleges-schools-data.json')
OUT = os.path.join(REPO, 'pages/academics/colleges-schools.html')
DEPTH = _chrome.depth_of(OUT)   # pages/academics/ -> '../../'

tpl = open(TEMPLATE, encoding='utf-8').read().split('\n')
colleges = json.load(open(DATA, encoding='utf-8'))

def e(s):
    return html.escape(s, quote=True)

# ---------------------------------------------------------------- head
# Everything before TEMPLATE's closing </style> is the inlined critical.css
# block, copied verbatim (page-builder/CLAUDE.md: never trim it).
# Boundaries are located by content, NOT by line number — TEMPLATE.html grows
# whenever critical.css does, and hardcoded indices break silently on the next
# upstream edit.
crit_end = next(i for i, l in enumerate(tpl) if l.strip() == '</style>')
head_close = next(i for i, l in enumerate(tpl) if l.strip() == '</head>' and i > crit_end)
head_top = _chrome.with_robots('\n'.join(tpl[:crit_end]))
# </style> .. cdn.js, WITHOUT </head> — the shared chrome-CSS block is emitted
# after it (so it wins at equal specificity) and this file closes </head> itself.
head_tail_open = '\n'.join(tpl[crit_end:head_close])
assert 'cdn.js' in head_tail_open, 'TEMPLATE head is missing the cdn.js script tag'

head_top = head_top.replace(
    '<title>{{PAGE_TITLE}} — {{SITE_NAME}} | University of Maryland</title>',
    '<title>Colleges &amp; Schools — Undergraduate Admissions | University of Maryland</title>')
if '{{' in head_top:
    raise SystemExit('unreplaced placeholder in head: ' + re.findall(r'\{\{\w+\}\}', head_top)[0])

# ---------------------------------------------------------------- chrome
# Header, footer, chrome CSS and chrome scripts all come from shared/ via
# scripts/_chrome.py, emitted inside SHARED:<key> markers. scripts/build-chrome.py
# splices the identical blocks into hand-authored pages, so running either tool
# converges on the same bytes.
#
# The other shadow injections this project uses (pathway aspect ratio,
# banner-promo stacked actions) are driven by page CONTENT, and this page has
# neither element -- verified zero umd-element-pathway and zero
# umd-element-banner-promo in the markup below -- so they are not emitted here.

# ---------------------------------------------------------------- page CSS
PAGE_CSS = '''
    /* ============================================================
       25. COLLEGES & SCHOOLS — expandable card grid
       Page-built pattern (no DS equivalent). A responsive grid of
       bordered college tiles; activating a tile's toggle opens a
       full-width majors panel that JS relocates to sit after the
       LAST tile in that tile's grid row, so a row never breaks
       mid-way. Panel chrome borrows the accordion's red rule +
       light-gray body. Single-open, like an accordion group.
       ============================================================ */
    .cs-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 32px;
    }
    @media (min-width: 650px) {
      .cs-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (min-width: 1024px) {
      .cs-grid { grid-template-columns: repeat(3, 1fr); gap: 40px 32px; }
    }

    /* --- tile ------------------------------------------------- */
    .cs-tile {
      display: flex;
      flex-direction: column;
      background: var(--umd-color-white);
      border: 1px solid var(--umd-color-gray-light);
      transition: border-color .3s ease, box-shadow .3s ease;
    }
    .cs-tile:hover {
      border-color: var(--umd-color-gray-medium);
      box-shadow: 0 4px 16px rgba(0, 0, 0, .08);
    }
    .cs-tile[data-open="true"] {
      border-color: var(--umd-color-red);
      box-shadow: 0 4px 16px rgba(0, 0, 0, .10);
    }

    .cs-tile-figure {
      margin: 0;
      overflow: hidden;
      aspect-ratio: 2 / 1;
      background: var(--umd-color-gray-lightest);
    }
    .cs-tile-figure img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform .5s ease;
    }
    .cs-tile:hover .cs-tile-figure img { transform: scale(1.04); }

    /* Type scale mirrors the DS card-standard shadow DOM, measured directly
       from a live umd-element-card: eyebrow 12px/700, headline 18px/700
       (.umd-sans-larger-scaling), body 16px/400 #454545. The card's
       .umd-element-eyebrow lives in its shadow styles and ships in no CDN
       bundle, so the eyebrow is restated here rather than imported.

       Type classes resolve as follows in the LIVE bundle (measured at 1280px;
       the values in a locally downloaded typography.min.css disagree, so
       measure rather than read the file): smaller 14 / small 16 /
       medium 18 / large 18-bold / larger 22 / largest 44-bold. Hence
       .umd-sans-small for the 16px DS card body. */
    .cs-tile-body {
      display: flex;
      flex: 1 1 auto;
      flex-direction: column;
      padding: 24px;
    }
    .cs-tile-abbr {
      margin: 0 0 8px;
      color: var(--umd-color-red);
      font-size: 12px;
      font-weight: 700;
      line-height: 1.16em;
      letter-spacing: .05em;
      text-transform: uppercase;
    }
    .cs-tile-name { margin: 0; }
    .cs-tile-name a {
      color: var(--umd-color-black);
      text-decoration: none;
      background-image: linear-gradient(var(--umd-color-black), var(--umd-color-black));
      background-position: left calc(100% - 1px);
      background-repeat: no-repeat;
      background-size: 0 1px;
      transition: color .3s, background-size .3s, background-image .3s;
    }
    .cs-tile-name a:hover,
    .cs-tile-name a:focus {
      color: var(--umd-color-red);
      background-image: linear-gradient(var(--umd-color-red), var(--umd-color-red));
      background-size: 100% 1px;
    }
    /* Clamped on the tile; the panel carries the full text. */
    .cs-tile-desc {
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
      margin: 12px 0 0;
      color: var(--umd-color-gray-dark);
    }

    /* --- toggle ------------------------------------------------ */
    .cs-tile-foot { margin-top: auto; padding-top: 24px; }
    .cs-toggle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      width: 100%;
      margin: 0;
      padding: 14px 0 0;
      border: 0;
      border-top: 1px solid var(--umd-color-gray-light);
      background: none;
      color: var(--umd-color-black);
      font-weight: 700;
      text-align: left;
      cursor: pointer;
    }
    .cs-toggle:hover { color: var(--umd-color-red); }
    .cs-toggle:focus-visible {
      outline: 2px solid var(--umd-color-red);
      outline-offset: 4px;
    }
    .cs-toggle-chev {
      flex: 0 0 auto;
      width: 14px;
      height: 14px;
      fill: currentColor;
      transition: transform .3s ease;
    }
    .cs-tile[data-open="true"] .cs-toggle-chev { transform: rotate(180deg); }

    /* Letters & Sciences has no major list — plain link, no toggle. */
    .cs-tile-link {
      display: inline-block;
      padding-top: 14px;
      border-top: 1px solid var(--umd-color-gray-light);
      width: 100%;
      color: var(--umd-color-black);
      font-weight: 700;
      text-decoration: none;
    }
    .cs-tile-link:hover { color: var(--umd-color-red); }

    /* --- panel ------------------------------------------------- */
    .cs-panel { grid-column: 1 / -1; }
    .cs-panel[hidden] { display: none; }
    .cs-panel-inner {
      padding: 32px 24px;
      border: 1px solid var(--umd-color-gray-light);
      border-top: 4px solid var(--umd-color-red);
      background: var(--umd-color-gray-lightest);
      animation: cs-panel-in .35s ease both;
    }
    @media (min-width: 1024px) { .cs-panel-inner { padding: 40px; } }
    @keyframes cs-panel-in {
      from { opacity: 0; transform: translateY(-8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
      .cs-panel-inner { animation: none; }
    }

    .cs-panel-head {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px 32px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--umd-color-gray-light);
    }
    .cs-panel-headline { margin: 0; font-weight: 700; }
    /* Same treatment as .cs-tile-name above: no underline at rest, a
       red one wipes in left-to-right on hover/focus. The panel headline
       and the tile it expands from are the same link, so they animate
       identically — keep these two rules in sync. */
    .cs-panel-headline a {
      color: var(--umd-color-black);
      text-decoration: none;
      background-image: linear-gradient(var(--umd-color-black), var(--umd-color-black));
      background-position: left calc(100% - 1px);
      background-repeat: no-repeat;
      background-size: 0 1px;
      transition: color .3s, background-size .3s, background-image .3s;
    }
    .cs-panel-headline a:hover,
    .cs-panel-headline a:focus {
      color: var(--umd-color-red);
      background-image: linear-gradient(var(--umd-color-red), var(--umd-color-red));
      background-size: 100% 1px;
    }
    .cs-panel-head > div { flex: 1 1 480px; }
    /* Constrained measure — the panel spans the full 1600px lock, far too wide
       to read a paragraph across. 960px is the DS paragraph measure, lifted from
       element.min.css:
         :is(.umd-text-rich-advanced,.umd-rich-text) p,ul,ol,pre,blockquote
           { max-width: 960px }
       The value is restated rather than inherited by wrapping in .umd-rich-text,
       because that class also forces font-size:18px on its children and this
       paragraph is .umd-sans-small (16px). */
    .cs-panel-desc {
      max-width: 960px;
      margin: 12px 0 0;
      color: var(--umd-color-gray-dark);
    }
    .cs-panel-close {
      flex: 0 0 auto;
      padding: 8px 0;
      border: 0;
      background: none;
      color: var(--umd-color-gray-dark);
      font-weight: 700;
      letter-spacing: .06em;
      text-transform: uppercase;
      cursor: pointer;
    }
    .cs-panel-close:hover { color: var(--umd-color-red); }
    .cs-panel-close:focus-visible {
      outline: 2px solid var(--umd-color-red);
      outline-offset: 2px;
    }

    /* --- majors list ------------------------------------------- */
    .cs-majors {
      display: grid;
      grid-template-columns: 1fr;
      column-gap: 40px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    /* Caps at 3 columns. A 4th column narrows cells to ~274px at 1440px, which
       is under the ~323px a Major+Minor+Limited Enrollment Program pill trio
       needs; the group then wraps and that row runs 44px taller than its
       neighbours. 3 columns (~378px) fits the trio on one line — measured row
       heights 91/113 vs 91/131/135, and zero wrapped pill groups. */
    @media (min-width: 650px)  { .cs-majors { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1024px) { .cs-majors { grid-template-columns: repeat(3, 1fr); } }

    .cs-major {
      padding: 14px 0;
      border-bottom: 1px solid var(--umd-color-gray-light);
    }
    .cs-major a {
      color: var(--umd-color-black);
      font-weight: 700;
      text-decoration: none;
      background-image: linear-gradient(var(--umd-color-black), var(--umd-color-black));
      background-position: left calc(100% - 1px);
      background-repeat: no-repeat;
      background-size: 0 1px;
      transition: color .3s, background-size .3s, background-image .3s;
    }
    .cs-major a:hover,
    .cs-major a:focus {
      color: var(--umd-color-red);
      background-image: linear-gradient(var(--umd-color-red), var(--umd-color-red));
      background-size: 100% 1px;
    }
    /* Program-type labels use the DS pill geometry (.umd-text-cluster-pill: 12px,
       padding 8px 12px, #FAFAFA, 8px rhythm) with an added outline. Children
       are <span>, not <a> — the DS hover-yellow rule is scoped to a:hover, so
       spans stay inert and read as labels rather than controls. No per-type
       colour coding: Major/Minor/Certificate/LEP are peers, and colouring them
       implied a hierarchy that doesn't exist. */
    .cs-major-name { display: block; }
    /* Pills sit on their own line under the program name. Flex owns the 8px
       spacing in both axes, so the DS pill rhythm (wrapper margin-top:-8px +
       child margin-top:8px) is neutralised — left in place it double-counts
       against the flex gap and knocks the rows out of alignment. */
    .cs-types {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }
    .cs-types > .cs-type {
      margin-top: 0;
      border: 1px solid var(--umd-color-gray-light);
      color: var(--umd-color-gray-dark);
      white-space: nowrap;
    }
'''

# ---------------------------------------------------------------- tiles
CHEV = ('<svg class="cs-toggle-chev" viewBox="0 0 24 24" aria-hidden="true" '
        'xmlns="http://www.w3.org/2000/svg"><path d="M12 16.5 2.5 7l1.6-1.6L12 13.3l7.9-7.9L21.5 7z"/></svg>')

tiles, panels = [], []
for c in colleges:
    slug, n = c['slug'], len(c['majors'])
    label = f'View {n} program{"s" if n != 1 else ""}'
    if n:
        foot = (f'        <button type="button" class="cs-toggle umd-interactive-sans-small"\n'
                f'                data-college="{slug}" aria-expanded="false" aria-controls="cs-panel-{slug}">\n'
                f'          <span>{label}</span>\n'
                f'          {CHEV}\n'
                f'        </button>')
    else:
        foot = (f'        <a class="cs-tile-link umd-interactive-sans-small" href="{e(c["url"])}"\n'
                f'           target="_blank" rel="noopener">Visit {e(c["name"])}</a>')

    tiles.append(f'''        <article class="cs-tile" id="cs-tile-{slug}" data-college="{slug}" data-open="false">
          <figure class="cs-tile-figure">
            <img src="{e(c['image'])}" alt="{e(c['alt'])}" loading="lazy" width="880" height="440" />
          </figure>
          <div class="cs-tile-body">
            <p class="cs-tile-abbr">{e(c['abbr'])}</p>
            <h3 class="cs-tile-name umd-sans-large">
              <a href="{e(c['url'])}" target="_blank" rel="noopener">{e(c['name'])}</a>
            </h3>
            <p class="cs-tile-desc umd-sans-small">{e(c['desc'])}</p>
            <div class="cs-tile-foot">
{foot}
            </div>
          </div>
        </article>''')

    if not n:
        continue

    items = []
    for m in c['majors']:
        types = ''.join(f'<span class="cs-type">{e(t)}</span>' for t in m['types'])
        name = e(m['name'])
        link = (f'<a href="{e(m["url"])}" target="_blank" rel="noopener">{name}</a>'
                if m['url'] else name)
        items.append(f'            <li class="cs-major">\n'
                     f'              <span class="cs-major-name umd-sans-small">{link}</span>\n'
                     f'              <span class="cs-types umd-text-cluster-pill">{types}</span>\n'
                     f'            </li>')
    items = '\n'.join(items)

    panels.append(f'''        <section class="cs-panel" id="cs-panel-{slug}" data-college="{slug}"
                 role="region" aria-labelledby="cs-panel-{slug}-h" hidden>
          <div class="cs-panel-inner">
            <div class="cs-panel-head">
              <div>
                <h3 class="cs-panel-headline umd-sans-larger" id="cs-panel-{slug}-h" tabindex="-1">
                  <a href="{e(c['url'])}" target="_blank" rel="noopener">{e(c['name'])}</a>
                </h3>
                <p class="cs-panel-desc umd-sans-small">{e(c['desc'])}</p>
              </div>
              <button type="button" class="cs-panel-close umd-sans-min" data-close="{slug}">Close</button>
            </div>
            <ul class="cs-majors">
{items}
            </ul>
          </div>
        </section>''')

tiles_html = '\n\n'.join(tiles)
panels_html = '\n\n'.join(panels)
total = sum(len(c['majors']) for c in colleges)

# ---------------------------------------------------------------- page JS
PAGE_JS = '''  <!-- ============================================================
       COLLEGES & SCHOOLS — expandable card grid
       Single-open accordion behaviour. The open panel is moved to
       sit immediately after the LAST tile of the clicked tile's
       grid row, so the row never breaks part-way through. Closed
       panels are parked at the end of the grid where their
       display:none keeps them out of grid flow entirely.
  ============================================================ -->
  <script>
  (function () {
    var grid = document.getElementById('cs-grid');
    if (!grid) return;

    var tiles = Array.prototype.slice.call(grid.querySelectorAll('.cs-tile'));
    var panels = {};
    Array.prototype.forEach.call(grid.querySelectorAll('.cs-panel'), function (p) {
      panels[p.getAttribute('data-college')] = p;
      grid.appendChild(p);            // park every panel at the end
    });
    var openId = null;

    function columnCount() {
      var t = window.getComputedStyle(grid).getPropertyValue('grid-template-columns');
      var n = t ? t.split(' ').filter(Boolean).length : 1;
      return n > 0 ? n : 1;
    }

    // Move the panel so it follows the last tile in its own row.
    function placePanel(id) {
      var tile = document.getElementById('cs-tile-' + id);
      var idx = tiles.indexOf(tile);
      if (idx < 0) return;
      var cols = columnCount();
      var rowEnd = Math.min(Math.ceil((idx + 1) / cols) * cols - 1, tiles.length - 1);
      var anchor = tiles[rowEnd];
      if (anchor.nextElementSibling !== panels[id]) {
        anchor.insertAdjacentElement('afterend', panels[id]);
      }
    }

    function setToggle(id, expanded) {
      var btn = grid.querySelector('.cs-toggle[data-college="' + id + '"]');
      if (btn) btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      var tile = document.getElementById('cs-tile-' + id);
      if (tile) tile.setAttribute('data-open', expanded ? 'true' : 'false');
    }

    function close(id) {
      if (!id || !panels[id]) return;
      panels[id].hidden = true;
      grid.appendChild(panels[id]);   // park it again
      setToggle(id, false);
      if (openId === id) openId = null;
    }

    function open(id, focus) {
      if (!panels[id]) return;
      if (openId && openId !== id) close(openId);
      placePanel(id);
      panels[id].hidden = false;
      setToggle(id, true);
      openId = id;
      if (focus) {
        var h = document.getElementById('cs-panel-' + id + '-h');
        if (h) h.focus({ preventScroll: true });
        panels[id].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }

    grid.addEventListener('click', function (ev) {
      var toggle = ev.target.closest('.cs-toggle');
      if (toggle) {
        var id = toggle.getAttribute('data-college');
        if (openId === id) {
          close(id);
          toggle.focus();
        } else {
          open(id, true);
        }
        return;
      }
      var closer = ev.target.closest('.cs-panel-close');
      if (closer) {
        var cid = closer.getAttribute('data-close');
        close(cid);
        var btn = grid.querySelector('.cs-toggle[data-college="' + cid + '"]');
        if (btn) {
          btn.focus();
          btn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    });

    grid.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && openId) {
        var btn = grid.querySelector('.cs-toggle[data-college="' + openId + '"]');
        close(openId);
        if (btn) btn.focus();
      }
    });

    // Column count changes with the breakpoint — re-anchor the open panel.
    // Driven by matchMedia, which fires reliably even where requestAnimationFrame
    // is throttled (backgrounded / offscreen tabs). A debounced resize listener
    // is the fallback for reflows that don't cross a breakpoint.
    function reanchor() { if (openId) placePanel(openId); }

    ['(min-width: 650px)', '(min-width: 1024px)'].forEach(function (q) {
      var mq = window.matchMedia(q);
      if (mq.addEventListener) mq.addEventListener('change', reanchor);
      else if (mq.addListener) mq.addListener(reanchor);   // Safari < 14
    });

    var resizeTimer = null;
    window.addEventListener('resize', function () {
      if (!openId) return;
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(reanchor, 150);
    });

    // Deep link: /colleges-schools.html#agnr opens that college.
    function fromHash() {
      var id = (window.location.hash || '').replace('#', '');
      if (id && panels[id]) open(id, true);
    }
    window.addEventListener('hashchange', fromHash);
    fromHash();
  })();
  </script>'''

# ---------------------------------------------------------------- assemble
page = f'''{head_top}
{PAGE_CSS}{head_tail_open}
{_chrome.block('chrome-css', OUT)}
{_chrome.block('gate', OUT)}
</head>
<body>

{_chrome.block('header', OUT)}

  <!-- 3. HERO — small background, left-aligned text + CTA.
       Same recipe as pages/academics/programs.html. -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small">
      <img slot="image" src="../../images/colleges-schools/hero-sundial.jpg" alt="Sundial on McKeldin Mall" />
      <h1 slot="headline">Colleges &amp; Schools</h1>
      <div slot="text"><p>Within the University of Maryland&#8217;s 12 colleges &amp; schools, you can choose from more than 100 majors. No matter your interests, we have you covered.</p></div>
      <div slot="actions">
        <umd-element-call-to-action data-display="primary">
          <a href="programs.html">Explore All Programs</a>
        </umd-element-call-to-action>
      </div>
    </umd-element-hero>
  </section>

  <!-- 4. INTRO — mirrors the rich-text lockup at the top of the sibling
       landing pages (pages/academics/index.html "study here"): narrow centred
       -small lock, rule, lead paragraph, rich-text body. The sibling's
       lead is uppercase; here it is not, per design direction. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black">Discover which of our colleges and schools inspire your fearless ideas and review their list of majors to learn more about academics at UMD.</p>
      <div class="umd-text-rich-advanced">
        <p>Our colleges and schools are researching hot topics such as alternative energy, advising federal officials on homeland security, working with the state to reduce children&#8217;s obesity and investigating many other pressing issues. You can work side-by-side with faculty at the top of their fields: Pulitzer Prize recipients, Nobel laureates, and Emmy and Tony winners. Numbering more than 4,000, our faculty also include world-renowned performers, successful entrepreneurs and big-name journalists, all ready to share their experiences and expertise with you.</p>
      </div>
    </div>
  </section>

  <!-- 5. COLLEGES & SCHOOLS — {len(colleges)} tiles / {total} programs -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <div class="cs-grid" id="cs-grid" data-animation="off">

{tiles_html}

{panels_html}

      </div>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right (pin lives in shared/chrome.css) -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

{_chrome.block('footer', OUT)}

{_chrome.block('chrome-scripts', OUT)}

  <!-- Canonical grid-entry animations (page-builder/CLAUDE.md: never inline). -->
  <script src="../../page-builder/scripts/grid-animations.js"></script>

{PAGE_JS}

</body>
</html>
'''

# Image paths in colleges-schools-data.json are repo-root-relative behind
# {{ROOT}}, like the chrome's; resolve them for this page's depth.
page = page.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)

open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(page.split(chr(10))), 'lines')
print('colleges', len(colleges), 'programs', total)
