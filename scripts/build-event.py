#!/usr/bin/env python3
"""Regenerate event detail pages under pages/calendar/.

Sources
  briefs/calendar-data.json           64 events harvested from the live
                                      admissions calendar (see build-calendar.py)
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Outputs
  pages/calendar/<detail_page>.html   one page per event record that carries
                                      a "detail_page" field in calendar-data.json

Usage:
    python3 scripts/build-event.py                          # every flagged event
    python3 scripts/build-event.py bmgt-smith-friday-92526-900am.html

Adding an event's page is a data edit, not a code edit: add "detail_page" (and,
if the CMS-only fields below aren't already on the record, "register" /
"address") to its entry in briefs/calendar-data.json and re-run. Do not
hand-edit the generated HTML -- it is overwritten wholesale.

Why this exists as its own script rather than folding into build-calendar.py
  The calendar landing page is a client-side explorer -- it embeds the whole
  64-event JSON array and renders cards with JS (see build-calendar.py's
  cardHTML). A single event's detail page has nothing to filter or paginate,
  so it is rendered once, server-side, in Python -- like the admission-reps
  bio pages, not like the calendar list.

Design: the right-hand info rail
  Built from the same design-system primitives the calendar page's cards use
  (umd-element-event-sign's date-sign classes, umd-element-event-meta's icon
  row) but hand-assembled rather than driven by <umd-element-event>: that
  component's slots produce one compact meta line, not the labeled
  Date & Time / Location / Event Type / Audience fields this page needs.

  Each field's icon+text row reuses the real umd-element-event-meta-item
  class (same typography, same 18px icon column, same calendar/clock/pin
  icon SVGs the design system ships) -- but the DS only makes that class lay
  out icon-beside-text via position selectors on its own
  umd-element-event-meta-wrapper ('> *:first-child > *' / '> *:not(:first-
  child)'), which a standalone item outside that wrapper never matches (icon
  and text stack instead). This page supplies that one missing rule itself
  rather than reproducing the wrapper's fragile position-dependent nesting.

  Event Type / Audience use the DS's pill-list class
  (umd-text-cluster-pill), one pill per value, per LAYOUT-PATTERNS.md's
  "Active-filter chips" note (neutralise the container's negative
  margin-top hack with flex gap).

  "Upcoming Events" reproduces the bordered, image-less three-up card grid
  the calendar page used to close with (removed 2026-09-10 simplification,
  commit 015bb3c) -- see OVERRIDES.md "Upcoming Events — and the
  bordered-event-card gap": umd-element-event has no working
  data-visual-bordered (confirmed inert), so the border is a page-level
  shadow injection reproducing exactly what card.block({hasBorder:true})
  renders on card-standard.
"""
import json, os, re, sys
import html as _html
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
DATA = os.path.join(REPO, 'briefs/calendar-data.json')
OUTDIR = os.path.join(REPO, 'pages', 'calendar')
DEPTH = _chrome.depth_of(os.path.join(OUTDIR, 'x.html'))   # pages/calendar/ -> '../../'

IMG_PREFIX = '../' * DEPTH + 'images/calendar/'

# Icon SVGs -- copied verbatim from the design system's own icon package
# (design-system/packages/icons/source/{calendar,location}/index.ts) so the
# icon markup matches what umd-element-event-meta renders internally.
ICON_CALENDAR = '<svg title="calendar icon" aria-hidden="true" viewBox="0 0 14 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M1.48311 0H3.46959V1.66667H10.7534V0H12.7399V1.66667H13.8986V4.33333H0.158783V1.66667H1.48311V0ZM13.8986 5.33333H0.158783V14.1667H13.8986V5.33333Z" fill="#454545"/></svg>'
ICON_CLOCK = '<svg title="clock icon" aria-hidden="true" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg"><g><path fill-rule="evenodd" clip-rule="evenodd" d="M8.83804 15.8332C12.8608 15.8332 16.1218 12.5499 16.1218 8.49984C16.1218 4.44975 12.8608 1.1665 8.83804 1.1665C4.81532 1.1665 1.55426 4.44975 1.55426 8.49984C1.55426 12.5499 4.81532 15.8332 8.83804 15.8332ZM12.3062 8.78831L9.29439 8.956L9.51624 4.71753L8.03757 3.2288L7.51459 10.2691L7.47224 10.7914L7.47581 10.7911L7.47554 10.7947L9.20559 10.6525L9.20571 10.6502L13.7848 10.277L12.3062 8.78831Z" fill="#454545"/></g></svg>'
ICON_PIN = '<svg title="pin icon" aria-hidden="true" viewBox="0 0 14 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5.7842 0.5C2.86055 0.5 0.481873 2.59352 0.481873 5.16668C0.481873 5.93914 0.701308 6.70504 1.11846 7.38436L5.49424 14.3496C5.55249 14.4425 5.6635 14.5 5.7842 14.5C5.9049 14.5 6.0159 14.4425 6.07416 14.3496L10.4516 7.38207C10.8671 6.70504 11.0865 5.93911 11.0865 5.16665C11.0865 2.59352 8.70784 0.5 5.7842 0.5ZM5.7842 8.16667C4.32237 8.16667 3.29972 6.95325 3.29972 5.66668C3.29972 4.3801 4.32237 3.16669 5.7842 3.16669C7.24602 3.16669 8.26868 4.3801 8.26868 5.66668C8.26868 6.95325 7.24602 8.16667 5.7842 8.16667Z" fill="#454545"/></svg>'

MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

UPCOMING_COUNT = 3   # fills one row of the 3-up grid


def e(s):
    return _html.escape(s or '', quote=True)


def parse_date(d):
    return datetime.date.fromisoformat(d)


def start24(rec):
    """'3:00 PM' -> '15:00'. All-day events sort to the top of their day."""
    if rec['allDay'] or not rec.get('start'):
        return None
    hh, mm = rec['start'][:-3].strip().split(':')
    hh = int(hh) % 12
    if rec['start'].strip().upper().endswith('PM'):
        hh += 12
    return '%02d:%s' % (hh, mm)


def full_date_text(rec):
    d = parse_date(rec['date'])
    return d.strftime('%A, %B ') + str(d.day) + d.strftime(', %Y')


def full_address(rec):
    addr = rec.get('address')
    if not addr:
        return None
    return ', '.join(p for p in [addr.get('venue'), addr.get('street'), addr.get('city')] if p)


def type_values(rec):
    return list(rec.get('types', [])) + list(rec.get('colleges', []))


def audience_values(rec):
    return list(rec.get('audience', []))


def pill_list_html(values):
    items = '\n'.join('          <span>%s</span>' % e(v) for v in values)
    return '<div class="umd-text-cluster-pill">\n%s\n        </div>' % items


# ---------------------------------------------------------------- head
tpl = open(TEMPLATE, encoding='utf-8').read().split('\n')
crit_end = next(i for i, l in enumerate(tpl) if l.strip() == '</style>')
head_close = next(i for i, l in enumerate(tpl) if l.strip() == '</head>' and i > crit_end)
HEAD_TOP = _chrome.with_robots('\n'.join(tpl[:crit_end]))
HEAD_TAIL_OPEN = '\n'.join(tpl[crit_end:head_close])
assert 'cdn.js' in HEAD_TAIL_OPEN, 'TEMPLATE head is missing the cdn.js script tag'


def head_for(title):
    return re.sub(r'<title>.*?</title>', '<title>' + e(title) + '</title>', HEAD_TOP, count=1)


# ---------------------------------------------------------------- page CSS
PAGE_CSS = '''
    /* ============================================================
       EVENT DETAIL PAGE — content + info rail, and the Upcoming
       Events grid. No page colour variables: every colour is a DS
       token from tokens.min.css, same as the calendar page.
       ============================================================ */

    /* --- content + rail ------------------------------------------
       Stacks on mobile in DOM order (main content, then the rail) --
       no order:-1 flip; see the zig-zag pattern notes in CLAUDE.md
       for why this project avoids that. 1024px matches the DS's own
       desktop.min breakpoint. */
    .event-layout { display: block; }

    @media (min-width: 1024px) {
      .event-layout { display: flex; align-items: flex-start; gap: 64px; }
      .event-main { flex: 1; min-width: 0; }
      .event-rail { width: 360px; flex: none; }
    }

    .event-main figure { margin-top: 32px; }
    .event-main img { display: block; width: 100%; height: auto; }

    /* --- rail fields -----------------------------------------------
       Plain white -- same background the trailing-rule label already
       paints on itself (composeTrailing's default theme). A gray card
       behind it put two different whites next to each other, which is
       what read as broken; the fix is to not fight it with a second
       background. */
    .event-rail-field + .event-rail-field { margin-top: 32px; }

    /* umd-text-line-trailing (composeTrailing's default theme) sets no
       text `color` of its own -- only elements.labelSmall (font/size/
       letter-spacing/line-height), and composeTrailing itself sets only
       backgroundColor:white for this theme. The rule (::before) is
       already color.black unconditionally, so it renders correctly with
       no help. The label TEXT does not: on an <h2> (e.g. the Upcoming
       Events heading below) that is enough to read black regardless,
       because critical.css/base.min.css set no competing h2 color and
       inheritance wins by default. On a <p> -- every field label here --
       base.min.css's bare `p{color:#454545}` directly matches the
       element and beats inheritance (same root cause as the date-sign
       fix above), so the label read gray-dark instead of black. Verified
       against the live reference for this exact class
       (umdrightnow.umd.edu/experts's "REFINE" / "Filter Experts",
       umd-tailwing-right-headline / umd-text-line-trailing-light): both
       compute color:#000 there too -- they just happen to be <h2>s, so
       they never hit the collision this page's <p> labels do. */
    .event-rail-field .umd-text-line-trailing { color: var(--umd-color-black); }

    /* umd-element-event-sign-container ships no box and no colour: the
       plain umd-sans-small / umd-sans-extralarge classes only get a
       `color` declaration when composed with a theme
       (packages/styles/source/typography/sans.ts `compose()` — color is
       set only inside `...(theme && {color: finalColor})`), and the
       static exports these classes come from call compose() with no
       theme. So the date sign otherwise just inherits whatever colour
       its context happens to be — pin it to the token explicitly.

       The rule has to target .event-sign-start (the <p>) directly, not
       just the container div: base.min.css ships a bare `p{color:
       #454545}` element rule, and a rule that DIRECTLY matches an
       element always wins over an inherited value, no matter how much
       higher the inherited rule's specificity was one level up. Setting
       color only on the container left the container itself black while
       its <p> (and the spans inside it) stayed gray-dark. */
    .umd-element-event-sign-container,
    .event-sign-start { color: var(--umd-color-black); }

    /* umd-element-event-meta-item is only ever laid out icon-beside-
       text by umd-element-event-meta-wrapper's position selectors
       (> *:first-child > *, > *:not(:first-child)) — a standalone item
       outside that wrapper matches neither, so icon and text stack.
       Same class, same icon sizing/colour/typography; this just adds
       the one rule the wrapper would have supplied.

       align-items: flex-start, not center — the wrapper's own rule for
       the location row (the one likely to wrap: "> *:not(:first-child)")
       sets display:flex with no align-items of its own (so it does not
       center either), and center reads wrong the moment location wraps
       to a second line, pulling the pin icon down to the middle of both
       lines instead of sitting level with the first. */
    .event-rail-field .umd-element-event-meta-item {
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }
    .event-rail-field .umd-element-event-meta-item + .umd-element-event-meta-item {
      margin-top: 8px;
    }

    /* Event Type / Audience — umd-text-cluster-pill, one pill per value.
       Per LAYOUT-PATTERNS.md's "Active-filter chips" note: neutralise the
       container's margin-top:-8px hack and the children's matching
       margin-top:8px with flex + gap, or wrapped rows double up. */
    .event-rail-field .umd-text-cluster-pill {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 0;
    }
    .event-rail-field .umd-text-cluster-pill > * {
      margin-top: 0;
    }

    .event-rail-actions {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .event-rail-actions umd-element-call-to-action { display: block; }

    /* --- Upcoming Events — bordered, image-less card grid, three up
       (the calendar page's own pre-2026-09-10 "Upcoming Events" block;
       see OVERRIDES.md). Border comes from a shadow injection, not this
       CSS -- umd-element-event has no working data-visual-bordered. */
    .event-upcoming-heading { background-color: var(--umd-color-white); margin: 0; }

    .event-upcoming-grid { margin-top: var(--umd-space-xl); }

    @media (max-width: 767px) { .event-upcoming-grid { grid-template-columns: 1fr; } }

    @media (min-width: 768px) and (max-width: 1019px) {
      .event-upcoming-grid { grid-template-columns: repeat(2, 1fr); }
    }
'''


# ---------------------------------------------------------------- upcoming-events cards
def summarize(s, limit=160):
    if not s:
        return ''
    if len(s) <= limit:
        return s
    cut = s[:limit]
    return cut[:cut.rfind(' ')] + '…'


def upcoming_card_html(rec):
    """Bordered, image-less block card -- default umd-element-event layout
    (no data-display), matching the calendar page's old Upcoming Events grid.
    Default layout never renders a date sign (OVERRIDES.md's dateSign table),
    so the date rides in the event meta row only, exactly as before."""
    t = start24(rec)
    stamp = '%sT%s:00' % (rec['date'], t or '00:00')
    text_html = ''
    if rec.get('description'):
        text_html = '<p slot="text">%s</p>' % e(summarize(rec['description']))
    actions_html = ''
    if rec.get('register'):
        actions_html = (
            '<div slot="actions"><umd-element-call-to-action data-display="secondary">'
            '<a href="%s" target="_blank" rel="noopener">%s</a>'
            '</umd-element-call-to-action></div>'
            % (e(rec['register']['url']), e(rec['register'].get('label', 'Register'))))
    href = rec.get('detail_page') or rec['url']
    return (
        '<umd-element-event class="event-upcoming-card" data-visual-time="%s">'
        '<h3 slot="headline"><a href="%s">%s</a></h3>'
        '%s'
        '<time slot="start-date-iso" datetime="%s">%s</time>'
        '<time slot="end-date-iso" datetime="%s">%s</time>'
        '<p slot="location">%s</p>'
        '%s'
        '</umd-element-event>'
        % ('true' if t else 'false',
           e(href), e(rec['title']),
           text_html,
           stamp, stamp, stamp, stamp,
           e(rec['location']),
           actions_html)
    )


def pick_upcoming(all_events, current, count=UPCOMING_COUNT):
    """Next `count` events strictly after `current`, chronological, self excluded."""
    def key(r):
        return (r['date'], start24(r) or '')
    cur_key = key(current)
    later = [r for r in all_events
             if r is not current and key(r) > cur_key]
    later.sort(key=key)
    return later[:count]


# ---------------------------------------------------------------- page
def render_event(rec, upcoming):
    out = os.path.join(OUTDIR, rec['detail_page'])
    d = parse_date(rec['date'])
    month = MONTH_ABBR[d.month - 1]
    day = str(d.day)

    address = full_address(rec)
    location_text = address or rec['location']

    types = type_values(rec)
    audience = audience_values(rec)

    register_html = ''
    if rec.get('register'):
        register_html = (
            '''<umd-element-call-to-action data-display="primary">
            <a href="%s" target="_blank" rel="noopener">%s</a>
          </umd-element-call-to-action>'''
            % (e(rec['register']['url']), e(rec['register'].get('label', 'Register Now'))))

    image_html = ''
    if rec.get('image'):
        image_html = '''
        <figure class="umd-layout-alignment-block-stacked">
          <img src="%s" alt="%s" />
        </figure>''' % (e(IMG_PREFIX + rec['image']['file']), e(rec['image'].get('alt', '')))

    # The source page has no heading over its description -- just copy. The
    # first paragraph carries umd-sans-large (the one size class that is NOT
    # inert inside .umd-text-rich-advanced, per CLAUDE.md's lede rules,
    # because it is already the block's own collapsed 18px) so it reads with
    # a touch more weight than the paragraph(s) that follow -- the same class
    # combination (umd-sans-large text-black) frederick-douglass-
    # scholarship.html uses for its own in-rich-text lede.
    desc_paragraphs = [p for p in rec['description'].split('\n') if p.strip()]
    description_parts = []
    for i, p in enumerate(desc_paragraphs):
        cls = ' class="umd-sans-large text-black"' if i == 0 else ''
        description_parts.append('<p%s>%s</p>' % (cls, e(p)))
    description_html = '\n          '.join(description_parts)

    upcoming_html = '\n        '.join(upcoming_card_html(u) for u in upcoming)

    type_field = ''
    if types:
        type_field = '''
              <div class="event-rail-field">
                <p class="umd-text-line-trailing"><span>Event Type</span></p>
                %s
              </div>
''' % pill_list_html(types)

    audience_field = ''
    if audience:
        audience_field = '''
              <div class="event-rail-field">
                <p class="umd-text-line-trailing"><span>Audience</span></p>
                %s
              </div>
''' % pill_list_html(audience)

    return '''%(head)s
%(head_tail)s

  <!-- Page CSS gets its OWN style block, after cdn.js -- see the same note
       in scripts/build-representatives.py: page CSS must not land inside the
       inlined critical.css block above, or tools/inline-critical.py deletes
       it on the next pass. -->
  <style>%(css)s  </style>
%(chrome_css)s
%(gate)s
</head>
<body>

%(header)s

  <main id="main-content">
    <!-- 2. HERO — minimal, dark, chevron pattern. Same treatment every
         interior page in this project uses; eyebrow is the parent section. -->
    <section>
      <umd-element-hero-minimal data-theme="dark">
        <p slot="eyebrow">Calendar</p>
        <h1 slot="headline">%(title)s</h1>
        <img slot="image" src="%(root)simages/shared/interior-hero-pattern.png" alt="" />
      </umd-element-hero-minimal>
    </section>

    <!-- 3. BREADCRUMB -->
    <div class="umd-layout-space-horizontal-larger umd-layout-space-vertical-interior">
      <umd-element-breadcrumb>
        <div slot="paths">
          <a href="%(root)spages/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
          <a href="index.html"><span>Calendar</span></a>
          <p aria-label="Current Page"><span>%(title)s</span></p>
        </div>
      </umd-element-breadcrumb>
    </div>

    <!-- 4. CONTENT + INFO RAIL — main column left, event details right.
         The rail reuses the event-sign date-sign classes and the
         event-meta calendar/clock/pin icons the calendar page's cards use,
         hand-assembled into labeled fields (Date & Time / Location / Event
         Type / Audience) rather than the compact single-line meta the
         <umd-element-event> component itself renders. -->
    <section class="umd-layout-space-vertical-interior">
      <div class="umd-layout-space-horizontal-larger">
        <div class="event-layout">
          <div class="event-main">
            <div class="umd-text-rich-advanced">
              %(description)s
            </div>%(image)s
          </div>

          <aside class="event-rail">
            <div class="event-rail-field">
              <div class="umd-element-event-sign-container">
                <p class="event-sign-start">
                  <span class="umd-sans-small">%(month)s</span>
                  <span class="umd-sans-extralarge">%(day)s</span>
                </p>
              </div>
            </div>

            <div class="event-rail-field">
              <p class="umd-text-line-trailing"><span>Date &amp; Time</span></p>
              <p class="umd-element-event-meta-item">
                <span>%(icon_calendar)s</span>
                <span>%(date_text)s</span>
              </p>
              <p class="umd-element-event-meta-item">
                <span>%(icon_clock)s</span>
                <span>%(start_time)s</span>
              </p>
            </div>

            <div class="event-rail-field">
              <p class="umd-text-line-trailing"><span>Location</span></p>
              <p class="umd-element-event-meta-item">
                <span>%(icon_pin)s</span>
                <span>%(location)s</span>
              </p>
            </div>
%(type_field)s%(audience_field)s
            <div class="event-rail-field event-rail-actions">
              %(register)s
              <umd-element-call-to-action data-display="secondary">
                <a href="index.html">Back to Calendar</a>
              </umd-element-call-to-action>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <!-- 5. UPCOMING EVENTS — bordered, image-less card grid, three up.
         Reproduces the calendar page's own pre-2026-09-10 closing block
         (see OVERRIDES.md "Upcoming Events — and the bordered-event-card
         gap"); the border is a shadow injection below, not CSS. -->
    <section class="umd-layout-space-vertical-interior">
      <div class="umd-layout-space-horizontal-larger">
        <h2 class="event-upcoming-heading umd-text-line-trailing"><span>Upcoming Events</span></h2>
        <div class="event-upcoming-grid umd-layout-grid-gap-three" data-animation="off">
        %(upcoming)s
        </div>
      </div>
    </section>

    <!-- 6. STAY CONNECTED — banner promo, per-site page closer convention.
         Wrapped in the -larger lock per RULES.md's carousel/banner-promo
         matrix. -->
    <section class="umd-layout-space-vertical-interior">
      <div class="umd-layout-space-horizontal-larger">
        <umd-element-banner-promo>
          <h2 slot="headline">There is a lot more to learn about UMD</h2>
          <p slot="text">Let&rsquo;s stay in touch! <a href="https://apply.umd.edu/register/request-info" target="_blank" rel="noopener noreferrer">Join the mailing list</a> or <a href="https://admissions.umd.edu/connect">connect</a>!</p>
          <div slot="actions">
            <umd-element-call-to-action data-display="primary">
              <a href="https://apply.umd.edu/register/request-info" target="_blank" rel="noopener noreferrer">Subscribe</a>
            </umd-element-call-to-action>
          </div>
        </umd-element-banner-promo>
      </div>
    </section>

    <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>
  </main>

%(footer)s

  <!-- UPCOMING EVENTS — border injection. umd-element-event has no working
       data-visual-bordered (OVERRIDES.md: confirmed inert by A/B against the
       shadow node), so this reproduces exactly what card.block({hasBorder:
       true}) renders on card-standard: 1px gray-light on
       .layout-block-stacked-container, 24px padding on
       .layout-block-stacked-text. Driven by page content, not chrome, so it
       lives here rather than in shared/. -->
  <script>
    (function () {
      var CARD_BORDER_CSS =
        '.layout-block-stacked-container{border:1px solid var(--umd-color-gray-light)}' +
        '.layout-block-stacked-text{padding:24px}';

      function inject(el) {
        if (!el.shadowRoot || el.__eventCardBorderInjected) return;
        var style = document.createElement('style');
        style.textContent = CARD_BORDER_CSS;
        el.shadowRoot.appendChild(style);
        el.__eventCardBorderInjected = true;
      }
      function applyAll() {
        document.querySelectorAll('.event-upcoming-card').forEach(inject);
      }
      customElements.whenDefined('umd-element-event').then(function () {
        applyAll();
        setTimeout(applyAll, 0);
        setTimeout(applyAll, 250);
        setTimeout(applyAll, 1000);
      });
    })();
  </script>

%(chrome_scripts)s

</body>
</html>
''' % dict(
        head=head_for('%s — Undergraduate Admissions | University of Maryland' % rec['title']),
        head_tail=HEAD_TAIL_OPEN,
        css=PAGE_CSS,
        chrome_css=_chrome.block('chrome-css', out),
        gate=_chrome.block('gate', out),
        header=_chrome.block('header', out),
        footer=_chrome.block('footer', out),
        chrome_scripts=_chrome.block('chrome-scripts', out),
        root=_chrome.ROOT_TOKEN,
        title=e(rec['title']),
        description=description_html,
        image=image_html,
        month=month, day=day,
        icon_calendar=ICON_CALENDAR, icon_clock=ICON_CLOCK, icon_pin=ICON_PIN,
        date_text=e(full_date_text(rec)),
        start_time=e(rec['start']) if not rec['allDay'] else 'All day',
        location=e(location_text),
        type_field=type_field,
        audience_field=audience_field,
        register=register_html,
        upcoming=upcoming_html,
    )


# ---------------------------------------------------------------- main
def write(path, text):
    text = text.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
    print('wrote', os.path.relpath(path, REPO), len(text.split('\n')), 'lines')


def main():
    doc = json.load(open(DATA, encoding='utf-8'))
    events = doc['events']
    flagged = [r for r in events if r.get('detail_page')]
    by_slug = {r['detail_page']: r for r in flagged}

    if sys.argv[1:]:
        for slug in sys.argv[1:]:
            if slug not in by_slug:
                raise SystemExit('unknown event detail_page "%s" -- valid: %s'
                                 % (slug, ', '.join(sorted(by_slug))))
            rec = by_slug[slug]
            write(os.path.join(OUTDIR, slug), render_event(rec, pick_upcoming(events, rec)))
        return

    for rec in flagged:
        write(os.path.join(OUTDIR, rec['detail_page']), render_event(rec, pick_upcoming(events, rec)))


if __name__ == '__main__':
    main()
