# English Language Proficiency — Layout B, text-heavy

**Output:** `pages/how-to-apply/english-language-proficiency.html`
**Source:** https://admissions.umd.edu/apply/english-language-proficiency
**Built:** 2026-09-14

Built to test Layout B on a page that is mostly prose, a list and a table rather
than photography. It has **no images at all** — the first page in the project
that doesn't.

## Layout: B, checked first

`main.querySelectorAll('nav, aside, [class*=sidebar]')` returns empty at 1440px;
content is a single centred 954px column. No left nav → Layout B.

No `shared/header.html` change was needed: the How To Apply drawer group has no
entry for this page, so nothing to repoint and no whole-repo rebuild.

## What the text-heavy case proves

This is where the Layout B measure rule earns itself. `element.min.css` caps
rich-text `p` / `ul` / `ol` at 960px **in place**, so on a 1152px content box:

- every paragraph and the waiver list render **960px**, a comfortable measure;
- the three-card grid renders the full **1152px** (3 × 363px);
- the country table renders the full **1152px**.

One lock, three different effective widths, no page CSS. A page-level measure
wrapper would have constrained the table and the cards too.

## The table

Wrapped in `.umd-text-rich-advanced` — that wrapper is the styling hook for
tables, not any table class (OVERRIDES.md § *Tables*). Verified it took the
upstream treatment: `thead th` background `#F1F1F1` on black text,
`border-collapse: collapse`, `table-layout: fixed`, `display: block` with
`overflow-x: auto`.

**That `overflow-x` is why the page survives mobile.** At 375px the table's
content is 362px inside a 327px box, so the *table* scrolls and the page body
does not — measured page overflow 0.

Two additions the source does not have, both accessibility rather than styling:

- a `<caption>`, since the table had no accessible name;
- `.elp-sr` visually-hidden text in the 2nd and 3rd `<th>`. The table is one
  logical list of countries split across three columns, and those two headers
  are empty in the source — a screen reader announces nothing for two of the
  three columns otherwise.

## Headings — this page settled the `headline-five` tie

The source's section headings are `h2.headline-five-san-serif` at **20px**, the
first time `headline-five` has appeared *in content* across every page sampled.
The mapping table had guessed level 3 for it and marked the row "rare in
content."

**Level 3 was wrong here.** At 18px the three section headings rendered the same
size as the body copy and read as bold sentences rather than headings, even with
a divider above them. They are now **level 2** (`umd-sans-larger-bold`, 22px).

20px sits exactly 2px from level 2 and 2px from level 3, so size cannot break the
tie. CLAUDE.md now breaks it by role: `headline-five` that follows an `<hr>` and
introduces a block is level 2; `headline-five` used as a label inside a block is
level 3. A script can apply that mechanically.

## Component mapping

| Live page | This page |
|---|---|
| `h1.headline-one-san-serif` | `umd-element-hero-minimal`, eyebrow `International Applicants` |
| `umd-breadcrumb` | `umd-element-breadcrumb`, own `-normal` lock |
| `.rich-text.intro` | `umd-element-section-intro include-separator`, 992px lock |
| `hr.thick` + `h2.headline-five` | `hr.umd-text-divider` + `h2.umd-sans-larger-bold` |
| 3 × `umd-card` (tests) | 3 × `umd-element-card` in `umd-layout-grid-gap-three` |
| `umd-table` | `<table>` inside `.umd-text-rich-advanced` |
| `umd-admissions-resources` (1 item) | 1 × `umd-element-card-icon` on the 2-up grid |
| `.footer-cta` | `umd-element-banner-promo` (default gold page closer) |

The breadcrumb gains a **How To Apply** step the source omits, so the section
landing stays reachable — the same treatment `find-community.html` got.

The test cards carry no image on the source and none here. The two score lines
in each are `<strong>`-labelled rather than run as plain sentences, which is a
small legibility change from the source.

## Verified

- Layout B at 1440px: `-normal` lock 1280px, content box 1152px, no sidebar.
  Section-intro lock 992px at x=217 with the accent line.
- Prose and list 960px; cards 3 × 363px equal height; table 1152px.
- Table takes the rich-text treatment (`#F1F1F1` header, collapsed borders).
- Section `h2`s 22px desktop / 18px mobile.
- Mobile 375px: everything stacks to 327px, table scrolls inside itself
  (362 > 327), **page overflow 0**.
- `build-chrome.py --check` → 0/28.
- Console: the two `process is not defined` errors from the CDN bundle, same as
  every other page.

## Still duplicated

`.elp-lock-992` is the third copy of the same 992px section-intro lock
(`.kbyg-lock-992`, `.ss-lock-992`). Page-scoped prefixes are the project
convention, but this rule is now on its third page and clearly belongs to
Layout B rather than to any one page. Flagged in `briefs/student-support.md`
too; still no shared home for page-layout utilities in this repo.
