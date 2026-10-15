# Transfer Applicants

**Output:** `pages/how-to-apply/transfer-applicants.html`
**Source:** <https://admissions.umd.edu/apply/transfer-applicants>
**Source capture:** scraped to a scratch dir during the build; not retained.
**Images:** `images/transfer-applicants/` (8 files)
**Reference page:** `pages/how-to-apply/freshman-applicants.html` (head + page CSS + SHARED chrome copied verbatim)

Sibling of `freshman-applicants.html` under the same `how-to-apply/` section. Built to
exercise the **landing-page component set** — this round adds the thumbnail carousel and
two sticky-columns-with-list treatments that no other page in the project used yet.

Both the "How To Apply" nav dropdown and the two in-body links on
`pages/how-to-apply/index.html` now point at this local page instead of the production URL,
so the apply journey stays inside the prototype end to end (same call as the freshman page).

## What changed from the source

The source is the same Craft-CMS stack as the freshman page (`umd-stepper`, `umd-highlight`,
`umd-list-columns`, `umd-card data-type="row"`). Everything maps onto design-system components.

| Section | Choice |
|---|---|
| Hero | `umd-element-hero data-layout-height="small" data-layout-text="center"`, `IribeCenter_01282019_5806.jpg`. The ApplyWeb CTA moves down into the intro (RULES §22: hero carries the title, not a CTA row), and the hero subhead drops the source's trailing "Apply to UMD as a transfer student using ApplyWeb" now that the button says it. |
| Transfer to UMD | `.umd-admissions-study-here-section` lockup — brand chevron + `<hr>` + uppercase eyebrow + rich text — then the single ApplyWeb primary CTA. Identical treatment to the freshman page. |
| Applicant Requirements | `umd-element-sticky-columns` — sticky heading + intro, three `umd-element-accordion-item` in the static column. **Imageless by direction:** the source's band photo (`Financial-Aid-Resources.jpg`) is not used. |
| Choosing a Major | **White overlay** pathway on the dark band — `data-display="overlay" data-theme="white"`, image left. First of the three-band dark run. |
| Benefits of Applying Early Action → **Application Deadlines** | Dark band: `umd-element-section-intro data-theme="dark"` + `umd-element-carousel-thumbnail data-theme="dark"` with four slides. The section is retitled: the early-action benefit argument lives entirely in one paragraph, so it becomes the section-intro copy, and the four deadline data points become the four slides. The "View All Application Deadlines" CTA sits in the section-intro's `slot="actions"`, above the carousel. See "The four-slide split" below. |
| Application Platform | **White overlay** pathway on the dark band — `data-display="overlay" data-theme="white"`, image right (mirrors §5). Carries the Transfer Application FAQs CTA in `slot="actions"`. Last of the three-band dark run. |
| Application Checklist | The freshman page's page-built stepper (`.fa-*`), 6 steps. The source's "Step" label is dropped by direction — the numeral alone carries the sequence. See `OVERRIDES.md`. |
| Making Sure … Complete | **Standard** `umd-element-pathway`, image **right** (the component default), normal background — `students-studying.jpg`. Not the overlay variant and not a dark band. |
| Services for Transfer Students | `umd-element-sticky-columns` in the RULES §20 **"featured item + list"** shape: a `umd-element-card-overlay type="image" class="size-large"` in the sticky column carrying `students-kirwan.jpg` *and* the section headline, with the three services as `data-display="list"` cards in the static column. The section therefore has no separate `<h2>` above it — the card is the heading. |
| Resources | Dark `section-intro` + three dark `umd-element-card-icon`, the same bank as freshman §9 with this page's copy. |
| Stay in touch | Gold `umd-element-banner-promo` closer (site convention). |
| Breadcrumb | Dropped — no page in this project uses `umd-element-breadcrumb`. |

## The four-slide split

The source's "Benefits of Applying Early Action" band contains exactly **two** stated benefits
(priority consideration for admission; merit-based scholarships) and **four** deadline data
points. Splitting it into four *benefit* slides would have meant inventing two. The call
instead: keep 100% source copy, retitle the section to what the slides actually are, and let
the benefit paragraph do its work as section intro.

| Slide | eyebrow | headline | text |
|---|---|---|---|
| 1 | Fall | Early Action Deadline | March 1 |
| 2 | Fall | Regular Deadline | June 1 |
| 3 | Spring | Early Action Deadline | August 1 |
| 4 | Spring | Regular Deadline | November 15 |

Slides are **text-only** `umd-element-card data-visual-transparent="true" data-visual-image-aligned="true"`
with **no `data-thumbnail`** — the host markup admissions.umd.edu itself uses on this component.
Note the consequence: with no `data-thumbnail` the component renders no thumbnail strip, only
prev/next buttons, and four short text cards make a shallow band (149px at 1280px wide, 3 of 4
slides visible). That is what this markup produces; if a taller, image-backed treatment is
wanted later, add `data-thumbnail` + `slot="image"` per RULES §27.

The `.relative` / `.bg-white` classes on the carousel host are Tailwind-shaped utilities the
production page carries but that the DS bundles do **not** ship (verified: absent from every
`css/*.min.css` in `web-styles-library`). They are defined in the page `<style>` block so the
markup behaves as written rather than silently no-opping.

## Dark rhythm

Sections 5–7 (Choosing a Major, Application Deadlines, Application Platform) are one
continuous black run, then §8 Application Checklist returns to white.

```
hero · intro · requirements  →  MAJOR · DEADLINES · PLATFORM  →  checklist · complete · services  →  RESOURCES  →  gold closer
   light                              ███ dark ███                        light                       ███         light
```

Mechanics, verified on the built page:

- All three carry `umd-layout-background-full-dark`, which supplies its own 48 / 80 / 104px
  vertical padding. Sections 5 and 6 carry **no** `umd-layout-vertical-landing` — their
  margin-bottom would punch a white gap between two dark bands (RULES §19). Measured
  `margin-bottom: 0px` on both, so the three bands are flush.
- §7 is the last dark band. `critical.css` §22
  (`.umd-layout-background-full-dark + section:not(.umd-layout-background-full-dark)`) puts the
  120px transition gap on §8, so §7 does not need to provide it.
- **§5 and §7 are white overlay pathways, not dark ones.** `data-theme` on the overlay variant
  names the **panel**, not the surround: `white` paints
  `.pathway-overlay-container-background` in `#FFFFFF` with black headline and `#454545` body,
  floating on the black band. Straight `data-theme="dark"` pathways read as one unbroken slab
  over three sections; the white panels break the run up.
- **`white`, not `light`.** `light` is a *gray* panel (`#F1F1F1`) **and** adds `80px 0` padding
  to `.pathway-overlay-container-lock-wrapper`, inflating the pathways to 918px / 729px. `white`
  has zero wrapper padding: 758px / 569px, matching `pages/admissions.html`. See `OVERRIDES.md`
  § "Overlay pathway on a dark band — use `data-theme="white"`, not `"light"`".
- The panel is 1853px wide at a 1265px lock, so it deliberately **bleeds off one edge** and
  leaves black showing on the other — and because §5 is image-left and §7 image-right, the two
  mirror each other. 104px of black above and below each, from the band's own padding.
- Image sides: §5 left, §7 right, §9 right.
- Everything inside the deadlines band is themed: section-intro, carousel, all four slide
  cards, and the CTA (`data-theme="dark"`). Verified white text at every level — the slide
  cards' shadow classes flip to `umd-element-eyebrow-dark` /
  `umd-sans-larger-scaling-dark` / `umd-text-rich-simple-scaling-dark`.
- `.bg-white` came off the carousel host when the band went dark; `.relative` stays.

## Accordions, not list cards

Applicant Requirements' static column holds three `umd-element-accordion-item` as **bare
adjacent siblings** — no `umd-layout-grid-gap-stacked` wrapper and no inner lock. The upstream
bundle already ships the separator:

```
umd-element-accordion-item + umd-element-accordion-item { margin-top: 8px }
```

A grid gap stacks with that and doubles the space (RULES §32); the sticky-columns exception in
§32 is why there is no `umd-layout-space-horizontal-small` inside the slot either — the host's
`umd-layout-space-horizontal-larger` governs the width. Measured: `0px / 8px / 8px`.

Markup follows the project's existing accordion convention (`pages/tuition/index.html`):
`<p slot="headline">` and a `<div class="umd-text-rich-advanced">` inside `slot="text"`, which
is what gives the `ApplyMaryland@umd.edu` mailto its RULES §34 gradient underline.

Services for Transfer Students still uses `umd-element-card data-display="list"`, as bare
adjacent siblings for the same reason — there the separator rule is:

```
umd-element-card[data-display="list"] + umd-element-card[data-display="list"]
  { margin-top: 24px; padding-top: 24px; border-top: 1px solid #E6E6E6 }
```

## The feature card's `size-large` needed an explicit height

`size-large` was on the card from the first build and the **host** measured 560px — but the
**painted card** (`.card-overlay-image`) was only 424px, leaving 136px of dead space under it.
The bundle ships only the `min-height` half of the class, and the image variant's shadow uses
`height: 100%`, which will not resolve against a host whose own height is `auto`.

The page now sets the other half, tablet-and-up only:

```css
@media (min-width: 768px) {
  umd-element-card-overlay.size-large { height: 560px; }
}
```

Mobile is deliberately left alone — the registry's `height: 320px` would clamp the card 40px
*below* its natural 360px, making `size-large` shrink it. Measured after the fix: desktop
560/560, mobile 360/360, zero dead space and no clipping at either width.

This is image-variant-only; `freshman-applicants.html`'s colour cards fill from `min-height`
alone (verified 560/560, no page CSS). Full write-up in `OVERRIDES.md` §
"Card-overlay `.size-large`: the IMAGE variant needs an explicit `height`".

## Copy fidelity

All visible text is lifted verbatim from the source, including `<strong>` emphasis and the
`Label | description` separator in the checklist sub-items. Deliberate calls:

- The section retitle described above.
- The two preliminary checklist questions become `umd-sans-large` sub-headings with plain
  answer paragraphs rather than a `<ul>` of `<strong>Q</strong> | A` — matching how the
  freshman page handles the identical source pattern.
- The source's fee-waiver link is a signed staging URL
  (`umd-admissions-production.cl-umd-edu-1.servd.dev/persona/fee-waiver?token=…`). Normalized
  to `https://admissions.umd.edu/persona/fee-waiver`, as on the freshman page.
- Internal links point at local pages where one exists (`../academics/programs.html`);
  everything else keeps the production `admissions.umd.edu` URL. Off-site links carry
  `target="_blank" rel="noreferrer noopener"`, matching the source.

## Images

| File | Source | Used by |
|---|---|---|
| `IribeCenter_01282019_5806.jpg` (1974×718) | supplied — not from the source page | Hero |
| `students-esj.jpg` (640×960) | `rich-text/Students_ESJLTC_…` | Choosing a Major pathway |
| `M_Gate_09212006_20.jpg` (1600×1067) | supplied — not from the source page | Application Platform pathway |
| `students-studying.jpg` (607×932) | `highlights/kids-studying-jpg.jpg` | Making Sure … Complete (overlay pathway) |
| `students-kirwan.jpg` (1200×630) | `highlights/Students_Outdoors_Kirwan_Hall.jpg` | Services feature overlay card |
| `classroom-papers.jpg` (1920×1080) | `rich-text/Classroom_Papers_…` | Pre-Transfer Advising list card |
| `annearundel-hall.jpg` (1920×1280) | `rich-text/annearundel-hall.jpg` | Transfer Credit Services list card |
| `maryland-logo.jpg` (1920×1080) | `rich-text/Maryland-Logo-horizontal.jpg` | MTAP list card |

`highlights/Financial-Aid-Resources.jpg` was fetched but is **not** in the repo — its only home
was the Applicant Requirements band, which is imageless here.

**Two supplied replacements.** The hero and the Application Platform pathway no longer use the
source page's photography: `IribeCenter_01282019_5806.jpg` and `M_Gate_09212006_20.jpg` were
dropped in directly. Both arrived at ~1MB — 5–10× heavier than everything else on the page and
at/over the 1MB threshold in `CLAUDE.md` — so both were resaved in place at q82,
progressive, **at their original pixel dimensions**: 993KB → 288KB (71% smaller) and
1034KB → 202KB (80% smaller).

**Superseded and removed:** the source page's own hero and platform photos
(`students-sitting-iribe.jpg`, `student-applying.jpg`) were replaced by the two supplied
images above and have been deleted — they are re-fetchable from the source URL if ever needed.

## Page CSS

Copied from `freshman-applicants.html`, minus two blocks that have no content on this page:
`.umd-admissions-call-to-action-section` / `.umd-admissions-call-to-action-chevron` (no dark overlay-card pair — its content is the deadlines
carousel instead) and `.umd-admissions-requirements-grid` (no masonry icon cards — list cards instead). The
brand-chevron positioning script at end-of-body went with them. Added: `.relative` (the one
Tailwind-shaped utility on the carousel host that the DS bundles do not ship) and the
`umd-element-card-overlay.size-large { height: 560px }` rule described above.

## Verified

Built and verified on **web-components-library 1.19.5 / web-styles-library 1.8.16** (see
`OVERRIDES.md` § "CDN version pins"). 1280px and 375px, fresh tabs (see `CLAUDE.md` on the
preview pane's viewport desync):

- 9 CSS bundles, all components registered, 30 images loaded, 0 broken
- `hOverflow: 0` at both widths, including with all three accordions expanded; no element
  wider than the viewport at 375px
- Section backgrounds top to bottom: `light light light DARK DARK DARK light light light DARK light`
- Dark run flush: `margin-bottom: 0` on §5 and §6; §8 picks up `margin-top: 120px`
- Accordions: all three expand (89px → 234 / 420 / 234), sibling gaps `0 / 8 / 8`
- Deadlines CTA reprojects into the section-intro's shadow above the carousel
  (`umd-layout-grid-inline-tablet-rows`), white text, and sits above the carousel top
- Pathways: the standard §9 image is 569×569 via the project's 1:1 injection; §5 and §7's
  overlay images sit in a 569×569 wrapper with `overflow: hidden`, so the taller sources are
  clipped square as intended
- Overlay panels paint `rgb(255, 255, 255)` with black headlines on both §5 and §7, at 1280px
  and 375px — no black-on-black failure; lock-wrapper padding `0px` on both
- Feature overlay card: host **and painted card** both 560px at desktop, both 360px at mobile,
  zero dead space, nothing clipped
- Stepper: 6 steps, numerals 1–6, no "Step" text anywhere in the list
- `umd-element-scroll-top` computes `right/bottom: 24px`
- Console: the two `process is not defined` errors the CDN bundle throws on **every** page in
  this project, plus two `ElementBuilder: "resize" is a DOM event…` warnings that are **new at
  1.19.5** and appear on every carousel-bearing page. The latter is a false positive in
  ElementBuilder's own heuristic (upstream `041c88e`) — console noise only. See
  `OVERRIDES.md` § "CDN version pins".

## Open items

- **Applicant Requirements is still light** and remains the open question from the dark/light
  pass — it is the one section whose theme was explicitly left undecided.
- **`students-studying.jpg` is 607×932** and loses ~35% of the frame to the 1:1 crop. Same
  note as the freshman page; a landscape or square replacement is preferable. The source CDN
  signs its transform URLs, so no wider crop of this photo is fetchable.
- The deadlines carousel's shallow band, per "The four-slide split" above.
- **The carousel's prev/next arrows could not be verified.** They render and are not disabled,
  but neither a synthetic nor a real click advances the track — and the same is true of the
  16-slide thumbnail carousel on `pages/academics/index.html` and at 1.18.12, so it is neither
  this page's markup nor the version upgrade. The in-app preview returns blank screenshots, so
  a missed click cannot be distinguished from a dead button there; this needs checking in a
  real browser. Slide 4 (Spring / Regular / November 15) sits at the clip boundary
  (inner track 1452px in a 1089px window), so if the arrows are genuinely inert, one of the
  four deadlines is only partly reachable.

## Regenerating chrome

The page is hand-written; only the four SHARED regions are generated.

```bash
python3 scripts/build-chrome.py
```
