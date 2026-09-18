# Claude Code — Admissions Design

This is the **Admissions design project**. It builds on the design-system page builder (vendored as a submodule at `page-builder/`).

## Where to find things

| What | Location |
|---|---|
| Slash commands | `page-builder/.claude/commands/*.md` |
| Layout/spacing/component rules | `page-builder/RULES.md` |
| Component slots & attributes | `page-builder/registry/` |
| Critical CSS (canonical) | `page-builder/styles/critical.css` |
| Skeleton + inlined CSS | `page-builder/TEMPLATE.html` |
| Layout HTML patterns | `page-builder/LAYOUT-PATTERNS.md` |
| Generic page-builder overrides | `page-builder/OVERRIDES.md` |
| **Admissions-specific overrides** | `OVERRIDES.md` (this repo) |

The page-builder's own `CLAUDE.md` (`page-builder/CLAUDE.md`) defines the canonical rules — read it. This file layers admissions-specific guidance on top.

## Output paths

Pages are organised by site section, one directory per section, with the section's
landing page as `index.html` so `/pages/<section>/` serves it:

```
pages/
├── index.html                               site home (stays at the top)
├── know-before-you-go.html                  section-less interior page (Layout B)
├── academics/
│   ├── index.html                           Academics landing
│   ├── programs.html
│   ├── colleges-schools.html
│   └── interest-<slug>.html
├── student-life/index.html
├── how-to-apply/
│   ├── index.html
│   ├── freshman-applicants.html
│   └── transfer-applicants.html
├── personas/
│   └── prospective-students.html            audience landing pages
├── admission-representatives/
│   ├── index.html                           the 24-person directory
│   ├── search.html                          same directory, filterable (CMS person-index pattern)
│   └── <first-last>.html                    one profile page per rep
├── tuition/index.html
└── calendar/index.html
```

`personas/` and `admission-representatives/` have no `data-child-ref` group in
`shared/header.html`, so their pages open the mobile drawer at the top level
rather than on a section — correct until the section earns a nav item.

- New admissions pages → `pages/<section>/<page-name>.html`; a new section starts with its own `index.html`
- New admissions images → `images/academics/`, `images/admissions/`, `images/calendar/`, or a new `images/<page>/` folder per page
- Briefs / source notes → `briefs/<page-name>.md`

### Depth: never hard-code `../`

Pages sit at two different depths (`pages/index.html` vs
`pages/academics/programs.html`), so a fixed `../` prefix is wrong on half of
them. Anything shared across pages — `shared/header.html`, `shared/footer.html`,
and the image paths in `briefs/*-data.json` — writes its paths **repo-root-relative
behind a `{{ROOT}}` token**:

```html
<img src="{{ROOT}}images/logos/admissions-logo.svg" />
<a href="{{ROOT}}pages/academics/programs.html">All Programs</a>
```

`scripts/_chrome.py` expands `{{ROOT}}` to the right number of `../` for the page
being written (`depth_of(path)` → 1 for `pages/index.html`, 2 for anything in
a section folder). Generated pages resolve any remaining tokens from their data
just before writing. A page that moves between directories is then a path change
and nothing else.

Inside a single page's own body, ordinary relative paths are fine — they just have
to match that page's depth (`../../images/...` from a section folder).

Do **not** write to `examples/` or `test/` — test/qa fixtures live in the page-builder repo, and demo/example pages live in the separate `page-builder-examples` repo, not here.

## Image paths

- **Admissions-owned** (logos, page-specific photography): `../images/...`
- **Shared library** (large/small/medium campus, people, events, default): `../page-builder/images/large/...` etc.
- **Sitewide chrome art** (art reused across pages rather than owned by one): `images/shared/` — currently just `interior-hero-pattern.png`, the interior hero graphic

When `images-index.json` is needed, read `page-builder/images/images-index.json`.

### Image optimization scope

When shrinking oversized images (the `/optimize-images` skill or ad-hoc), only touch **static** JPG/PNG/WebP. **GIFs, animated WebPs, and video files are out of scope** — don't resave or report on them (resampling breaks animation, and they need dedicated tooling). Exclude `.gif` and video extensions from scans, and check `n_frames > 1` on any WebP before touching it. This rule is also baked into `~/.claude/commands/optimize-images.md`.

## ⚠️ Interior pages pulled (2026-09-18)

Dev feedback: the interior-page work below **cannot be implemented as built**.
Six pages were removed from `main` and every link to them now points at the
**live site** instead:

| Removed page | Links now point to |
|---|---|
| `student-life/student-support.html` | `https://admissions.umd.edu/student/student-support` |
| `student-life/find-community.html` | `https://admissions.umd.edu/student/find-community` |
| `tuition/cost-of-attendance.html` | `https://admissions.umd.edu/tuition/cost-of-attendance` |
| `how-to-apply/freshman-application-faqs.html` | `https://admissions.umd.edu/apply/freshman-application-faqs` |
| `how-to-apply/english-language-proficiency.html` | `https://admissions.umd.edu/apply/english-language-proficiency` |
| `know-before-you-go.html` | `https://admissions.umd.edu/page/know-before-you-go` |

**Everything is preserved on the `archive/interior-pages` branch** — the pages,
their builders (`build-student-support.py`,
`build-freshman-application-faqs.py`, `build-english-language-proficiency.py`),
`scripts/rich_text.py`, `styles/rich-text-table.css` and
`briefs/freshman-application-faqs-data.json`, all of which were deleted from
`main` as orphans. Recover with
`git checkout archive/interior-pages -- <path>`.

**What this means for the sections below.** The layout, zig-zag, lede and
heading-scale rules are kept as the **design record** — they were reasoned
through carefully and still apply to interior pages built in future. But their
worked examples now name pages that no longer exist on `main`, and
`tuition/frederick-douglass-scholarship.html` is the only interior page left.
**Do not rebuild a removed page from these notes**, and re-verify any claim
against the tree before relying on it.

## Interior page layouts

Only one interior page remains on `main`:
`tuition/frederick-douglass-scholarship.html`, which retains the version
restored on 2026-09-15. The other three described here
(`student-life/student-support.html`,
`how-to-apply/english-language-proficiency.html`,
`tuition/cost-of-attendance.html`) were pulled on 2026-09-18 — see the banner
above. Shared navigation links out to the live site for each.


Every interior page (anything that is not a section landing page) uses **one of
exactly two layouts**. They share the same hero and breadcrumb; they differ only
in whether the left nav is present and, consequently, which horizontal lock the
content area sits in.

### Which layout — read the source page, don't infer it

**The layout is a per-page decision made by the source design, and the only
reliable way to pick is to look at the page you are recreating.** Open it and
check whether `main` actually contains a left nav.

Section membership does **not** decide it. An earlier version of this rule said
to use Layout A whenever the page sits in a section with "a real sibling set
worth navigating", and named `student-life` as one such section. That is wrong
and it produced a wrong build: `pages/student-life/find-community.html` was
first built with a sidebar on that reasoning, when
`https://admissions.umd.edu/student/find-community` has no left nav at all —
its `main` contains no `nav` or `aside`, just a single centred column. The
sidebar had to be torn out.

The drawer group in `shared/header.html` is about the *mobile* nav and says
nothing about whether a given page shows a *desktop* sidebar. Two pages in the
same section can legitimately differ.

Reference pages:

| Layout | Reference |
|---|---|
| A — with left nav | [`pages/tuition/frederick-douglass-scholarship.html`](pages/tuition/frederick-douglass-scholarship.html) — recreates `https://admissions.umd.edu/tuition/frederick-douglass-scholarship` |
| B — no left nav | [`pages/know-before-you-go.html`](pages/know-before-you-go.html) — recreates `https://admissions.umd.edu/page/know-before-you-go` |

### The shared hero — same on both layouts

Interior pages do **not** get a photographic hero. They get the minimal hero,
dark, with the UMD chevron pattern in the image slot and the **parent page's
name in the eyebrow**:

```html
<section>
  <umd-element-hero-minimal data-theme="dark">
    <p slot="eyebrow">Tuition &amp; Aid</p>
    <h1 slot="headline">Frederick Douglass Scholarship</h1>
    <img slot="image" src="{{ROOT}}images/shared/interior-hero-pattern.png" alt="" />
  </umd-element-hero-minimal>
</section>
```

- **The graphic is `images/shared/interior-hero-pattern.png`** (2602×1022 PNG).
  It is sitewide chrome for interior pages, not page art, which is why it lives
  in `images/shared/` and not in a per-page folder. *(It was
  `images/tuition/ff-pattern-hero.png` until 2026-09-14 — that path is dead.)*
- **`alt=""` is required.** The pattern is decoration; an empty alt keeps it out
  of the accessibility tree so the `<h1>` is the first thing announced.
- **The eyebrow is the parent page**, i.e. the section landing page the
  breadcrumb's last link points at — `Tuition & Aid` for a page under
  `pages/tuition/`, `How to Apply` for one under `pages/how-to-apply/`. It is
  not a category, a tagline, or the page's own name.
- `data-theme="dark"` is not optional. The pattern graphic is drawn for the
  dark panel and has no contrast on the light or maryland themes.

### Layout A — with left nav

`umd-layout-space-horizontal-larger` (1600px max-width, 64px side padding at
≥1200px) wrapping `umd-layout-space-columns-left`: a 242px `umd-element-nav-slider`
sidebar plus the content column, which is capped at 800px for reading measure.

```html
<!-- breadcrumb: its own lock, matching the content lock -->
<div class="umd-layout-space-horizontal-larger umd-layout-space-vertical-interior">
  <umd-element-breadcrumb>…</umd-element-breadcrumb>
</div>

<div class="umd-layout-space-horizontal-larger">
  <div class="umd-layout-space-columns-left">
    <div id="umd-shell-sidebar-container">
      <umd-element-nav-slider>…</umd-element-nav-slider>
    </div>
    <div id="umd-shell-content" class="max-w-[800px]">
      <section class="umd-layout-space-vertical-interior">…</section>
    </div>
  </div>
</div>
```

Measured at a 1280px viewport: lock 1280 → columns 1152 → sidebar 242 at x=64,
content 790 at x=426.

**The sidebar is page content, not shared chrome.** It mirrors the matching
`data-child-ref` group in `shared/header.html`, but `scripts/_chrome.py` does
not stamp it — write its `data-active` / `data-selected` by hand.

Use layout A when **the page being recreated has a left nav**.

### Layout B — no left nav

Same hero, same breadcrumb, **no sidebar and no `umd-layout-space-columns-left`**.
The content area uses a different lock:

> **`umd-layout-space-horizontal-normal`** (1280px max-width, 64px side padding
> at ≥1200px → content box caps at 1152px).

```html
<div class="umd-layout-space-horizontal-normal umd-layout-space-vertical-interior">
  <umd-element-breadcrumb>…</umd-element-breadcrumb>
</div>

<div class="umd-layout-space-horizontal-normal">
  <section class="umd-layout-space-vertical-interior">…</section>
</div>
```

Use layout B when **the page being recreated has no left nav**.

**A section-less page is written at the top of `pages/`, not in a directory of
its own** — `pages/know-before-you-go.html`, alongside `pages/index.html`. Don't
invent a section folder with no `index.html` to justify it. `_chrome.py` then
finds no section ref for the path and the mobile drawer opens at its top level,
which is correct.

**Do not use `-larger` here.** Without the 242px sidebar absorbing the left edge,
a 1600px lock puts content at a width nothing else on the site sits at, and the
breadcrumb and body copy stop lining up with the rest of the page stack.

**Four things that follow from the narrower lock and the missing sidebar:**

1. **Section intros: `umd-element-section-intro`, not `-wide`.** RULES §11 picks
   the variant from the lock, not the page — `-wide` over `-normal` spans
   further than the content beneath it.
2. **The `-larger` CSS augmentation does not apply.** Both `critical.css` §3 and
   the per-page §3 block set `position: relative; container-type: inline-size;
   isolation: isolate` on `.umd-layout-space-horizontal-larger` **only**. A
   watermark or a `@container`-driven component inside a `-normal` lock has no
   containing block or query container. Add the same three properties to the
   `-normal` rule on that page if you need either.
3. **Rich text needs no page-level measure — the DS already caps it.**
   `element.min.css` ships

   ```css
   :is(.umd-text-rich-advanced,.umd-rich-text) p,  /* + ul, ol, pre, blockquote */
   { max-width: 960px; }
   ```

   and that rule sets `max-width` and **nothing else — no auto margins** — so
   copy caps at 960px **in place**, flush to the left edge of the lock, while
   the card grids and media still use the full 1152px content box. Do not add a
   narrower page-level cap: it only fights the design system. (Layout A's 800px
   `#umd-shell-content` cap is a *column* width for the sidebar layout, not a
   measure to copy into Layout B.)
4. **`umd-layout-space-vertical-interior-child` is margin-BOTTOM only** (32px,
   margin-top 0). It spaces an `<h2>` away from the content it introduces, but
   gives nothing to an element that *follows* a block of copy — a sub-heading or
   a CTA row set after rich text collapses onto the paragraph above it and reads
   as part of it. There is no `mt-*` utility to reach for: `mt-md` / `mt-lg` /
   `mt-xl` all compute to 0 in this bundle set, so this needs a page-level rule.
   Layout A hides the problem because its sections are shorter and divider-led.

### What is the same on both

- The `noindex` meta pair, the shared header/footer regions, and the access gate
  — all spliced by `scripts/build-chrome.py`, identical on every page.
- `umd-layout-space-vertical-interior` on each `<section>` — interior pages use
  the `*-interior` spacing scale. `umd-layout-vertical-landing` is landing-page
  only.
- The breadcrumb's lock always matches the content lock. Don't mix `-larger`
  breadcrumb with `-normal` content.
- The closing `umd-element-banner-promo` "stay connected" block, per the
  sitewide page-closer convention.

## The zig-zag pattern — one shape, settled 2026-09-17

Every two-column image + text block on the site uses **one** structure. It
originally ran across five pages; after the 2026-09-18 removal **two carry it on
`main`** — `how-to-apply/international-applicants.html` (4 blocks) and
`student-life/index.html` (3, landing). The three that are gone —
`student-life/find-community.html` (5), `student-life/student-support.html`
(3, generated) and `know-before-you-go.html` (1) — are on
`archive/interior-pages`, and are still the fullest worked examples of the
pattern, which is why they are described below.
Before this they diverged on seven axes; the two that are now fixed sitewide
are the **text-side order** and the **alternation mechanism**.

**The heading-then-rule order is not limited to zig-zag blocks.** On
`know-before-you-go.html` it applies to all five section heads, card grids
included — a page should not put the rule above the heading in one section and
below it in the next.

```html
<div class="umd-layout-grid-gap-two">
  <!-- alternating blocks author the <figure> FIRST, here -->
  <div>
    <h2 class="text-black umd-sans-... umd-layout-space-vertical-headline-large">Heading</h2>
    <div class="umd-text-rich-advanced">
      <hr>                      <!-- FIRST CHILD, below the heading -->
      <p>Body copy.</p>
    </div>
  </div>
  <figure class="umd-layout-alignment-block-stacked">
    <img src="…" alt="…" />
  </figure>
</div>
```

This is LAYOUT-PATTERNS.md's canonical example, unchanged.

### Alternation is by DOM order — never by `order: -1`

`find-community.html` and `international-applicants.html` both used to flip the
column with a page-level rule (`.fc-media-first > figure { order: -1 }`,
`.intl-zigzag-reverse > figure { order: -1 }`) at the 650px breakpoint, which
keeps the heading first in the single-column mobile stack. **It reads better and
it is not available to us.** Migrated CMS content cannot carry a page-level CSS
rule, so the prototypes must show what the CMS can actually emit: the `<figure>`
authored first on alternating blocks, and therefore stacked above the heading at
375px. Both rules were removed on 2026-09-17.

Do not reintroduce an `order`-based flip on one page. A prototype that reads
better than the thing being prototyped is a false signal.

### The rule goes BELOW the heading — this follows from the above

Because the figure stacks first at 375px, the divider's position stops being
cosmetic:

| Rule position | 375px reading order | Result |
|---|---|---|
| `hr.umd-text-divider` **above** the heading | photo → caption → **rule** → heading → text | The rule lands between the photo and its own heading. The photo reads as the *previous* section's tail. **Wrong.** |
| `<hr>` as **first child of the body rich text** | photo → caption → heading → rule → text | Photo stays grouped with its own section. **Correct.** |

Measured at 375px: 16px heading→rule, 32px rule→body, in both. The asymmetry is
the design system's own rich-text `hr` margin, not something the pattern adds.

`<hr>` inside a rich-text block needs one page-level rule — `critical.css` gives
`<hr>` no border:

```css
.umd-layout-grid-gap-two .umd-text-rich-advanced hr {
  border: 0; border-top: 1px solid #000; height: 0;
}
```

Do **not** use a separate wrapper div plus a margin rule for the divider.
`student-support.html` did (`.student-support-title-rule` around its own
rich-text div, plus `.student-support-copy > h2 { margin-bottom: 16px }`); it
renders identically to the canonical form, so both the wrapper and the two CSS
rules were deleted. The figure also must be a **direct child of the grid** — not
wrapped in a `.umd-text-rich-advanced` div, as `student-support.html` and
`student-life/index.html` both did.

### There is no exception — `know-before-you-go.html` matches too

It was briefly left as one, on the reasoning that its single "What to Do" block
never alternates so the mis-grouping cannot occur, and that flipping one of
three section heads would make the page internally inconsistent. Both halves
were resolved the same day by flipping **all five** of its rules instead, so the
page is internally consistent *and* matches the site.

That page is hand-authored rather than migrated, so it could have kept a
page-level `order` rule. It does not: a reader moving between pages should not
meet two different treatments of the same block, and the pattern is easier to
hold if it has no exceptions.

**Two mechanics, one result.** Where a rich-text block follows the heading, the
rule is a bare `<hr>` as that block's first child (the canonical form above).
The two card sections — Where to Stay, Resources — have no rich-text block to
host one, so they keep `hr.umd-text-divider` and simply place it *after* the
heading, and their `<h2>` swaps `umd-layout-space-vertical-interior-child`
(32px) for `umd-layout-space-vertical-headline-large` to match the
heading→rule gap. Below the rule they differ on purpose: 24px into a card grid
(the divider's own margin), 32px into body copy (the rich-text wrapper's).

`umd-layout-space-vertical-headline-large` is **responsive** — 16px at 375px,
24px at 1280px. Quote a measurement with its viewport.

### The other axes

- **Heading level — PROVISIONALLY unified at level 1** (2026-09-17). This was
  previously listed here as deliberately *not* unified, on the reasoning that
  level follows the source page. That reasoning is still live and unresolved —
  see "⚠️ PROVISIONAL (2026-09-17): section heads are at level 1 sitewide".
  Treat the current uniformity as a state to evaluate, not a rule to enforce,
  and do not write a migration script against it yet.
- **Image crop — not unified.** find-community native, student-support `4 / 3`,
  international-applicants `1 / 1` on 3 of 4 rows. A per-page art decision, and
  the axis most likely to be worth unifying next if the pattern gets another
  pass.
- **The lock — not unified.** international-applicants sits in `-small` (992px)
  with its own 56/80px row rhythm; the others use the page lock with
  `umd-layout-space-vertical-interior` per section. This is the largest
  remaining structural difference between the zig-zag pages.

### Content fidelity is part of the pattern

Two invented-content bugs were found on `find-community.html` while unifying it,
both in the same two cards, and both worth generalising from:

1. **An invented section heading.** "Multicultural & Faith Programs" was built
   as an `<h2>` + `hr.umd-text-divider`. The source has no such heading — the
   phrase is an **eyebrow on each card**. Removed; the eyebrows are now
   `<p slot="eyebrow">` on both cards.
2. **An inline link promoted to a CTA.** The source puts each office's link
   *inline on its name* inside the paragraph and gives neither card a CTA. Ours
   had lifted the link into a "Visit OMSE" / "Visit MICA" button, which then
   required trimming the words the link had been attached to ("OMSE works to
   serve…" for the source's "The Office of Multi-Ethnic Student Education (OMSE)
   works to serve…"). Both cards were resynced to the source copy.

A third, smaller one on the same page: the **`<hr>` under the Resources
heading was ours too**. On the source, Resources is
`<h2 class="headline-two-san-serif">` inside a `<umd-admissions-resources>`
component with no `<hr>` anywhere in its lock. Removed 2026-09-17, and the
heading moved to `umd-layout-space-vertical-interior-child` (32px
margin-bottom, the class for a heading introducing a block) since there is no
longer a rule to space it away from. `find-community.html` now carries **no
`hr.umd-text-divider` at all** — its only rules are the bare `<hr>`s inside the
zig-zag rich-text blocks.

**Promoting an inline link to a CTA rewrites the copy around it.** That is the
transferable lesson: a composition choice about affordance quietly became an
edit to the text. When recreating a page, transcribe the links where they sit.

**And a divider is content, not decoration.** Two of the three fixes above were
rules we added that the source never had. Before carrying `hr.umd-text-divider`
into a section, check the source has a rule there — `!lock.querySelector('hr')`
is enough to settle it.

**Verifying links inside `umd-element-card`:** the design system draws its
rich-text link underline as a `background-image` gradient (black, red on hover),
**not** `text-decoration`. Checking `text-decoration-line` reports `none` on a
perfectly styled link. Card slot content is also *cloned into the shadow root*,
so the light-DOM node measures zero height while the rendered copy lives at
`.umd-element-eyebrow` / `.umd-text-rich-simple-scaling` inside `shadowRoot` —
measure there, or a working card looks broken.

## Shared chrome and reference pages

Every page within a single design project must use the **same site header, navigation, logo, and footer**. Pages in this project should look like a coherent site — they should not invent their own chrome, nav items, or logo treatment.

### The chrome lives in `shared/` — never copy it between pages

| File | What it holds |
|---|---|
| `shared/header.html` | Header stack: `umd-element-navigation-utility` + `umd-element-navigation-header` with the project nav items and logo |
| `shared/footer.html` | `umd-element-footer data-display="visual"` |
| `shared/chrome.css` | CSS companions the chrome markup depends on (see below) |
| `shared/chrome-scripts.html` | Chrome-driven shadow injections (nav-header logo width) |
| `shared/gate.html` | Prototype access gate — head-only `<style>` + `<script>`; blanks the page until a reviewer signs in |

**Edit `shared/`, then run the inliner:**

```bash
python3 scripts/build-chrome.py          # splices shared/ into every page under pages/ (recursively)
python3 scripts/build-chrome.py --check  # exits non-zero if any page is stale (CI-friendly)
```

Each region sits between `SHARED:<key>:START` / `:END` markers in the page. **Do not hand-edit anything between those markers** — the next run overwrites it. On a page that has no markers yet, the script finds the existing chrome by content and wraps it, so adding a new page needs no special setup.

The generated pages (`scripts/build-programs.py`, `scripts/build-colleges-schools.py`, `scripts/build-interest.py`, `scripts/build-calendar.py`, `scripts/build-representatives.py`) emit the *same* blocks via `scripts/_chrome.py`, so running any of them converges on identical bytes — there is no ordering dependency between them.

### Generated pages

| Script | Emits | Data |
|---|---|---|
| `build-programs.py` | `pages/academics/programs.html` | `briefs/programs-data.json` |
| `build-colleges-schools.py` | `pages/academics/colleges-schools.html` | `briefs/colleges-schools-data.json` |
| `build-interest.py [slug]` | `pages/academics/interest-<slug>.html` | `briefs/interests-data.json` + the two above |
| `build-calendar.py` | `pages/calendar/index.html` | `briefs/calendar-data.json` |
| `build-representatives.py [slug]` | `pages/admission-representatives/index.html`, `search.html`, + `<slug>.html` | `briefs/representatives-data.json` |

`build-interest.py` derives the majors grid from the `interests` facet already present on every program in `programs-data.json`, so a new interest page is a data edit (one block in `briefs/interests-data.json`), not a code edit. Run with no argument to rebuild every slug.

`build-representatives.py` works the same way: `representatives-data.json` holds all 24 reps, and the ones carrying `"page": true` get a profile page. Adding the rest is a data edit — flip the flag and re-run. Run with a slug to rebuild one rep without touching the landing page.

**Every region in `shared/` must be emitted by every generator.** `_chrome.keys()` is the list, and `build-programs.py` / `build-calendar.py` assert that their template has a slot for each key — so adding a region to `_chrome.py` breaks those builds until they are wired, which is deliberate. The access gate learned this the hard way: it was originally spliced in by hand, and the next run of `build-programs.py` and `build-calendar.py` silently dropped it, leaving both pages ungated on `main` until it became a proper region (2026-08-31).

Only the content between the header and footer is page-specific.

### ⚠️ Why the CSS and scripts live with the markup

**`page-builder/TEMPLATE.html` does not contain every rule the chrome needs.** Before the extraction these rules sat in a page-specific `<style>` block while the markup was copied from a sibling page — so building a `<head>` from TEMPLATE while copying markup from a page silently dropped them. No console error, no layout break, just unstyled chrome. That happened twice.

| Rule | Why TEMPLATE isn't enough |
|---|---|
| `umd-element-navigation-header div[slot="utility-navigation"] a` | `critical.css` §11's BASE layer styles `.umd-shell-utility-item a`, which never matches this project's plain `<a>` children — they render browser-default blue and underlined without it. Must load **after** the critical block to win at equal specificity. |
| `umd-element-scroll-top[data-layout-fixed="true"]` | Pins to `right:24px; bottom:24px`; the DS default is `right:40px; bottom:10vh`. Opt-in per page, but styled from `shared/` wherever used. |
| `.umd-nav-promo` | The nav dropdown promos. `slot="dropdown-callout"` is projected through a real `<slot>`, so the promo stays in the **light DOM** — the nav-item's shadow CSS cannot reach it, and a bare `<a>` there gets no colour from `critical.css` and renders default blue. Same root cause as the utility-nav row above. |

**Chrome vs. page-level shadow injections.** Only injections driven by the *chrome* belong in `shared/chrome-scripts.html` — currently just the nav-header logo width. The pathway aspect-ratio, banner-promo stacked-actions, call-to-action and card-overlay injections are driven by **page content** and stay in the page that uses them. Don't move them to `shared/`; a page with no `umd-element-pathway` should not carry the pathway injection.

### The mobile drawer is contextual — and its refs are directory names

`umd-element-navigation-header` renders the hamburger **only** when
`slot="primary-slide-links"` is present (`drawer.CreateElement()` returns `null`
otherwise and the header silently collapses to logo-only on mobile — that is how
this project shipped without one). The DS appends the button to the logo column
with no media query, so the hamburger is **persistent at every width**, beside
the desktop nav, as on umd.edu.

All three drawer slots (`primary-slide-links`, `primary-slide-secondary-links`,
`children-slides`) must be **direct children** of the header element — the
component collects them with `:scope > [slot]` — and are **cloned into the shadow
root**, so page CSS cannot style them. Every link's text needs its own `<span>`
or the selected-state underline has nothing to draw on.

The drawer opens on the section the reader is already in. That comes from two DS
attributes which `scripts/_chrome.py` stamps per page while hrefs are still
`{{ROOT}}`-relative:

| Attribute | Where | Effect |
|---|---|---|
| `data-active` | the `children-slides` group for the page's section | drawer opens on that slide, with a Back button to the top level |
| `data-selected` | any drawer link pointing at the page itself | gold underline on the current page |

**The `data-child-ref` / `data-parent-ref` values ARE the section directory names
under `pages/`** (`academics`, `student-life`, `how-to-apply`, `tuition`) — that
coupling is what lets the stamping work without a lookup table. Rename a section
directory and its drawer refs have to follow. A page in no section
(`pages/index.html`) or in a section with no drawer group
(`pages/calendar/`) matches nothing and the drawer opens at its top level, which
is correct.

### ⚠️ The nav carries top-level entries only — not every page we build

`shared/header.html` mirrors the live site's **top-level** nav entries. A page
that is a *child* of one of those entries on the live site does not get its own
nav item, however much we want to link it: the flat dropdown has no second
level to put it on, and adding the children of one entry while omitting the
children of every other entry is worse than omitting them all.

Two worked examples, both settled on 2026-09-15:

- **`how-to-apply/english-language-proficiency.html`** is a sub-page of
  **International Applicants** on the live site, alongside Obtaining a Visa and
  Financial Certification. It was added to the How to Apply dropdown and drawer
  and removed the same day.
- **`tuition/frederick-douglass-scholarship.html`** is a sub-page of **Transfer
  Merit Scholarships**, and came off the Tuition & Aid dropdown and drawer for
  the same reason.

In both cases the position *looked* right — each sits immediately after its
parent in the live site's markup — but that ordering is a nested child rendered
inline, not a sibling. Scraping link order out of the live page cannot tell the
two apart; check whether the entry is a child before adding it.

**A built page with no nav entry is normal, and is not a bug to fix.** Such a
page gets `data-active` on its section's drawer group and **no `data-selected`**
anywhere, because no drawer link points at it. That asymmetry is the expected
signature of a child page — do not "correct" it by adding a nav item. Reach the
page the way the live site does: from its parent's body copy
(`how-to-apply/international-applicants.html` links English Language
Proficiency twice) and from `pages/search/index.html`.

**A Layout A page keeps its sub-page in its own left nav** — that sidebar is
*section* navigation and is page content, not chrome. `frederick-douglass-
scholarship.html` still lists itself with `data-selected` in its
`umd-element-nav-slider`, which is correct and unaffected by the dropdown
removal. Only the shared chrome is top-level-only.

Because the chrome is now rendered per page rather than per depth,
`_chrome.block(key, page)` / `payload(key, page)` take the **output page path**,
not a depth — `depth_of()` is derived from it.

**When verifying:** assert utility-nav `gap: 24px` **at ≥1024px** — the DS hides the utility slot below desktop, so it measures 0×0 at tablet width and a narrow viewport masks the bug entirely. Also check `umd-element-scroll-top` computes `right/bottom: 24px` and that the nav logo's shadow `max-width` is `320px`. For the drawer, assert the hamburger computes `display: flex` **at desktop too** (it is meant to be persistent) and that the slide carrying `data-active` matches the page's section.

### Projects that don't yet have a reference page

Not every design project will start with an existing `shared/` chrome. In that case, the **first page built establishes it** — make the header/nav/logo/footer choices intentionally, extract them into `shared/` straight away, and treat that as authoritative for every subsequent page in the project.

### The chrome is project-scoped

`shared/` lives in this repo only — never copy this project's chrome into the `page-builder/` submodule, and never assume a different design project (e.g. a future `engineering-design` repo) will share these specific nav items, logos, or footer image. The submodule provides the components; each design project owns its own chrome composition.

That scoping is why `shared/chrome.css` is not upstreamed: the flat-`<a>` utility-nav treatment is *this project's* composition choice, not a design-system default. The one genuinely generic bug it exposed — `critical.css` §11 zeroing the slot gap unconditionally — was fixed upstream instead (`design-system-page-builder` `be3ea6c`).

## Interior page headings — the three-step scale

Interior pages use **exactly three heading classes**. This exists so a scripted
migration has a deterministic target.

| Level | Class | 375px | 768px | ≥1024px |
|---|---|---|---|---|
| 1 | `umd-sans-extralarge-bold` | 22 / 700 | 26.9 / 700 | **32 / 700** |
| 2 | `umd-sans-larger-bold` | 18 / 700 | 21.8 / 700 | **22 / 700** |
| 3 | `umd-sans-large` | 18 / 700 | 18 / 700 | **18 / 700** |

Body copy is 18 / 400 for contrast.

**Those columns are samples of a fluid curve, not three steps.** Levels 1 and 2
interpolate continuously between 375px and ~1024px, and level 2 **overshoots its
own ≥1024 value in the middle of the range** — measured 18px at 375, 21.84 at
768, **22.5 at 900**, 22 at 1024 and flat thereafter. Consequences:

- **Quote a measurement with its viewport.** "22px" and "18px" are both correct
  for level 2 depending on where you measured.
- **Never reproduce one of these classes with a hard-coded `font-size`.** No
  ladder of breakpoint values reproduces the 768–1024 curve, so a page rule that
  restates a size will diverge from the real class mid-range. Apply the class
  somewhere it can actually take effect instead — see the lede rules below.
- **Level 3 is the only flat one.** `umd-sans-large` is 18px at every width.

### ⚠️ PROVISIONAL (2026-09-17): section heads are at level 1 sitewide

**This is an open decision, not a settled rule. Do not build new automation on
it and do not "conform" anything else to it.**

**Tracked in a ticket** (2026-09-17). The question on it is exactly the two
options below — map every interior heading to one level, or let the source's
text sizing pass through on migration. **Current leaning is toward uniform
mapping** as the easier of the two, but it is explicitly TBD. Until that ticket
closes, leave the current state alone rather than extending or reverting it.

Every *section-level* heading on the four zig-zag pages currently carries
`umd-sans-extralarge-bold` (level 1) — `find-community.html` ×6,
`student-support.html` ×4, `international-applicants.html` ×4,
`know-before-you-go.html` ×3. Applied 2026-09-17 to see it in context. Two
things were deliberately left alone:

- **`frederick-douglass-scholarship.html`** — untouched. It is the Layout A
  reference and it was the page wrongly inflated in the 2026-09-14 incident
  below; it keeps its own levels until the decision lands.
- **`know-before-you-go.html`'s two nested sub-topics** (Self-Guided Tour,
  Transportation & Parking) — level 2. They sit *inside* the "What to Do"
  section, so promoting them would make them equal to their own parent and
  flatten a real nesting level. Unifying a scale must not eat a hierarchy.

**Revert:** `scripts/`-adjacent throwaway; regenerate from git history. The
builders assert the current classes, so a revert must touch
`build-student-support.py` too.

#### The history this has to respect

An audit on 2026-09-14 "conformed" every interior `h2` to level 1, silently
inflating three pages — including `frederick-douglass-scholarship.html`, which
had been **correct** at level 2. All three were reverted the same day. The
current state is the same *shape* of change, entered deliberately and with the
FDS page excluded.

#### Why pass-through is the crux

The live site distinguishes `headline-three` (32px) from `headline-four` (24px),
and most interior pages use **four**. If the CMS carries that class through on
migration, heading size is a per-source-page fact and a sitewide level-1 rule
misrepresents it. That splits by page, and it is why the current state is
provisional rather than settled:

| Page | Source markup | Passes through as | Unifying is |
|---|---|---|---|
| `find-community.html` | bare `<strong>` ×5 — **no heading class** | nothing to inherit | **free** — picking a level is our call either way |
| `student-support.html` | `headline-four` ×4 | ~24px ≈ level 2 | **lossy** — level 1 overshoots by 8px |
| `know-before-you-go.html` | `headline-three` ×2 + `headline-four` ×2 | 32px and 24px | mixed — its section heads were already level 1 |
| `international-applicants.html` | not in the mapping sample | unknown | unverified |

`h2` says where a heading sits in the document outline; the class says how big
it is. They stay independent, and a page can legitimately have `h2`s at level 2
or 3 whatever this decision settles on.

### Migration mapping

Measured at 1440px. Across five sampled `/student/*` and `/page/*` pages, only
these ever appear inside `umd-interior-content` — the region a migration carries
over:

| Source | Size | Migrate to | Note |
|---|---|---|---|
| `headline-three-san-serif` | 32px | **level 1** `umd-sans-extralarge-bold` | exact match |
| `headline-four-san-serif` | 24px | **level 2** `umd-sans-larger-bold` (22px) | nearest step; the most common case |
| `headline-five-san-serif` | 20px | **level 2 or 3 — break the tie by role** | see below |
| bare `<strong>` used as a label | 18px | **level 3** `umd-sans-large` (18px) | exact match — see below |
| `.rich-text.intro` (the page lede) | 24px / **400** | `<p class="umd-sans-larger-bold text-black page-lede">` **outside** `.umd-text-rich-advanced` | a paragraph, **not** a heading, and **not** inside the rich-text block — see below |

Chrome and section components need no class: `headline-one` becomes the hero's
`slot="headline"`, `headline-two` is the Resources component's own heading, and
`headline-five` inside that component is component-styled.

### The lede — settled 2026-09-17

**Migrate the source lede as a PARAGRAPH, and put it OUTSIDE the rich-text
block.** Source `.rich-text.intro` copy becomes:

```html
<section class="umd-layout-space-vertical-interior">
  <p class="umd-sans-larger-bold text-black page-lede">Full introduction.</p>
  <div class="umd-text-rich-advanced">
    <p>Body copy follows here, if the section has any.</p>
  </div>
</section>
```

with this CSS, **byte-identical on every page that has a lede — do not rename
it per page**:

```css
.page-lede { max-width: 960px; }
.page-lede + .umd-text-rich-advanced { margin-top: 24px; }
```

#### ⚠️ Why it cannot live inside the rich-text block

`.umd-text-rich-advanced > *` sets `font-size: 18px` on every direct child. So a
size class inside that block is **not wrong, it is inert** — swapping
`umd-sans-large` for `umd-sans-larger-bold` or even `umd-sans-extralarge-bold`
in place measures **18px / 700 before and after**. Nothing breaks, nothing
changes, and nothing tells you. That is the whole reason the lede used to be
`umd-sans-large`: it is already 18px, so the pin took nothing from it.

Moving the `<p>` out of the block is the only way the class renders its real
fluid scale (18px at 375 → 22.5 at 900 → 22 at 1024+). A page rule that restates
a `font-size` cannot substitute — see the fluidity note under the scale table.

#### What the two rules are for

- **`max-width: 960px`** replaces the measure the wrapper was supplying
  (`element.min.css` caps rich-text `p`/`ul`/`ol` at 960px *in place*). Without
  it a 22px lede runs the full 1152px Layout B content box. **This is not the
  old `.interior-lede` 800px cap** — it is the design system's own rich-text
  measure, re-applied to a paragraph that can no longer inherit it. Do not let
  it drift back to 800px, and do not add an accent line or any other lede
  chrome.
- **The adjacency rule** supplies the gap where body copy follows the lede
  directly; the block's own `> *:first-child { margin-top: 0 }` would otherwise
  zero it. It is **inert on the three pages whose lede sits alone in its
  section** — shipped there anyway so the block stays identical everywhere. That
  is a deliberate trade of three dead rules for one copy-pasteable block.

**It is not a heading.** An earlier pass shipped the lede as an `<h2>` on
`student-life/student-support.html` and
`how-to-apply/english-language-proficiency.html`, and it was wrong on both: a
lede is a multi-sentence paragraph (392 characters on the latter), so wrapping
it in a heading puts a paragraph in the document outline and makes
screen-reader heading navigation announce the whole thing. On
`student-support.html` it was also the only element in its section, giving a
heading with nothing beneath it. Both were converted back to `<p>` on
2026-09-15, and their builders now assert it.

#### Where each lede stands

| Page | Lede | How |
|---|---|---|
| `know-before-you-go.html` | `page-lede`, 22px | wrapper dropped (lede was its section's only child) |
| `student-life/student-support.html` | `page-lede`, 22px | wrapper dropped, via `build-student-support.py` |
| `how-to-apply/freshman-application-faqs.html` | `page-lede`, 22px | wrapper dropped, via its builder |
| `how-to-apply/english-language-proficiency.html` | `page-lede`, 22px | lede **lifted above** the block — it has sibling paragraphs |
| `tuition/frederick-douglass-scholarship.html` | `umd-sans-large`, 18px, **inside** rich text | **a different pattern, deliberately — float-wrapped prose, see below** |

**`frederick-douglass-scholarship.html` keeps its 18px lede inside the
rich-text block. This is correct and settled — it is a different pattern, not a
page waiting to be brought into line.**

Its lede sits in `slot="text"` of `umd-element-media-inline`, which is what
makes the copy **wrap around the floated statue photo**. That is the genuine
media-inline use case, and FDS is the only page in this project using it that
way — everywhere else the "image beside text" need is a short blurb paired with
a picture, i.e. the zig-zag grid, which is a different thing wearing a similar
shape. Keep the lede in the text with the floated image.

Two things follow:

- **Do not "fix" it to match the four `page-lede` pages.** The `slot` attribute
  is on the rich-text div itself, so the lede cannot leave that block and stay
  in the slot — and it should not. Restructuring the component to hoist the lede
  out would break the float wrap, which is the whole point of the page.
- **On migration it maps to a headline in rich text**, and that is fine. It does
  not need the `page-lede` treatment.

It is no longer the reference page for the *lede size* (the four `page-lede`
pages are), but it remains the reference for **float-wrapped prose**.

Each of the three generated pages asserts `'umd-sans-large text-black' not in
output`, so the inert in-place class cannot come back silently. Keep that
assertion when touching those builders: it is guarding against a change that is
invisible rather than broken.

A real heading still uses a heading tag and the three-step scale; that is a
separate element from the lede.

Layout A keeps the `max-w-[800px]` utility on its content column — that is a
*column* width, unrelated to the lede's 960px measure.

**`headline-five` is the one ambiguous row.** At 20px it sits exactly 2px from
level 2 (22px) and 2px from level 3 (18px), so size cannot break the tie. Break
it by role instead:

- **Section heading** — follows an `<hr>`, introduces a block → **level 2**.
- **Label inside a block** → **level 3**.

`how-to-apply/english-language-proficiency.html` is the first page where
`headline-five` appeared in content, and it settled this: mapped to level 3 its
three section headings rendered 18px against 18px body copy and read as bold
sentences rather than headings, even with a divider above them. At level 2 they
read correctly. A script can apply the role test mechanically — `headline-five`
immediately preceded by an `hr` is level 2.

**`<strong>` as a pseudo-heading.** Authors bold a line instead of using a
heading. Promote it to a real heading *tag* for outline and screen-reader
structure. Its **size** is the open question:

- The rule used to be "keep 18px, level 3", citing `find-community.html`
  shipping five 18px `<strong>` labels at 32px as the thing that went wrong.
- **Those same five are deliberately at level 1 again as of 2026-09-17**, under
  the provisional decision above. The reasoning that overturned it: the source
  has no heading class to be faithful *to* — an author bolded a line — so there
  is no size passing through and no fidelity to lose. At level 3 those headings
  measured 18px against 18px body copy and were distinguished only by position,
  which is the documented weakness of level 3.

So this row is **unresolved and tracks the provisional decision**, not a
standing rule. What survives either way: promote the tag, and never assume a
`<strong>` label's size without checking what the source actually had.

### What each built page maps to

Source column is what the live page has; "level" is what we ship **today**
under the provisional decision. Where the two disagree, that disagreement *is*
the open question.

| Page | Source | Level shipped | Matches source? |
|---|---|---|---|
| `tuition/frederick-douglass-scholarship.html` | `headline-four` ×2 | 2 | yes — excluded from the level-1 pass |
| `know-before-you-go.html` | `headline-three` ×2, `headline-four` ×2 | 1 (section heads), 2 (nested sub-topics) | partly |
| `student-life/find-community.html` | `<strong>` ×5 | 1 ×6 | n/a — source has no heading class |
| `student-life/student-support.html` | `headline-four` ×4 | 1 ×4 | **no** — overshoots 24px by 8px |
| `how-to-apply/international-applicants.html` | not sampled | 1 ×4 | unverified |
| `how-to-apply/freshman-application-faqs.html` | `headline-four` ×6 | 2 | yes — not a zig-zag page, untouched |

`find-community.html` shows 6 heads, not 7: its "Multicultural & Faith
Programs" heading was **removed** on 2026-09-17 because the source has no such
heading — the phrase is an *eyebrow on each card*
(`<span class="eyebrow">` inside each `umd-card`). See that page's own comment;
do not restore it.

`know-before-you-go.html` remains the one source page carrying both
`headline-three` and `headline-four`, so it is still the only page that
demonstrates the source-side level-1/level-2 distinction.

### Rules that fall out of this

- **Never put a `umd-sans-*` class on a slotted heading.** A heading in
  `slot="headline"` is styled by the component's shadow CSS and the class is
  inert. Audited: 0 occurrences — keep it that way.
- **Never put a `umd-sans-*` size inside `.umd-text-rich-advanced`** — it
  collapses to 18px (RULES §18). Headings go *before* the rich-text block, and
  so does the lede. The collapse is a **silent no-op, not a visible break**:
  the class applies, the weight lands, the size is simply ignored, so the only
  way to catch it is to measure. `umd-sans-large` is the one size class that is
  unaffected, because it is already 18px — which is exactly why it reads as
  "working" inside the block and why it was the lede class until 2026-09-17.
  `frederick-douglass-scholarship.html` still relies on this: its lede carries
  `umd-sans-large text-black` and renders 18px / 700 / #000 inside the
  rich-text block, against 18px / 400 / #454545 for the paragraphs after it.
  Note the source's own bold is the *same* colour as its body copy — the
  `text-black` is a deliberate project choice to push it further, not a
  reproduction of the source.
- **`umd-sans-large-bold` does not exist.** It computes 16 / 400, the unstyled
  fallback. `umd-sans-large` is already bold.
- **`umd-sans-larger` is not a smaller step** — it is `-larger-bold` at weight
  400. Don't use it for a heading.
- **Level 3 is not fluid.** `umd-sans-large` is 18px at every width, so at 375px
  levels 2 and 3 are both 18 / 700 and are distinguished only by position.

### Landing pages are deliberately different

Landing pages use `umd-sans-largest-uppercase` (44 / 800, uppercase) for section
headings. That contrast is intended — do not fold it into the scale above, and
do not let a migration script touch landing pages.

## Search indexing — every page is `noindex`

Every page under `pages/` carries, immediately after the viewport meta:

```html
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
```

These are prototypes; none of them should surface in search results.

**A `robots.txt` would not work here.** It is only fetched from the *host* root,
and a GitHub Pages project site is served from `/<repo>/` — a `robots.txt`
committed to this repo never gets read. The meta is the mechanism that actually
applies. The `googlebot` line is a deliberate belt-and-braces duplicate, matching
the treatment on the page-builder's own preview harness.

`page-builder/TEMPLATE.html` does **not** carry the meta (indexing is a project
decision, not a design-system one), so a new hand-written page has to add it.
The generated pages get it from `_chrome.with_robots(head)`, which the four
`build-*.py` scripts apply to the TEMPLATE-derived head — a rebuild cannot drop
it. The helper is idempotent and asserts if TEMPLATE ever loses its viewport
meta anchor.

## Logos

| Slot | Path |
|---|---|
| Header (`umd-element-navigation-header` `slot="logo"`) | `../images/logos/admissions-logo.svg` |
| Footer (`umd-element-footer` `slot="logo"`) | `../images/logos/footer-logo.svg` |
| Fallback (header onerror) | `../images/logos/primary-logo-dark.svg` |

Always include the `onerror` runtime fallback for hotlink-protected URLs (see page-builder/CLAUDE.md).

## Verifying pages in the preview pane

When checking admissions pages in the in-app Browser pane (`mcp__Claude_Browser__*`) against the `admissions-static` dev server, watch for these known quirks:

- **Viewport desync.** A *fresh* tab reports the correct `window.innerWidth` on first measure, but after `location.reload()` or re-`navigate` on the same tab it often sticks at `0` (or a stale width like `375`). When `innerWidth` is `0`, all media queries fail and computed styles read as base/mobile values — this is **not** a CSS bug. Fix: open a fresh tab (and close old ones — there's an ~8-tab cap).
- **Blank screenshots.** `computer{action:screenshot}` frequently returns a blank light-gray image even when the DOM/CSS engine is healthy. Rely on DOM/computed-style assertions via `javascript_tool` for verification, not screenshots.
- **Stale cache.** Navigating to a just-edited page can serve a cached copy. Confirm with `curl` that the dev server serves the change, then navigate with a cache-buster query (`?v=2`) to force a fresh load.

Practical verification recipe: assert on computed styles (9 CSS bundles loaded, `customElements.get(...)` registered, utility-nav gap `24px`, no horizontal overflow) via `javascript_tool` in a fresh tab, rather than trusting screenshots or a reused tab.

## Source of truth hierarchy (admissions)

1. Slash commands in `page-builder/.claude/commands/*.md`
2. `page-builder/RULES.md`
3. `page-builder/registry/`
4. `page-builder/styles/critical.css`
5. `OVERRIDES.md` (this repo) — admissions-specific shadow injections and class overrides
6. `page-builder/OVERRIDES.md` — generic shadow injections (visit-card, banner-promo, etc.)
