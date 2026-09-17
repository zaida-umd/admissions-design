# Freshman Application FAQs

- Source page: https://admissions.umd.edu/apply/freshman-application-faqs (copy
  captured 2026-09-17, verbatim)
- Output: `pages/how-to-apply/freshman-application-faqs.html`
- Content data: `briefs/freshman-application-faqs-data.json`
- Builder: `scripts/build-freshman-application-faqs.py`

## Layout — B, the "wide interior" style

The source page's `<main>` contains **no `nav` and no `aside`**: one centred
column under `umd-interior-content`. That makes this Layout B — the same style
as `pages/how-to-apply/english-language-proficiency.html`:
`umd-layout-space-horizontal-normal` on both the breadcrumb and the content
lock, `#umd-shell-content` with **no** `max-w-[800px]` cap, and no
`umd-element-nav-slider`.

## Hero and breadcrumb

Shared interior hero: `umd-element-hero-minimal data-theme="dark"` with
`images/shared/interior-hero-pattern.png` (`alt=""`).

The breadcrumb's last link is the page's parent, and the eyebrow repeats it —
here **Application FAQs**, which is what the source breadcrumb shows
(Home / Application FAQs / Freshman Application FAQs). The parent now points
to the local `application-faqs.html` listing page, matching the nav dropdown,
drawer and search index. The How To Apply section landing is inserted ahead
of it, matching English Language Proficiency.

## No nav entry

Freshman Application FAQs is a **child of Application FAQs** on the live site,
not a top-level entry, so it gets no item in `shared/header.html` — see
CLAUDE.md § "The nav carries top-level entries only". The page therefore has
`data-active` on the how-to-apply drawer group and no `data-selected` anywhere,
which is the expected signature. It is reached from the Freshman Applicants
resources card and from the search index.

## Headings

Every section heading in the source is `headline-four-san-serif` (24px), which
migrates to **level 2**, `umd-sans-larger-bold` — the same mapping as Student
Support and English Language Proficiency. There is no `headline-three` on this
page, so nothing is level 1.

The source lede (`.rich-text.intro`) is a **paragraph**, not a heading:
`<p class="umd-sans-large text-black">` inside `.umd-text-rich-advanced`.

## Components

- **Accordion.** 39 Q&A pairs in six groups, one
  `umd-element-accordion-item` per question, `<p slot="headline">` for the
  question and `<div slot="text"><div class="umd-text-rich-advanced">` for the
  answer — the markup already used on `how-to-apply/international-applicants.html`.
  All start closed: the source renders every panel `aria-expanded="false"`, so
  no item carries `data-visual-open="true"`.
- **Image.** The source's `umd-image-caption data-size="full"` is an image with
  no caption text, so it maps to `umd-element-media-inline` with **only**
  `slot="image"` — standard mode, full content width (OVERRIDES.md §
  `umd-element-media-inline`). Downloaded to
  `images/how-to-apply/campus-spring-students-walking.jpg` (1199×476).
- **Closing banner promo** — the shared interior page-closer, identical to the
  other Layout B pages.

## Links

Copy is verbatim, including its links, with two exceptions rewritten to the
local prototype pages we already have: `apply/freshman-applicants` and
`apply/english-language-proficiency`. Everything else stays pointed at the live
site. The rewrite map lives in the builder.
