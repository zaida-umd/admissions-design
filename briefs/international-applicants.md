# International Applicants — page brief

**Source:** https://admissions.umd.edu/apply/international-applicants
**Output:** `pages/how-to-apply/international-applicants.html`

Scaffolded from `freshman-applicants.html`, which the source page mirrors almost
section for section. Interior page, depth 2, already present in the nav dropdown
and the mobile drawer.

## Section map

| # | Section | Component | Precedent |
|---|---|---|---|
| 2 | Hero | `umd-element-hero` small / center | freshman §2 |
| 3 | Applying as an International Student | rule + uppercase eyebrow + rich text + brand chevron; the hero's Apply Now CTA pulled down here | freshman §3 |
| 4 | Application Requirements | `umd-element-pathway data-display="sticky"` — text column sticks, image scrolls | — |
| 5 | Choosing a Major | `umd-element-pathway`, standard, light, image left | freshman §5 (light, not the overlay/dark it uses) |
| 6 | Benefits of Applying Early Action + Application Platforms | dark band, `umd-element-card-overlay` pair **with the brand chevron** (`.fa-cta-section` / `.fa-chevron` + the end-of-body positioning script) | freshman §6 |
| 7 | Application Checklist | `umd-element-sticky-columns` — sticky intro, static column holds one `umd-element-accordion-item` per applicant type, each wrapping an `<ol>` of 7 steps | source accordion + transfer §4 sticky/accordion |
| 8 | Making Sure Your Application is Complete | `umd-element-pathway data-display="sticky"`, light, image left, square image | — |
| 9 | Services for International Students | LIGHT band + **dark `umd-element-banner-promo`** as the headline/divider + 4 zig-zag rich-text/image rows | LAYOUT-PATTERNS.md § "…two-column image + text (zig-zag)", inverted |
| 10 | Resources | **dark band** + dark section-intro + 3 dark icon-link cards | freshman §9 / transfer §11 — the shared Resources treatment |
| 11 | Stay connected | `umd-element-banner-promo` | freshman §10 |

## The ordered lists are numbered by the DESIGN SYSTEM — do not restyle them

`.umd-text-rich-advanced` sets `list-style: none !important` on `<ol>` **on
purpose** and draws the numerals itself: the `<ol>` carries `counter-reset: item`
and every `<li>::before` is an absolutely-positioned `content: counter(item)`
sitting inside the li's own 40px left padding.

This page was first built with `ol.intl-checklist { list-style: decimal;
padding-left: 24px }`, on the assumption that a bare `<ol>` had been left
unstyled. Both are wrong:

- `list-style: decimal !important` **does** win the cascade — and then you get
  **two** sets of numbers, the marker and the counter.
- a `padding-left` on the `<ol>` double-indents on top of the li's 40px.

The surviving rule only sets step spacing (32px, 0 on the last) and makes each
step's opening `<strong>` a block-level uppercase label. Numbering is the DS's.

This is the same reset that made `freshman-applicants.html` render its `.fa-steps`
numerals as real content rather than list markers.

## The sticky pathway is a DS variant — and the 1:1 injection must skip it

§8 uses `umd-element-pathway data-display="sticky"` (registry alias "pathway
sticky"), NOT `umd-element-sticky-columns`. The variant makes the image column
`position: sticky; top: 0; height: 100%` so it runs the full height of the text
column.

**The 1:1 aspect-ratio shadow injection DOES apply to it.**
`registry-content.json` warns against capping the sticky image, but that warning
is about a cap that leaves the container with no resolved height. This page's
injection pairs `aspect-ratio` with `height: auto`, so the container resolves a
definite square height and keeps `position: sticky`.

Measured: 495×495, `position: sticky`, `top: 0`, container height 495 against a
969px text column — so it genuinely pins and holds while the copy scrolls past.
The uncapped full-height version filled the whole column and could never move,
which is the *less* sticky behaviour of the two.

### Why §4 is NOT sticky

It was, and it shape-shifted. The DS applies its 656px min-height to a sticky
image only once the **container** is ≥1200px; below that the image sizes to the
text column. §4's copy is short, so it rendered 649×656 (square) at 1440px but
collapsed to 495×387 — a squat 1.28 ratio — at 1100px, while §5 stayed square and
§8 stayed tall. Three pathway images, three shapes, one of them viewport-dependent.

Standard variant instead: it takes the 1:1 injection and is square at every width.
§8 keeps sticky because its copy is long enough to give the column real height
(649×996 at 1440px), and one deliberately tall image beside two squares reads as
intentional rather than accidental.

Measured after the change — §4 `1.00`, §5 `1.00`, §8 `0.65` at both 1440px and
1100px; §4's collapse is gone.

## The zig-zag runs on a dark band

§9 is the page's second dark section (with §6). `.umd-text-rich-advanced *`
paints every descendant `#454545` and the headline utilities assume a light
ground, so `.intl-services-dark` repaints the h3, body, links and the `<hr>`
white — the `<hr>` matching `.umd-text-divider.dark` — and keeps the
gradient-underline link treatment inverted. `data-theme="dark"` goes on the
section-intro and all four CTAs.

The `text-black` class was removed from the four h3s; it would have fought the
dark scope.

## Zig-zag rows invert at the breakpoint, not in the source order

Every §9 row is TEXT-then-FIGURE in the markup; alternate rows carry
`.intl-zigzag-reverse`, which sets `figure { order: -1 }` **only at ≥650px**.

Authoring the alternate rows figure-first instead — which is what
LAYOUT-PATTERNS.md's "swap the order of the text `<div>` and the `<figure>`"
literally says — puts an unlabelled photo above the service name on half the rows
once the grid collapses to one column at 375px. Source order has to stay
text-first so the mobile stack always leads with the heading.

## Zig-zag image treatment

- The rows **top-align** (`align-items: start`). Centring floated each image to a
  different vertical offset depending on how long its copy ran, so the four rows
  had no shared top edge.
- Rows **1, 3 and 4 are cropped square** via `.intl-figure-square img
  { aspect-ratio: 1/1; object-fit: cover }`. Row 2 is the MEI **wordmark** — a
  logo, not a photo — and stays at its native 460×300; squaring it would clip
  the lettering.
- The crop is CSS, not a re-crop of the files, **deliberately**: all three photos
  are shared with other pages in this repo (`international-flags.jpg` is on
  how-to-apply, `classroom-papers.jpg` and `annearundel-hall.jpg` on
  transfer-applicants). Editing them in place would silently change those pages.

## Only one dark band remains

§6 (Early Action / Application Platforms) is now the page's only dark section —
and it is the one carrying the brand chevron. §5, §8 and §10 were all pulled to
light over the course of the flow pass.

## Deliberate departures from the source

- **§4 is a sticky pathway, not the source's plain text block.** The source's own
  photo there is 441×899 and too low-res to enlarge, so it reuses
  `images/how-to-apply/students-walking-around-fall.webp`.
- **§5 and §8 are light; §8 is a sticky pathway, not a dark overlay.** The source
  runs §8 as a dark overlay. Three dark bands in the page's first half read as
  heavy, and §8 is a long procedural list — the sticky variant keeps the heading
  with the reader while the steps scroll. Two dark bands remain: §6 and §10.
- **§9 is the zig-zag rich-text/image pattern, not a 2×2 card grid.** Four
  services with two paragraphs each overfilled the cards.
- **§10 Resources runs light**, like `apply-now/index.html` §7, rather than the
  dark band `freshman-applicants.html` §9 uses.
- **§7 keeps the source's accordion** rather than the `.fa-steps` stepper used on
  the freshman page — 14 steps across two applicant types would otherwise be one
  unbroken wall.
- **Apply Now CTAs point at `../apply-now/`**, the prototype, not admissions.umd.edu.
- **Freshman / Transfer requirement CTAs link locally.**

## Assets

Only two new files; five images were already in the repo, byte-identical to what
the source serves.

| File | Status |
|---|---|
| `images/international-applicants/Students_Walking_04032007_06.JPG` | supplied (hero, 2000×720) — a wide banner crop that fills the 400px small hero at close to its native height |
| `images/international-applicants/mei-logo.jpg` | new (460×300) |
| `images/how-to-apply/students-walking-around-fall.webp` | reused (§4) |
| `images/freshman-applicants/students-esj.jpg` | reused (§5) — same photo as the source's `Students_5429.jpg` |
| `images/freshman-applicants/students-studying.jpg` | reused (§8) |
| `images/admissions/international-flags.jpg` | reused (§9 ISSS) |
| `images/transfer-applicants/classroom-papers.jpg` | reused (§9 Pre-Transfer Advising) |
| `images/transfer-applicants/annearundel-hall.jpg` | reused (§9 Transfer Credit Services) |

## Cross-link cleanup this page caused

`shared/header.html` had two references to the external international page (nav
dropdown + drawer); both now point at `{{ROOT}}pages/how-to-apply/international-applicants.html`,
propagated to all 14 pages by `build-chrome.py`. Seven body links on
`freshman-applicants.html` (3), `transfer-applicants.html` (2),
`how-to-apply/index.html` (1) and `apply-now/index.html` (1) were repointed too.
