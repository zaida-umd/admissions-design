# Prospective Students — brief

**Output:** `pages/personas/prospective-students.html` (new `personas/` section)
**Source:** https://admissions.umd.edu/persona/prospective-students (captured 2026-08-26)

## Why this page exists

It is the first page in this project that needs the legacy site's
`umd-spotlight-deadlines` component: a photo beside a text lockup that carries
**intro copy + two CTAs + a two-up stat pair + an application-deadline table**.
Nothing in the design system covers the last two together.

The recreation resolves it as a **variation of the sticky pathway** — see
`OVERRIDES.md` → "Applicant spotlight — stats and deadlines in the pathway
stats slot".

## Section order

| # | Section | Component |
|---|---|---|
| 1 | Hero | `umd-element-hero` small / centred |
| 2 | Getting Started | `.study-here-*` eyebrow lockup + brand chevron, then YouTube embed |
| 3 | Freshman Applicants | applicant spotlight (pathway sticky, image left) |
| 4 | Transfer Applicants | applicant spotlight (image right) |
| 5 | International Applicants | applicant spotlight (image left, no deadlines) |
| 6 | Shady Grove Applicants | applicant spotlight (image right, no group label) |
| 7 | Special Audiences | `umd-element-sticky-columns` + accordion ×11 |
| 8 | Visit UMD | dark band, two overlay cards |
| 9 | Stay connected | `umd-element-banner-promo` |

## Content decisions

- **`B or better`** replaces the source's `B average or better` as the transfer
  stat value; the sentence it displaced moved into the stat's label text
  ("Grade average earned by our most successful transfer students."). The stat
  value slot is a display line, not a sentence.
- **`A's or B's`** kept verbatim — 10 characters fits the uniform stat size, and
  `As/Bs` reads as an abbreviation nobody uses.
- **Requirements & checklist CTAs** point at this project's own
  `pages/how-to-apply/freshman-applicants.html` and `transfer-applicants.html`
  rather than admissions.umd.edu. International and Shady Grove have no local
  page yet, so those stay external.
- **Getting Started** uses the same `.umd-admissions-study-here-section` lockup as
  `pages/how-to-apply/index.html` and `pages/tuition/index.html` — rule, uppercase
  eyebrow, rich text, CTA, brand chevron behind it. The video below sits in the
  992px list-card lock (`umd-layout-space-horizontal-small`, RULES.md §33), with
  `umd-layout-space-vertical-landing-child` carried by the intro block above it —
  that class is a margin-**bottom**, so it belongs on the preceding element.
- **Breadcrumb dropped.** The source has `Home > Prospective Students`; no page
  in this project uses `umd-element-breadcrumb`.
- **U.S. Veterans** keeps its Freshman / Transfer sub-headings inside the one
  accordion item rather than splitting into two.

## Images

| Slot | File | Origin |
|---|---|---|
| Hero | `images/personas/prospective-students-hero.jpg` | source page (1440×544, used as-is) |
| Shady Grove | `images/personas/shady-grove-students.jpg` | source page, 2406×1598 → 1600×1063 |
| Freshman | `images/admissions/freshman-kirwan.jpg` | already in repo |
| Transfer | `images/admissions/transfer-mcircle.jpg` | already in repo |
| International | `images/admissions/international-flags.jpg` | already in repo |
| Visit UMD | `images/calendar/next-stop-maryland.jpg`, `images/calendar/edward-st-john.jpg` | already in repo |

The source page's four `rich-text` photos are served at 568×472 and the CDN
signs its transform URLs, so no larger original is reachable. A sticky pathway
gives its image `min-height: 656px` at ≥1200px container, which would upscale
them ~1.4×. The four applicant photos already in `images/admissions/` — the same
four subjects, used on `pages/how-to-apply/index.html` — are 1181–2048px wide
and were used instead.

## Not carried over

- `data-active` drawer state. `personas/` has no `data-child-ref` group in
  `shared/header.html`, so the drawer opens at its top level. Adding a
  "Personas" nav item would rewrite the chrome on all twelve pages — left for a
  separate decision.
