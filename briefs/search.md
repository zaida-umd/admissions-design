# Search — `pages/search/index.html`

Source: <https://admissions.umd.edu/search> (captured 2026-09-04).

## What the live page does

`main > .search-page` is an `<h1>`, a form, a `.feedback` count, a thick rule,
then `.results > .list`. Every result is a bare `<div>` with an `h2` and a
`.rich-text` blurb — **no images anywhere**, and no pagination: a query returns
the whole set (99 rows for "scholarships", which is every indexed page, so the
term is barely filtering). Promoted rows are the same `<div>` plus
`class="featured"` and a `<p class="category">featured</p>` label; they are the
only rows carrying any styling of their own.

The query lives in `?q=`, so an executed search is linkable.

## What this prototype changes

| Live | Prototype |
|---|---|
| `h1` on a plain white band | `umd-element-hero data-layout-height="small" data-layout-text="center"` + image |
| Bare form | `umd-layout-background-highlight-light` band + `.umd-filter-search-row` |
| `div` + `h2` + `.rich-text` | `umd-element-card data-display="list"` |
| Flat run of results | `.umd-filter-list` divider list (1px `#d0d0d0` rules) |
| `.featured` rows, unstyled | one 1px black box, red `Featured` eyebrow |
| No empty/idle state | "Popular searches" pills; a "No results" panel |

## Component and class choices

- **Hero** — background hero, small, centred: the same treatment as every
  section landing page (academics, student-life, how-to-apply, tuition,
  apply-now), so search does not read as a different kind of page. Headline
  only — a paragraph between the `h1` and the input is one thing to read
  before the only control that matters.
- **Hero image is shared with `pages/calendar/`** (`images/calendar/
  blurry-testudo-…webp`). Both are utility pages, and the motion-blurred crowd
  around a still Testudo reads as time passing on one and as the whole site
  moving past on the other. The calendar hero changed from
  `umd-element-hero-minimal data-theme="dark"` to match; it is emitted by
  `scripts/build-calendar.py`, not hand-edited.
- **Lock** — `umd-layout-space-horizontal-small` (992px), not `-larger`
  (1152px). A single column of text rows wants the narrower measure.
- **Search field is underlined, not boxed, and carries no label.**
  `critical.css` §23's boxed treatment (white ground, grey border, red 44x44
  submit) suits a filter band sitting beside selects; here the field is the
  only control on the page, so `#search-form` restyles it as one rule under
  the whole row with the DS magnifier as a plain glyph. Focus turns the rule
  red via `:focus-within` with no reflow. Scoped to this page — see
  OVERRIDES.md.
- **`type="search"`, not `"text"`.** Correct for a site search, and it takes
  the field out of §23's `.umd-filter-search-row input[type="text"]` selector
  (0,2,1), which would otherwise outrank the `umd-sans-larger` utility (0,1,0)
  and pin the field at 16px. That utility is a fluid ramp — 18px,
  `calc(18px + 0.5vw)`, 22px — so re-asserting it at higher specificity would
  mean copying a type scale into the page. WebKit's `type="search"`
  decorations and native clear button are suppressed; the band has its own
  Clear search.
- **No visible band heading.** The hero directly above already says SEARCH,
  so the `umd-text-line-trailing-light` "Search this site" label was saying it
  twice. The name it carried moves to `aria-label` on the `role="search"`
  form, so the landmark is still announced. Clear search moves below the
  field, right-aligned, as a direct grid child — `hidden` then takes it out of
  the layout entirely, so the idle band is field-only. The form's gap is
  overridden to 16px: `umd-layout-grid-gap-stacked`'s 32/40px is the rhythm
  for separating discrete blocks, and it left Clear search floating away from
  the control it acts on.
- **Band** — the Filter Band pattern minus the select. Everything is upstream:
  `umd-layout-background-highlight-light` (the `#F1F1F1` panel + `2px` red left
  rule), `umd-text-line-trailing-light`, `umd-animation-line-slide-graydark-red`,
  plus `critical.css` §23 for `.umd-filter-search-row` / `.umd-filter-search-btn`
  / `.umd-filter-results-count` / `.umd-filter-list`.
- **One label per result, always above the headline** — the section
  (`How to Apply`, `Academics`), on pinned and ranked rows alike. The list
  card's other short slot, `date`, renders *below* the body copy, which reads
  as a footnote rather than a category, so it is unused here. (That is the
  opposite of the programs page, which uses `date` for the `Major | Minor`
  type label; there the row has no eyebrow competing for it.)
- **Pinned treatment** is one box, not three: `1px solid #000` with 32px of
  padding (24px below 768px), holding ordinary list cards. `Featured` is a
  single red eyebrow inside the box — it labels the group, not any one row —
  set to the same metrics the cards' own `.umd-element-eyebrow` renders
  (Interstate 12px/700, uppercase, 0.6px tracking, measured off the live
  component). A promoted result is therefore byte-for-byte the ranked card;
  only the surround differs.
- **`data-visual-image-aligned="true"`** on pinned cards only. Without it the
  card sizes each image intrinsically and promoted rows land at different
  heights (measured: 176px vs 224px on two real photos).

## The two message states

Neither wears `umd-text-line-trailing-light` — that treatment belongs to the
search band's own heading, and reusing it made the states read as peer sections
rather than as responses to the query. Plain sans instead: `umd-sans-large` on
"Popular searches", `umd-sans-larger-bold` on "No results".

The no-results body sits in a `umd-text-rich-advanced` wrapper. That is the
whole fix for the link colours — without it the anchors fall through to the
browser's blue/purple; with it they are black, underlined with a gradient rule
that goes Maryland red on hover, over `#454545` body copy at 18px.

The suggested terms are **anchors, not buttons** (`<a href="?q=scholarships">`),
so a suggestion behaves like a link: middle-click, open-in-new-tab, and a real
navigation to the results URL rather than a scripted swap. The chip ground,
box model, 12px Interstate type, `transition:background-color .3s` and the
`#FFD200` hover on `<a>` children **all ship in the styles package** — read out
of `web-styles-library@1.8.16` and out of `composePill()` in
`packages/styles/source/element/text/cluster.ts`, not inferred from the page —
so none of it is restated here.

Exactly two things are absent, and they are the page's whole pill CSS: the
**light** variant declares no `color` (the **dark** variant declares
`color:#FFFFFF` and `#000000` on hover, so this is an upstream asymmetry, not an
implied black), and nothing removes the UA underline. Together those make a bare
`<a>` chip render browser-blue — the same class of bug as the flat utility-nav
anchors `shared/chrome.css` exists to fix. Upstream fix: `color: color.black` on
the light branch of `composePill()`. The container's `margin-top:-8px` wrapping
hack is swapped for a flex gap, which means zeroing the children's matching
`margin-top:8px` too, or wrapped rows get 8 + 8.

The class is `umd-text-cluster-pill`. `umd-pill-list` is the **deprecated alias**
for the same rule — the whole repo was moved off it in the same pass that added
this page (programs, colleges-schools, calendar and their generators), so there
is no old-name usage left to match.

## One DS collision worth knowing about

Consecutive `umd-element-card[data-display="list"]` siblings get
`border-top: 1px solid #E6E6E6` + `padding-top: 24px` from the component's own
CSS. Inside the pinned box that is exactly the wanted rhythm, so
`.search-pinned-list` sets `gap: 0` and lets the component space itself — a
flex gap there stacks on top of the 24px and pushes the rows apart while the
DS rule keeps drawing its divider at the old spacing.

In `.umd-filter-list` it is a **defect**: critical.css §23 already draws a 1px
`#d0d0d0` `border-bottom` on every `.umd-filter-item`, and the two land
adjacent and render as one doubled 2px rule. The page zeroes the component's
border with a selector specific enough to win (`0,3,2` against the DS's
`0,2,2`). **Upstream candidate:** §23 should zero `border-top` on
`.umd-filter-list > .umd-filter-item` itself — this will hit any page that puts
list cards on a divider list, not just this one.

## Data

The index is inline (`<script type="application/json" id="search-index">`),
~45 rows drawn from the real result set and re-pointed at this prototype's own
pages where an equivalent exists. Rows carrying a `pin` array are promoted when
the query names one of those terms.

Matching is tokenized and AND-ed across tokens, with a `-s` fold so
`scholarships`/`scholarship` and `majors`/`major` are the same token. That is
not a relevance model — it is only enough that two-word queries and plurals
don't lie about how many results a term has. Production replaces the index and
the two matching functions with the CMS endpoint; the render path and the
markup it emits are the part being designed.

## Open

- **Pagination.** Not built. The live page returns everything at once; "apply"
  returns 15 here. Needs a decision at real corpus size.
- **Pinned images.** Which promoted rows get one, and at what ratio. Four of the
  eight pinnable rows currently have one.
- **Section labels.** Currently one per row, derived by hand. Real ones come
  from CMS meta and may not exist on every page.
