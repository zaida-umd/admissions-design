# Freshman Applicants

**Output:** `pages/freshman-applicants.html`
**Source:** <https://admissions.umd.edu/apply/freshman-applicants>
**Images:** `images/freshman-applicants/` (3 files — 1920×1080 hero, 1067×1600 pathway, 607×932 overlay)
**Reference page:** `pages/how-to-apply.html` (head + SHARED chrome copied verbatim)

Child of `pages/how-to-apply.html`, which linked out to the production URL in two places. Both
in-body links and the "How To Apply" nav dropdown now point at this local page, so the apply
journey stays inside the prototype end to end.

## What changed from the source

The source is a Craft-CMS page built from bespoke elements (`umd-stepper`, `umd-highlight`,
`umd-cta-strip`, `umd-admissions-resources`). Everything maps onto design-system components except
the numbered materials checklist, which has no DS equivalent and is page-built.

| Decision | Choice |
|---|---|
| Hero | Matches `how-to-apply.html` — image + H1 + subhead, `data-layout-height="small"`, centered. The two apply CTAs move down into the study-here intro (RULES §22: hero carries the title, not a CTA row). |
| Application Requirements | `umd-element-sticky-columns` — sticky heading + intro, 5 stacked large stats. The source's dark `statColumns` band with `stamp.jpg` is replaced by the imageless "breathing section" pattern. |
| Early Action + Application Platforms | Kept as a **pair**, as in the source's `umd-cta-strip`: one dark band, two imageless `umd-element-card-overlay data-theme="dark"` (the colour variant), with an animated brand chevron entering from the left and tucking under the cards — the same motif as the When-to-Apply band on `how-to-apply.html`. |
| Application Checklist | **New page-built stepper** (`.fa-*`), not an accordion stack — reproduces the source's own `umd-stepper`. See `OVERRIDES.md`. |
| Choosing A Major | Dark **overlay** pathway (`data-display="overlay" data-theme="dark"`) rather than a standard pathway — the section needed more weight. Self-contained, so no dark section wrapper. |
| Making Sure … Complete | **Light band with a sticky pathway** (`data-display="sticky" data-layout-image-position="left"`), matching `international-applicants.html` §8. Was a dark band with a white overlay pathway; the overlay put a long procedural list on top of a photo, and the band ran straight into the dark Resources band below it. |
| Resources | Dark `section-intro` + three dark `umd-element-card-icon` — the same bank as `how-to-apply.html` §11, with this page's copy. |
| `stamp.jpg` | **Not used.** Its only home was the Application Requirements band, which is imageless under the sticky-columns treatment. |
| Breadcrumb | Dropped — no page in this project uses `umd-element-breadcrumb` (same call as `colleges-schools.html`). |

## Page structure

1. **Hero** — `umd-element-hero data-layout-height="small" data-layout-text="center"`, `students-outdoors.jpg`.
2. **Apply as a Freshman** — `.umd-admissions-study-here-section` lockup (chevron + `<hr>` + uppercase eyebrow + rich text), then the Common App / ApplyWeb primary CTAs.
3. **Application Requirements** — `umd-element-sticky-columns` (`umd-layout-space-horizontal-larger`, `data-layout-position="100px"`); static column is `umd-layout-grid-gap-stacked` with 5 `umd-element-stat data-visual-size="large" data-decoration-line data-animation="offset"`.
4. **Choosing A Major** — `umd-element-pathway data-display="overlay" data-theme="dark" data-layout-image-position="left"`, `students-esj.jpg`. Black panel, white copy, image overlapping on the left.
5. **Early Action + Application Platforms** — dark band (`.umd-admissions-call-to-action-section`), `umd-layout-grid-gap-two umd-animation-grid`, two `umd-element-card-overlay data-theme="dark" class="size-large"` (no image → colour variant; `size-large` gives the 320 → 560px min-height that keeps the pair level) with secondary dark CTAs in `slot="actions"`, plus `.umd-admissions-call-to-action-chevron` behind them. The two platform links are `<a>` + `<br>`, not a `<ul>`.
6. **Application Checklist** — `umd-layout-space-horizontal-small` (992px): heading + intro + the three preliminary questions as a rich-text `<ul>` (carrying `umd-layout-vertical-landing-child` for the 48px gap), then the `.umd-admissions-application-steps` stepper (6 items).
7. **Making Sure Your UMD Application is Complete** — light band (`umd-layout-vertical-landing`, now required since §8 Resources is dark and this is not), `umd-element-pathway data-display="sticky" data-layout-image-position="left"`, `students-studying.jpg`. The 1:1 injection squares the image; the container keeps `position: sticky` and, at 495px against a 756px text column, actually pins while the steps scroll.
8. **Resources** — dark band, `umd-element-section-intro data-theme="dark"` + `umd-layout-grid-gap-three` of three dark `umd-element-card-icon`.
9. **Stay in touch** — gold `umd-element-banner-promo` closer (site convention).
10. **Scroll-to-top** — `umd-element-scroll-top data-layout-fixed="true"`.

Rhythm: light hero → light intro → light sticky-stats → **dark overlay pathway** → **dark cards** →
light checklist → light sticky pathway → **dark card bank** → gold closer. Two dark
pathway-plus-cards pairs bracket the long light checklist.

## Copy fidelity

All visible text is lifted verbatim from the source, including `<strong>`/`<em>` emphasis, the
`Label | description` separator in the checklist sub-items and preliminary questions, and the
`$80` / `A-/B+` / `#`-free punctuation. Two deliberate calls:

- The 5th stat's source label reads "**4** Years of math, including Algebra I, Geometry & Algebra II"
  — the numeral is duplicated inside the label. `slot="stat"` already carries the 4, so the label
  drops the leading numeral to match the other four stats. This is the only copy normalization.
- The source CTAs carry a short visible label plus an `sr-only` long form ("Common App" /
  "Apply through the Common App"). The DS CTA has one label, so the two hero-derived apply buttons
  use the long form; the two overlay-card CTAs use the short visible form ("View All Application
  Deadlines", "Apply Now") because they read as button labels.

The **image** variant of `umd-element-card-overlay` silently truncates `slot="text"` at a hard-coded
budget (300 characters, tightening to ~220 once `slot="actions"` is present) and appends " ...",
destructively in the shadow DOM. The 451-character Early Action paragraph lost its final two
sentences during the first build and needed a `MutationObserver` restore. Moving these cards to the
**colour** variant (no `slot="image"`) removed the clamp entirely — no injection needed. See
`OVERRIDES.md` § "Card-overlay: the IMAGE variant clamps `slot="text"`, the COLOR variant does not".

## Links

Internal links point at local pages where one exists (`programs.html` for "explore UMD's academic
programs"); everything else keeps the production `admissions.umd.edu` URL. Off-site links
(Common App, ApplyWeb, Board of Regents, transfercredit, School of Music) carry
`target="_blank" rel="noreferrer noopener"`, matching the source.

## Regenerating chrome

The page is hand-written; only the four SHARED regions are generated.

```bash
python3 scripts/build-chrome.py
```

## Notes / open items

- **The 1:1 injection now covers the sticky variant too.** `registry-content.json` warns against
  capping a sticky pathway's image, but that warning is about a cap leaving the container with no
  resolved height. This page's injection pairs `aspect-ratio` with `height: auto`, so the container
  resolves a definite square height and keeps `position: sticky`. Verified in-browser.

- **`students-studying.jpg` is 607×932.** Its portrait aspect was what made § "Making Sure … Complete"
  1316px tall: the overlay pathway lays the image out as a grid column, so at 649px wide it rendered
  996px tall and outgrew the 816px text column. The project's 1:1 pathway crop now applies to the
  overlay variant too, putting the image at 649px and the section at 1136px. A square crop of a
  607×932 source loses ~35% of the frame, so a landscape or square replacement is preferable — the
  source CDN signs its transform URLs (403 on a wider `w=`, 401 with no params), so no larger crop of
  this photo is fetchable. A replacement is expected.
- **`stamp.jpg` (441×882) was downloaded but is unused** — see the decision table.
- The numeral uses `.umd-campaign-medium` (Barlow Condensed italic 700; 44px → 64px at ≥1200px),
  which lands on the source stepper's 64px. `.umd-campaign-small` (32 → 44px) is the fallback if
  64px ever reads too heavy.
