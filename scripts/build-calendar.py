#!/usr/bin/env python3
"""Regenerate pages/calendar/index.html.

Sources
  briefs/calendar-data.json           64 events harvested from the live
                                      admissions calendar (see briefs/calendar.md)
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Everything else -- the page-specific <style> blocks, the hero, the control bar,
the filter band, the month grid, and the calendar JS -- is the BODY literal
below, because this page is their only source.

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

def short_time(e):
    """'3:00 PM' -> '3:00pm'; the compact form the grid cells use."""
    return None if e['allDay'] else e['start'].replace(' ', '').lower()

# Compacted projection of the data file: short keys, the image reduced to a
# resolved src + alt, the time reduced to the 24h string the ISO stamp needs
# plus the display string the grid cells print.
records = []
for e in data['events']:
    r = {
        'd': e['date'],
        't': start24(e),
        's': short_time(e),
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

# ---------------------------------------------------------------- upcoming
# The page-bottom "Upcoming Events" block is STATIC — the next six events on
# or after today, rendered at build time. It is deliberately outside the
# explorer: it does not read the filters, the month cursor or the view
# toggle, so it needs no JS and ships as real HTML.
#
# The live page's version is a curated block that had gone stale (it was
# still showing March 2025 Terrapin Tours against an August 2026 date);
# deriving it from the data keeps it honest.
UPCOMING_COUNT = 6

def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))

def summarize(text, limit=160):
    if not text:
        return ''
    if len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[:cut.rfind(' ')] + '\u2026'

def upcoming_card(r):
    stamp = r['d'] + 'T' + (r['t'] or '00:00') + ':00'
    parts = ['<umd-element-event class="cal-upcoming-card" data-visual-time="%s">'
             % ('true' if r['t'] else 'false')]
    parts.append('<h3 slot="headline"><a href="%s">%s</a></h3>' % (esc(r['u']), esc(r['n'])))
    if r.get('x'):
        parts.append('<p slot="text">%s</p>' % esc(summarize(r['x'])))
    # start/end repeated: see the note on the list cards — a missing
    # end-date-iso makes the DS meta print "undefined"
    for slot in ('start-date-iso', 'end-date-iso'):
        parts.append('<time slot="%s" datetime="%s">%s</time>' % (slot, stamp, stamp))
    parts.append('<p slot="location">%s</p>' % esc(r['l']))
    if r.get('r'):
        parts.append(
            '<div slot="actions"><umd-element-call-to-action data-display="secondary">'
            '<a href="%s" target="_blank" rel="noopener">%s</a>'
            '</umd-element-call-to-action></div>' % (esc(r['r']), esc(r.get('rl') or 'Register')))
    parts.append('</umd-element-event>')
    return '\n          '.join(parts)

upcoming = [r for r in records if r['d'] >= data['today']][:UPCOMING_COUNT]
upcoming_html = '\n          '.join(upcoming_card(r) for r in upcoming)

events_json = json.dumps(records, ensure_ascii=False, separators=(',', ':'))
facets_json = json.dumps(data['facets'], ensure_ascii=False, separators=(',', ':'))
today_json  = json.dumps(data['today'])

# ---------------------------------------------------------------- body
BODY = r'''  </style>

  <script src="https://unpkg.com/@universityofmaryland/web-components-library@1.19.5/dist/cdn.js"></script>

  <!-- Calendar — page-specific styles -->
  <style>
    /* No page colour variables. Every colour on this page is a DS token
       from tokens.min.css (TEMPLATE links it second, so they are live):
       --umd-color-red / -red-dark / -gold / -white / -black /
       -gray-darker / -gray-dark / -gray-medium-a-a / -gray-light /
       -gray-lighter / -gray-lightest. A local `--umd-red: #e21833` alias
       used to sit here; it was a hand-rolled duplicate of
       --umd-color-red and is gone. */

    /* ============================================================
       CONTROL BAR — month cursor + view toggle
       Mirrors the live calendar's .main-controls: the month and its
       prev/next/Today nav on the left, the List | Calendar toggle on
       the right. One date cursor drives both views.
       ============================================================ */
    /* Order on the page is: filter band -> active pills -> THIS bar ->
       results. The band answers "which events", the bar answers "when, and
       shown how" — so it belongs directly above the thing it labels, not
       stranded above the filters.

       Spacing uses the DS space tokens from tokens.min.css (TEMPLATE links it
       second, so the custom properties are live): --umd-space-md = 24px,
       --umd-space-3xl = 56px. At desktop the bar gets 56px of air top and
       bottom so it reads as its own band between the filters and the results;
       the top margin collapses with the band's (or the pill row's) 32px
       bottom, landing on 56. */
    .cal-controls {
      display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
      gap:16px 24px; margin-bottom:var(--umd-space-md);
    }

    /* 1020px is this page's one desktop threshold — the same breakpoint the
       rail/results split uses. Don't introduce a second. */
    @media (min-width:1020px) {
      .cal-controls {
        margin-top:var(--umd-space-3xl);
        margin-bottom:var(--umd-space-3xl);
      }
    }

    /* the arrows flank the month rather than trailing it, so the label reads as
       the thing being stepped through */
    .cal-controls-date { display:flex; align-items:center; gap:16px; }

    /* .umd-campaign-small is Barlow Condensed italic 700, 32px -> 44px.
       There is no `-uppercase` sibling for the campaign faces (unlike
       umd-sans-*), so the transform is stated here. min-width holds the
       arrows still as the month name changes length; it is in `ch` rather
       than `em` because the condensed face's em is much narrower than its
       average glyph. */
    .cal-controls-date h2 {
      margin:0; min-width:11ch; text-align:center; text-transform:uppercase;
    }

    /* Colours are DS tokens from tokens.min.css: gray-light chip, black
       glyph, glyph goes Maryland red on hover. The chip itself does NOT
       change — the point of moving off a red button was to take the red
       block out of the bar, so reintroducing it on hover would undo that.
       The glyph carries the state instead, which is also how the DS's own
       gray-to-red interactions read (umd-animation-line-slide-graydark-red). */
    .cal-nav {
      flex:0 0 auto; width:var(--umd-space-lg); height:var(--umd-space-lg);
      padding:0; border:0; cursor:pointer;
      background-color:var(--umd-color-gray-light);
      display:flex; align-items:center; justify-content:center;
    }

    .cal-nav svg {
      width:14px; height:14px;
      fill:var(--umd-color-black); transition:fill .3s;
    }

    /* `fill` on the <svg> does not reach a <path> that sets its own fill, and
       the DS chevron markup does not — but be explicit so a future glyph swap
       can't quietly break the hover. */
    .cal-nav:hover svg, .cal-nav:focus-visible svg,
    .cal-nav:hover svg path, .cal-nav:focus-visible svg path { fill:var(--umd-color-red); }

    /* Desktop takes a smaller glyph in the same 32px button — more air around
       the chevron. Tighter viewports keep 14px, where the button is also a
       touch target. --umd-space-xs is 12px; a space token for an icon box
       matches how the button itself is sized (var(--umd-space-lg)).

       Must sit AFTER the base rule above — same selector, so specificity ties
       and source order decides. The 1020px block further down is declared
       BEFORE this rule, so putting it there would lose silently. */
    @media (min-width:1020px) {
      .cal-nav svg { width:var(--umd-space-xs); height:var(--umd-space-xs); }
    }

    .cal-nav[data-dir="prev"] svg { transform:scaleX(-1); }

    .cal-today {
      background:none; border:0; padding:0 0 0 8px; cursor:pointer; color:var(--umd-color-black);
      font:inherit; font-size:14px; font-weight:700;
      text-transform:uppercase; letter-spacing:.08em;
      transition:color .3s;
    }

    .cal-today:hover, .cal-today:focus-visible { color:var(--umd-color-red); }

    .cal-view-group { display:flex; }

    .cal-view {
      background:none; border:0; border-bottom:2px solid transparent;
      padding:6px 14px; cursor:pointer; color:var(--umd-color-gray-dark);
      font:inherit; font-size:14px; font-weight:700;
      text-transform:uppercase; letter-spacing:.08em;
      transition:color .3s, border-color .3s;
    }

    .cal-view:hover, .cal-view:focus-visible { color:var(--umd-color-black); }

    .cal-view[aria-pressed="true"] { color:var(--umd-color-black); border-bottom-color:var(--umd-color-red); }

    /* The month grid needs ~90px per column to hold a readable title. Below
       768px there is no honest way to render seven of them, so the toggle
       goes away and the page is list-only — which is exactly what the live
       site does (its umd-calendar-grid measures 0x0 at 375px). */
    @media (max-width:767px) { .cal-view-group { display:none; } }

    /* ============================================================
       LIST VIEW LAYOUT — mini-calendar rail + results
       Only the list view splits. The grid view is the calendar, so a
       second month picker beside it would both duplicate the control
       and steal the width the seven columns need — it renders full
       bleed instead.
       ============================================================ */
    .cal-layout { display:block; }

    /* The view toggle hides these with the `hidden` ATTRIBUTE, whose
       `display:none` comes from the UA stylesheet — any author `display`
       rule beats it. `.cal-layout` sets display:block/flex, so without
       this the rail stayed on screen in grid view while `el.hidden`
       reported true. Specificity 0,2,0 wins over the media query's
       0,1,0, so no !important is needed. Assert getComputedStyle().display,
       never the .hidden property. */
    .cal-layout[hidden], #cal-grid[hidden] { display:none; }

    @media (min-width:1020px) {
      .cal-layout { display:flex; align-items:flex-start; gap:64px; }
      /* deliberately NOT sticky — the rail scrolls with the page, so nothing
         on this page has its own scrollbar */
      .cal-rail { width:30%; min-width:280px; max-width:340px; }

      /* The rail sits on the RIGHT, matching calendar.umd.edu, where this same
         month grid is a right-rail element. Done with `order` rather than DOM
         position so the rail still stacks ABOVE the list when the layout goes
         single-column — moving it after .cal-results in the markup would bury
         the date picker under 51 event cards on mobile. The cost is that
         keyboard focus reaches the rail before the results it sits beside;
         acceptable here, since the rail is a handful of enabled day buttons
         and it is a control for the list rather than a peer of it. */
      .cal-rail { order:2; }
      .cal-results { order:1; }
    }

    /* Once the layout wraps to a single column the rail is no longer a
       narrow column beside the list — it is a band across the page. So it
       centres, grows to 600px (85px mini-calendar cells rather than 48px),
       and takes 40px of air top and bottom to separate it from the control
       bar above and the results below. */
    @media (max-width:1019px) {
      .cal-rail {
        max-width:600px;
        margin:var(--umd-space-xl) auto;
      }
    }

    .cal-results { flex:1; min-width:0; }

    /* the query container for the mini calendar's type scale (see below) */
    .cal-rail { container-type:inline-size; }

    /* ============================================================
       MINI MONTH CALENDAR
       Recreated from the calendar.umd.edu right-rail month grid:
       var(--umd-color-gray-lightest) panel, 7-column 1px-gutter grid of square cells, 12px/800
       centered numerals, days-with-events underlined, out-of-month cells
       knocked back to var(--umd-color-gray-lighter), selected day ringed in UMD red.

       Two deliberate departures from the source:
       - cells are <button>s, not <a>s — there is no per-day URL here, a
         day click sets the from-date and re-filters in place;
       - the selected/today ring is an inset box-shadow rather than a
         border. The square cell is sized by `padding-bottom:100%` on a
         zero-height box, which a real border would knock out of square.

       It carries no month nav of its own: the control bar owns the month
       cursor, and two sets of arrows for one value invites them to drift.
       ============================================================ */
    .cal-mini { background:var(--umd-color-gray-lightest); padding:24px 14px; }

    .cal-mini h2 {
      margin:0 0 var(--umd-space-sm); text-align:center;
      font-size:18px; font-weight:700; line-height:1.25;
    }

    .cal-mini-days, .cal-mini-dates { display:grid; grid-template-columns:repeat(7,1fr); gap:1px; }

    .cal-mini-days { margin-bottom:1px; }

    .cal-mini-days p, .cal-day {
      position:relative; width:100%; height:0; padding:0 0 100%; margin:0;
      font-family:inherit; font-weight:800; text-align:center;
      font-size:var(--umd-font-size-min); line-height:var(--umd-font-size-min);
    }

    .cal-mini-days p { color:var(--umd-color-gray-dark); }

    .cal-mini-days span, .cal-day .num {
      position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    }

    .cal-day {
      display:block; border:0; background:var(--umd-color-white); color:var(--umd-color-black); cursor:pointer;
      transition:background-color .2s, box-shadow .2s;
    }

    .cal-day[data-ismonth="false"] { background:var(--umd-color-gray-lighter); }

    .cal-day[data-ispast="true"] { color:var(--umd-color-gray-dark); }

    /* the source's only "there is something here" cue */
    .cal-day[data-hasevents="true"] .num { text-decoration:underline; }

    .cal-day[data-hasevents="true"]:hover,
    .cal-day[data-hasevents="true"]:focus-visible { background:var(--umd-color-gold); }

    .cal-day[data-hasevents="false"] { cursor:default; }

    .cal-day[data-istoday="true"] { box-shadow:inset 0 0 0 2px var(--umd-color-black); }

    .cal-day[data-isselected="true"] { box-shadow:inset 0 0 0 2px var(--umd-color-red); }

    /* Numeral size follows the RAIL's own width, not the viewport's.
       A media query was tried first and was wrong: at a 760px viewport the
       rail is still at its full 600px (the horizontal lock leaves enough
       room), so a `max-width:1019px and min-width:768px` query switched the
       type back down while the cells were still 81px. A container query asks
       the only question that matters — how wide is this calendar?

         rail 340px (desktop column) -> 48px cells -> 12px
         rail 600px (wrapped band)   -> 81px cells -> 18px
         rail 327px (mobile)         -> 42px cells -> 12px

       This must sit AFTER the base `.cal-mini-days p, .cal-day` rule: the
       selectors are identical, so specificity ties and source order decides.
       Placed before it (as it first was) it loses silently. */
    @container (min-width:480px) {
      .cal-mini-days p, .cal-day {
        font-size:var(--umd-font-size-lg); line-height:var(--umd-font-size-lg);
      }
    }


    /* ============================================================
       FILTER BAND — page-builder "Filter Band" pattern
       (LAYOUT-PATTERNS.md). The panel, control grid, select chrome,
       heading rule and clear-button underline are all upstream DS
       classes; the results count is critical.css §23. Only the tweaks
       below are page CSS.

       The band's text-search half is deliberately unused — the live
       calendar has no search, and four facets over 64 events do not
       need one.
       ============================================================ */
    #cal-filters { margin-bottom:32px; }

    /* the band's heading row puts the h2 and Clear on one line; the DS rule
       gives the first child flex:1 0 auto, so the trailing rule fills */
    #cal-filters .umd-text-line-trailing-light { background-color:var(--umd-color-gray-lighter); }

    /* Box model and colour only -- type comes from .umd-sans-smaller on the
       button itself. This rule used to carry `font:inherit; font-size:14px`,
       which left the button on the browser's default face (a <button> does
       not inherit font-family unless told to, and `inherit` here resolved to
       the form, which sets none) AND outranked any umd-sans-* class the
       button might carry, at 1,1,1 against 0,1,0. Same treatment as the
       representatives filter band. */
    #cal-filters button[type="reset"] {
      background:none; border:0; padding:0; cursor:pointer; color:var(--umd-color-gray-darker);
      white-space:nowrap;
    }

    /* the DS select wrapper supplies the white box and chevron; the select
       itself only needs the box model */
    #cal-filters select { width:100%; padding:12px 16px; border:0; font:inherit; font-size:16px; }

    #cal-filters select:focus-visible { outline:2px solid var(--umd-color-red); outline-offset:-2px; }

    /* active-filter pills use the DS .umd-text-cluster-pill chip (var(--umd-color-gray-lightest), 12px);
       neutralize its wrapping-margin hack and use flex gap instead. */
    /* 32px below, matching the band's own gap above, so the pill row sits in
       its own band of space rather than crowding the month line under it */
    .pf-pills { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-bottom:32px; }

    /* same UA-vs-author trap as .cal-layout[hidden] below: display:flex beats
       the UA sheet's [hidden]{display:none}, so an empty pill row kept leaking
       its 16px margin between the band and the control bar */
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

    .cal-empty { font-size:18px; }

    /* ---- LIST VIEW
       Just the cards. One month per page and the control bar already reads
       that month, so there is no group heading to repeat it — the eyebrow
       ribbon that used to sit here was duplication.

       The cards are direct siblings of #cal-list, which is what upstream
       web-components.min.css needs for its
       `umd-element-event[data-display="list"] + umd-element-event[...]`
       divider (24px + 1px var(--umd-color-gray-light)). Do not wrap them in a section. */

    /* ============================================================
       UPCOMING EVENTS — bordered, image-less event cards, three up

       `umd-element-event` has NO bordered variant. The capability
       exists one layer down — `card.block()` takes `hasBorder` — and
       `umd-element-card` / `umd-element-article` expose it as
       `data-visual-bordered` through `card/_model.ts`. But
       `card/event.ts` has its own `createComponent` that never reads
       `Attributes.isVisual.bordered` and never passes `hasBorder`, so
       the attribute is inert on this element. The registry lists only
       data-display / data-theme / data-visual-transparent /
       data-visual-time. Upstream candidate.

       So the border comes from a shadow injection (end of body) that
       reproduces exactly what `hasBorder` renders on card-standard:
       1px var(--umd-color-gray-light) on .layout-block-stacked-container, 24px padding on
       .layout-block-stacked-text.

       Omitting slot="image" is what makes these image-less. It also
       means no date sign — `card.block` hangs the sign off the image —
       so the date rides in the event meta row instead, exactly as the
       live page's cards do.
       ============================================================ */
    /* Tailwing heading — .umd-text-line-trailing-light (aka
       .umd-tailwing-right-headline[theme="light"]), the same treatment the
       filter band's "FILTER EVENTS" uses. It masks its trailing rule with
       `background-color: inherit` on the <span>, so the <h2> MUST carry an
       explicit background or the rule runs straight through the text. */
    .cal-upcoming-heading { background-color:var(--umd-color-white); margin:0; }

    .cal-upcoming { margin-top:var(--umd-space-xl); }

    @media (max-width:767px) { .cal-upcoming { grid-template-columns:1fr; } }

    @media (min-width:768px) and (max-width:1019px) {
      .cal-upcoming { grid-template-columns:repeat(2,1fr); }
    }

    /* ============================================================
       MONTH PAGER — the `umd-shell-pagination` pattern
       (as on <https://today.umd.edu/tags/athletics>)

       These class names are NOT in any web-styles-library bundle. All
       eight were searched: `umd-shell-*` belongs to the CMS shell layer,
       not the styles package, and `critical.css` carries only the
       utility-nav and person-grid members of that family. So the rules
       below are restated here from the live computed styles — the same
       situation as critical.css §23's `umd-filter-*`. Values measured,
       not guessed.

       Page boxes are numbers, exactly as on the source — page N is the
       Nth month the data covers, so stepping a page steps a month.
       8px gaps, 40×40 boxes, 2px black current, 1px var(--umd-color-gray-light) page, black
       40px steppers going var(--umd-color-gray-light) when disabled, 16px white chevron
       rotated 180° for prev.
       ============================================================ */
    .cal-pager { margin-top:56px; padding-top:32px; border-top:1px solid var(--umd-color-gray-light); }

    .umd-shell-pagination-wrapper,
    .umd-shell-pagination-list {
      display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap;
    }

    .umd-shell-pagination-current,
    .umd-shell-pagination-page-action {
      display:flex; align-items:center; justify-content:center;
      min-width:40px; height:40px; padding:8px;
      background-color:var(--umd-color-white); color:var(--umd-color-black); text-decoration:none;
      font-family:inherit; font-size:18px; font-weight:700; line-height:18px;
    }

    .umd-shell-pagination-current { border:2px solid var(--umd-color-black); }

    .umd-shell-pagination-page-action {
      border:1px solid var(--umd-color-gray-light); cursor:pointer;
      transition:border-color .3s, color .3s;
    }

    .umd-shell-pagination-page-action:hover,
    .umd-shell-pagination-page-action:focus-visible { border-color:var(--umd-color-black); color:var(--umd-color-red); }

    .umd-shell-pagination-ellipsis {
      display:flex; align-items:center;
      font-size:18px; font-weight:700; line-height:18px;
    }

    .umd-shell-pagination-stepper-action {
      flex:0 0 auto; width:40px; height:40px; padding:12px; border:0; cursor:pointer;
      background-color:var(--umd-color-black); display:flex; align-items:center; justify-content:center;
      transition:background-color .3s;
    }

    .umd-shell-pagination-stepper-action:hover:not([disabled]),
    .umd-shell-pagination-stepper-action:focus-visible:not([disabled]) { background-color:var(--umd-color-red); }

    .umd-shell-pagination-stepper-action[disabled] { background-color:var(--umd-color-gray-light); cursor:default; }

    .umd-shell-pagination-stepper-action svg { width:16px; height:16px; fill:var(--umd-color-white); }

    .umd-shell-pagination-stepper-action[data-page="prev"] svg { transform:rotate(180deg); }

    /* ============================================================
       GRID VIEW — full month
       Grid lines are the 1px gap showing through a var(--umd-color-gray-light) backdrop,
       so there are no double borders to collapse. Weekday header row
       and var(--umd-color-gray-lightest) leading/trailing blanks follow the live calendar.

       Unlike the live grid — whose cells carry nothing but a date
       number, making a day with events indistinguishable from an empty
       one — each cell lists its events.
       ============================================================ */
    .cal-grid {
      display:grid; grid-template-columns:repeat(7,1fr); gap:1px;
      background:var(--umd-color-gray-light); border:1px solid var(--umd-color-gray-light);
    }

    /* The grid's lines are the 1px `gap` showing the gray-light backdrop
       through. That is right between date cells, but it would cut the black
       header into seven chips with light seams — so the header cells bleed
       1px outward via box-shadow to fill their own gutters and read as one
       solid band. */
    .cal-wd {
      background-color:var(--umd-color-black); color:var(--umd-color-white);
      box-shadow:0 0 0 1px var(--umd-color-black);
      padding:8px 4px; text-align:center;
      font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.08em;
    }

    .cal-cell { background:var(--umd-color-white); min-height:170px; padding:12px 10px; }

    .cal-cell.is-blank { background:var(--umd-color-gray-lightest); min-height:0; }

    .cal-cell[data-istoday="true"] { box-shadow:inset 0 0 0 2px var(--umd-color-red); }

    .cal-cell-date {
      margin:0 0 10px; font-size:14px; font-weight:700; line-height:1;
      font-variant-numeric:tabular-nums; color:var(--umd-color-black);
    }

    .cal-cell[data-ispast="true"] .cal-cell-date { color:var(--umd-color-gray-medium-a-a); }

    .cal-cell-events { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }

    .cal-cell-events a {
      display:block; padding-left:8px; border-left:2px solid var(--umd-color-red);
      font-size:13px; line-height:1.3; color:var(--umd-color-black); text-decoration:none;
      transition:color .3s;
    }

    .cal-cell-events a:hover, .cal-cell-events a:focus-visible { color:var(--umd-color-red); text-decoration:underline; }

    .cal-cell-time { display:block; color:var(--umd-color-gray-medium-a-a); font-size:12px; font-weight:700; }

    /* days past CELL_LIMIT hide behind a "+N more" toggle rather than
       stretching one week's row to the height of its busiest day */
    .cal-cell.is-collapsed .cal-cell-extra { display:none; }

    .cal-more {
      margin-top:8px; padding:0; background:none; border:0; cursor:pointer;
      font:inherit; font-size:12px; font-weight:700; color:var(--umd-color-gray-dark);
      text-decoration:underline; text-underline-offset:.15em;
    }

    .cal-more:hover, .cal-more:focus-visible { color:var(--umd-color-red); }

    @media (max-width:1019px) {
      .cal-cell { min-height:130px; padding:8px 6px; }
      .cal-cell-events a { font-size:12px; padding-left:6px; }
    }
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
      <h1 slot="headline">Calendar</h1>
    </umd-element-hero>
  </section>

  <!-- EVENTS EXPLORER — control bar, filter band, list or month grid -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">

      <!-- FILTER BAND — page-builder Filter Band pattern -->
      <form id="cal-filters" class="umd-layout-background-highlight-light umd-layout-grid-gap-stacked" data-animation="off" action="#">

        <div class="umd-layout-grid-inline-stretch">
          <h2 class="umd-text-line-trailing-light"><span>Filter Events</span></h2>
          <button type="reset" class="umd-sans-smaller umd-animation-line-slide-graydark-red">
            <span aria-hidden="true">Clear filters</span>
            <span class="sr-only">Clear all filters</span>
          </button>
        </div>

        <div class="umd-layout-grid-gap-four" data-animation="off" id="cal-selects"></div>
      </form>

      <div class="pf-pills" id="pf-pills" hidden></div>

      <!-- CONTROL BAR -->
      <div class="cal-controls">
        <div class="cal-controls-date">
          <button type="button" class="cal-nav" data-dir="prev" id="cal-prev">
            <span class="sr-only">Previous month</span>
            <svg aria-hidden="true" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M63.0351 40L36 13H60.214L95.5269 47.539L95.1858 47.8801L95.5269 48.2212L60.214 82.7602H36L62.795 56H5V40H63.0351Z"></path></svg>
          </button>
          <h2 class="umd-campaign-small" id="cal-month-label">&nbsp;</h2>
          <button type="button" class="cal-nav" data-dir="next" id="cal-next">
            <span class="sr-only">Next month</span>
            <svg aria-hidden="true" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M63.0351 40L36 13H60.214L95.5269 47.539L95.1858 47.8801L95.5269 48.2212L60.214 82.7602H36L62.795 56H5V40H63.0351Z"></path></svg>
          </button>
          <button type="button" class="cal-today" id="cal-today">
            <span aria-hidden="true">Today</span>
            <span class="sr-only">Back to today</span>
          </button>
        </div>

        <div class="cal-view-group" role="group" aria-label="Display events as">
          <button type="button" class="cal-view" data-view="list" aria-pressed="true">
            <span aria-hidden="true">List</span><span class="sr-only">Display as events list</span>
          </button>
          <button type="button" class="cal-view" data-view="grid" aria-pressed="false">
            <span aria-hidden="true">Calendar</span><span class="sr-only">Display as calendar grid</span>
          </button>
        </div>
      </div>

      <!-- LIST VIEW — mini-calendar rail + results -->
      <div class="cal-layout" id="cal-layout">
        <aside class="cal-rail" aria-label="Browse by date">
          <div class="cal-mini">
            <h2 id="cal-mini-label">&nbsp;</h2>
            <div class="cal-mini-days">
              <p><span aria-hidden="true">S</span><span class="sr-only">Sunday</span></p>
              <p><span aria-hidden="true">M</span><span class="sr-only">Monday</span></p>
              <p><span aria-hidden="true">T</span><span class="sr-only">Tuesday</span></p>
              <p><span aria-hidden="true">W</span><span class="sr-only">Wednesday</span></p>
              <p><span aria-hidden="true">T</span><span class="sr-only">Thursday</span></p>
              <p><span aria-hidden="true">F</span><span class="sr-only">Friday</span></p>
              <p><span aria-hidden="true">S</span><span class="sr-only">Saturday</span></p>
            </div>
            <div class="cal-mini-dates" id="cal-dates"></div>
          </div>
        </aside>

        <div class="cal-results">
          <div id="cal-list" role="status" aria-live="polite"></div>
          <p id="cal-empty" class="cal-empty" hidden></p>
          <nav class="cal-pager umd-shell-pagination" id="cal-pager" aria-label="Month navigation"></nav>
        </div>
      </div>

      <!-- GRID VIEW — full bleed, no rail -->
      <div id="cal-grid" hidden></div>

    </div>
  </section>

  <!-- UPCOMING EVENTS — static block, next six from today.
       Bordered, image-less event cards, three up. See the CSS note: the
       border is a shadow injection because umd-element-event does not
       expose data-visual-bordered. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <h2 class="cal-upcoming-heading umd-text-line-trailing-light"><span>Upcoming Events</span></h2>
      <div class="cal-upcoming umd-layout-grid-gap-three" data-animation="off">
          @@UPCOMING@@
      </div>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

@@CHROME:footer@@

  <!-- Calendar data + control-bar / filter / view logic -->
  <script>
  (function () {
    var EVENTS = @@EVENTS@@;
    var FACETS = @@FACETS@@;
    var TODAY  = @@TODAY@@;

    var GROUP_ORDER  = ['audience', 'location', 'type', 'college'];
    var GROUP_LABELS = {
      audience: 'Audience',
      location: 'Location',
      type: 'Event Type',
      college: 'College or School'
    };
    // the "no choice" option label per group, matching the live filter menu
    var GROUP_ALL = {
      audience: 'All Audiences',
      location: 'All Locations',
      type: 'All Event Types',
      college: 'All Colleges & Schools'
    };
    // facet key -> the event field it tests
    var GROUP_FIELD = { audience:'a', location:'l', type:'y', college:'c' };

    var MONTHS = ['January','February','March','April','May','June','July',
                  'August','September','October','November','December'];
    var WEEKDAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

    // events printed in a grid cell before the rest hide behind "+N more"
    var CELL_LIMIT = 3;

    var form       = document.getElementById('cal-filters');
    var selectHost = document.getElementById('cal-selects');
    var layoutEl   = document.getElementById('cal-layout');
    var listHost   = document.getElementById('cal-list');
    var gridHost   = document.getElementById('cal-grid');
    var datesHost  = document.getElementById('cal-dates');
    var emptyEl    = document.getElementById('cal-empty');
    var pagerEl    = document.getElementById('cal-pager');
    var pillsHost  = document.getElementById('pf-pills');
    var monthLabel = document.getElementById('cal-month-label');
    var miniLabel  = document.getElementById('cal-mini-label');

    function esc(s) {
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ---- date helpers. Everything is a 'YYYY-MM-DD' string; no Date object
    // is used for identity, so nothing shifts across a timezone boundary. ----
    function iso(y, m, d) {
      return y + '-' + ('0' + (m + 1)).slice(-2) + '-' + ('0' + d).slice(-2);
    }
    function ymOf(date) { return date.slice(0, 7); }
    function monthTitle(ym) {
      return MONTHS[parseInt(ym.slice(5, 7), 10) - 1] + ' ' + ym.slice(0, 4);
    }
    // the months the data actually covers — the pager and the control-bar
    // arrows both clamp to this so neither can walk off into empty months
    var YM_MIN = EVENTS[0].d.slice(0, 7);
    var YM_MAX = EVENTS[EVENTS.length - 1].d.slice(0, 7);

    // every month in range, so the pager can number and window them
    var YM_ALL = (function () {
      var out = [], cur = YM_MIN;
      while (cur <= YM_MAX) { out.push(cur); cur = shiftYM(cur, 1); }
      return out;
    })();


    // ONE date cursor drives both views: the list shows events on or after it
    // (the live site's ?date= contract) and the grid renders the month that
    // contains it. Month nav moves the cursor; it is not a separate "view
    // month" that could drift out of sync with the list.
    // `from` is the cursor; `picked` records whether the user chose that DAY
    // (mini-calendar click, or Today) as opposed to landing on it by moving
    // months. Only a picked day gets the red ring — month navigation snaps
    // `from` to the 1st, and ringing an empty 1st reads as a selection the
    // user never made.
    var state = { audience:'', location:'', type:'', college:'', from:TODAY, picked:true, view:'list' };

    // ---- build the band's selects ----
    function buildSelects() {
      selectHost.innerHTML = GROUP_ORDER.map(function (key) {
        var opts = (FACETS[key] || []).map(function (o) {
          return '<option value="' + esc(o.title) + '">' + esc(o.title) + ' (' + o.count + ')</option>';
        }).join('');
        return '<div>' +
          '<label class="sr-only" for="f-' + key + '">Filter by ' + GROUP_LABELS[key] + '</label>' +
          '<div class="umd-field-select-wrapper">' +
          '<select id="f-' + key + '" data-group="' + key + '">' +
          '<option value="">' + GROUP_ALL[key] + '</option>' + opts +
          '</select></div></div>';
      }).join('');
    }

    // ---- collect state from the DOM ----
    function collect() {
      GROUP_ORDER.forEach(function (k) {
        var sel = document.getElementById('f-' + k);
        state[k] = sel ? sel.value : '';
      });
    }

    // ---- facet match. Deliberately does NOT test the date — the list and the
    // grid each apply their own date window to this same result. ----
    function matchFacets(e) {
      for (var i = 0; i < GROUP_ORDER.length; i++) {
        var k = GROUP_ORDER[i];
        if (!state[k]) continue;
        var vals = e[GROUP_FIELD[k]];
        vals = (typeof vals === 'string') ? [vals] : (vals || []);
        if (vals.indexOf(state[k]) === -1) return false;
      }
      return true;
    }

    // ---- LIST VIEW ----------------------------------------------------
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

    function renderList(matched) {
      listHost.innerHTML = matched.map(cardHTML).join('');
    }

    // The UMD chevron, same glyph the control-bar arrows use; the prev
    // stepper rotates it 180deg in CSS exactly as today.umd.edu does.
    var CHEVRON = '<svg aria-hidden="true" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">' +
      '<path fill-rule="evenodd" clip-rule="evenodd" d="M63.0351 40L36 13H60.214L95.5269 47.539L95.1858 ' +
      '47.8801L95.5269 48.2212L60.214 82.7602H36L62.795 56H5V40H63.0351Z"></path></svg>';

    function stepper(dir, target, label) {
      var off = !target;
      return '<button type="button" class="umd-shell-pagination-stepper-action" data-page="' + dir + '"' +
        (off ? ' disabled' : '') + ' aria-label="' + esc(label) + '">' + CHEVRON + '</button>';
    }

    // Page N is the Nth month the data covers, so a page step is a month step.
    // The visible label is the number; the month lives in the aria-label.
    function pageBox(n, currentIndex) {
      var ym = YM_ALL[n];
      if (n === currentIndex) {
        return '<span class="umd-shell-pagination-current" aria-label="Current page:">' +
          (n + 1) + '</span>';
      }
      return '<button type="button" class="umd-shell-pagination-page-action" data-goto="' + ym +
        '" aria-label="View page ' + (n + 1) + ' of ' + YM_ALL.length + ', ' + monthTitle(ym) +
        '"><span aria-hidden="true">' + (n + 1) + '</span></button>';
    }

    // First, the current month and its neighbours, and last — with ellipses
    // where the run is broken. Same shape as the source's "1 2 3 4 5 … 18".
    function renderPager(ym) {
      var i = YM_ALL.indexOf(ym);
      var prev = i > 0 ? YM_ALL[i - 1] : null;
      var next = i > -1 && i < YM_ALL.length - 1 ? YM_ALL[i + 1] : null;

      var want = {};
      [0, i - 1, i, i + 1, YM_ALL.length - 1].forEach(function (n) {
        if (n >= 0 && n < YM_ALL.length) want[n] = true;
      });
      var idx = Object.keys(want).map(Number).sort(function (a, b) { return a - b; });

      var boxes = '', last = null;
      idx.forEach(function (n) {
        if (last !== null && n - last > 1) {
          boxes += '<span aria-hidden="true" class="umd-shell-pagination-ellipsis">…</span>';
        }
        boxes += pageBox(n, i);
        last = n;
      });

      pagerEl.innerHTML =
        '<span class="sr-only">Page ' + (i + 1) + ' of ' + YM_ALL.length + ', ' + monthTitle(ym) + '</span>' +
        '<div class="umd-shell-pagination-wrapper">' +
        stepper('prev', prev, prev ? 'Previous month: ' + monthTitle(prev) : 'No earlier months') +
        '<div class="umd-shell-pagination-list">' + boxes + '</div>' +
        stepper('next', next, next ? 'Next month: ' + monthTitle(next) : 'No later months') +
        '</div>';
    }

    // ---- MINI CALENDAR (list view rail) --------------------------------
    // Six weeks from the Sunday on or before the 1st. data-hasevents reflects
    // the FACET filters, not the from-date — otherwise the grid empties out
    // the moment the list scrolls past a month, which is when it is useful.
    function renderMini(ym, faceted) {
      var y = parseInt(ym.slice(0, 4), 10), m = parseInt(ym.slice(5, 7), 10) - 1;

      var hits = {};
      faceted.forEach(function (e) { hits[e.d] = (hits[e.d] || 0) + 1; });

      miniLabel.textContent = MONTHS[m] + ' ' + y;

      var cursor = new Date(y, m, 1 - new Date(y, m, 1).getDay());
      var cells = [];
      for (var i = 0; i < 42; i++) {
        var cy = cursor.getFullYear(), cm = cursor.getMonth(), cd = cursor.getDate();
        var key = iso(cy, cm, cd);
        var count = hits[key] || 0;
        cells.push(
          '<button type="button" class="cal-day" data-date="' + key + '"' +
          ' data-ismonth="' + (cm === m && cy === y) + '"' +
          ' data-ispast="' + (key < TODAY) + '"' +
          ' data-hasevents="' + (count > 0) + '"' +
          ' data-istoday="' + (key === TODAY) + '"' +
          ' data-isselected="' + (state.picked && key === state.from) + '"' +
          (count ? '' : ' disabled') + '>' +
          '<span class="num" aria-hidden="true">' + cd + '</span>' +
          '<span class="sr-only">' + MONTHS[cm] + ' ' + cd + ', ' + cy +
          (count ? ' — ' + count + (count === 1 ? ' event' : ' events') : ' — no events') +
          '</span></button>'
        );
        cursor.setDate(cursor.getDate() + 1);
      }
      datesHost.innerHTML = cells.join('');
    }

    // ---- GRID VIEW -----------------------------------------------------
    // Six weeks from the Sunday on or before the 1st. Leading and trailing
    // cells are blank (no adjacent-month numbers), matching the live grid's
    // .empty-date; a trailing week that is entirely blank is dropped.
    function renderGrid(ym, matched) {
      var y = parseInt(ym.slice(0, 4), 10), m = parseInt(ym.slice(5, 7), 10) - 1;

      var byDay = {};
      matched.forEach(function (e) { (byDay[e.d] = byDay[e.d] || []).push(e); });

      var cells = WEEKDAYS.map(function (w) {
        return '<div class="cal-wd"><span aria-hidden="true">' + w.slice(0, 3) +
          '</span><span class="sr-only">' + w + '</span></div>';
      });

      var lead = new Date(y, m, 1).getDay();
      var days = new Date(y, m + 1, 0).getDate();
      var total = Math.ceil((lead + days) / 7) * 7;

      for (var i = 0; i < total; i++) {
        var day = i - lead + 1;
        if (day < 1 || day > days) { cells.push('<div class="cal-cell is-blank"></div>'); continue; }

        var key = iso(y, m, day);
        var list = byDay[key] || [];
        var extra = list.length - CELL_LIMIT;

        var items = list.map(function (e, n) {
          var time = e.s ? '<span class="cal-cell-time">' + esc(e.s) + '</span>' : '';
          return '<li' + (n >= CELL_LIMIT ? ' class="cal-cell-extra"' : '') + '>' +
            '<a href="' + esc(e.u) + '">' + time + esc(e.n) + '</a></li>';
        }).join('');

        var more = extra > 0
          ? '<button type="button" class="cal-more">+' + extra + ' more</button>'
          : '';

        cells.push(
          '<div class="cal-cell' + (extra > 0 ? ' is-collapsed' : '') + '"' +
          ' data-date="' + key + '"' +
          ' data-ispast="' + (key < TODAY) + '"' +
          ' data-istoday="' + (key === TODAY) + '">' +
          '<p class="cal-cell-date"><time datetime="' + key + '">' + day + '</time>' +
          '<span class="sr-only"> ' + MONTHS[m] + ' ' + day + ', ' + y +
          (list.length ? ' — ' + list.length + (list.length === 1 ? ' event' : ' events') : ' — no events') +
          '</span></p>' +
          (items ? '<ul class="cal-cell-events">' + items + '</ul>' : '') +
          more +
          '</div>'
        );
      }

      gridHost.innerHTML = '<div class="cal-grid">' + cells.join('') + '</div>';
    }

    // ---- render --------------------------------------------------------
    function render() {
      var faceted = EVENTS.filter(matchFacets);
      var ym = ymOf(state.from);
      var isGrid = state.view === 'grid';

      // BOTH views window to the same month. The list used to run from the
      // cursor to the end of the data, which meant the control bar could read
      // AUGUST 2026 above a list that opened in September. One month per page
      // makes the bar an honest label and makes the pager below it meaningful.
      var shown = faceted.filter(function (e) { return ymOf(e.d) === ym; });

      monthLabel.textContent = monthTitle(ym);
      document.getElementById('cal-prev').querySelector('.sr-only').textContent =
        'Previous month: ' + monthTitle(shiftYM(ym, -1));
      document.getElementById('cal-next').querySelector('.sr-only').textContent =
        'Next month: ' + monthTitle(shiftYM(ym, 1));

      layoutEl.hidden = isGrid;
      gridHost.hidden = !isGrid;

      // the grid draws its own empty month (a month with no events is still a
      // month), so the empty state belongs to the list only
      emptyEl.hidden = isGrid || shown.length > 0;
      emptyEl.textContent = hasFacets()
        ? 'No events in ' + monthTitle(ym) + ' match your filters.'
        : 'No events in ' + monthTitle(ym) + '.';

      if (isGrid) {
        renderGrid(ym, shown);
        listHost.innerHTML = '';
      } else {
        renderList(shown);
        renderMini(ym, faceted);
        renderPager(ym);
        gridHost.innerHTML = '';
      }

      renderPills();
    }

    function hasFacets() {
      return GROUP_ORDER.some(function (k) { return !!state[k]; });
    }

    function renderPills() {
      var items = [];
      GROUP_ORDER.forEach(function (k) {
        if (state[k]) items.push({ k:k, label:state[k] });
      });
      if (!items.length) { pillsHost.hidden = true; pillsHost.innerHTML = ''; return; }
      pillsHost.hidden = false;
      pillsHost.innerHTML = '<span class="pf-pills-label">Filtered by:</span>' +
        '<span class="umd-text-cluster-pill pf-pill-cluster">' +
        items.map(function (it) {
          return '<button type="button" class="pf-pill" data-k="' + it.k + '"><span>' +
            esc(it.label) + ' <span aria-hidden="true">×</span></span></button>';
        }).join('') +
        '</span>' +
        '<button type="button" class="pf-clear umd-sans-smaller" id="pf-clearall">Clear all</button>';
    }

    // ---- month arithmetic on a 'YYYY-MM' string ----
    function shiftYM(ym, delta) {
      var y = parseInt(ym.slice(0, 4), 10), m = parseInt(ym.slice(5, 7), 10) - 1 + delta;
      y += Math.floor(m / 12);
      m = ((m % 12) + 12) % 12;
      return y + '-' + ('0' + (m + 1)).slice(-2);
    }

    // ---- events --------------------------------------------------------
    form.addEventListener('submit', function (e) { e.preventDefault(); collect(); render(); });

    form.addEventListener('change', function (e) {
      if (e.target.matches('select')) { collect(); render(); }
    });

    // the band is a plain form with native controls, so type="reset" really
    // resets it — unlike the CTA-wrapped reset the old rail needed. Re-read
    // after the browser has applied the reset.
    form.addEventListener('reset', function () {
      setTimeout(function () { collect(); render(); }, 0);
    });

    pillsHost.addEventListener('click', function (e) {
      if (e.target.closest('#pf-clearall')) { form.reset(); return; }
      var pill = e.target.closest('.pf-pill');
      if (!pill) return;
      document.getElementById('f-' + pill.getAttribute('data-k')).value = '';
      collect(); render();
    });

    // month nav moves the one date cursor, snapping to the 1st. "Today"
    // returns it to today's date, not just today's month.
    function goMonth(delta) {
      var target = shiftYM(ymOf(state.from), delta);
      if (target < YM_MIN || target > YM_MAX) return;
      state.from = target + '-01';
      state.picked = false;
      render();
    }
    document.getElementById('cal-prev').addEventListener('click', function () { goMonth(-1); });
    document.getElementById('cal-next').addEventListener('click', function () { goMonth(1); });
    document.getElementById('cal-today').addEventListener('click', function () {
      state.from = TODAY; state.picked = true; render();
    });

    // a day click in the rail sets the from-date — the same contract as the
    // control bar's month nav, just at day granularity
    // A day click moves the cursor (which may cross into an adjacent month,
    // since the grid shows leading/trailing days) and then scrolls to that
    // day's ribbon. It no longer narrows the list — the month IS the window.
    datesHost.addEventListener('click', function (e) {
      var cell = e.target.closest('.cal-day');
      if (!cell || cell.disabled) return;
      state.from = cell.getAttribute('data-date');
      state.picked = true;
      render();
      var card = listHost.querySelector('umd-element-event[data-date="' + state.from + '"]');
      (card || document.querySelector('.cal-results')).scrollIntoView({ behavior:'smooth', block:'start' });
    });

    // month pager under the list — same cursor as the control-bar arrows
    pagerEl.addEventListener('click', function (e) {
      var goto = e.target.closest('[data-goto]');
      var step = e.target.closest('[data-page]');
      if (goto) {
        state.from = goto.getAttribute('data-goto') + '-01';
        state.picked = false;
        render();
      } else if (step && !step.disabled) {
        goMonth(step.getAttribute('data-page') === 'prev' ? -1 : 1);
      } else {
        return;
      }
      document.querySelector('.cal-controls').scrollIntoView({ behavior:'smooth', block:'start' });
    });

    // view toggle
    document.querySelector('.cal-view-group').addEventListener('click', function (e) {
      var btn = e.target.closest('.cal-view');
      if (!btn) return;
      state.view = btn.getAttribute('data-view');
      document.querySelectorAll('.cal-view').forEach(function (b) {
        b.setAttribute('aria-pressed', String(b === btn));
      });
      render();
    });

    // "+N more" inside a grid cell
    gridHost.addEventListener('click', function (e) {
      var more = e.target.closest('.cal-more');
      if (!more) return;
      var cell = more.closest('.cal-cell');
      var collapsed = cell.classList.toggle('is-collapsed');
      more.textContent = collapsed
        ? '+' + cell.querySelectorAll('.cal-cell-extra').length + ' more'
        : 'Show less';
    });

    buildSelects();
    collect();
    render();
  })();
  </script>

  <!-- UPCOMING EVENTS — border injection.
       Driven by page content, not by the chrome, so it lives here rather
       than in shared/ (see OVERRIDES.md "Chrome vs. page-level shadow
       injections"). -->
  <script>
    (function () {
      // exactly what card.block({ hasBorder: true }) renders on card-standard
      const CARD_BORDER_CSS =
        '.layout-block-stacked-container{border:1px solid var(--umd-color-gray-light)}' +
        '.layout-block-stacked-text{padding:24px}';

      function inject(el) {
        if (!el.shadowRoot || el.__calCardBorderInjected) return;
        const style = document.createElement('style');
        style.textContent = CARD_BORDER_CSS;
        el.shadowRoot.appendChild(style);
        el.__calCardBorderInjected = true;
      }
      function applyAll() {
        document.querySelectorAll('.cal-upcoming-card').forEach(inject);
      }
      customElements.whenDefined('umd-element-event').then(() => {
        applyAll();
        setTimeout(applyAll, 0);
        setTimeout(applyAll, 250);
        setTimeout(applyAll, 1000);
      });
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
body = BODY.replace('@@UPCOMING@@', upcoming_html)
body = body.replace('@@EVENTS@@', events_json)
body = body.replace('@@FACETS@@', facets_json)
body = body.replace('@@TODAY@@', today_json)
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
