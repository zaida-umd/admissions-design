# Frederick Douglass Scholarship — `pages/tuition/frederick-douglass-scholarship.html`

**Type:** interior page (the first one in this project)
**Section:** Tuition & Aid
**Source:** https://admissions.umd.edu/tuition/frederick-douglass-scholarship
**Built:** 2026-09-10

## What the page is

A merit scholarship for transfer students from Maryland community colleges —
30 full and 15 partial tuition awards, application due March 1. The reader
arrives asking two questions in order: *am I eligible*, and *what do I have to
send*. The page is those two lists, and everything above them is context for
whether it is worth reading on.

## Layout

The page-builder interior skeleton, unchanged (`page-builder/RULES.md` §21):

| Region | Component |
|---|---|
| Hero | `umd-element-hero-minimal data-theme="dark"` + `ff-pattern-hero.png` in the image slot |
| Breadcrumb | `umd-element-breadcrumb`, own `umd-layout-space-horizontal-larger` wrapper |
| Sidebar | `umd-element-nav-slider`, mirrors the Tuition & Aid group in `shared/header.html` |
| Content | `#umd-shell-content.max-w-[800px]` |

The hero image is the UMD chevron pattern — decoration, not content, so
`alt=""` keeps it out of the accessibility tree and the h1 stays the first
thing announced. It renders as the right-hand half of the hero at desktop
(633×346) and as a band above the headline at 375px.

Body sections are divided by `<hr class="umd-text-divider">` (critical.css §13),
matching the `<hr class="thick">` rules on the live page.

## Content components

- **`umd-element-media-inline data-layout-alignment="right"`** for the Douglass
  statue photo — image and caption floated right with the lede wrapping down
  the left. The alignment attribute alone does nothing: **`slot="text"` is what
  activates wrapped mode**, so the three intro paragraphs live *inside* the
  component as `<div class="umd-text-rich-advanced" slot="text">` rather than in
  a sibling div. At 375px the float collapses to stacked on its own.
- **`.umd-text-rich-advanced`** for all body copy, including both lists.
  The eligibility `<ul>` and the How-to-Apply `<ol>` need **no page CSS** —
  see below.

### The `<ol>` needs nothing (this cost a detour)

The first build added `list-style: decimal; padding-left: 24px` to the ordered
list, because `getComputedStyle` reported `list-style-type: none`. That reading
is correct and the conclusion was wrong: upstream sets `none !important` on
purpose and draws the numeral as a `::before` with a **red rule beside it**
(`border-right: 1px solid #E21833`). The added CSS was fighting the design
system and has been removed. Written up in `OVERRIDES.md`.

## Images

| File | Source |
|---|---|
| `images/tuition/ff-pattern-hero.png` | supplied for this page |
| `images/tuition/frederick-douglass-statue.jpg` | downloaded from the live page's CDN (1454×931, 219KB) rather than hotlinked |

## Banner promo — new sitewide treatment

The promo sits in the 800px content column here, so it is much narrower than on
a landing page and the old primary + secondary button pair did not fit. The
treatment changed everywhere instead of just here, so the site stays coherent:

```html
<p slot="text">Let's stay in touch!
  <a href="…request-info">Join the mailing list</a> or
  <a href="…connect">connect</a>!</p>
<div slot="actions" class="banner-promo-actions">
  <umd-element-call-to-action data-display="primary">
    <a href="…request-info">Subscribe</a>
  </umd-element-call-to-action>
</div>
```

Applied to the ten pages carrying the "There is a lot more to learn about UMD"
promo. The two admission-representative directory pages carry a different promo
("Stay in touch with UMD", longer copy, "Sign Up Now") and were left alone.

Both text links and the button point at `apply.umd.edu/register/request-info`,
replacing three different URLs the pages had drifted into — including a bare
`#mailing-list` anchor on the home page that went nowhere.

**One trap worth knowing:** `umd-element-banner-promo` *clones* `slot="text"`
and `slot="actions"` into its shadow root rather than projecting them through a
real `<slot>`. The light-DOM originals stay in the document at 0×0. Measuring
those is how you get a false "the links render default blue" reading — the
rendered copies in the shadow root are correctly black with the DS underline on
the yellow band.

**The stacked-actions shadow injection is gone.** It claimed to space a stacked
pair of CTAs, but the component reads `slot="actions"` with `querySelector` —
singular — and gives the result only `max-width: 30%; margin-left: 24px`. It has
no multi-action layout to begin with, so the injection never did anything the
component was going to undo. Removed from all 11 pages that carried it and from
`build-programs.py` / `build-representatives.py`; the actions box measures
identically without it. Written up in `OVERRIDES.md`.

## Nav wiring

Frederick Douglass Scholarship was added to the Tuition & Aid dropdown and the
mobile drawer in `shared/header.html`, after Transfer Merit Scholarships, matching
the live site's order. `scripts/build-chrome.py` stamps `data-active` /
`data-selected` on this page's drawer automatically. The page's own sidebar
carries the same state by hand — the sidebar is page content, not a shared region.

`pages/search/`'s index had an entry titled "Banneker/Key Scholarship" whose URL
pointed at the Frederick Douglass Scholarship page — a pre-existing mismatch.
It is now a correct Frederick Douglass Scholarship entry pointing at this page.
