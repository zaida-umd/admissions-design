#!/usr/bin/env python3
"""Regenerate pages/calendar/index.html.

Sources
  briefs/calendar-data.json           64 events harvested from the live
                                      admissions calendar (see briefs/calendar.md)
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Everything else -- the page-specific <style> block, the hero, the filter rail
and the results column -- is the BODY literal below, because this page is their
only source.

SHAPE (2026-09-10 simplification). The page is a hero over one explorer:
a left filter rail and a flat, chronological event list. The month cursor and
its control bar, the mini-calendar rail, the List|Calendar toggle, the month
grid, the month pager and the static "Upcoming Events" block are all GONE --
the last one because with the list running from today it was literally its own
first six rows. Pagination is by COUNT (15) behind a Load More button, and
there is no text search, matching <https://calendar.umd.edu/search>.

The rail is the programs page's rail (scripts/build-programs.py): the same
`pf-*` markup, accordion groups, "Show all N" toggles, pill row and reset CTA,
over this page's four facets. It differs in one place -- a leading Date group
holding a start/end `input[type=date]` pair, which programs has no use for.

Run after editing briefs/calendar-data.json, shared/, or the BODY literal:
    python3 scripts/build-calendar.py
Do not hand-edit the generated HTML - it is overwritten wholesale.

BODY is a RAW string: it carries CSS/JS backslash escapes that Python would
otherwise reinterpret, corrupting the output silently.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
DATA     = os.path.join(REPO, 'briefs/calendar-data.json')
OUT      = os.path.join(REPO, 'pages/calendar/index.html')
DEPTH    = _chrome.depth_of(OUT)   # pages/calendar/ -> '../../'

TITLE = 'Calendar — Undergraduate Admissions | University of Maryland'

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
data = json.load(open(DATA, encoding='utf-8'))

IMG_PREFIX = '../' * DEPTH + 'images/calendar/'

def start24(e):
    """'3:00 PM' -> '15:00'. All-day events sort to the top of their day."""
    if e['allDay']:
        return None
    hh, mm = e['start'][:-3].strip().split(':')
    hh = int(hh) % 12
    if e['start'].strip().upper().endswith('PM'):
        hh += 12
    return '%02d:%s' % (hh, mm)

# Compacted projection of the data file: short keys, the image reduced to a
# resolved src + alt, the time reduced to the 24h string the ISO stamp needs.
# The grid cells' compact '3:00pm' form went with the grid.
records = []
for e in data['events']:
    r = {
        'd': e['date'],
        't': start24(e),
        'n': e['title'],
        'u': e['url'],
        'l': e['location'],
        'y': e['types'],
        'c': e['colleges'],
        'a': e['audience'],
        'x': e['description'],
    }
    if e['image']:
        r['i'] = IMG_PREFIX + e['image']['file']
        r['g'] = e['image']['alt']
    if e['register']:
        r['r'] = e['register']['url']
        r['rl'] = e['register']['label']
    records.append(r)

# The list is chronological and never re-sorts client-side, so sort here.
# All-day events (t is None) lead their day.
records.sort(key=lambda r: (r['d'], r['t'] or ''))

events_json = json.dumps(records, ensure_ascii=False, separators=(',', ':'))
facets_json = json.dumps(data['facets'], ensure_ascii=False, separators=(',', ':'))
today_json  = json.dumps(data['today'])
range_json  = json.dumps([records[0]['d'], records[-1]['d']])

# ---------------------------------------------------------------- body
BODY = r'''  </style>

  <script src="https://unpkg.com/@universityofmaryland/web-components-library@2.0.0/dist/cdn.js"></script>

  <!-- Calendar explorer — page-specific styles -->
  <style>
    /* No page colour variables. Every colour on this page is a DS token
       from tokens.min.css (TEMPLATE links it second, so they are live):
       --umd-color-red / -red-dark / -gold / -white / -black /
       -gray-darker / -gray-dark / -gray-medium-a-a / -gray-light /
       -gray-lighter / -gray-lightest. */

    /* ============================================================
       TWO-COLUMN LAYOUT — filter rail left, event list right
       Same structure and same 1020px threshold as the programs page
       (scripts/build-programs.py). 1020px is this page's ONE desktop
       breakpoint; don't introduce a second.
       ============================================================ */
    .cal-layout { display:block; }

    @media (min-width:1020px) {
      .cal-layout { display:flex; align-items:flex-start; gap:64px; }
      /* deliberately NOT sticky: a pinned rail has to cap its own height, and
         that nested scroller (plus the per-group ones) meant up to three
         scrollbars on one screen. The rail scrolls with the page instead. */
      .cal-filters { width:30%; min-width:260px; max-width:360px; }
    }

    .cal-results { flex:1; min-width:0; }

    /* ============================================================
       FILTER RAIL — the programs page's rail, verbatim apart from the
       Date group. Kept as a copy rather than a shared partial because
       these two pages are the only users and the build scripts have no
       include mechanism; if a third page wants it, extract then.
       ============================================================ */
    .pf-mobile-toggle {
      display:flex; justify-content:space-between; align-items:center; gap:16px;
      width:100%; padding:14px 16px; margin-bottom:16px; cursor:pointer;
      background:var(--umd-color-black); color:var(--umd-color-white); border:0; font-weight:700;
    }

    .pf-mobile-toggle::after { content:"+"; font-size:22px; line-height:1; }

    .pf-mobile-toggle[aria-expanded="true"]::after { content:"\2212"; }

    @media (min-width:1020px) { .pf-mobile-toggle { display:none; } }

    #pf-form { display:block; }

    @media (max-width:1019px) {
      #pf-form { display:none; }
      #pf-form.is-open { display:block; }
    }

    .pf-group { border-bottom:1px solid var(--umd-color-black); margin-bottom:24px; padding-bottom:24px; }

    .pf-group:last-of-type { border-bottom:0; }

    .pf-group > button {
      display:flex; position:relative; justify-content:space-between; align-items:center;
      gap:16px; width:100%; padding:0 24px 0 0; background:none; border:0; cursor:pointer;
      font:inherit; font-weight:700; font-size:18px; text-align:left; color:var(--umd-color-black);
      transition:color .3s;
    }

    .pf-group > button:hover, .pf-group > button:focus-visible { color:var(--umd-color-red); }

    /* The open/closed glyph is a PLUS that becomes a MINUS: two 12x2 bars
       stacked at the same spot, ::before horizontal and ::after rotated
       upright, so together they read as "+". Opening rotates ::after back to
       0deg and the two bars collapse onto each other into a "-".

       Both bars are required. An earlier revision here hid ::before and left
       ::after alone, which rendered a bare vertical bar closed and a bare
       horizontal one open -- no plus at any point. `position:relative` on the
       button and its 24px right padding are what the absolutely-placed bars
       hang off; without them they escape to the nearest positioned ancestor. */
    .pf-group > button::before, .pf-group > button::after {
      content:""; position:absolute; top:calc(50% - 1px); right:0;
      width:12px; height:2px; background:currentColor; transition:transform .3s;
    }

    .pf-group > button::after { transform:rotate(90deg); }

    .pf-group.open > button::after { transform:rotate(0); }

    .pf-body { display:grid; grid-template-rows:0fr; transition:grid-template-rows .3s ease; }

    .pf-group.open .pf-body { grid-template-rows:1fr; }

    .pf-body > div { min-height:0; overflow:hidden; }

    .pf-body fieldset {
      border:0; margin:0; padding:16px 0 0; display:flex; flex-direction:column; gap:12px;
    }

    .pf-body fieldset.is-collapsed .pf-extra { display:none; }

    /* the DS pill chip is a display element, so its wrapping-margin hack and
       border have to be neutralized before it can be a button */
    .pf-more-cluster.umd-text-cluster-pill { display:inline-flex; margin-top:8px; }

    .pf-more-cluster.umd-text-cluster-pill > .pf-more { margin-top:0; border:0; cursor:pointer; color:var(--umd-color-black); }

    .pf-more-cluster.umd-text-cluster-pill > .pf-more:hover,
    .pf-more-cluster.umd-text-cluster-pill > .pf-more:focus-visible { background-color:var(--umd-color-gold); }

    .pf-body .umd-field-checkbox-wrapper { align-items:flex-start; gap:12px; margin-bottom:0; line-height:1.3; }

    .pf-body input[type="checkbox"] { margin:.15em 0 0; width:18px; height:18px; accent-color:var(--umd-color-red); flex:0 0 auto; }

    .pf-count { color:var(--umd-color-gray-medium-a-a); font-variant-numeric:tabular-nums; }

    .pf-actions { margin-top:24px; }

    /* ---- DATE GROUP ----------------------------------------------------
       The one thing the programs rail has no equivalent of. Two native
       `input[type=date]` fields SIDE BY SIDE with a "to" between them, as on
       <https://calendar.umd.edu/search>. Native rather than a scripted picker:
       the browser's own calendar popup is keyboard- and screen-reader-complete,
       localises itself, and costs no JS.

       `min`/`max` are stamped from the data range at build time, so the popup
       cannot wander into years the page has no events for.

       The field chrome is NOT page CSS. `.umd-field-input` and
       `.umd-field-input-date-time-wrapper` are upstream element.min.css
       classes -- the same pair the live search page uses -- and they carry the
       border, padding, Interstate face, the gray-to-red calendar glyph, and
       the rules that hide the native webkit picker indicator behind it. An
       earlier revision hand-rolled all of that, which critical.css's header
       explicitly warns against. Only the row below is page CSS. */
    .pf-dates { display:flex; align-items:center; gap:8px; padding-top:16px; }

    /* the wrappers share the row evenly; min-width:0 lets them shrink below
       the input's intrinsic width instead of forcing the row wider than the
       rail (a flex item's default min-width:auto would) */
    .pf-dates .umd-field-input-date-time-wrapper { flex:1 1 0; min-width:0; }

    .pf-date-sep { flex:0 0 auto; font-size:14px; font-weight:700; color:var(--umd-color-gray-dark); }

    /* The rail is the query container, as the old mini-calendar rail was, so
       the date type keys off the RAIL's width rather than the viewport's —
       which is the width that actually decides whether two fields fit.

       Below ~308px of rail the DS base size (calc(14px + 0.16vw), ~15.6px at
       this breakpoint) runs "mm/dd/yyyy" under the wrapper's calendar glyph,
       which is absolutely placed 16px from the right and cannot reflow. The
       rail only reaches that band between 1020px — where it is 277px, its
       narrowest, since below 1020 it stacks full width — and about 1130px.
       Shrinking the type there is what the live search page does too: its
       fields measure 12px where the rail is narrow. */
    .cal-filters { container-type:inline-size; }

    @container (max-width:320px) {
      .pf-dates .umd-field-input { font-size:13px; padding-left:12px; padding-right:12px; }
    }

    /* ============================================================
       RESULTS COLUMN — pills, count line, event list, Load More
       ============================================================ */
    /* active-filter pills use the DS .umd-text-cluster-pill chip
       (var(--umd-color-gray-lightest), 12px); neutralize its wrapping-margin
       hack and use flex gap instead. */
    .pf-pills { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:24px; }

    /* display:flex beats the UA sheet's [hidden]{display:none}, so without
       this an empty pill row leaks its margin above the count line */
    .pf-pills[hidden] { display:none; }

    .pf-pills-label { font-weight:700; margin-right:4px; }

    .pf-pill-cluster.umd-text-cluster-pill { margin-top:0; display:inline-flex; flex-wrap:wrap; gap:8px; }

    .pf-pills .umd-text-cluster-pill > * { margin-top:0; border:0; cursor:pointer; color:var(--umd-color-black); }

    .pf-pills .umd-text-cluster-pill > button:hover,
    .pf-pills .umd-text-cluster-pill > button:focus-visible { background-color:var(--umd-color-gold); }

    .pf-clear {
      background:none; border:0; padding:0 0 0 6px; cursor:pointer; color:var(--umd-color-black);
      text-decoration:underline; text-underline-offset:.15em;
    }

    .pf-clear:hover { color:var(--umd-color-red); }

    .pf-count-line { margin:0 0 24px; }

    .pf-empty { font-size:18px; }

    /* The cards are direct siblings of #cal-list, which is what upstream
       web-components.min.css needs for its
       `umd-element-event[data-display="list"] + umd-element-event[...]`
       divider (24px + 1px var(--umd-color-gray-light)). Do not wrap them. */

    /* Load More sits under the list on the same 56px/32px rule the month
       pager used, so the results column keeps its old bottom rhythm. */
    .cal-more-wrap {
      margin-top:56px; padding-top:32px; border-top:1px solid var(--umd-color-gray-light);
      display:flex; justify-content:center;
    }

    .cal-more-wrap[hidden] { display:none; }
  </style>

@@CHROME:chrome-css@@
@@CHROME:gate@@
</head>

<body>

@@CHROME:header@@

  <!-- HERO — background, small, centered. Matches the section landing
       pages and pages/search/. Headline only: the live calendar page
       carries a breadcrumb and an <h1> and nothing else. An earlier
       revision added a supporting paragraph and a "Plan Your Visit"
       CTA; both were invented here, not taken from the source, and are
       gone. The image is shared with the search page on purpose --
       both are utility pages, and the motion-blurred crowd around a
       still Testudo reads as time passing on one and as everything on
       the site moving past on the other. -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small" data-layout-text="center">
      <img slot="image" src="../../images/calendar/blurry-testudo-FirstDayofClass_08262024_DS_2384_DAM.webp" alt="Students streaming past the Testudo statue outside McKeldin Library" />
      <p slot="eyebrow">Visit UMD</p>
      <h1 slot="headline">Calendar</h1>
    </umd-element-hero>
  </section>

  <!-- EVENTS EXPLORER — filter rail + flat chronological list -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <div class="cal-layout">

        <!-- FILTER RAIL -->
        <aside class="cal-filters" aria-label="Filter events">
          <button type="button" id="pf-mobile-toggle" class="pf-mobile-toggle" aria-expanded="false" aria-controls="pf-form">
            <span>Filter events</span>
          </button>
          <form id="pf-form" action="#">
            <h2 class="umd-tailwing-right-headline"><span>REFINE</span></h2>
            <div id="pf-groups"></div>
            <div class="pf-actions">
              <umd-element-call-to-action data-display="outline">
                <button type="button" id="pf-reset">Reset filters</button>
              </umd-element-call-to-action>
            </div>
          </form>
        </aside>

        <!-- RESULTS -->
        <div class="cal-results">
          <div class="pf-pills" id="pf-pills" hidden></div>
          <p class="pf-count-line umd-sans-smaller" id="pf-count" role="status" aria-live="polite"></p>
          <div id="cal-list"></div>
          <p id="pf-empty" class="pf-empty" hidden></p>
          <div class="cal-more-wrap" id="cal-more-wrap" hidden>
            <umd-element-call-to-action data-display="outline">
              <button type="button" id="cal-more">Load More Events</button>
            </umd-element-call-to-action>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

@@CHROME:footer@@

  <!-- Calendar data + filter / load-more logic -->
  <script>
  (function () {
    var EVENTS = @@EVENTS@@;
    var FACETS = @@FACETS@@;
    var TODAY  = @@TODAY@@;
    var RANGE  = @@RANGE@@;   // [earliest event date, latest event date]

    var GROUP_ORDER  = ['audience', 'location', 'type', 'college'];
    var GROUP_LABELS = {
      audience: 'Audience',
      location: 'Location',
      type: 'Event Type',
      college: 'College or School'
    };
    // facet key -> the event field it tests
    var GROUP_FIELD = { audience:'a', location:'l', type:'y', college:'c' };

    var MONTHS_SHORT = ['Jan','Feb','Mar','Apr','May','Jun',
                        'Jul','Aug','Sep','Oct','Nov','Dec'];

    // options shown before a group collapses behind its "Show all" toggle
    var PF_SHOW_LIMIT = 7;

    // events per page — Load More reveals another PAGE_SIZE
    var PAGE_SIZE = 15;

    var form       = document.getElementById('pf-form');
    var groupsHost = document.getElementById('pf-groups');
    var listHost   = document.getElementById('cal-list');
    var emptyEl    = document.getElementById('pf-empty');
    var countEl    = document.getElementById('pf-count');
    var pillsHost  = document.getElementById('pf-pills');
    var moreWrap   = document.getElementById('cal-more-wrap');

    function esc(s) {
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // 'YYYY-MM-DD' -> 'Sep 1, 2026'. Sliced, never parsed into a Date --
    // `new Date('2026-09-01')` is UTC midnight and prints as Aug 31 west of
    // Greenwich. Every date on this page is a string comparison for the same
    // reason: nothing shifts across a timezone boundary.
    function prettyDate(d) {
      return MONTHS_SHORT[parseInt(d.slice(5, 7), 10) - 1] + ' ' +
        parseInt(d.slice(8, 10), 10) + ', ' + d.slice(0, 4);
    }

    // The default window is "today onward" -- the start field is PRE-FILLED
    // with today rather than left blank, so the filter that is actually
    // running is visible in the control instead of being implied. Reset
    // returns here, not to a blank field (past events are not what this page
    // is for; the field still accepts an earlier date to reach them).
    var state = { start:TODAY, end:'', audience:[], location:[], type:[], college:[], shown:PAGE_SIZE };

    function isDefaultRange() { return state.start === TODAY && !state.end; }

    // ---- build the rail ----
    // Date leads, as on calendar.umd.edu/search, then the four facets.
    // Date and the first facet open on load; the rest are one click away.
    // One field: the upstream wrapper (which draws the calendar glyph) around
    // an .umd-field-input. The label rides inside the wrapper, as on the live
    // page -- the wrapper is position:relative and the glyph is absolutely
    // placed against it, so nothing else may sit between the two.
    function dateField(id, label, value) {
      return '<div class="umd-field-input-date-time-wrapper">' +
        '<label class="sr-only" for="' + id + '">' + label + '</label>' +
        '<input type="date" class="umd-field-input" id="' + id + '"' +
        ' value="' + esc(value) + '"' +
        ' min="' + esc(RANGE[0]) + '" max="' + esc(RANGE[1]) + '" />' +
        '</div>';
    }

    function dateGroup() {
      return '<div class="pf-group open" data-group="date">' +
        '<button type="button" aria-expanded="true" aria-controls="pf-body-date">' +
        '<span>Date</span></button>' +
        '<div class="pf-body" id="pf-body-date"><div>' +
        '<div class="pf-dates">' +
        dateField('pf-start', 'Start date', TODAY) +
        '<span class="pf-date-sep" aria-hidden="true">to</span>' +
        dateField('pf-end', 'End date', '') +
        '</div></div></div></div>';
    }

    function buildGroups() {
      groupsHost.innerHTML = dateGroup() + GROUP_ORDER.map(function (key, idx) {
        var opts = FACETS[key] || [];
        var long = opts.length > PF_SHOW_LIMIT;
        var rows = opts.map(function (o, i) {
          return '<label class="umd-field-checkbox-wrapper' +
            (long && i >= PF_SHOW_LIMIT ? ' pf-extra' : '') +
            '"><input type="checkbox" data-group="' + key +
            '" value="' + esc(o.title) + '"><span>' + esc(o.title) +
            ' <span class="pf-count umd-sans-smaller">(' + o.count + ')</span></span></label>';
        }).join('');
        var more = long
          ? '<span class="umd-text-cluster-pill pf-more-cluster">' +
            '<button type="button" class="pf-more" aria-expanded="false" aria-controls="pf-set-' + key + '">' +
            'Show all ' + opts.length + '</button></span>'
          : '';
        var open = idx === 0;
        return '<div class="pf-group' + (open ? ' open' : '') + '" data-group="' + key + '">' +
          '<button type="button" aria-expanded="' + open + '" aria-controls="pf-body-' + key + '">' +
          '<span>' + GROUP_LABELS[key] + '</span></button>' +
          '<div class="pf-body" id="pf-body-' + key + '"><div>' +
          '<fieldset id="pf-set-' + key + '"' + (long ? ' class="is-collapsed"' : '') + '>' +
          rows + '</fieldset>' + more + '</div></div></div>';
      }).join('');
    }

    // ---- collect state from the DOM ----
    function collect() {
      state.start = document.getElementById('pf-start').value;
      state.end   = document.getElementById('pf-end').value;
      GROUP_ORDER.forEach(function (k) { state[k] = []; });
      form.querySelectorAll('input[type="checkbox"]:checked').forEach(function (cb) {
        state[cb.getAttribute('data-group')].push(cb.value);
      });
    }

    // ---- match an event against active filters (AND across groups, OR within) ----
    function match(e) {
      if (state.start && e.d < state.start) return false;
      if (state.end && e.d > state.end) return false;
      for (var i = 0; i < GROUP_ORDER.length; i++) {
        var k = GROUP_ORDER[i];
        if (!state[k].length) continue;
        var vals = e[GROUP_FIELD[k]];
        vals = (typeof vals === 'string') ? [vals] : (vals || []);
        var hit = vals.some(function (v) { return state[k].indexOf(v) > -1; });
        if (!hit) return false;
      }
      return true;
    }

    // ---- LIST ----------------------------------------------------------
    // start-date-iso is read from the element's TEXT CONTENT, not the datetime
    // attribute (parseDateFromElement). The light-DOM text never renders — the
    // component builds its own shadow content.
    //
    // end-date-iso repeats the start stamp on purpose. The DS event meta
    // decides it is a range with `startDay != endDay || startMonth != endMonth`
    // and `startTime != endTime`; with the slot absent those read `undefined`,
    // so a single-point event renders "Thu. Aug 20 - undefined. undefined
    // undefined" and "3:00pm - undefined". Repeating the stamp makes both
    // comparisons false and the meta collapses to the single date and time.
    //
    // data-visual-time is opt-OUT, not opt-in: Attributes.isVisual.showTime
    // defaults to true, so an all-day event with the attribute absent renders
    // "12:00am". Emit it explicitly on every card. See OVERRIDES.md.
    function summarize(s) {
      if (!s) return '';
      if (s.length <= 240) return s;
      var cut = s.slice(0, 240);
      return cut.slice(0, cut.lastIndexOf(' ')) + '…';
    }

    function cardHTML(e) {
      var stamp = e.d + 'T' + (e.t || '00:00') + ':00';
      var img = e.i ? '<img slot="image" src="' + esc(e.i) + '" alt="' + esc(e.g || '') + '" />' : '';
      var text = e.x ? '<p slot="text">' + esc(summarize(e.x)) + '</p>' : '';
      var actions = e.r
        ? '<div slot="actions"><umd-element-call-to-action data-display="secondary">' +
          '<a href="' + esc(e.r) + '" target="_blank" rel="noopener">' + esc(e.rl || 'Register') + '</a>' +
          '</umd-element-call-to-action></div>'
        : '';
      return '<umd-element-event data-display="list" data-date="' + e.d +
        '" data-visual-time="' + (e.t ? 'true' : 'false') + '">' +
        img +
        '<h3 slot="headline"><a href="' + esc(e.u) + '">' + esc(e.n) + '</a></h3>' +
        text +
        '<time slot="start-date-iso" datetime="' + stamp + '">' + stamp + '</time>' +
        '<time slot="end-date-iso" datetime="' + stamp + '">' + stamp + '</time>' +
        '<p slot="location">' + esc(e.l) + '</p>' +
        actions +
        '</umd-element-event>';
    }

    // ---- render --------------------------------------------------------
    function render() {
      var matched = EVENTS.filter(match);
      var visible = matched.slice(0, state.shown);

      listHost.innerHTML = visible.map(cardHTML).join('');

      emptyEl.hidden = matched.length > 0;
      emptyEl.textContent = hasFilters()
        ? 'No events match your filters. Try removing a filter or widening the dates.'
        : 'No events to show.';

      // "Showing 15 of 51 events" only while there is more to load — once the
      // list is complete the "of" half is noise, so it collapses to a total.
      countEl.textContent = !matched.length
        ? ''
        : (visible.length < matched.length
            ? 'Showing ' + visible.length + ' of ' + matched.length + ' events'
            : matched.length + (matched.length === 1 ? ' event' : ' events'));

      moreWrap.hidden = visible.length >= matched.length;

      renderPills();
    }

    function hasFilters() {
      if (!isDefaultRange()) return true;
      return GROUP_ORDER.some(function (k) { return state[k].length > 0; });
    }

    // A new filter always returns to page one — leaving `shown` where it was
    // would silently show 45 of a 3-event result, or hold a stale scroll
    // position in a list that no longer has those rows.
    function refilter() { collect(); state.shown = PAGE_SIZE; render(); }

    // ---- pills ---------------------------------------------------------
    // The date range is ONE pill, and only when it is not the default —
    // otherwise every visit opens with a "From Aug 20, 2026" chip the reader
    // did not choose.
    function dateLabel() {
      if (state.start && state.end) return prettyDate(state.start) + ' – ' + prettyDate(state.end);
      if (state.start) return 'From ' + prettyDate(state.start);
      return 'Through ' + prettyDate(state.end);
    }

    function renderPills() {
      var items = [];
      if (!isDefaultRange()) items.push({ k:'date', v:'', label:dateLabel() });
      GROUP_ORDER.forEach(function (k) {
        state[k].forEach(function (v) { items.push({ k:k, v:v, label:v }); });
      });
      if (!items.length) { pillsHost.hidden = true; pillsHost.innerHTML = ''; return; }
      pillsHost.hidden = false;
      pillsHost.innerHTML = '<span class="pf-pills-label">Filtered by:</span>' +
        '<span class="umd-text-cluster-pill pf-pill-cluster">' +
        items.map(function (it) {
          return '<button type="button" class="pf-pill" data-k="' + it.k + '" data-v="' +
            esc(it.v) + '"><span>' + esc(it.label) +
            ' <span aria-hidden="true">×</span></span></button>';
        }).join('') +
        '</span>' +
        '<button type="button" class="pf-clear umd-sans-smaller" id="pf-clearall">Clear all</button>';
    }

    // ---- events --------------------------------------------------------
    form.addEventListener('submit', function (e) { e.preventDefault(); refilter(); });

    // one listener for both control kinds: the date fields fire `change` on
    // commit (not on every keystroke), so no debounce is needed
    form.addEventListener('change', function (e) {
      if (e.target.matches('input[type="checkbox"], input[type="date"]')) refilter();
    });

    // "Show all N" / "Show less" toggle on long groups
    groupsHost.addEventListener('click', function (e) {
      var more = e.target.closest('.pf-more');
      if (!more) return;
      var set = document.getElementById(more.getAttribute('aria-controls'));
      var collapsed = set.classList.toggle('is-collapsed');
      more.setAttribute('aria-expanded', String(!collapsed));
      more.textContent = collapsed
        ? 'Show all ' + set.querySelectorAll('input[type="checkbox"]').length
        : 'Show less';
    });

    // accordion toggle — the group's own header button only, so the nested
    // .pf-more button doesn't fall through and toggle the fieldset
    groupsHost.addEventListener('click', function (e) {
      var btn = e.target.closest('.pf-group > button');
      if (!btn) return;
      var group = btn.parentElement;
      var open = group.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });

    // reset — the "Reset filters" outline CTA clones its <button> into shadow DOM,
    // so the visible click can't drive a native form reset. Catch it on the
    // light-DOM .pf-actions wrapper (the composed click retargets to the CTA host
    // and bubbles here) and clear state explicitly.
    function clearAll() {
      form.querySelectorAll('input[type="checkbox"]:checked').forEach(function (cb) { cb.checked = false; });
      document.getElementById('pf-start').value = TODAY;
      document.getElementById('pf-end').value = '';
      refilter();
    }
    document.querySelector('.pf-actions').addEventListener('click', clearAll);
    form.addEventListener('reset', function () { setTimeout(clearAll, 0); });

    // pill removal / clear all
    pillsHost.addEventListener('click', function (e) {
      if (e.target.closest('#pf-clearall')) { clearAll(); return; }
      var pill = e.target.closest('.pf-pill');
      if (!pill) return;
      var k = pill.getAttribute('data-k'), v = pill.getAttribute('data-v');
      if (k === 'date') {
        document.getElementById('pf-start').value = TODAY;
        document.getElementById('pf-end').value = '';
      } else {
        form.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
          if (cb.getAttribute('data-group') === k && cb.value === v) cb.checked = false;
        });
      }
      refilter();
    });

    // Load More — same shadow-clone problem as the reset CTA, so the listener
    // sits on the light-DOM wrapper. Focus moves to the first newly revealed
    // card: without it a keyboard user is left on a button that may have just
    // disappeared, and a screen reader hears only the count line update.
    moreWrap.addEventListener('click', function () {
      var first = state.shown;
      state.shown += PAGE_SIZE;
      render();
      var card = listHost.children[first];
      if (!card) return;
      var link = card.querySelector('h3 a');
      if (link) { link.setAttribute('tabindex', '-1'); link.focus({ preventScroll:true }); }
      card.scrollIntoView({ behavior:'smooth', block:'center' });
    });

    // mobile filter toggle
    var mobileToggle = document.getElementById('pf-mobile-toggle');
    mobileToggle.addEventListener('click', function () {
      var open = form.classList.toggle('is-open');
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

# ---------------------------------------------------------------- assemble
body = BODY.replace('@@EVENTS@@', events_json)
body = body.replace('@@FACETS@@', facets_json)
body = body.replace('@@TODAY@@', today_json)
body = body.replace('@@RANGE@@', range_json)
for key in _chrome.keys():
    token = '@@CHROME:%s@@' % key
    assert token in body, 'BODY lost the %s slot' % key
    body = body.replace(token, _chrome.block(key, OUT))
assert '@@' not in body, 'unsubstituted token remains'

page = head + '\n' + body
page = page.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(page.split('\n')), 'lines')
print('events', len(records))
