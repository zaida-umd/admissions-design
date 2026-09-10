# Calendar — brief

**Output:** `pages/calendar/index.html` (generated — run `python3 scripts/build-calendar.py`)
**Data:** `briefs/calendar-data.json`

## What this page is

The admissions events calendar, recreated in the design system. Replaces
<https://admissions.umd.edu/calendar?date=2026-08-20&layout=list>.

One layout: a **filter rail on the left and a flat, chronological event list on
the right**, modelled on <https://calendar.umd.edu/search>.

| Piece | Comes from |
|---|---|
| Event rows | `umd-element-event data-display="list"` (DS event card, list variant) |
| Filter rail | the programs page's rail (`scripts/build-programs.py`) — same `pf-*` markup, accordions, "Show all N", pills and reset CTA |
| Date range picker | the Start/End `input[type=date]` pair on <https://calendar.umd.edu/search> |
| Load More | the live search page's "Load More Events" button |

There is no search field. The live calendar's own list has none, and the search
page's text input was dropped here deliberately — four facets and a date range
over 64 events do not need one.

### Simplified 2026-09-10

The page used to carry a month cursor with a prev/next/Today control bar, a
List | Calendar toggle, a full month grid, a mini-calendar rail, a
`umd-shell-pagination` month pager, and a static "Upcoming Events" block. All of
it is gone. The last one went because with the list running from today it was
literally its own first six rows; everything else went with the month cursor,
which no longer has anything to drive now that pagination counts events rather
than months.

## Content

64 real events harvested 2026-08-20 from the live admissions calendar — the
month list pages (`?date=…&layout=list`) for Aug 2026 through Aug 2027, plus
every event's own detail page for the fields the list view omits (event type,
audience, full description, register link, feature image). Four entries the
live site publishes with an empty detail page were dropped.

Event images are the three the source uses, downloaded to `images/calendar/`
rather than hotlinked from the Craft CDN (its URLs carry a signature tied to
the exact `w`/`h` params, so they can't be resized or reliably deep-linked).

Facet vocabularies match the live filter menu:

| Group | Values |
|---|---|
| Audience | Prospective Students · Admitted/Enrolled Students |
| Location | On Campus · Virtual |
| Event Type | Academic Programs · Important Deadlines · Tours & Information Sessions |
| College or School | the eight colleges that actually tag events |

The live site nests colleges *inside* its Event Type select, so that one
control mixes two dimensions. Here they are their own rail group, which is what
lets a reader hold a college and an event type at the same time.

## Behavior

- **Page order is** rail (left) → pills → count line → results → Load More.
  Below 1020px the rail collapses behind a black "Filter events" toggle and
  stacks above the results, exactly as the programs rail does.
- **The rail is the programs rail**, down to the accordion glyph: two 12x2 bars
  at the same spot, `::before` horizontal and `::after` upright, so a closed
  group reads "+" and opening rotates `::after` flat into "-". Both bars are
  required — hiding one leaves a bare vertical stroke that is a plus at no
  point. Accordion groups, checkboxes with counts,
  a "Show all N" toggle on any group over seven options (here only College or
  School), removable "Filtered by:" pills, and an outline "Reset filters" CTA.
  It is a copy rather than a shared partial because these two pages are its
  only users and the build scripts have no include mechanism — if a third page
  wants it, extract then.
- **Facets are multi-select** (checkboxes), AND across groups, OR within one.
  The old page used single `<select>`s; the rail's checkboxes are what make it
  behave like the programs page.
- **Date is the first group**, matching the live search page, and holds two
  native `input[type=date]` fields **side by side** with a "to" between them —
  the same row the example uses. Native rather than a scripted picker: the
  browser's own popup is keyboard- and screen-reader-complete, localises
  itself, and costs no JS. `min`/`max` are stamped from the data range at build
  time so the popup can't wander into empty years.
- **The field chrome is upstream, not page CSS.** `.umd-field-input` and
  `.umd-field-input-date-time-wrapper` (element.min.css) are the same pair the
  live search page uses; they carry the border, padding, Interstate face, the
  gray-to-red calendar glyph and the rules hiding the native webkit indicator
  behind it. Only the flex row is page CSS. A first pass hand-rolled all of it,
  which critical.css's own header warns against.
- **The rail is a query container** so the date type keys off the rail's width,
  not the viewport's. Below ~308px of rail the DS base size runs the date text
  under the calendar glyph, which is absolutely placed and can't reflow; the
  rail only reaches that band between 1020px (where it is 277px, its narrowest
  — below 1020 it stacks full width) and about 1130px. The example does the
  same thing, dropping its fields to 12px where its rail is narrow.
- **Start date is pre-filled with today** (2026-08-20) rather than left blank,
  so the window that is actually running is visible in the control instead of
  being implied. "Reset filters" and the pill's × return here, not to a blank
  field. That default is also why the date pill only appears once the range
  *differs* from it — otherwise every visit would open with a chip the reader
  never chose.
- **Every date is a string comparison.** `new Date('2026-09-01')` is UTC
  midnight and prints as Aug 31 west of Greenwich, so nothing on this page is
  parsed into a `Date`; the list is sorted at build time instead.
- **Pagination is by count: 15 events, then a "Load More Events" button.**
  The count line reads "Showing 15 of 51 events" while more remain and collapses
  to a plain total once the list is complete. Any filter change returns to page
  one — leaving the offset alone would show "45 of 3", or hold a scroll position
  in rows that no longer exist. Load More moves focus to the first newly
  revealed card, since the button it was on may have just disappeared.
- **No group heading in the list.** The cards sit directly in `#cal-list` with
  no wrapper — that adjacency is what gives them their upstream divider.
- **Both CTAs listen on their light-DOM wrapper.** `umd-element-call-to-action`
  clones its `<button>` into shadow DOM, so the visible click never reaches the
  original; Reset filters and Load More both catch the retargeted composed click
  on the wrapper instead.

## Notes

- `umd-element-event` reads its date from the `<time>` element's **text
  content**, not the `datetime` attribute (`parseDateFromElement`). The slot is
  `start-date-iso`, not `date-start-iso` — the component's own JSDoc is wrong
  here; `Slots.name.DATE_START_ISO` resolves to `start-date-iso`.
- `data-visual-time` is opt-**out**, not opt-in — `Attributes.isVisual.showTime`
  defaults to `true`, so an all-day deadline with the attribute absent renders
  "12:00am". Every card emits it explicitly: `"true"` when timed, `"false"`
  when all-day.
- `end-date-iso` repeats the start stamp. Without it the DS event meta prints
  "Thu. Aug 20 - undefined. undefined undefined". See OVERRIDES.md.
- Consecutive `umd-element-event[data-display="list"]` siblings get their
  24px + top-rule divider from upstream `web-components.min.css`. Don't add it.
- The hero is `umd-element-hero data-layout-height="small" data-layout-text="center"`
  with an eyebrow and a headline — matching the live page, which carries a
  breadcrumb and an `h1` and
  nothing else. An earlier revision used a standard background hero with a
  supporting paragraph and a "Plan Your Visit" CTA; that copy was invented here,
  not taken from the source, and is gone.
