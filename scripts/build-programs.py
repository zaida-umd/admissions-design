#!/usr/bin/env python3
"""Regenerate pages/academics/programs.html.

Sources
  briefs/programs-data.json           203 programs, as harvested from the
                                      admissions Craft GraphQL endpoint
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Everything else -- the page-specific <style> blocks, the hero, the filter rail
and A-Z directory markup, the pathway/banner-promo shadow injections, and the
filter JS -- is the BODY literal below, because this page is their only source.

Run after editing briefs/programs-data.json, shared/, or the BODY literal:
    python3 scripts/build-programs.py
Do not hand-edit the generated HTML - it is overwritten wholesale.

BODY is a RAW string: it carries CSS/JS backslash escapes (\\2212, \\u201c)
that Python would otherwise reinterpret, corrupting the output silently.
"""
import json, os, re, sys
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
DATA     = os.path.join(REPO, 'briefs/programs-data.json')
OUT      = os.path.join(REPO, 'pages/academics/programs.html')
DEPTH    = _chrome.depth_of(OUT)   # pages/academics/ -> '../../'

TITLE = 'Explore Our Programs \u2014 Undergraduate Admissions | University of Maryland'

# ---------------------------------------------------------------- head
# Everything before TEMPLATE's closing </style> is the inlined critical.css
# block, copied verbatim (page-builder/CLAUDE.md: never trim it). Located by
# content, not line number -- TEMPLATE grows whenever critical.css does.
tpl = open(TEMPLATE, encoding='utf-8').read().split('\n')
crit_end = next(i for i, l in enumerate(tpl) if l.strip() == '</style>')
head = _chrome.with_robots('\n'.join(tpl[:crit_end]))
head = re.sub(r'<title>.*?</title>', '<title>' + TITLE + '</title>', head, count=1)
assert '{{' not in head, 'unreplaced placeholder in TEMPLATE head'
# The cdn.js pin below lives in BODY, not in the TEMPLATE-derived head, so it can
# drift when the submodule bumps. Fail loudly instead of silently emitting a page
# on a different component version than every hand-written page.
_tpl_pin = re.search(r'web-components-library@([\d.]+)/dist/cdn\.js',
                     open(TEMPLATE, encoding='utf-8').read())

# ---------------------------------------------------------------- data
# The inline PROGRAMS array is a compacted projection of the raw GraphQL
# response: short keys, descriptions reduced to plain text. The three
# description steps are ORDER-SENSITIVE -- strip tags, THEN unescape entities,
# THEN collapse whitespace. Any other order changes the bytes (a stray double
# space where a tag was removed, or "&amp;" surviving as-is).
raw = json.load(open(DATA, encoding='utf-8'))['data']['programsEntries']

def plain(desc):
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', '', desc or ''))).strip()

records = [{
    'n': r['title'],
    'u': r['titleLink'],
    't': [x['title'] for x in r['types']],
    'c': [x['title'] for x in r['colleges']],
    'i': [x['title'] for x in r['interests']],
    'l': [x['title'] for x in r.get('locations') or []],
    'd': plain(r['description']),
} for r in raw]

# Compact separators keep the inlined array near 129KB instead of 132KB.
programs_json = json.dumps(records, ensure_ascii=False, separators=(',', ':'))

# ---------------------------------------------------------------- body
BODY = r'''  </style>

  <script src="https://unpkg.com/@universityofmaryland/web-components-library@2.0.0/dist/cdn.js"></script>

  <style>
    /* Brand chevron animation flanking the Study Here rich text and
       overlapping ~120px up into the hero above. Hidden below tablet
       to avoid crowding the single-column stacked content. */
    .umd-admissions-study-here-section {
      position: relative;
      overflow: visible;
      z-index: 100;
    }

    .umd-admissions-study-here-content {
      position: relative;
      z-index: 2;
    }

    /* The brand-logo-animation hardcodes its inner container to
       width:100vw, height:50vw and anchors chevrons to right:0. So
       the host must span full width — sizing/clipping won't work. */
    .umd-admissions-study-here-chevron {
      position: absolute;
      top: -180px;
      left: 0;
      right: 0;
      bottom: -80px;
      pointer-events: none;
      z-index: 1;
      overflow: visible;
    }

    .umd-admissions-study-here-chevron > umd-element-brand-logo-animation {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      display: block;
    }

    @media (max-width: 1023px) {
      .umd-admissions-study-here-chevron { display: none; }
    }
  </style>
  <!-- Programs explorer — page-specific styles -->
  <style>
    /* No page colour variables — every colour is a DS token from
       tokens.min.css. A local `--umd-red: #e21833` alias used to sit here;
       it was a hand-rolled duplicate of --umd-color-red and is gone. */

    /* two-column layout: filter rail + results */
    .umd-admissions-filter-layout { display:block; }

    @media (min-width:1020px) {
      .umd-admissions-filter-layout { display:flex; align-items:flex-start; gap:64px; }
      /* deliberately NOT sticky: a pinned rail has to cap its own height, and
         that nested scroller (plus the per-group ones) meant up to three
         scrollbars on one screen. The rail scrolls with the page instead. */
      .umd-admissions-filter-sidebar { width:30%; min-width:260px; max-width:360px; }
    }

    .umd-admissions-filter-results { flex:1; min-width:0; }

    /* mobile filter toggle */
    .umd-admissions-filter-mobile-toggle {
      display:flex; justify-content:space-between; align-items:center; gap:16px;
      width:100%; padding:14px 16px; margin-bottom:16px; cursor:pointer;
      background:var(--umd-color-black); color:var(--umd-color-white); border:0; font-weight:700;
    }

    .umd-admissions-filter-mobile-toggle::after { content:"+"; font-size:22px; line-height:1; }

    .umd-admissions-filter-mobile-toggle[aria-expanded="true"]::after { content:"\2212"; }

    @media (min-width:1020px) { .umd-admissions-filter-mobile-toggle { display:none; } }

    #pf-form { display:block; }

    @media (max-width:1019px) {
      #pf-form { display:none; }
      #pf-form[data-open] { display:block; }
    }

    /* search bar — lifted from the experts page (input + red square submit) */
    .umd-admissions-filter-search-bar { margin:0 0 32px; }

    .umd-admissions-filter-search-row { display:flex; gap:8px; align-items:center; }

    .umd-admissions-filter-search-row input {
      flex:1 1 auto; min-width:0; height:48px; padding:12px 16px;
      border:1px solid var(--umd-color-gray-light); border-radius:0; background:var(--umd-color-white);
      font:inherit; font-size:16px; -webkit-appearance:none; appearance:none;
    }

    .umd-admissions-filter-search-row input:focus-visible { outline:2px solid var(--umd-color-red); outline-offset:1px; border-color:var(--umd-color-red); }

    .umd-admissions-filter-search-submit {
      flex:0 0 auto; width:48px; height:48px; border:0; border-radius:0; cursor:pointer;
      background:var(--umd-color-red); display:flex; align-items:center; justify-content:center;
      transition:background-color .5s;
    }

    .umd-admissions-filter-search-submit:hover, .umd-admissions-filter-search-submit:focus-visible { background:var(--umd-color-red-dark); }

    .umd-admissions-filter-search-submit svg { width:20px; height:20px; fill:var(--umd-color-white); }

    /* accordion filter groups (adapted from the experts REFINE rail) */
    .umd-admissions-filter-group { border-bottom:1px solid var(--umd-color-black); margin-bottom:24px; padding-bottom:24px; }

    .umd-admissions-filter-group:last-of-type { border-bottom:0; }

    .umd-admissions-filter-group > button {
      display:flex; position:relative; justify-content:space-between; align-items:center;
      gap:16px; width:100%; padding:0 24px 0 0; background:none; border:0; cursor:pointer;
      font:inherit; font-weight:700; font-size:18px; text-align:left; color:var(--umd-color-black);
      transition:color .3s;
    }

    .umd-admissions-filter-group > button:hover, .umd-admissions-filter-group > button:focus-visible { color:var(--umd-color-red); }

    .umd-admissions-filter-group > button::before, .umd-admissions-filter-group > button::after {
      content:""; position:absolute; top:calc(50% - 1px); right:0;
      width:12px; height:2px; background:currentColor; transition:transform .3s;
    }

    .umd-admissions-filter-group > button::after { transform:rotate(90deg); }

    .umd-admissions-filter-group[data-open] > button::after { transform:rotate(0); }

    .umd-admissions-filter-group-body { display:grid; grid-template-rows:0fr; transition:grid-template-rows .3s ease; }

    .umd-admissions-filter-group[data-open] .umd-admissions-filter-group-body { grid-template-rows:1fr; }

    .umd-admissions-filter-group-body > div { min-height:0; overflow:hidden; }

    .umd-admissions-filter-group-body fieldset {
      border:0; margin:0; padding:18px 0 2px; display:flex; flex-direction:column; gap:14px;
    }

    /* groups longer than PF_SHOW_LIMIT hide the tail behind a "Show all" toggle
       rather than a nested scrollbar (see buildGroups) */
    .umd-admissions-filter-group-body fieldset[data-collapsed] .umd-admissions-filter-option-extra { display:none; }

    /* the toggle reuses the DS .umd-text-cluster-pill chip, same as the active-filter
       pills above; neutralize its wrapping-margin hack and set our own offset. */
    .umd-admissions-filter-show-all-cluster.umd-text-cluster-pill { display:inline-flex; margin-top:8px; }

    .umd-admissions-filter-show-all-cluster.umd-text-cluster-pill > .umd-admissions-filter-show-all { margin-top:0; border:0; cursor:pointer; color:var(--umd-color-black); }

    .umd-admissions-filter-show-all-cluster.umd-text-cluster-pill > .umd-admissions-filter-show-all:hover,
    .umd-admissions-filter-show-all-cluster.umd-text-cluster-pill > .umd-admissions-filter-show-all:focus-visible { background-color:var(--umd-color-gold); }

    /* option rows use the DS .umd-field-checkbox-wrapper (font-weight:400 — the
       DS-native counter to the global label{font-weight:700}

    rule) so only the
       group header stays bold. */
    .umd-admissions-filter-group-body .umd-field-checkbox-wrapper { align-items:flex-start; gap:12px; margin-bottom:0; line-height:1.3; }

    .umd-admissions-filter-group-body input[type="checkbox"] { margin:.15em 0 0; width:18px; height:18px; accent-color:var(--umd-color-red); flex:0 0 auto; }

    .umd-admissions-filter-count { color:var(--umd-color-gray-medium-a-a); font-variant-numeric:tabular-nums; }

    .umd-admissions-filter-actions { margin-top:24px; }

    /* A–Z quick-nav (umd-campaign-extrasmall provides the italic Barlow face) */
    .umd-admissions-alphabet-nav { display:flex; flex-wrap:wrap; gap:6px 18px; margin:0 0 40px; padding-bottom:24px; border-bottom:2px solid var(--umd-color-red); }

    .umd-admissions-alphabet-nav a { color:var(--umd-color-red); text-decoration:none; line-height:1; transition:opacity .2s; }

    .umd-admissions-alphabet-nav a:hover, .umd-admissions-alphabet-nav a:focus-visible { text-decoration:underline; }

    .umd-admissions-alphabet-nav .umd-admissions-alphabet-letter-empty { color:var(--umd-color-gray-medium); opacity:.5; line-height:1; pointer-events:none; }

    /* active-filter pills */
    .umd-admissions-filter-pills { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:24px; }

    .umd-admissions-filter-pills-label { font-weight:700; margin-right:4px; }

    /* active-filter pills use the DS .umd-text-cluster-pill chip (#FAFAFA, 12px);
       neutralize its wrapping-margin hack and use flex gap instead. */
    .umd-admissions-filter-pill-cluster.umd-text-cluster-pill { margin-top:0; display:inline-flex; flex-wrap:wrap; gap:8px; }

    .umd-admissions-filter-pills .umd-text-cluster-pill > * { margin-top:0; border:0; cursor:pointer; color:var(--umd-color-black); }

    .umd-admissions-filter-pills .umd-text-cluster-pill > button:hover,
    .umd-admissions-filter-pills .umd-text-cluster-pill > button:focus-visible { background-color:var(--umd-color-gold); }

    .umd-admissions-filter-clear {
      background:none; border:0; padding:0 0 0 6px; cursor:pointer; color:var(--umd-color-black);
      text-decoration:underline; text-underline-offset:.15em;
    }

    .umd-admissions-filter-clear:hover { color:var(--umd-color-red); }

    .umd-admissions-filter-count-line { margin:0 0 24px; }

    .umd-admissions-filter-empty { font-size:18px; }

    /* letter sections + rows */
    .umd-admissions-alphabet-section { scroll-margin-top:120px; margin-bottom:40px; }

    .umd-admissions-alphabet-letter { color:var(--umd-color-red); margin:0 0 8px; }

    @media (min-width:1024px) { .umd-admissions-alphabet-letter { margin-bottom:24px; } }

    .umd-admissions-program-row { display:block; }

    .umd-admissions-program-row + .umd-admissions-program-row { margin-top:0; }
  </style>

@@CHROME:chrome-css@@
@@CHROME:gate@@
</head>
<body>

  <!-- 1. GLOBAL UNIVERSITY HEADER -->
@@CHROME:header@@

  <!-- 3. HERO — small background -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small">
      <img slot="image" src="../../images/academics/students-walking.jpg" alt="Students walking on the University of Maryland campus" />
      <p slot="eyebrow">Academics</p>
      <h1 slot="headline">Explore Our Programs</h1>
      <div slot="text"><p>With over 100 undergraduate majors across 12 colleges and schools, we have you covered.</p></div>
      <div slot="actions">
        <umd-element-call-to-action data-display="primary">
          <a href="colleges-schools.html">Explore Colleges &amp; Schools</a>
        </umd-element-call-to-action>
      </div>
    </umd-element-hero>
  </section>

  <!-- 4. PROGRAMS EXPLORER — experts-style faceted filter + A–Z directory -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <div class="umd-admissions-filter-layout">

        <!-- FILTER RAIL -->
        <aside class="umd-admissions-filter-sidebar" aria-label="Filter programs">
          <button type="button" id="umd-admissions-filter-mobile-toggle" class="umd-admissions-filter-mobile-toggle" aria-expanded="false" aria-controls="pf-form">
            <span>Filter programs</span>
          </button>
          <form id="pf-form">
            <h2 class="umd-tailwing-right-headline"><span>REFINE</span></h2>
            <div id="pf-groups"></div>
            <div class="umd-admissions-filter-actions">
              <umd-element-call-to-action data-display="outline">
                <button type="button" id="pf-reset">Reset filters</button>
              </umd-element-call-to-action>
            </div>
          </form>
        </aside>

        <!-- RESULTS -->
        <div class="umd-admissions-filter-results">
          <nav class="umd-admissions-alphabet-nav umd-campaign-extrasmall" id="umd-admissions-alphabet-nav" aria-label="Jump to programs by letter"></nav>

          <!-- search bar (styled after the umdrightnow.umd.edu/experts search:
               DS highlight card = gray bg + red left rule) -->
          <form id="umd-admissions-filter-search-bar" class="umd-admissions-filter-search-bar umd-layout-background-highlight-light" role="search" action="#">
            <label class="sr-only" for="pf-q">Search programs</label>
            <div class="umd-admissions-filter-search-row">
              <input type="search" id="pf-q" name="q" placeholder="Search programs" autocomplete="off" />
              <button type="submit" class="umd-admissions-filter-search-submit" aria-label="Submit search">
                <svg viewBox="0 0 96 96" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M79.3401 42.2306C79.3401 54.1438 69.6826 63.8013 57.7694 63.8013C45.8562 63.8013 36.1987 54.1438 36.1987 42.2306C36.1987 30.3174 45.8562 20.6599 57.7694 20.6599C69.6826 20.6599 79.3401 30.3174 79.3401 42.2306ZM91 42.2306C91 60.5833 76.1222 75.4612 57.7694 75.4612C51.3447 75.4612 45.3458 73.6379 40.2619 70.4806L24.2216 86.5209H5L30.2245 60.8255C26.6351 55.5189 24.5388 49.1195 24.5388 42.2306C24.5388 23.8778 39.4167 9 57.7694 9C76.1222 9 91 23.8778 91 42.2306Z"></path></svg>
              </button>
            </div>
          </form>

          <div class="umd-admissions-filter-pills" id="umd-admissions-filter-pills" hidden></div>
          <p class="umd-admissions-filter-count-line umd-sans-smaller" id="umd-admissions-filter-count" role="status" aria-live="polite"></p>
          <div id="pf-list"></div>
          <p id="umd-admissions-filter-empty" class="umd-admissions-filter-empty" hidden>No programs match your filters. Try removing a filter.</p>
        </div>

      </div>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

  <!-- 13. FOOTER — visual (uses default specially-formatted footer image) -->
@@CHROME:footer@@

  <!-- ============================================================
       SHADOW OVERRIDES
  ============================================================ -->
  <script>
    // umd-element-pathway — force 1:1 image aspect ratio.
    // No CSS variable / ::part hook for the pathway image container; inject
    // shadow CSS to override intrinsic image ratio.
    customElements.whenDefined('umd-element-pathway').then(() => {
      document.querySelectorAll('umd-element-pathway').forEach(el => {
        const style = document.createElement('style');
        style.textContent = '.pathway-image-container,.image-container,.umd-asset-image-wrapper-scaled{aspect-ratio:6/5!important;height:auto!important}.pathway-image-container img,.image-container img,.umd-asset-image-wrapper-scaled img{width:100%!important;height:100%!important;object-fit:cover!important}';
        el.shadowRoot && el.shadowRoot.appendChild(style);
      });
    });

    // GRID ENTRY ANIMATIONS — auto-applied to layout grids. Mirrors the
    // upstream observeGridAnimations() logic but expands the selector
    // set to all umd-layout-grid-* containers so authors don't need to
    // add umd-animation-grid manually. (This block is also in
    // page-builder/TEMPLATE.html — every new page gets it for free.)
    (function () {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      var GRID_SELECTORS = [
        '.umd-layout-grid-gap-two',
        '.umd-layout-grid-gap-three',
        '.umd-layout-grid-gap-stacked',
        '.umd-layout-grid-columns-four',
        '.umd-layout-grid-masonry',
        '.umd-layout-grid-inline-tablet-rows',
        '.umd-animation-grid',
        '.umd-grid-animation'
      ].join(',');
      var FADE_CLASS = 'umd-animation-transition-fade-bottom';
      var OFFSET_ATTR = 'data-animation';

      var style = document.createElement('style');
      style.textContent =
        '@keyframes fade-in-from-bottom{from{opacity:0;transform:translateY(50px)}to{opacity:1;transform:translateY(0)}}' +
        '@media (prefers-reduced-motion: no-preference){' +
          ':where(' + GRID_SELECTORS + ') > *{opacity:0;transform:translateY(50px)}' +
          '.' + FADE_CLASS + '{animation:fade-in-from-bottom 1s forwards;opacity:0;transform:translateY(50px)}' +
        '}';
      document.head.appendChild(style);

      function init() {
        var children = [];
        document.querySelectorAll(GRID_SELECTORS).forEach(function (grid) {
          Array.prototype.push.apply(children, grid.children);
        });
        if (!children.length) return;

        function setRowOffsets() {
          var prevTop = null;
          children.forEach(function (el) {
            var top = el.getBoundingClientRect().top;
            if (prevTop !== null && Math.abs(top - prevTop) < 1) {
              el.setAttribute(OFFSET_ATTR, 'offset');
            } else {
              el.removeAttribute(OFFSET_ATTR);
              prevTop = top;
            }
          });
        }

        var observer = new IntersectionObserver(function (entries) {
          var delay = 0;
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            if (el.getAttribute(OFFSET_ATTR) === 'offset') {
              delay += 350;
            } else {
              delay = 0;
            }
            el.style.animationDelay = delay + 'ms';
            el.classList.add(FADE_CLASS);
            observer.unobserve(el);
          });
        }, { rootMargin: '0px', threshold: [0.35] });

        children.forEach(function (el) { observer.observe(el); });
        setRowOffsets();
        window.addEventListener('resize', setRowOffsets);
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
      } else {
        init();
      }
    })();
  </script>

  <!-- Programs explorer data + client-side filter logic -->
  <script>
  (function () {
    var PROGRAMS = @@PROGRAMS@@;
    var FACETS   = {"type":[{"title":"Major","count":104},{"title":"Minor","count":104},{"title":"Limited Enrollment Program","count":26},{"title":"Pre-Professional Program","count":13},{"title":"Certificate","count":8}],"college":[{"title":"A. James Clark School of Engineering (ENGR)","count":20},{"title":"College of Agriculture & Natural Resources (AGNR)","count":17},{"title":"College of Arts & Humanities (ARHU)","count":59},{"title":"College of Behavioral & Social Sciences (BSOS)","count":20},{"title":"College of Computer, Mathematical, & Natural Sciences (CMNS)","count":31},{"title":"College of Education (EDUC)","count":16},{"title":"College of Information (INFO)","count":6},{"title":"Philip Merrill College of Journalism (JOUR)","count":1},{"title":"Robert H. Smith School of Business (BMGT)","count":12},{"title":"School of Architecture, Planning & Preservation (ARCH)","count":7},{"title":"School of Public Health (SPH)","count":8},{"title":"School of Public Policy (SPP)","count":6}],"interest":[{"title":"Art & Performance","count":18},{"title":"Business & Entrepreneurship","count":41},{"title":"Communication & Literature","count":42},{"title":"Cultures & Languages","count":67},{"title":"Data & Analysis","count":55},{"title":"Design & Planning","count":26},{"title":"Education & Human Development","count":31},{"title":"Engineering & Technology","count":34},{"title":"Environment & Natural Resources","count":41},{"title":"Health & Wellness","count":33},{"title":"Human Behavior & Social Thought","count":29},{"title":"Natural & Physical Sciences","count":59},{"title":"Plants & Animals","count":13},{"title":"Policy & Social Justice","count":46}],"location":[{"title":"Shady Grove","count":12},{"title":"College Park","count":5}]};
    var ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    var GROUP_LABELS = { type:'Program Types', college:'Colleges & Schools', interest:'Interests', location:'Locations' };
    var GROUP_ORDER  = ['type', 'college', 'interest', 'location'];

    var form      = document.getElementById('pf-form');
    var qInput    = document.getElementById('pf-q');
    var groupsHost= document.getElementById('pf-groups');
    var listHost  = document.getElementById('pf-list');
    var emptyEl   = document.getElementById('umd-admissions-filter-empty');
    var countEl   = document.getElementById('umd-admissions-filter-count');
    var pillsHost = document.getElementById('umd-admissions-filter-pills');
    var navEl     = document.getElementById('umd-admissions-alphabet-nav');

    function esc(s) {
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function letterOf(p) { return p.n.charAt(0).toUpperCase(); }

    // options shown before a group collapses behind its "Show all" toggle
    var PF_SHOW_LIMIT = 7;

    var state = { q:'', type:[], college:[], interest:[], location:[] };

    // ---- build checkbox filter groups ----
    function buildGroups() {
      groupsHost.innerHTML = GROUP_ORDER.map(function (key, idx) {
        var opts = FACETS[key] || [];
        var long = opts.length > PF_SHOW_LIMIT;
        var rows = opts.map(function (o, i) {
          return '<label class="umd-field-checkbox-wrapper' +
            (long && i >= PF_SHOW_LIMIT ? ' umd-admissions-filter-option-extra' : '') +
            '"><input type="checkbox" data-group="' + key +
            '" value="' + esc(o.title) + '"><span>' + esc(o.title) +
            ' <span class="umd-admissions-filter-count umd-sans-smaller">(' + o.count + ')</span></span></label>';
        }).join('');
        var more = long
          ? '<span class="umd-text-cluster-pill umd-admissions-filter-show-all-cluster">' +
            '<button type="button" class="umd-admissions-filter-show-all" aria-expanded="false" aria-controls="pf-set-' + key + '">' +
            'Show all ' + opts.length + '</button></span>'
          : '';
        var open = idx === 0;
        return '<div class="umd-admissions-filter-group"' + (open ? ' data-open' : '') + ' data-group="' + key + '">' +
          '<button type="button" aria-expanded="' + open + '" aria-controls="pf-body-' + key + '">' +
          '<span>' + GROUP_LABELS[key] + '</span></button>' +
          '<div class="umd-admissions-filter-group-body" id="pf-body-' + key + '"><div>' +
          '<fieldset id="pf-set-' + key + '"' + (long ? ' data-collapsed' : '') + '>' +
          rows + '</fieldset>' + more + '</div></div></div>';
      }).join('');
    }

    // ---- collect state from the DOM ----
    function collect() {
      state.q = qInput.value.trim().toLowerCase();
      state.type = []; state.college = []; state.interest = []; state.location = [];
      form.querySelectorAll('input[type="checkbox"]:checked').forEach(function (cb) {
        state[cb.getAttribute('data-group')].push(cb.value);
      });
    }

    // ---- match a program against active filters (AND across groups, OR within) ----
    function match(p) {
      if (state.q && p.n.toLowerCase().indexOf(state.q) === -1) return false;
      if (state.type.length && !p.t.some(function (t) { return state.type.indexOf(t) > -1; })) return false;
      if (state.college.length && !p.c.some(function (c) { return state.college.indexOf(c) > -1; })) return false;
      if (state.interest.length && !p.i.some(function (i) { return state.interest.indexOf(i) > -1; })) return false;
      if (state.location.length && !p.l.some(function (l) { return state.location.indexOf(l) > -1; })) return false;
      return true;
    }

    function cardHTML(p) {
      var text = p.d ? '<p slot="text">' + esc(p.d) + '</p>' : '';
      var types = p.t.length ? '<p slot="date">' + esc(p.t.join(' | ')) + '</p>' : '';
      return '<umd-element-card data-display="list" class="umd-admissions-program-row">' +
        '<h3 slot="headline"><a href="' + esc(p.u) + '">' + esc(p.n) + '</a></h3>' +
        text + types + '</umd-element-card>';
    }

    function render() {
      var matched = PROGRAMS.filter(match);
      var byLetter = {};
      matched.forEach(function (p) {
        var L = letterOf(p);
        (byLetter[L] = byLetter[L] || []).push(p);
      });

      // alphabet nav — active letters link+scroll, empty letters dimmed
      navEl.innerHTML = ALPHA.map(function (L) {
        return byLetter[L]
          ? '<a href="#letter-' + L + '" data-letter="' + L + '">' + L + '</a>'
          : '<span class="umd-admissions-alphabet-letter-empty" aria-hidden="true">' + L + '</span>';
      }).join('');

      // results
      if (!matched.length) {
        listHost.innerHTML = '';
        emptyEl.hidden = false;
      } else {
        emptyEl.hidden = true;
        listHost.innerHTML = ALPHA.filter(function (L) { return byLetter[L]; }).map(function (L) {
          return '<section class="umd-admissions-alphabet-section" id="letter-' + L + '" aria-labelledby="letter-h-' + L + '">' +
            '<h2 class="umd-admissions-alphabet-letter umd-campaign-small" id="letter-h-' + L + '">' + L + '</h2>' +
            byLetter[L].map(cardHTML).join('') + '</section>';
        }).join('');
      }

      countEl.textContent = matched.length + (matched.length === 1 ? ' program' : ' programs');
      renderPills();
    }

    function renderPills() {
      var items = [];
      if (state.q) items.push({ k:'q', v:'', label:'\u201c' + state.q + '\u201d' });
      GROUP_ORDER.forEach(function (k) {
        state[k].forEach(function (v) { items.push({ k:k, v:v, label:v }); });
      });
      if (!items.length) { pillsHost.hidden = true; pillsHost.innerHTML = ''; return; }
      pillsHost.hidden = false;
      pillsHost.innerHTML = '<span class="umd-admissions-filter-pills-label">Filtered by:</span>' +
        '<span class="umd-text-cluster-pill umd-admissions-filter-pill-cluster">' +
        items.map(function (it) {
          return '<button type="button" class="pf-pill" data-k="' + it.k + '" data-v="' +
            esc(it.v) + '"><span>' + esc(it.label) +
            ' <span aria-hidden="true">\u00d7</span></span></button>';
        }).join('') +
        '</span>' +
        '<button type="button" class="umd-admissions-filter-clear umd-sans-smaller" id="pf-clearall">Clear all</button>';
    }

    // ---- events ----
    var debounce;
    qInput.addEventListener('input', function () {
      clearTimeout(debounce);
      debounce = setTimeout(function () { collect(); render(); }, 200);
    });

    form.addEventListener('submit', function (e) { e.preventDefault(); collect(); render(); });

    var searchForm = document.getElementById('umd-admissions-filter-search-bar');
    searchForm.addEventListener('submit', function (e) { e.preventDefault(); collect(); render(); });

    form.addEventListener('change', function (e) {
      if (e.target.matches('input[type="checkbox"]')) { collect(); render(); }
    });

    // "Show all N" / "Show less" toggle on long groups
    groupsHost.addEventListener('click', function (e) {
      var more = e.target.closest('.umd-admissions-filter-show-all');
      if (!more) return;
      var set = document.getElementById(more.getAttribute('aria-controls'));
      var collapsed = set.toggleAttribute('data-collapsed');
      more.setAttribute('aria-expanded', String(!collapsed));
      more.textContent = collapsed
        ? 'Show all ' + set.querySelectorAll('input[type="checkbox"]').length
        : 'Show less';
    });

    // accordion toggle — the group's own header button only, so the nested
    // .umd-admissions-filter-show-all button doesn't fall through and toggle the fieldset
    groupsHost.addEventListener('click', function (e) {
      var btn = e.target.closest('.umd-admissions-filter-group > button');
      if (!btn) return;
      var group = btn.parentElement;
      var open = group.toggleAttribute('data-open');
      btn.setAttribute('aria-expanded', open);
    });

    // reset — the "Reset filters" outline CTA clones its <button> into shadow DOM,
    // so the visible click can't drive a native form reset. Catch it on the
    // light-DOM .umd-admissions-filter-actions wrapper (the composed click retargets to the CTA host
    // and bubbles here) and clear state explicitly.
    function clearAll() {
      form.querySelectorAll('input[type="checkbox"]:checked').forEach(function (cb) { cb.checked = false; });
      qInput.value = '';
      collect(); render();
    }
    document.querySelector('.umd-admissions-filter-actions').addEventListener('click', clearAll);
    form.addEventListener('reset', function () { setTimeout(clearAll, 0); });

    // pill removal / clear all
    pillsHost.addEventListener('click', function (e) {
      if (e.target.closest('#pf-clearall')) { clearAll(); return; }
      var pill = e.target.closest('.pf-pill');
      if (!pill) return;
      var k = pill.getAttribute('data-k'), v = pill.getAttribute('data-v');
      if (k === 'q') {
        qInput.value = '';
      } else {
        form.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
          if (cb.getAttribute('data-group') === k && cb.value === v) cb.checked = false;
        });
      }
      collect(); render();
    });

    // smooth scroll for the A–Z nav
    navEl.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-letter]');
      if (!a) return;
      e.preventDefault();
      var target = document.getElementById('letter-' + a.getAttribute('data-letter'));
      if (target) {
        target.scrollIntoView({ behavior:'smooth', block:'start' });
        history.replaceState(null, '', '#letter-' + a.getAttribute('data-letter'));
      }
    });

    // mobile filter toggle
    var mobileToggle = document.getElementById('umd-admissions-filter-mobile-toggle');
    mobileToggle.addEventListener('click', function () {
      var open = form.toggleAttribute('data-open');
      mobileToggle.setAttribute('aria-expanded', open);
    });

    buildGroups();
    collect();
    render();
  })();
  </script>

@@CHROME:chrome-scripts@@
</body>
</html>
'''
_body_pin = re.search(r'web-components-library@([\d.]+)/dist/cdn\.js', BODY)
assert _tpl_pin and _body_pin and _tpl_pin.group(1) == _body_pin.group(1), (
    f'cdn.js pin drift: TEMPLATE.html has {_tpl_pin and _tpl_pin.group(1)}, '
    f'this script emits {_body_pin and _body_pin.group(1)} — update the BODY literal.')

# The location facet is listed in the live site's order (Shady Grove first), so
# it is written out in BODY rather than sorted -- check its counts against the data.
_loc_counts = {}
for r in records:
    for l in r['l']:
        _loc_counts[l] = _loc_counts.get(l, 0) + 1
_loc_facet = json.loads(re.search(r'"location":(\[.*?\])', BODY).group(1))
assert {f['title']: f['count'] for f in _loc_facet} == _loc_counts, (
    'location facet out of sync with programs-data.json: %r' % _loc_counts)

# ---------------------------------------------------------------- assemble
body = BODY.replace('@@PROGRAMS@@', programs_json)
for key in _chrome.keys():
    token = '@@CHROME:%s@@' % key
    assert token in body, 'BODY lost the %s slot' % key
    body = body.replace(token, _chrome.block(key, OUT))
assert '@@' not in body, 'unsubstituted token remains'

page = head + '\n' + body
page = page.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(page.split('\n')), 'lines')
print('programs', len(records))
