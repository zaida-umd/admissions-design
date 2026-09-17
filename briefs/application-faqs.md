# Application FAQs

- Source: https://admissions.umd.edu/apply/application-faqs
- Retrieved: 2026-09-17
- Output: `pages/how-to-apply/application-faqs.html`
- Builder: `scripts/build-application-faqs.py`
- Content and image sources: `briefs/application-faqs-data.json`

## Component plan

The source has no sidebar or carousel. Use Layout B with matching normal-width
breadcrumb and content containers, the shared dark minimal hero and chevron
pattern, and How To Apply as the parent eyebrow. The source intro remains a
paragraph with `umd-sans-large text-black` inside rich text. Body measure comes
from the design system, with no page-level width cap.

Per the design direction, replace the four alternating source cards with four
adjacent `umd-element-card` components using `data-display="list"`, light theme,
and aligned images. Preserve their order: Freshman Application FAQs, Transfer
Application FAQs, Submitting Documents, Essay Questions. Preserve the source
headings, descriptions, images, alt text, CTA labels, and accessible CTA names.
The cards own their responsive layout, spacing and separators; do not add extra
dividers or a grid gap. Slotted headings use `h2` without typography classes.

Freshman FAQs links to the existing local page. The other three destinations
remain on the live site until local equivalents exist. Repoint the existing
Application FAQs navigation, search result, and Freshman FAQs parent breadcrumb
to this page. Finish with the project's standard interior banner and shared
footer.

## Design check

One list provides four equally weighted resource destinations with secondary
photography. No additional grid, filter, accordion, section heading or custom
page CSS is needed. The source has no content HRs; listing separators are the
component's own treatment. The standard shared page closer follows the local
interior-page convention.

## Overrides

No new page-specific CSS, custom components or shadow-style injections.

## Validation

The shared-chrome check passes for all 31 pages, and component theme validation
passes. Source copy, local image paths, search data, CTA destinations, and the
current-page drawer selection were checked. Existing pages change only their
shared navigation and links to the new page.

Desktop (1440px), tablet (768px), and mobile (375px) were rendered in a fresh
headless browser using an isolated layout fixture with the access gate omitted.
The shipped page retains the gate. All four listing images load, headings and
links render, and no horizontal overflow occurs. Desktop/mobile screenshots
were visually checked. The components 2.0.0 bundle reports two identical
`process is not defined` errors on both this page and the existing Freshman
FAQs baseline; these are pre-existing shared-bundle errors.
