# Admissions Overrides

Admissions-specific shadow-DOM injections, class overrides, and utility classes that aren't general enough to live in `page-builder/OVERRIDES.md` or `page-builder/styles/critical.css`.

## Admissions logo width override

`umd-element-navigation-header` shadow CSS hard-codes `.element-header-logo img { max-width: 240px }` at tablet+. The admissions wordmark is wider than the default UMD primary wordmark, so we shadow-inject `max-width: 320px`.

Source: **`shared/chrome-scripts.html`** — this is the one shadow injection driven by the chrome rather than by page content, so it ships with the header. Inlined into every page by `scripts/build-chrome.py`; do not copy it into a page.

Pages using this: all twelve (verified rendering at `max-width: 320px`).

## Pathway 1:1 image aspect ratio

`umd-element-pathway` has no CSS variable / `::part` hook for the image container; the design calls for a 1:1 image crop, so we shadow-inject `.pathway-image-container, .image-container, .umd-asset-image-wrapper-scaled { aspect-ratio: 1/1 !important; height: auto !important }` plus an `object-fit: cover` rule on the inner `<img>`.

**It applies to `data-display="overlay"` too, and there it is load-bearing rather than cosmetic.** The overlay variant lays its image out as a grid column (not as a full-bleed background), so without the cap the column takes the source photo's intrinsic aspect and can outgrow the text column — which then drives the height of the whole component. On `pages/how-to-apply/freshman-applicants.html` § "Making Sure Your UMD Application is Complete", a 607×932 portrait photo rendered 996px tall in a 649px column against an 816px text column, making the section 1316px. Capping at 1:1 puts the image at 649px, hands the height back to the text, and takes the section to 1136px. Don't scope the injection to `:not([data-display])` on the assumption that overlay uses a background image — it doesn't.

Pages using this: `pages/academics/index.html`, `pages/student-life/index.html`, `pages/tuition/index.html`, `pages/how-to-apply/freshman-applicants.html` (two overlay pathways, both capped).

## Overlay pathway as a dark editorial block

`umd-element-pathway data-display="overlay" data-theme="dark"` is self-contained — it paints its own black panel inside the content lock and needs **no** `umd-layout-background-full-dark` wrapper (that wrapper is only for the standard variant, which themes the text column alone; see RULES §5). It also swaps its rich-text class to `umd-text-rich-advanced-dark` on its own, so inline links get the white 1px gradient underline required by RULES §34 with no page CSS.

Two things to know before using it:

- **The panel deliberately overflows the viewport.** At 1440px it spans x 408 → 2381 (1973px wide) — the excess is suppressed by `critical.css` §21's `body { overflow-x: clip }`, exactly as with the hero-grid animation. Measured horizontal overflow stays 0; don't "fix" it with a width cap.
- **Stacking it above a `umd-layout-background-full-dark` section leaves a 120px white gap between two dark blocks of different widths** (the inset panel vs the full-bleed band). RULES §19's collapse rule doesn't fire, because the pathway's section isn't itself a dark section. On `pages/how-to-apply/freshman-applicants.html` this was judged to read correctly — the image sitting on white at the left gives the pathway its own identity, so the two register as separate dark moments rather than one interrupted band. Worth re-checking by eye on any other page that stacks them.

Pages using this: `pages/how-to-apply/freshman-applicants.html` (§ "Choosing A Major" dark, § "Making Sure Your UMD Application is Complete" light).

## Banner-promo stacked actions

`umd-element-banner-promo` reprojects `slot="actions"` into its shadow DOM under `.banner-promo-actions` with no gap when actions stack. Shadow-inject `display:flex; flex-direction:column; align-items:flex-end; gap:8px` so primary + secondary CTAs stack with 8px spacing.

Pages using this: `pages/academics/index.html`, `pages/student-life/index.html`, `pages/tuition/index.html`, `pages/how-to-apply/freshman-applicants.html`.

## Study-here / eyebrow + rich-text intro section

Custom `.study-here-section` / `.study-here-content` / `.study-here-chevron` layout — pairs a `umd-element-brand-logo-animation` chevron, anchored full-bleed and offset upward into the hero above, with an HR rule + uppercase eyebrow + rich-text body inside `umd-layout-space-horizontal-small`. Hidden below tablet to avoid single-column crowding. Used as the canonical "intro under the hero" pattern for landing pages in this project.

**`.study-here-chevron` must give the wrapper an explicit height and NOT clip.** A DS bump changed `umd-element-brand-logo-animation` so its host no longer contributes height to the wrapper; the earlier `top:-180px` + `overflow:hidden` (no `bottom`) rule then collapsed to a 0-height box and clipped the animation to nothing. Correct rule mirrors the working `.chevron-overlap` (admissions homepage): wrapper `position:absolute; top:-180px; left:0; right:0; bottom:-80px; overflow:visible;` and the animation itself `position:absolute; top:0; left:0; right:0;`. The inset `bottom` gives real height; `overflow:visible` prevents clipping.

Pages using this: `pages/academics/index.html`, `pages/student-life/index.html`, `pages/tuition/index.html`, `pages/how-to-apply/index.html`, `pages/how-to-apply/freshman-applicants.html`.

## Quote + brand chevron overlap

Custom `.quote-with-chevron` / `.chevron-overlap` layout used on the admissions homepage between the dark About UMD section and the overlay-card bank. Not generalizable yet — admissions-only for now.

## When-to-Apply gold band (`.wta-gold`)

Custom Maryland-gold (`#FFD200`) band housing the bespoke deadline-finder widget (there is no DS component for a dropdown filter). The gold background sits on an inner `.wta-gold` div **inside** the `umd-layout-space-horizontal-larger` lock (not the `<section>`), so the band width matches the pathway content lock at every breakpoint (they coincide at ≥1200px; below that the pathway uses component-internal padding, the same minor offset every section-intro on these pages already has). Padding is `80px 48px` (48/24 on mobile). All text is forced black; the widget uses DS typography classes where possible (`umd-sans-smaller` labels, `umd-sans-small` rows/hint, `umd-sans-larger-bold` result title). The result panel uses `background: rgba(0,0,0,0.05)` with a red (`#e21833`) left accent and black row rules. Reset is a `umd-element-call-to-action data-display="secondary"` shown only after a full query executes; its click is delegated on `.wta__foot` so it survives the CTA reprojecting its slotted `<button>`. Text links use `umd-text-link-red` (black text, red underline on hover — the DS default link).

Pages using this: `pages/how-to-apply/index.html`.

## When-to-Apply left chevron (`.wta-chevron`)

Reuses `umd-element-brand-logo-animation` (same element as the study-here chevron) as a decorative right-pointing chevron entering from the **screen's left edge** and tucking **under** the gold band. Kept **unmirrored** (mirroring reverses the arrows) and shifted a full viewport left. Because the component anchors its cluster to the right of a 100vw internal box, pure-CSS viewport math drifts it off-screen on wide monitors — so a small script anchors it to the gold band's **left edge** (`bandLeft + 70`, recomputed on resize and on scroll-in) instead. It slides in from off-screen-left via an `IntersectionObserver` toggling `.wta-chevron.is-in` + a CSS transition (the DS `umd-animation-transition-slide-right` view-timeline did **not** scrub reliably here — it snapped to its end state). Sits at `z-index:0` under the lock (`z-index:1`).

**Three separate clips must be removed for the full 3-chevron stack to show:** `overflow` on `.wta-section` and `.wta-chevron` (both dropped — the stack only overflows off-screen-left, which never creates horizontal scroll), **and** the DS rule `umd-element-brand-logo-animation:defined { overflow: clip }` (a 25vw box), overridden to `overflow: visible` scoped to `.wta-chevron > umd-element-brand-logo-animation` so the study-here chevron is unaffected. Hidden below 1024px.

Pages using this: `pages/how-to-apply/index.html`.

## Card-overlay horizontal padding (desktop+) — RETIRED 2026-09-09

**Landed upstream in `web-components-library@2.0.0`; the local injection is removed. Do NOT re-add.**

`umd-element-card-overlay` used to hard-code horizontal padding to `token.spacing.md`
(24px) at every breakpoint, crowding the headline/eyebrow/CTA against the card edges on
wide viewports. We shadow-injected a step-up (24 / 32 / 48px at 1200px / 1500px).

Upstream now ships the step-up itself, on **both** variants — `overlay/image.ts` and
`overlay/color.ts` each carry `@container (min-width: 600px) { padding-left/right:
token.spacing.xl }` (40px). Two consequences worth knowing:

- **It is container-based, not viewport-based**, which is strictly more correct: a narrow
  card in a wide viewport now correctly stays at 24px. The old injection could not do that.
- **The ceiling drops from 48px to 40px** on very wide screens. Accepted — matching the
  design system beats holding a local 8px.

The old injection actively *masked* the upstream rule: it used `!important` with viewport
media queries, so it won at every width. That is why it had to come out with the pin bump
rather than being left as harmless dead code.

The old scope caveat (full-bleed "lock" banks should keep 24px sides) is now handled for
free — a full-bleed bank's cards are wide containers, but a card narrower than 600px in one
keeps the tighter padding on its own.

## Hero-grid centre video overflows its grid row (2.0.0 regression)

**Page:** `pages/index.html` (the only page with `umd-element-hero-grid`).

`hero/custom/grid.ts` styles the centre video wrapper `width: 100%` + `aspect-ratio: 1 / 1`.
Those two declarations existed at 1.19.5 as well, but were nested one level too deep —
`additionalElementStyles: { additionalElementStyles: {...} }` — so the builder never emitted
them. Release 2.0 renamed the key to `customStyles` (a single level), which made the
previously dead rule go live.

The centre column is as wide as its grid track (640px at 1280px viewport, 900px at 1600px)
but the middle row of `grid-template-rows` is only 296px / 436px. A 1:1 video therefore
renders at the **column width**, not the row height:

| viewport | centre rows | video height | result |
|---|---|---|---|
| 1280px | `180 296 180` | **640px** | overflows row by 344px |
| 1600px | `250 436 250` | **900px** | overflows row by 464px |

At 1280px it swallowed the 32px row gap **and** the entire bottom image (712→892), then bled
132px past the hero onto the Information For band below — covering 63% of that 208px section,
which is why the band read as "missing its dark background". Nothing about the background was
wrong; it was being painted over.

Shadow-inject the video back to its row:

```css
.hero-grid-center .umd-element-video { aspect-ratio: auto !important; height: 100% !important; }
```

Restores the 1.19.5 geometry exactly (296px / 436px, both corner images visible, no bleed).
**Upstream candidate:** the wrapper should take `height: 100%` from its grid row and let
`aspect-ratio` apply only where the row is not already constrained. Remove this injection once
upstream constrains it.

## Dark pathway rich text: `<p>` must be a DIRECT child of `slot="text"` (2.0.0 regression)

**Upstream regression with a markup workaround.** We fixed it by deleting our wrapper, but the
fault is upstream — see "Why this is upstream's bug" below. Put `<p>` directly in `slot="text"`.

At 1.19.5 the pathway shadow sheet carried `.umd-text-rich-advanced-dark p { line-height: 1.5em }`.
2.0.0 **dropped that one rule** (everything else in the rich-text block is byte-identical), and
it was the only thing setting the paragraph's line-height.

The DS already wraps `slot="text"` in `.umd-text-rich-advanced-dark umd-rich-text-dark`, which
computes `line-height: 27px`. With `<p>` as a direct child, it inherits that 27px and is fine.
Nesting our own `<div class="umd-text-rich-advanced">` in between breaks the chain: that div
computes 18px inside the shadow (our project class is light-DOM only and cannot reach it), and
the `<p>` inherits 18px — `line-height: 1`, visibly cramped.

Measured on the About UMD pathway before the fix: `<p>` 18px vs 27px, section 1054px vs 1135px.
Every other pathway in the project was already correct because they all put `<p>` straight into
`slot="text"` — which is why only this one looked wrong.

Fix is to delete the wrapper, not to inject CSS. Removing only its *class* does not help: the
bare `<div>` still computes 18px, so the element itself has to go.

### Why this is upstream's bug, not just our markup

The nested element is not merely *failing to inherit* — it is handed an explicit
`line-height: 1` that **blocks** inheritance. Measured by probing a bare `<div>` appended
into the wrapper's shadow:

| test | result |
|---|---|
| bare `<div>` in the wrapper | 18px (wrapper is 27px) |
| force parent to `line-height: 27px` inline | child **still 18px** |
| set `line-height: inherit` on the child | 27px |

If this were ordinary inheritance the second row would read 27px. It does not, because the
component's shadow sheet carries a blanket element-selector reset:

```css
div { line-height: 1; }        /* in the pathway's shadow CSS */
```

So the full chain is:

1. `.umd-text-rich-advanced-dark { font-size: 18px; line-height: 1.5em }` → wrapper computes 27px
2. any nested `<div>` is caught by `div { line-height: 1 }` → 18px, which **blocks** inheritance
3. a `<p>` inside that div inherits the div's 18px — `line-height: 1`, visibly cramped

At 1.19.5 this was neutralised by `.umd-text-rich-advanced-dark p { line-height: 1.5em }`, which
reached paragraphs at *any* depth and outranked the bare `div` reset. 2.0.0 dropped that one rule,
so only a **direct-child** `<p>` still works — via the inheritance the wrapper provides.

Nested structure in a rich-text slot is legitimate usage: the component itself ships rules for
`ul`, `ol`, `li`, `blockquote` and `table` inside this wrapper (`li` and `blockquote` measure
25.2px and are unaffected, because they carry their own explicit line-height). A `<p>` inside a
wrapping `<div>` — ordinary CMS rich-text output — is the case that breaks. Any consumer nesting
a paragraph one level deep hits this, not just this project.

### Reproduced upstream (no project code involved)

Confirmed on the design system's own component page,
`https://beta.umd-staging.com/components/pathway/overlay/image`. All 11 pathways there render
correctly **because every one of them puts `<p>` directly in `slot="text"`** — the shape that
still works. The page never exercises the nested case.

Appending three probes into a dark pathway's shadow wrapper on that page reproduces it:

| probe | line-height |
|---|---|
| `<p>` appended directly to the wrapper | 27px ✓ |
| `<p>` inside a bare `<div>` | **18px** ✗ |
| `<p>` inside a `<div class="umd-text-rich-advanced">` | **18px** ✗ |

The second and third rows are identical, which rules our project class out entirely — an
unstyled `<div>` is sufficient to trigger it.

**Upstream candidate:** either restore `.umd-text-rich-advanced-dark p { line-height: 1.5em }`,
or drop the blanket `div { line-height: 1 }` reset so the wrapper's line-height inherits at any
depth. The blanket reset is the deeper problem — it makes any structural `<div>` in a rich-text
slot silently collapse the leading of everything beneath it.

## Card-overlay: the IMAGE variant clamps `slot="text"`, the COLOR variant does not

Not an override in force — a documented silent failure, kept because it cost a build iteration and because the two variants are one tag apart.

`umd-element-card-overlay` with `type="image"` + `slot="image"` renders `.card-overlay-image-*` shadow nodes and **clamps `slot="text"` to a hard-coded character budget**, appending `" ..."`. The helper is `maxTextSize` in `cdn.js@1.18.12`; the budget is **300 characters**, tightening to **~220** once `slot="actions"` is also present. It is exposed as no slot, attribute, or CSS variable.

**The clamp is destructive, not visual.** The copy is cut out of the shadow DOM, so no CSS (`line-clamp`, `max-height`, `overflow`) brings it back — those only hide text that is still there. Recovering it means writing the light-DOM slot's `innerHTML` back over the truncated node, and a one-shot restore does **not** hold: the card re-renders its scaling text block after first paint and re-truncates, so it needs a `MutationObserver` on `.card-overlay-image-text-content` (idempotent, because restored text no longer ends in `...`).

**Drop the image and the problem disappears.** Without `slot="image"` the component renders the colour variant instead — shadow root `.card-overlay-color` / `.card-overlay-color-wrapper`, `#242424` background — which has **no clamp at all**. Verified on `pages/how-to-apply/freshman-applicants.html`: the 451-character Early Action paragraph renders in full, untouched, with no injection.

Corollary: the "Card-overlay horizontal padding (desktop+)" entry above is also image-variant-only (it targets `.card-overlay-image-container`). Neither injection belongs on a page whose overlay cards are colour cards — both would be dead code.

**Upstream candidate:** expose the budget as an attribute (e.g. `data-text-max-length`, `0` = no clamp) on the image variant, rather than forcing every page with longer copy to fight the shadow DOM — or at minimum bring the two variants' behaviour into line.

Pages using this: none currently. `pages/how-to-apply/freshman-applicants.html` carried the restore injection until its cards moved from the image variant to the colour variant.

## CDN version pins

All 11 pages load **web-components-library 1.19.5** and **web-styles-library 1.8.16**, matching
`page-builder/TEMPLATE.html`.

Before 2026-08-21 the pages pinned components at `1.18.12` and linked the nine stylesheets
**unversioned** (`.../web-styles-library/css/…`), i.e. floating on unpkg's `latest`. That is why
the styles half of the upgrade produced almost no visual change — `latest` already resolved to
1.8.16 — but it also meant the CSS could change under the pages with no commit. Both halves are
now pinned.

**The generators hard-code the pin too.** `build-programs.py` and `build-calendar.py` emit the
`cdn.js` tag from their own `BODY` literal rather than from the TEMPLATE-derived head, so they
silently kept emitting 1.18.12 after the pages were bumped — re-running either would have
reverted its page. Both now carry a drift guard that compares the `BODY` pin against
`TEMPLATE.html` and fails the build on mismatch. (`build-colleges-schools.py` and
`build-interest.py` take the whole head from TEMPLATE, so they never drift.)

### Expected console output at 1.19.5

Two categories, both benign, both present on a clean load — do not chase them:

- `Uncaught (in promise) ReferenceError: process is not defined` ×2 — thrown by the CDN bundle
  on **every** page in this project, at 1.18.12 and 1.19.5 alike.
- `ElementBuilder: "resize" is a DOM event and should use .on('resize', handler)…` — **new at
  1.19.5**, two per carousel-bearing page. Zero of these at 1.18.12.

  **It is a false positive in ElementBuilder's own heuristic** (upstream `041c88e`, which
  corrects an earlier, partly-wrong reading). `withEvents()` is used deliberately as *storage
  for lifecycle-invoked handlers*, not as DOM-listener registration, so the DOM-event-name
  check misfires. Both handlers do run: `resize` via an explicit
  `window.addEventListener` at `equal-width-items.ts:556`, and `load` via
  `Lifecycle.hooks.loadOnConnect` (`model/utilities/lifecycle.ts:17` → `ref.events.load()`)
  for thumbnail/wide/cards/base plus an explicit `carousel.events.load()` at
  `image/multiple.ts:118`. Proven at runtime, not inferred: `Event.load` sets inline
  `display:flex` and a gap on the slide track and both are present, and `EventSwipe` is
  attached inside `Event.load`, so touch swipe is wired too. Console noise only.

### Upgrade verification (1.18.12 → 1.19.5)

Before/after probe of all 11 pages at 1280px — horizontal overflow, broken images, component
count, unregistered tags, section count and per-section heights:

- **No structural change on any page.** Same component counts, same section counts, zero broken
  images, overflow unchanged everywhere (`admissions.html` keeps its documented 64px).
- Four pages shifted height by small amounts, all in carousel-bearing sections:
  `academics/index` −8px, `interest-engineering-technology` +81/−6px,
  `transfer-applicants` +3px, `student-life` −32/−8px. Consistent with the 1.19 carousel
  refactor; nothing reflowed or broke.
- `umd-element-utility-header` reports as unregistered with no shadow root on **all 11 pages at
  both versions**. This was recorded as a pre-existing baseline condition; upstream later
  established (page-builder `0f35707`, 2026-09-08) that the tag never existed in any version.
  It has since been removed from `shared/header.html` and from every page here.

## Overlay pathway on a dark band — use `data-theme="white"`, not `"light"`

`RULES.md` already lists the panel colours (`white` → white panel, `light` → **light gray**
panel). What it does not say is that the two themes also differ in **layout**:

| `data-theme` | `.pathway-overlay-container-lock-wrapper` padding | Panel colour |
|---|---|---|
| `white` | `0` | `#FFFFFF` |
| `light` | **`80px 0`** | `#F1F1F1` |

So `light` silently adds 160px of vertical space (80 top + 80 bottom) *inside* the pathway, on
top of the component's own `104px` text padding and on top of the band's `104px`. Measured on
the same section, same content, changing only that one attribute:

| | `data-theme="light"` | `data-theme="white"` |
|---|---|---|
| Choosing a Major — pathway height | 918px | **758px** |
| Application Platform — pathway height | 729px | **569px** |

The tell is `.pathway-overlay-container-lock-wrapper`: the component's own `:host *` reset
zeroes padding, so `0px` is the baseline and anything else is the theme adding it. Check that
node, not the section, when an overlay pathway looks over-padded.

`pages/admissions.html` had this right from the start (`data-display="overlay"
data-theme="white"` on a `umd-layout-background-full-dark` section) — it is the reference for
this treatment. Note its section also carries `umd-layout-background-full-dark-no-top`, which
is **not defined anywhere** (absent from `critical.css`, every `web-styles-library` bundle, and
the page's own `<style>`); the section still computes `padding-top: 104px`. It is a dead class,
not part of why that page looks right — don't copy it forward expecting it to do something.

**Registry gap:** `registry-content.json` lists `data-theme` values as `dark | light | maryland`
for `umd-element-pathway` — `white` is missing, even though `RULES.md` documents it and it is
the correct value for a white panel on a dark band.

Pages using this: `pages/admissions.html`, `pages/how-to-apply/transfer-applicants.html`.

## Card-overlay `.size-large`: the IMAGE variant needs an explicit `height`

`web-components.min.css` ships only the **min-height** half of this class:

```css
umd-element-card-overlay.size-large { min-height: 320px }   /* mobile  */
umd-element-card-overlay.size-large { min-height: 560px }   /* 768px+  */
```

That sizes the **host** but not the **card**. The image variant's shadow root paints
`.card-overlay-image`, which is `height: 100%` — and a percentage height does not resolve
against a parent whose own height is `auto`. It falls back to content height, so
`.card-overlay-image-container`'s internal `min-height` (360px mobile / **424px** tablet+)
wins and the painted card stops short inside a taller host.

Measured on `pages/how-to-apply/transfer-applicants.html` before the fix: host **549×560**,
painted card **549×424** — 136px of dead space under a card that looked simply "not stretching".
Nothing in the console, nothing broken, the class *is* applied — which is what makes it hard to
spot. Look at `.card-overlay-image`, never the host, when checking whether `size-large` took.

An explicit height on the host gives the percentage something to resolve against:

```css
@media (min-width: 768px) {
  umd-element-card-overlay.size-large { height: 560px; }
}
```

**Tablet and up only.** The registry (`registry-cards.json`, `card-overlay.classes[]`) also
prescribes `height: 320px` at mobile, but the inner container's mobile `min-height` is 360px,
so an explicit 320 **clamps the card 40px shorter than its natural size** — `size-large` would
make the card *smaller*, which is backwards. Below 768px leave it alone; the bundle's
`min-height: 320px` stands as a floor and the card renders at its natural 360px.

**The COLOR variant is unaffected.** `.card-overlay-color` fills from `min-height` alone —
verified on `pages/how-to-apply/freshman-applicants.html`, whose two colour cards measure
host 560 / painted 560, zero dead space, with no page CSS at all. This is why the
"§16 RETIRED — OVERLAY CARD `.size-large` MIN-HEIGHT" note in the critical-CSS block reads as
correct: it was written when only colour cards were in play. It is accurate for the colour
variant and **wrong for the image variant** — the bundle took over `min-height` only, and the
image variant always needed the other half.

**Upstream candidate:** give `.card-overlay-image` a `min-height: inherit` (or make the
size-large rule set `height`, not `min-height`) so the two variants behave alike.

Pages using this: `pages/how-to-apply/transfer-applicants.html` (Services for Transfer
Students — feature card in a sticky column), `pages/tuition/index.html` (Terrapin Commitment /
Office of Student Financial Aid — the flush pair, see below).

## Flush overlay-card pair (`.umd-layout-grid-pair-flush`)

Two image-overlay cards butted edge to edge, so the pair reads as one dark band split down the
middle rather than two stacked promos. **No upstream class does this** — every `layout.min.css`
two-column grid ships a gap (`umd-layout-grid-gap-two` = 32px), and `gap: 0` is the entire point,
so it is page CSS rather than a missing bundle rule.

```css
.umd-layout-grid-pair-flush { display: grid; grid-template-columns: 1fr; gap: 0; }
@media (min-width: 768px) {
  .umd-layout-grid-pair-flush { grid-template-columns: 1fr 1fr; }
  .umd-layout-grid-pair-flush umd-element-card-overlay.size-large { height: 560px; }
}
```

The `height: 560px` half is not optional — it is the `.size-large` image-variant fix documented
directly above. Without it the two cards paint at 424px inside 560px hosts and the seam between
them shows as a band of dead space.

**The component clones, it does not slot.** `umd-element-card-overlay`'s shadow root contains no
`<slot>` elements at all; it copies `image` / `headline` / `text` / `actions` out of the light DOM.
So every light-DOM child measures `0×0` and reports `assignedSlot: null` **on a card that is
rendering perfectly** — verify against the clone inside `shadowRoot`, never the original. The CTA
nests one level deeper again (the cloned `umd-element-call-to-action` has its own shadow root), so
a visible-anchor check has to walk both roots.

Pages using this: `pages/tuition/index.html`.

## Application checklist stepper (`.fa-*`)

`pages/how-to-apply/freshman-applicants.html` § "Application Checklist" — a numbered stepper. There is **no steps / how-to / process component anywhere in `page-builder/registry/`** (all 15 category files checked); the nearest options are an accordion stack, `umd-element-tabs`, or numbered stats, none of which match the source's always-open numbered blocks. The source page uses its own `<umd-stepper>` element, reproduced here.

`.fa-steps` (`<ol role="list">`) / `.fa-step` / `.fa-step-num` / `.fa-step-body` / `.fa-step-title`. No JS, no shadow DOM.

**The numeral stands outside the card.** `.fa-step` is a bare grid (no surface of its own); the card surface lives on `.fa-step-body` so the numeral can sit in a gutter beside it. Geometry: a `#FAFAFA` (gray-lightest) card inside a `1px solid #F1F1F1` (gray-lighter) hairline, with `border-left` replaced by `2px solid #E21833` — the red rule moved off the numeral's right edge and onto the card's left edge. Corners are `border-radius: 0 var(--umd-space-md, 24px) 0 var(--umd-space-md, 24px)` — a "leaf" cut on the top-right and bottom-left only. **The DS ships no radius scale**, so that borrows the spacing token; if a radius scale is ever added upstream, this is the line to migrate. At the rounded bottom-left the 2px red left border meets the 1px gray-lighter bottom border, and browsers interpolate width and color across a curved corner — so the red rule tapers out rather than turning a crisp corner. That reads as an intentional taper here, but it is a rendering side effect of the mismatched borders, not something the CSS states. `40px` padding at ≥768px (`32px 24px` below), `var(--umd-space-xl, 40px)` between cards; two columns (`44px 1fr`, 24px gap) at ≥768px collapsing to one (8px row gap) below, so the copy keeps a full-width measure on mobile.

**The gutter is a fixed 44px and the numeral is right-aligned in it.** Barlow Condensed digits are proportional — at the 80px desktop size `1` measures 23.7px and `4` measures 39.1px — so an `auto` column would start each card at a different `x`, and left-aligning in a fixed column would leave 17–32px of ragged dead space before the rule. `text-align: right` (≥768px only; mobile stacks left-aligned above the card) puts every numeral exactly 24px from the card's red rule, making the rule the column the eye reads. 44px clears the widest digit with a little headroom.

**Spacing custom properties are `--umd-space-*`, not `--umd-spacing-*`.** `tokens.min.css` ships `--umd-space-min/xs/sm/md/lg/xl/2xl/…` (8/12/16/24/32/40/48px) alongside `--umd-color-*` and `--umd-font-size-*`; there is no `--umd-spacing-` prefix, so that spelling silently falls through to the declaration's fallback. The steps gap uses `var(--umd-space-xl, 40px)`.

The numeral is top-aligned with the card's top edge and needs no nudge: `.umd-campaign-large`'s `0.91em` line-height trims the line box to about cap height, which happens to land the numeral's baseline within ~4px of the card title's.

The 48px between the intro rich text and the first step comes from `umd-layout-vertical-landing-child` on the intro (32 / 40 / 48px), not a hand-rolled margin.

**Type comes from DS classes in the markup, not from this CSS** — `.umd-campaign-large` on the numeral (Barlow Condensed; 32px → 44px → `calc(44px + 2.66vw)` → **80px** at ≥1024px), colored `#E21833` here, `.umd-sans-larger-bold` on the title, `.umd-text-rich-advanced` on the body. The rich-text class also supplies the RULES §34 gradient-underline link treatment, so no hand-rolled link CSS is needed. Only geometry and the red are page-built.

`role="list"` on the `<ol>` is required: `list-style: none` strips list semantics in Safari/VoiceOver, and the numerals here are visible content rather than markers.

Pages using this: `pages/how-to-apply/freshman-applicants.html`.

## Brand chevron under a dark card band (`.fa-chevron`)

`pages/how-to-apply/freshman-applicants.html` § "Early Action / Application Platforms" — the same treatment as the When-to-Apply band above, ported to a `umd-layout-background-full-dark` section with two colour overlay cards. `umd-element-brand-logo-animation` enters from the **screen's left edge** and tucks under the card grid; kept **unmirrored** (mirroring reverses the arrows) and shifted a full viewport left, with `overflow: visible` scoped to `.fa-chevron > umd-element-brand-logo-animation` to defeat the DS `:defined { overflow: clip }` 25vw box. Slide-in is an `IntersectionObserver` toggling `.fa-chevron.is-in` plus a CSS transition, not the DS view-timeline animation. Hidden below 1024px.

**Anchor on the card grid, not the `umd-layout-space-horizontal-*` lock.** The lock is full-bleed and creates its inset with padding, so `getBoundingClientRect().left` is `0`; anchoring to it parks the chevron tip at the card's edge instead of 70px under it. `.umd-layout-grid-gap-two` reports the real content left (64px at 1440px), giving the intended tuck. The When-to-Apply original anchors on `.wta-gold`, which is an inner div and therefore already reports the content edge — the difference only shows up when porting.

**On a black band the black chevron in the stack disappears** and only the red and gold read. That is the intended layered effect here, but it means the motif carries less weight than it does on the white-background When-to-Apply band — worth checking against the design before reusing on another dark section.

Pages using this: `pages/how-to-apply/freshman-applicants.html`.

## Deadlines table

`.deadlines-table` — simple two-column rich-text table for the Important Dates section. Admissions-specific.

## Applicant spotlight — stats and deadlines in the pathway `stats` slot

The legacy site has a `umd-spotlight-deadlines` component: photo beside a text
lockup carrying **intro copy + two CTAs + a two-up stat pair + an
application-deadline table**. The design system covers the first two and nothing
covers the last two together. The recreation is
`umd-element-pathway data-display="sticky"` with the stat pair and the deadline
table both living in `slot="stats"`.

Pages using this: `pages/personas/prospective-students.html` (four instances).

### Why the CSS is a shadow injection and not page CSS

`slot="stats"` is the one pathway slot that is **cloned rather than slotted** —
`createCompositeStat` does `statWrapper.element.innerHTML = stats.innerHTML`
(`web-elements-library/dist/composite/pathway/_common.js`). The markup ends up
inside the shadow root, so the page `<style>` block cannot reach `.applicant-*`.
Every rule for the stat pair and the deadline table is injected into
`el.shadowRoot` at the foot of the page.

`slot="text"`, by contrast, goes through `createStyledSlotOrClone`: adding a bare
`styled` attribute to that div would make the component emit a real `<slot>` and
keep the content in the light DOM. **Do not try that on `stats`** — the composite
reads `stats.innerHTML`, and a `<slot>` element's `innerHTML` is empty, so the
whole block silently disappears.

### What the component already gives you

`.text-lockup-medium-stats` is a grid: one column with a 24px gap, becoming
`repeat(2, 1fr)` with a 32px gap from container width 800px. The stat pair fills
those two columns; `.applicant-deadlines` takes `grid-column: 1 / -1` and spans
the row beneath them. Below 800px the whole thing stacks and picks up the
component's own `border-top`.

### Why not `umd-element-stat`

`createStatElement` **hard-truncates `slot="stat"` to six characters** and logs
`Stat text is too long` — `A's or B's` renders as `A's or`, `B or better` as
`B or b`. The component is correct for numeric metrics and was left alone; the
applicant profile stats are qualitative, so `.applicant-stat` is a separate
treatment: one uniform value size for numeric and phrase stats alike, on the
gold left rule that `umd-element-stat data-decoration-line` uses.

The value is `.umd-campaign-small` (Barlow Condensed italic 700, `0.02em`
tracking) in `--umd-color-red`, stepping 32px → 44px.

### No new type styles in the injection

A shadow root cannot see the CDN stylesheets, so **every type style in the
injection is an existing styles-package class restated declaration for
declaration**, including its viewport `@media` steps — those work in a shadow
root unchanged. Nothing here is a new scale entry. If a size is needed that is
not on this list, take another class off the scale rather than inventing one.

| Selector | Restates | Plus |
|---|---|---|
| `.applicant-stat-value` | `.umd-campaign-small` | `--umd-color-red` |
| `.applicant-deadlines-title` | `.umd-sans-medium` | `font-weight: 700`, caps |
| `.applicant-stat-text p` | `.umd-sans-small` | `--umd-color-gray-dark` |
| `.applicant-deadlines-group` | `.umd-sans-small` | `--umd-color-gray-medium-a-a` |
| `.applicant-deadlines-table td` | `.umd-sans-small` | — |

The deadline header is set in caps by `text-transform`, not by typing
"APPLICATION DEADLINES" into the markup — it is an `<h3>`, and the transform
keeps the accessible name sentence case (some screen readers spell all-caps
strings out letter by letter). The home page's "EARLY ACTION DEADLINES" label
predates this and is typed literally.

Verified by comparison against live reference elements carrying the real CDN
classes: at 1280px the title computes 18px/27.9px (matching `.umd-sans-medium`)
and the small text 16px/22px (matching `.umd-sans-small`); at 375px, 16px/22px
and 14px/19.25px respectively.

The one exception is `.umd-campaign-small`'s **size ramp**, re-keyed from
viewport media queries to **container** queries — what the value has to fit is
the stat column, not the window.

Everything outside the shadow root uses the CDN classes directly and adds no
page CSS: the accordion sub-headings are `umd-sans-large text-black` (the pair
the home page uses for its "Early Action Deadlines" label), which works because
`umd-element-accordion-item` projects `slot="text"` through a real `<slot>` and
leaves the content in the light DOM.

The two-up grid is **held back to container width ≥ 1000px**, overriding the
component's own 800px. Half an 800px container leaves ~125px of text per stat:
`4,777` fits, `B or better` (127px at 32px) does not, and the row ends up with a
one-line stat beside a two-line one. Verified slack at each tier: 27px at
container 1009, 53px at container 1400 where the size steps up.

**Both numbers are tied to the typeface.** They were first set for an Interstate
value (`B or better` = 172px at 32px) and needed a 1150px breakpoint; Barlow
Condensed is narrow enough to bring it back to 1000. Measure the longest value
before changing either.

The override selector must be written
`.text-lockup-medium-stats:has(> *:nth-child(2))`, matching the component's own
rule. `:has()` takes the specificity of its argument, so the DS rule scores
(0,2,0) and a plain `.text-lockup-medium-stats` would lose.

### Content, not CSS

Two of the source page's stat values were rewritten rather than styled around.
`B average or better` became **`B or better`**, with the displaced sentence moved
into the stat's label ("Grade average earned by our most successful transfer
students."). The value slot is a display line; a sentence belongs underneath it.

### No 1:1 aspect-ratio injection on sticky pathways

The "Pathway 1:1 image aspect ratio" override above is for the standard and
overlay variants. A **sticky** pathway needs its image column to run the full
height of the text column — that is what it sticks against — so capping the
ratio would defeat the variant. Verified: at 1700px the Freshman block's image
column holds at 656px while its text column runs 1050px.

### Deadline table

Visually the same label/date list as `.deadlines-table` on the home page — black
rules, right-aligned bold dates — restated inside the injection because the
shadow root cannot see the page stylesheet. Both the audience label
(`.applicant-deadlines-group`, e.g. "U.S. Students") and the whole deadline block
are optional: International omits the block, Shady Grove omits the label.

No rule above "Application Deadlines" — the block is separated from the stats by
its `padding-top` alone. The gold left rules on the stats already read as the
divider; a border on top of them doubled it.

## Hero-grid overhang swallows clicks on the section below

`umd-element-hero-grid` renders `.hero-expand-text-container` in its shadow at
`position: relative; z-index: 9999` with the full host height, while offsetting
it upward — so the box ends roughly 1150px **below** the bottom of the host. The
host creates no stacking context of its own, so that `9999` competes at the
root, and the invisible overhang lies over whatever follows and intercepts every
pointer event in it.

On `pages/admissions.html` that is the "Information For" band: all four CTAs
were unclickable. The markup was never the problem — `document.elementFromPoint`
at each button's centre returned `UMD-ELEMENT-HERO-GRID`, and a scripted
`a.click()` still navigated because it bypasses hit-testing. **If a link looks
correct but "doesn't work", hit-test it before touching the href.**

Fix — a light-DOM rule on the host, in the page's own `<style>`:

```css
umd-element-hero-grid { isolation: isolate; }
```

That gives the host a stacking context, which keeps the `9999` inside the hero.
The section below is later in DOM order at `z-index: auto`, so it hit-tests
above the overhang. Verified: host height, every image height and total page
height identical before and after, and a real mouse click at the button's screen
coordinates navigates.

### ⚠️ Do not use `overflow: hidden` here

It also stops the escape, and a scan of painted descendants suggests it clips
nothing — but it **breaks the hero component**. The collage is scroll-driven and
`overflow: hidden` on the host cuts it off; the scan misses this because it
measures one frame of a component whose children move. `isolation` changes paint
order only, never geometry, which is why it is the safe form of this fix.

### Hit-testing across a shadow boundary

`document.elementFromPoint()` **retargets** anything inside a shadow root to its
host. A point over content inside `umd-element-hero-grid` therefore always
returns `UMD-ELEMENT-HERO-GRID`, whether that content is reachable or not — so
the method only diagnoses a block when the element you expect is in the **light
DOM**, as the "Information For" CTAs are. For anything inside a shadow root,
descend explicitly:

```js
let node = document.elementFromPoint(x, y);
while (node && node.shadowRoot) {
  const next = node.shadowRoot.elementFromPoint(x, y);
  if (!next || next === node) break;
  node = next;
}
```

Run against the hero's own "Explore Academics at UMD" CTA that yields
`UMD-ELEMENT-HERO-GRID → UMD-ELEMENT-CALL-TO-ACTION → A.umd-action-primary`:
reachable, and clicking it works. The bare `elementFromPoint` reading that
suggested otherwise was retargeting, not a block.

## Small pathway zig-zag — responsive image + balanced grid

Two-column image + text (zig-zag) rich-text sections — **now generalized in `page-builder/LAYOUT-PATTERNS.md`** ("Light background — two-column image + text (zig-zag)"), including the responsive-image / balanced-grid and `<hr>` border CSS; the headline-flattening gotcha (a true 32px headline must sit outside the `umd-text-rich-advanced` wrapper) lives in `page-builder/RULES.md §18`. Modeled on the QA design-team `/components/images-and-media` sections `section-60493` / `section-60498`.

Pages using this: `pages/student-life/index.html`.

## CDN-bundle architecture (migrated from self-contained inline CSS)

All four pages were migrated from the old **self-contained** model (a hand-rolled ~1.18.2-era critical.css inlined in full, no CDN CSS) to the canonical **`TEMPLATE.html` model**: the 9 DS CSS bundles loaded from unpkg, then the current Local-Only `critical.css` inlined, then `cdn.js`.

```html
<link ... css/font-faces.min.css>  <link ... css/tokens.min.css>       <link ... css/base.min.css>
<link ... css/typography.min.css>  <link ... css/element.min.css>      <link ... css/web-components.min.css>
<link ... css/layout.min.css>      <link ... css/animation.min.css>    <link ... css/accessibility.min.css>
<style> …verbatim styles/critical.css (header stripped)… </style>
<script src="…web-components-library@1.18.12/dist/cdn.js"></script>
```

Load order (CDN links → inline critical → `cdn.js`) matters: browsers block on stylesheet fetches before the script, so all CSS applies before elements upgrade. `cdn.js` was bumped `1.18.2 → 1.18.12` to align the component JS with the CSS bundles. This retired the hand-rolled carousel FOUC guards — `web-components.min.css` now ships the carousel host rules (`display`/`container-type`) + placeholder sizing; do **not** re-add a local `content-visibility: hidden` (it loads after the CDN link at equal specificity and reintroduces layout shift).

### Page-specific CSS preserved outside `critical.css`

The old inline block mixed critical CSS with project-specific rules. Those NOT in the CDN bundles or `critical.css` were moved to each page's second `<style>` block:

- **Utility-navigation flat links (all four pages).** These pages use plain `<a>` links in `div[slot="utility-navigation"]` (Visit UMD / Connect), **not** the DS `umd-shell-utility-item` pattern that `critical.css` §11 now targets. §11 scopes `umd-element-navigation-header div[slot="utility-navigation"] { gap: 0 }`, which jams flat links together. Fix: re-declare the flat-link `display:flex; gap:24px` + link styling at the **same** scoped specificity (`umd-element-navigation-header div[slot="utility-navigation"]`) in the page's second `<style>` so it wins by source order. (Future option: migrate the markup to the shell-utility-item pattern instead.)
- **`admissions.html` extras:** `.quote-with-chevron` / `.chevron-overlap`, `.deadlines-table`, `umd-element-hero-grid` height guard, `.banner-promo-actions`, rich-text heading specificity overrides, and `.umd-layout-grid-cards-no-gap` (used only on admissions; absent from CDN + critical.css) — preserved in a second `<style>` block appended after `cdn.js`.

`.umd-layout-grid-tuition-two` and `.umd-action-outline-block` live in `critical.css` (kept upstream), so they were not re-added except where already bundled in the admissions preserve block.

Pages: `pages/academics/index.html`, `pages/admissions.html`, `pages/student-life/index.html`, `pages/tuition/index.html`.

## `.text-black` loses inside rich text (fixed in `critical.css` + `TEMPLATE.html`)

`.text-black` had no effect on anything inside `.umd-text-rich-advanced` — the text rendered `#454545` (gray-dark) instead of `#000`. Both rules are specificity **(0,1,0)**: `.text-black` (§6 COLOR UTILITIES, line 223) and `.umd-text-rich-advanced *` (§7 RICH TEXT ADVANCED, line 243). `*` contributes nothing to specificity, so the tie breaks on source order — and §7 comes after §6, so the component rule beats the utility.

Fix: `.umd-text-rich-advanced .text-black { color: #000; }` added to §6. At (0,2,0) it wins regardless of file order, so it does not depend on the sections staying in sequence.

**No `!important`** — `pages/admissions.html` had already hit this and solved it locally with exactly this scoped rule in its preserved page-specific block; this promotes that precedent to `critical.css` so every page gets it. The local copy in `admissions.html` is now redundant but harmless (identical declaration) and was left in place.

Only the light variant needed it: of the wildcard colour rules in `critical.css`, `.umd-text-rich-advanced *` is the one that clobbers this utility. (`.umd-text-rich-simple-large-dark *` sets `#ffffff`, where a `.text-black` would be deliberate.) `.text-white` has the same latent bug but is currently unused in this repo — left alone.

Verified: every `.text-black` on `freshman-applicants.html` (10), `admissions.html` (4) and `academics/index.html` (1) computes `rgb(0,0,0)`, while ordinary rich-text body copy still computes `rgb(69,69,69)` — the utility wins without flattening the body-copy colour.

## Rich-text links: doubled underline (fixed in `critical.css` + `TEMPLATE.html`)

Rich-text links rendered with a **doubled underline** — visibly heavier and darker than the live site. Cause: the DS draws its link underline as a 1px `background-image: linear-gradient(...)` with `background-size: 100% 1px`, but **neither `element.min.css` nor `critical.css` ever set `text-decoration: none`**, so the browser's default UA underline stayed on *underneath* the gradient hairline. Two stacked underlines.

`base.min.css` is not the reset it looks like — it has **zero** `text-decoration` declarations and no `a` selector at all (it resets `*`, `body`, headings, `p`, `li`, and form fields only). Production UMD pages get the reset from a site-level preflight these standalone prototypes don't load, which is why the bug is invisible upstream.

The tell is the hover state: `element.min.css`'s hover rule carries `text-decoration: none !important`, so hovering *removed* the UA underline and the link got **lighter** on hover — backwards.

Fix: `text-decoration: none` added to the three rest-state rules (`.umd-text-rich-advanced a`, `.umd-text-rich-advanced-dark a`, `.umd-text-rich-simple-large-dark a`). Hover rules untouched.

**Two copies had to be patched.** `page-builder/styles/critical.css` is canonical, but the generated-page scripts inline their `<head>` from **`page-builder/TEMPLATE.html`**, which carries its own pre-inlined copy of the same CSS. Patching only `critical.css` looks correct and then silently reverts the moment `build-programs.py` / `build-colleges-schools.py` / `build-interest.py` runs. Both files, plus the already-inlined copy in all 9 pages, must move together.

⚠️ **Do not "clean up" a bad insert with a blanket string replace on `  text-decoration: none;`.** Declarations are 2-space indented in `critical.css`, so that pattern also matches the load-bearing `.umd-shell-utility-item a`, the utility-nav `button`, the dropdown `a`, and an action-button rule — silently deleting four rules including the flat-link treatment documented above. Patch by locating the specific rule and inserting only.

Pages using this: all nine (verified `text-decoration-line: none` on all 18 rich-text links on `freshman-applicants.html`, gradient hairline intact at `100% 1px`).

## Post-migration regression fixes

Two things regressed when the pages moved to the CDN-bundle architecture (the DS bundles differ from the old self-contained CSS):

**Rich-text eyebrow/header color.** The `umd-sans-*` typography classes set no color; `base.min.css` defaults paragraph text to the DS gray `#454545`, so section eyebrows ("Study Here", "Make UMD Yours", "College Is a Major Investment") rendered muddy gray instead of black. Fix: add `text-black` to the eyebrow `<p>` (light bg) — `.text-black` ships in `critical.css` and beats the base `p` color. Documented as a reusable pattern in `page-builder/RULES.md §18` and the `evaluate-design` component-risk list.

**"Information For" outline buttons (admissions).** Previously plain `<a class="umd-action-outline-block">` in a no-gap `umd-layout-grid-columns-four` (no spacing). Now the DS component: `umd-element-call-to-action[data-display="outline" data-theme="dark"]` in `umd-layout-grid-gap-four` (32px gap, 1→2→4 cols). The component's inner anchor is `inline-block` with a shadow-DOM `max-width:380px`, so it won't fill the cell — a shadow injection (see end-of-body script, keyed off `.information-for-actions`) forces the inner `[class*="umd-action-outline"]` to `width:100%; max-width:none; display:block; text-align:center`. Host filled via light-DOM `.information-for-actions umd-element-call-to-action { display:block; width:100% }`.

## `pages/academics/programs.html` — A–Z program explorer (experts-style filter)

New page recreating <https://admissions.umd.edu/programs> in the DS. Chrome (header/nav/footer/end-of-body scripts + inlined `critical.css`) copied verbatim from the `pages/academics/index.html` reference. Only `<main>` is page-specific: a small hero + a two-column **filter rail + A–Z directory**, modeled on the client-side filter UX of <https://umdrightnow.umd.edu/experts> (which has no alphabet nav of its own — that piece is original).

- **Data is embedded, not fetched.** All 203 programs (name, dept link, type labels, colleges, interests, **plain-text description**) are inlined as a JS array in an end-of-body `<script>` (harvested once from the admissions Craft GraphQL endpoint; descriptions stripped of HTML). Filtering is 100% client-side over that in-memory array — no runtime API/token dependency. Regenerate via `python3 scripts/build-programs.py` (reads `briefs/programs-data.json`, takes the `<head>` from `page-builder/TEMPLATE.html` and the header stack from `pages/academics/index.html`). The generated HTML is overwritten wholesale — edit the JSON or the generator's literal blocks, not the page.
  - **The description transform is order-sensitive:** strip tags → unescape entities → collapse whitespace. Any other order changes the bytes (a stray double space where a tag was removed, or `&amp;` surviving literally). The array is serialised with `separators=(',', ':')`, which keeps it at ~129KB instead of ~132KB.
  - **The generator's literal blocks are RAW strings** (`r'''…'''`). They contain CSS/JS backslash escapes (`\2212`, `“`); as normal triple-quoted strings Python reinterprets those and the output is silently corrupted.
  - Grid-entry animations stay **inlined** on this page rather than using `<script src="../page-builder/scripts/grid-animations.js">`. The inlined copy (77 lines) predates and differs from the canonical script (114 lines), so switching is a behavioural change, not a refactor — do it deliberately, not as a side effect of regenerating.
- **Filter model** mirrors experts: free-text search + three accordion checkbox groups (Program Types / Colleges & Schools / Interests). **AND across groups, OR within a group.** Removable "Filtered by:" pills + Clear all; Reset; mobile Filter toggle. Page-built control classes are `pf-*`. The rail's **REFINE** heading uses the DS **`.umd-tailwing-right-headline`** (from `element.min.css`) — a 14px uppercase label with a thin rule trailing to the right; it requires a `<span>` child (masks the line behind the text via inherited white bg) and auto-adds `margin-top:40px` to the following element.
- **Search bar** sits in the results column under the A–Z nav (its own `#pf-search-bar` form, not in the rail), styled after the experts search. The input needs *no* custom box CSS — the DS global `base.min.css` rule `input{}` already supplies the experts look (white bg, `1px solid #E6E6E6`, `12px 16px` padding, full width). The form itself wears the DS **`.umd-layout-background-highlight-light`** class (from `layout.min.css`): gray `#F1F1F1` panel + `border-left:2px solid #E21833` + responsive padding (24→32→56px) — the experts "highlight card". The only page-built piece is the 48px square Maryland-red submit button (`.pf-search-submit`, `#e21833`, hover `#a90007`) holding the experts search-glyph SVG, in a `flex; gap:8px` row.
- **Option labels use the DS `.umd-field-checkbox-wrapper` class** — the DS-native fix for the global `base.min.css` rule `label{font-weight:700}` (that element rule is why bare `<label>` choice text renders bold). `.umd-field-checkbox-wrapper` ships `font-weight:400`, so only the group **header** button stays bold. No page-level weight override, no upstream change needed. Per-option result counts (`(104)`) use `.umd-sans-smaller` (14px grey) rather than a pill, to keep the checkbox/text baseline aligned.
- **Program rows use `umd-element-card data-display="list"`** (no image slot): `headline` = program name (linked to dept page), **`text` = the program description**, and the **`date` slot carries the type labels** (`Major | Limited Enrollment Program`) — the DS list card has no dedicated badge slot, so the bottom date slot is repurposed per design direction. `<p slot="date">`, not `<time>`, renders fine.
- **Active-filter pills** ("Filtered by: …") use the DS **`.umd-text-cluster-pill`** child treatment (`#FAFAFA` 12px squared chip, hover yellow `#FFD200`) — the pill buttons are wrapped in a `<span class="umd-text-cluster-pill pf-pill-cluster">` (the wrapper's DS `margin-top:-8px` hack is neutralized in favor of flex gap; button hover-yellow added in page CSS since the DS rule targets `a`). Each pill's text + × sit in an inner `<span>` (DS `> span{display:flex;gap:4px}`). The **results count** (`.pf-count-line`) and the **Clear all** link use `.umd-sans-smaller` (14px).
- **Hero** is left-aligned (omit `data-layout-text` — `center` is its only alignment value, left is the default), height `small`, with a primary CTA in `slot="actions"` linking to the colleges-schools page. Image `images/academics/students-walking.jpg` (converted from the sibling `.webp` via `sips`; 2880×1088, ~460KB).
- **`.az-letter`** in-list letter headings: `margin-bottom` 8px mobile, **24px at ≥1024px**.
- **Scroll-to-top** (`umd-element-scroll-top`) is placed once at the end of `<main>`, before the footer. Gotcha: the DS fixed-position rule (`web-components.min.css`) keys on `[data-layout-fixed="true"]` (explicit value) or a bare `[fixed]` attribute — a boolean `data-layout-fixed=""` does **not** match and the button stays `position:static` in flow. Use `data-layout-fixed="true"`. DS default is `right:40px; bottom:10vh`; page CSS overrides to `right:24px; bottom:24px` (fixed to the viewport bottom-right). Component is 52×52 at `z-index:9999`; smooth-scrolls to top on click.
- **"Reset filters" is an outline CTA** (`umd-element-call-to-action data-display="outline"` wrapping a `<button type="button">`). The CTA clones its child into shadow DOM, so a native `type="reset"` can't reach the light-DOM form; the reset is wired by listening for `click` on the light-DOM `.pf-actions` wrapper (the composed click on the shadow-cloned button retargets to the CTA host and bubbles there) → `clearAll()` unchecks all boxes, clears the search, re-renders. Same `clearAll()` backs the "Clear all" pill.
- **A–Z typography:** letter quick-nav uses `.umd-campaign-extrasmall` (32px) and in-list letter headings use `.umd-campaign-small` (44px desktop), both recolored to Maryland red `#e21833`. Nav letters with no matches render as dimmed grey `.az-off` spans; active letters smooth-scroll to their section (`scroll-margin-top:120px` clears the sticky nav). Active letters recompute on every filter change.

No shadow injections introduced. Page-specific CSS lives in its own `<style>` block before `</head>`; data + filter logic in a `<script>` before `</body>`.

## `pages/academics/colleges-schools.html` — expandable college card grid

New page recreating <https://admissions.umd.edu/programs/colleges-schools> in the DS. Chrome (header/nav/footer + inlined `critical.css`) copied verbatim from the `pages/academics/programs.html` sibling; only the hero, intro, and the college grid are page-specific. Regenerate via `python3 scripts/build-colleges-schools.py` (reads `briefs/colleges-schools-data.json`, splices into the `TEMPLATE.html` head + programs chrome). The generated HTML is overwritten wholesale — edit the JSON or the generator's `PAGE_CSS`/`PAGE_JS` blocks, not the page.

- **Hero is identical to `pages/academics/programs.html`** — `umd-element-hero data-layout-height="small"`, no `data-layout-text` (left is the default; `center` is its only alternative), CTA in `slot="actions"`. Verified pixel-identical to the sibling: 400px host height, `h1.umd-campaign-extralarge` at 80px, headline and CTA both at `left: 64px` inside the shadow `umd-layout-space-horizontal-larger umd-lock`.
- **Lock is `umd-layout-space-horizontal-larger` (1600px)**, matching the other card grids in this project. (`umd-layout-space-horizontal-large` / 1400px was tried first; it is a real class — see the lock table in `page-builder/RULES.md` § "Available classes", which lists all six including `-large`.)
- **Intro mirrors the sibling landing pages' rich-text lockup** (`pages/academics/index.html` "Study Here"): narrow centred `umd-layout-space-horizontal-small` (992px) column, 1px black `<hr>`, lead paragraph, then `.umd-text-rich-advanced` body. Unlike the sibling, the lead is **not** `text-transform: uppercase`, per design direction. There is no breadcrumb — the source page has one, but no other page in this project uses it.
- **Replaces the source's 13 stacked full-width rows with a bordered card grid** (1 / 2 / 3 cols at 650 / 1024px, `gap: 40px 32px` at desktop). Page-built classes are `cs-*`. Cards carry image + red uppercase abbreviation eyebrow + college name + description; description is `-webkit-line-clamp: 4` on the card and repeated in full inside the panel, so no copy is unreachable. Flex `margin-top:auto` on `.cs-tile-foot` pins the toggle to the bottom so tiles in a row equalize (478px at 1440px).
- **Card type scale is copied from the DS card-standard, measured off a live `umd-element-card` rather than read from source**: eyebrow 12px/700, headline 18px/700, body 16px/400 `#454545`. The card's `.umd-element-eyebrow` lives in its shadow styles and ships in **no** CDN bundle, so the eyebrow is restated in page CSS. The real `umd-element-card` is deliberately **not** used: it clones slotted content into shadow DOM, so a slotted toggle button's later `aria-expanded` / chevron-state mutations would never reach the rendered clone.
- **Measure the type classes, don't read them.** A locally downloaded `typography.min.css` disagrees with what the live bundle serves. Live, at 1280px: `smaller` 14 / `small` 16 / `medium` 18 / `large` 18-bold / `larger` 22 / `largest` **44**-bold (they scale fluidly below ~1200px). Reading the file instead cost a round trip here — `umd-sans-largest` was picked for the panel heading expecting 22px and rendered 44px.
- **Expansion is an "expander row", not a per-card accordion.** All 12 panels are children of the same grid, `grid-column: 1 / -1`, parked at the **end** of the grid where `display:none` removes them from grid flow. On open, JS moves the panel to sit immediately after the **last tile in the clicked tile's row** — `rowEnd = min(ceil((idx+1)/cols)*cols - 1, tiles.length-1)`, with `cols` read from `getComputedStyle(grid).gridTemplateColumns`. Without this the panel would break its row part-way and shunt its row-mates down. Single-open, like an accordion group. At 1 column this degrades to a plain accordion (panel lands directly after its own tile) for free.
- **Re-anchoring on viewport change is driven by `matchMedia` change events plus a 150ms-debounced `resize` fallback — deliberately NOT `requestAnimationFrame`.** rAF never fires while `document.hidden` is true, which is permanently the case in the in-app Browser pane (it renders offscreen); an rAF-based re-anchor silently no-ops there and would also stall in any backgrounded tab. Note the preview pane changes the viewport via a CDP metrics override that re-evaluates media queries but dispatches **no** `resize` or `change` event, so this path cannot be exercised by `resize_window` alone — verify by dispatching `new Event('resize')` after resizing.
- **Panel chrome borrows the DS accordion** without using the component (which has no multi-column body or grid-row placement): `border-top: 4px solid #e21833` over a `--umd-color-gray-lightest` body. Majors list is 1 / 2 / 3 / 4 columns at 650 / 1024 / 1280px; program names are `umd-sans-small` (16px). The heading is `umd-sans-larger` (22px) and the lead paragraph `umd-sans-medium` (18px).
- **The panel's lead paragraph is capped at `max-width: 960px`** — the DS paragraph measure, lifted from `element.min.css`: `:is(.umd-text-rich-advanced,.umd-rich-text) p,ul,ol,pre,blockquote { max-width: 960px }`. The value is **restated** rather than inherited by wrapping the paragraph in `.umd-rich-text`, because that class also forces `font-size: 18px` on its children and this paragraph is `.umd-sans-small` (16px). The majors grid below it still uses the panel's full width.
- **Program-type labels use the DS pill geometry with an outline, and are not clickable.** `.cs-types` wears `umd-text-cluster-pill` (12px, `padding: 8px 12px`, `#FAFAFA`) and `.cs-type` adds a 1px `--umd-color-gray-light` border. Children are `<span>`, not `<a>` — the DS hover-yellow rule is scoped to `a:hover`/`a:focus`, so spans stay inert and read as labels. **No per-type colour coding:** `Major` / `Minor` / `Certificate` / `Limited Enrollment Program` are peers, and an earlier revision that gave `Major` a black rule and LEP a red one implied a hierarchy that doesn't exist.
- **Pills sit on their own line below the program name**, which is `display: block` (`.cs-major-name`). `.cs-types` is `display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px`, so the 8px separation is identical horizontally, vertically between wrapped pill rows, and between the name and the pills. The DS pill rhythm (`.umd-text-cluster-pill` wrapper `margin-top: -8px` + child `margin-top: 8px`) is **neutralised** via `.cs-types > .cs-type { margin-top: 0 }` — left in place it double-counts against the flex gap and knocks rows out of alignment. Note `.cs-types > .cs-type` (0,2,0) is needed to beat the DS `:is(.umd-text-cluster-pill,.umd-pill-list) > *` (0,1,0).
- **Majors grid caps at 3 columns (1 / 2 / 3 at 650 / 1024px) — don't add a 4th.** The constraint is `Limited Enrollment Program`, the widest pill at 183px: a Major+Minor+LEP trio needs ~323px on one line. Measured at 1440px on CMNS (31 programs): **4 cols** (274px) → the trio wraps, row heights 91/131/135, spread 44px, 2 pill groups wrapping; **3 cols** (378px) → trio fits on one line, heights 91/113, spread 22px, **0** wrapping; **2 cols** (588px) → uniform 91px. 3 is the sweet spot — it buys row-height evenness for +16% panel height (1067 → 1238px), where 2 costs +56% for little further gain. Verified the same at 59 programs (ARHU: spread 22px, 0 wrapping). If the LEP label is ever shortened, a 4th column becomes viable again.
- **No CTAs inside the panels.** The college website is reachable from two places that already exist: the **card headline** and the **panel headline**, both linked to the college domain (`target="_blank" rel="noopener"`). An earlier revision also put a "Visit …" outline CTA at the foot of every panel — redundant, and 12 of them added noise.
- **Letters & Sciences has zero majors** (it's the undeclared-advising home), so its tile renders a direct `.cs-tile-link` to `ltsc.umd.edu` instead of a toggle, and no panel is generated. Journalism has exactly one program, so the toggle label is singularized ("View 1 program").
- **A11y:** each toggle carries `aria-expanded` + `aria-controls`; each panel is `role="region"` with `aria-labelledby` pointing at its `tabindex="-1"` heading, which receives focus on open. `Escape` closes and returns focus to the toggle; the Close button does the same. Deep links (`#agnr`) open the matching college on load and on `hashchange`.
- **Grid entry animations are opted out** (`data-animation="off"` on `.cs-grid`) — the stagger fights the expand/collapse motion.

- **Chrome CSS is harvested from the reference page, not hand-copied** (§24 "PROJECT CHROME COMPANIONS" in the generated page). Two chrome rules live in `pages/academics/programs.html`'s *page-specific* `<style>` block rather than `TEMPLATE.html`: the `div[slot="utility-navigation"]` flat-link restore (critical.css §11 targets the DS `.umd-shell-utility-item` pattern and scopes `gap: 0`, which jams this chrome's plain `<a>` children together unstyled) and the `umd-element-scroll-top[data-layout-fixed]` 24px/24px pin (DS default is `right:40px; bottom:10vh`). Building the head from TEMPLATE alone shipped the chrome markup without either, and **both regressions were silent** — no console error, correct-looking DOM, just wrong rendering. The generator now extracts any rule whose selector matches `CHROME_CSS_SELECTORS` from the reference page's page-specific CSS and **asserts at build time** that the markup and its CSS are both present, so the two cannot drift apart. Verified pixel-identical to `programs.html` at 1440px: slot 141×18 at top 68, links at x 1220/1307, gap 24px, scroll-top fixed 24/24. See `CLAUDE.md` § "Chrome markup alone is not enough".
- **Verify the utility nav at ≥1024px.** The DS hides the utility slot below desktop, so it measures 0×0 at tablet width — a narrow viewport masks this bug entirely. (An earlier check in this session recorded `utilityNavGap: "0px"` and it was mistaken for normal.)

No shadow injections introduced. The page references the canonical `../page-builder/scripts/grid-animations.js` by `src` rather than inlining it (per `page-builder/CLAUDE.md`); the older sibling pages still inline that block.

## `pages/interest-*.html` — interest pages

New page type recreating <https://admissions.umd.edu/programs/interest/engineering-technology> in the DS. Regenerate via `python3 scripts/build-interest.py [slug]` (no slug = every slug in the JSON). The generated HTML is overwritten wholesale — edit `briefs/interests-data.json` or the generator, not the page.

The page is almost entirely **derived**: the majors grid is `briefs/programs-data.json` filtered on the `interests` facet (which already tags all 203 programs across the 14 interests — E&T yields 34), and the college cards read `briefs/colleges-schools-data.json`. Only the editorial copy — hero/intro text, pathway copy, the careers list, and the curated college slugs — lives in `briefs/interests-data.json`. Adding the other 13 interests is a data edit, not a code edit.

- **Bordered cards are `umd-element-card[data-visual-bordered="true"]` — a boolean attribute on card-standard, not the article card's enum.** The DS handles it natively: `.layout-block-stacked-container` gets `1px solid rgb(230,230,230)` and `.layout-block-stacked-text` gets `padding: 24px`, both inside the shadow tree. **Write no page CSS for the border** — an earlier revision here hand-drew `border` + `padding: 24px` on the host and arrived at byte-identical values, which is exactly the redundancy to avoid.
  - **Two near-miss spellings that silently do nothing.** `umd-element-article` with `data-visual="bordered"` (the enum the registry *does* document, on the *article* card) renders no border at all in `cdn.js@1.18.12` — measured: host, `.layout-block-stacked-container` and `.layout-block-stacked-text` all compute `0px none rgb(0,0,0)`. Neither spelling errors; both just render unbordered, so **verify by computed style on `.layout-block-stacked-container`, never by the attribute being present in the markup.**
  - **Registry gap:** `page-builder/registry/registry-cards.json` lists only `data-display`, `data-theme` and `data-visual-image-aligned` under `umd-element-card` — `data-visual-bordered` is undocumented there despite being implemented, which is what sent this page to the article card's non-functional `data-visual="bordered"` first. **Upstream candidate:** add it to the card-standard entry, and either implement or drop the article card's `data-visual` values.
- **`umd-element-card` and `umd-element-pathway` CLONE their light-DOM slot content into shadow DOM.** The originals are left in the light tree measuring 0×0, so a page-level rule targeting slotted content styles a copy nobody sees — silently, with no console error. Class names *do* survive the clone, so the one slot-content rule this page needs — the 4-line clamp on `.interest-major-desc` — is shadow-injected against the surviving class. This is the same trap as the `cs-tile` note in §"colleges-schools" above, from the other direction — there the clone broke a slotted *button*'s state mutations; here it breaks slotted *CSS*.

- **Equal row heights are `umd-layout-grid-child-fill-height`** on each card (the DS class `page-builder/RULES.md` §9 uses for block stats), not a page `height: 100%` rule — another value hand-written here first and identical to the DS. Verified every grid row internally uniform at 1280 / 768 / 375, with the shadow `.layout-block-stacked-container` filling the full card height so the border wraps the whole card rather than hugging the text.
- **No description clamp — every program description displays in full.** Descriptions run 250–875 characters and the longest is shown entire. Truncating one is a content decision, not a layout one, and this page is the reader's index of what a major actually is. An earlier revision shadow-injected a 4-line `-webkit-line-clamp`; it is gone. The cost is uneven row heights (measured 387–754px at 1280px, the tall row being the 875-char AI program) — accepted, because `umd-layout-grid-child-fill-height` keeps each row internally uniform so the raggedness reads as varying row depth, not as broken cards. **Verify by asserting `scrollHeight <= clientHeight` on every card's shadow paragraph**, not by eyeballing — a clamp hides overflow, so a clipped card looks deliberate.
- **Pathway image injection uses the project's documented selector**, `.pathway-image-container, .image-container, .umd-asset-image-wrapper-scaled` (see §"Pathway 1:1 image aspect ratio"). An invented selector (`.umd-element-composite-pathway-image img`) matched nothing and failed silently — `data-pathwayCssDone` still read `1`, because the injection *ran*; it just had no targets. Check `getComputedStyle(container).aspectRatio` computes `1 / 1`, not that the script executed.
- **Photography is the source page's own, in `images/interest/`.** Three assets pulled from the live page's Sanity CDN: `hero-kim-building.jpg` (4000×2658, the `hero/DSC09225.JPG` banner), `wind-tunnel.jpg` (1024×683, the majors pathway) and `neutral-buoyancy.jpg` (1024×768, the careers pathway). The college card images are the same source files already vendored in `images/colleges-schools/`. **The CDN URLs are signed** (`s=<hash>` over the `w`/`h` params), so a larger crop cannot be requested by editing the query string — take the dimensions the page itself uses. Pathway images want ≥1000px: the 1:1 crop renders ~569px at a 1280px viewport, and a card-sized asset upscales badly (`images/academics/field-researcher-card-*.jpg`, 292×220, was tried first and rendered 650px tall).
- **The careers list is the source page's plain rich-text `<ul>`, single column.** A two-column grid was tried and reverted — the items are short and unevenly weighted, and two columns read as a table with a missing header. No page CSS and no injection; bullets and spacing come from the DS.
- **The careers pathway is `data-display="overlay" data-theme="dark"`.** Self-contained per §"Overlay pathway as a dark editorial block" — no `umd-layout-background-full-dark` wrapper. Verified: `.pathway-overlay-container-background` paints `rgb(0,0,0)`, headline and list items compute white, and the component swaps itself to `umd-text-rich-advanced-dark` + the white underline animation with no page CSS. The panel spans 348→2201 at a 1280px viewport (1853px wide, deliberately wider than the viewport); `critical.css` §21's `body { overflow-x: clip }` suppresses it and measured horizontal overflow stays 0 — don't "fix" it with a width cap.
  - **On the overlay variant the image column stretches to the text column, so a 1:1 image is a floor, not a lock.** Here the 10-item list makes the text column 656px, so the image renders 569×656 with `object-fit: cover`. That is the intended direction — text driving height, image following. The injection still matters: without it a tall source drives the height instead. Check which side is winning before treating a non-square overlay image as a bug.
- **Majors grid is 1 / 2 / 3 columns at 650 / 1024px.** 4-up was tried and reverted: at 260px wide, 34 cards read as a wall. 3-up gives 358px cards. The DS grid class ships in a CDN bundle, **not** `critical.css`, so the columns are restated in page CSS (34 cards would otherwise silently collapse to one column if the bundle failed), with the DS class left on the element for its gap/animation hooks. Colleges use the plain DS `umd-layout-grid-gap-three`. Note 34 is not divisible by 3, so the last row holds a single card.
- **Vertical rhythm inside a section: `umd-layout-vertical-landing` between two components, `-child` under a section intro.** The majors pathway and its card grid are two stacked *components*, so the pathway wrapper takes the full `umd-layout-vertical-landing` gap (56 / 80 / **120**px) — `-child` was tried first and its 48px read as cramped. The colleges section intro takes `umd-layout-vertical-landing-child` (32 / 40 / **48**px), which is exactly the 48px RULES §10 requires between an intro and the content it introduces. Measured on the page: 120 / 80 / 56 pathway→grid, 48 / 48 / 32 intro→grid.
- **The page ends after Related Colleges & Schools.** The source page repeats the majors grid below that section; it is a duplicate render, not a section, and is deliberately not reproduced. Assert `document.querySelectorAll('.interest-majors-grid').length === 1`.
- **College cards are curated per interest, not derived.** E&T has programs in 9 colleges but shows the source page's 3 (ENGR, CMNS, BMGT). The generator raises on an unknown slug rather than dropping a card. Card-standard does **not** clamp `slot="text"` — the 277–318 char college descriptions render in full, verified identical light vs. shadow.

## `pages/calendar/index.html` — events calendar

New page recreating <https://admissions.umd.edu/calendar> in the DS, both of its layouts. Regenerate via `python3 scripts/build-calendar.py`; the generated HTML is overwritten wholesale — edit `briefs/calendar-data.json`, `shared/`, or the generator's `BODY` literal, not the page. Content notes and the harvest method are in `briefs/calendar.md`.

Composition: a **control bar** (month cursor + List/Calendar toggle), the page-builder **Filter Band** across the top, and then either a **list** of `umd-element-event[data-display="list"]` beside a mini-calendar rail, or a **full-bleed month grid**.

### Why the filters are on top and the rail is not

The first build put the facets in a left rail (the `.pf-*` accordion from the programs page). That works for a list, but a seven-column month grid needs the full content width — a 360px rail leaves ~93px columns at 1280px, which is tablet-grade at desktop. The live site reaches the same conclusion: at desktop its grid layout puts three selects in a row under the control bar, and the "Filters" overlay button is only its narrow-screen fallback. Moving the band up also widened the list rows, which was a free win.

The rail still exists — it just holds the **mini month calendar** and nothing else, sits on the **right** (where calendar.umd.edu puts this same month grid), and appears **only in list view**.

The right placement is `order:2` / `order:1` inside the flex row, not DOM position. Moving `.cal-rail` after `.cal-results` in the markup would also put it on the right, but then the single-column stack below 1020px would bury the date picker under 51 event cards. The trade is that keyboard focus reaches the rail before the results beside it — acceptable here: the rail is a handful of enabled day buttons and it is a *control for* the list, not a peer of it. In grid view `#cal-layout` is hidden entirely and the grid renders full bleed: a second month picker beside the month grid would duplicate the control *and* take back the width the relayout was for.

> **`hidden` loses to any author `display` rule.** The view toggle switches by setting the `hidden` *attribute*, whose `display:none` comes from the **UA stylesheet** — so any author rule that sets `display` on the same element beats it. `.cal-layout` declares `display:block` (and `flex` at ≥1020px), and the rail therefore stayed on screen in grid view while `el.hidden` reported `true`. The guard is one rule at specificity 0,2,0, which clears the media query's 0,1,0 without `!important`:
>
> ```css
> .cal-layout[hidden], #cal-grid[hidden] { display: none; }
> .pf-pills[hidden] { display: none; }
> ```
>
> `.pf-pills` is the same bug in a quieter form — `display:flex` kept an empty pill row alive at zero height, leaking its `margin-bottom:16px` into the gap between the band and the control bar. It only became visible once the bar moved below the band, and it was found by measuring the gap, not by looking at it.
>
> **Verify with `getComputedStyle(el).display`, never `el.hidden`** — the property is what you just set, not what the browser painted. This is the same class of mistake as checking that an injection *ran* rather than that it *matched* (see the pathway note under interest pages).

### Hero

`umd-element-hero-minimal data-theme="dark"`, headline only — 288px tall, black panel, 80px white `h1`. The live calendar page has a breadcrumb and an `h1` and nothing else, so there is no supporting paragraph and no CTA. An earlier revision used `umd-element-hero` `data-layout-height="small"` with a photo, a line of body copy and a "Plan Your Visit" button; the copy and the button were **invented for this page**, not sourced, which is exactly the kind of filler an interior utility page does not need. `umd-element-hero-minimal` needs no `critical.css` entry — upstream `web-components.min.css` already ships its `:not(:defined)` placeholder sizing and `container-type`.

### Control bar

**Order on the page is: filter band → active pills → control bar → count → results.** The band answers *which* events; the bar answers *when*, and *shown how*. Putting the bar first (the first build's order, and the live site's) stranded a 32px month heading above the filters that changed it, so it read as a page title rather than as a label for the results. Below the band it labels the thing directly under it. Spacing measures 32px band→bar (32 → pills → 16 → bar when a filter is active), 24px bar→count, 24px count→results.

- Month label is **`umd-campaign-small`** — Barlow Condensed italic 700, 44px desktop / 32px mobile — matching the hero wordmark. **There is no `-uppercase` sibling for the campaign faces** the way `umd-sans-*` has one, so `text-transform` is stated in page CSS. The arrows **flank** it rather than trailing it, so the label reads as the thing being stepped through; `text-align:center` plus `min-width:11ch` on the `<h2>` keeps them from jittering as the month name changes length — `ch`, not `em`, because the condensed face's em is far narrower than its average glyph.
- Arrows are `var(--umd-space-lg)` (32px) squares in `--umd-color-gray-light`, holding a black (`--umd-color-black`) UMD chevron that goes `--umd-color-red` on hover and focus. The prev button flips its glyph with `transform: scaleX(-1)`. Glyph is 12px (`--umd-space-xs`) at desktop, 14px below — the button doubles as a touch target there.
  - **The chip colour does not change on hover; the glyph does.** They were red buttons first, and the point of moving off that was to take the red block out of the bar — turning the chip red on hover would put it straight back. A gray-to-red glyph is also how the DS's own interactions read (`umd-animation-line-slide-graydark-red`).
  - The hover rule targets **both** `svg` and `svg path`. The current DS chevron sets no `fill` on its `<path>`, so `fill` on the `<svg>` inherits down — but a glyph that does set its own would silently ignore the hover.
- **No rule under the bar.** An earlier revision had a `border-bottom` there; it stacked with the filter band's own top edge and read as a double divider.

### No search field

The band's text-search half is deliberately unused. The live calendar has no search, and four `<select>` facets over 64 events do not need one. `critical.css` §23's `.umd-filter-search-row` / `.umd-filter-search-btn` rules stay in the inlined block (it is copied verbatim from TEMPLATE) but nothing on the page matches them.

### Filter Band — what is reusable and what is not

The **layout** is the page-builder's Filter Band (`LAYOUT-PATTERNS.md`), and almost all of it is already vendored:

| Piece | Source |
|---|---|
| Gray panel + red left rule | `.umd-layout-background-highlight-light` (layout.min.css) — `#F1F1F1`, `border-left:2px solid #E21833`, padding 24 → 32 → 56px |
| Heading + Clear on one line | `.umd-layout-grid-inline-stretch` (first child gets `flex:1 0 auto`, so the rule fills) |
| Heading rule | `.umd-text-line-trailing-light` — **needs an explicit `background-color`** on the heading; its `<span>` inherits that colour to mask the rule, and on the `#F1F1F1` panel the default white leaves a white notch |
| Clear button underline | `.umd-animation-line-slide-graydark-red` (animation.min.css) |
| Select box + chevron | `.umd-field-select-wrapper` (element.min.css) — supplies the white box and the SVG chevron; the `<select>` itself only needs the box model |
| Control row | `.umd-layout-grid-gap-four` — 1 → 2 → 4 columns, 32px gap; exactly four facets fit |
| Results count | `.umd-filter-results-count` (critical.css §23). It ships `margin:24px 0 0`; with the band already supplying the space above, override to `0 0 24px` or the count collides with the first month heading |

(If a search is ever wanted back: the band's search row is `.umd-filter-search-row` + `.umd-filter-search-btn`, and **the input must be `type="text"`** — the rule is `.umd-filter-search-row input[type="text"]`, so a `type="search"` input silently gets none of it.)

The **behavior** is not reusable. `page-builder/scripts/filter-band.js` handles one `data-filter-select` plus a `textContent` search; this page has four facets, a date cursor and two views over the same result set, so it keeps its own filter JS (as LAYOUT-PATTERNS says the facet variant must). `.umd-filter-list` is likewise unused — the list is grouped into month sections whose `umd-element-event` children already carry upstream dividers.

One thing the band buys back: because it is a plain `<form>` of native controls, `type="reset"` genuinely resets it. The old rail needed a hand-rolled `clearAll()` because `umd-element-call-to-action` clones its child button into shadow DOM and a native reset never reaches the light-DOM form.

### One date cursor, two views, one month per page

`state.from` is the only date, and **both views window to its month**. The list used to run from the cursor to the end of the data, which meant the control bar could read AUGUST 2026 above a list that opened in September. One month per page makes the bar an honest label, makes the pager beneath it meaningful, and let the "N events from …" line go away entirely.

Month nav moves the cursor to the 1st of the next/previous month; "Today" returns it to today's date. Resisting a second "view month" variable is the point — two cursors drift, and the label above the two views would stop meaning one thing.

`state.picked` rides alongside it: true when the user chose that *day* (mini-calendar click, or Today), false when they merely landed on it by moving months. **Only a picked day gets the red ring.** Month navigation snaps `from` to the 1st, and ringing an empty 1st reads as a selection nobody made.

**The list carries no group heading at all.** One month per page, and the control bar directly above already reads that month — a `AUGUST 2026` ribbon under an `AUGUST 2026` heading is duplication. Two variants were tried and removed: a per-day ribbon set ("Today" / "Thursday, Aug 20", matching `umd-feed-events-grouped`), and a single per-month ribbon. Neither survived pagination.

The cards are therefore **direct children of `#cal-list` with no wrapper section**, which is what upstream `web-components.min.css` needs for its `umd-element-event[data-display="list"] + umd-element-event[data-display="list"]` divider (24px + 1px `#E6E6E6`). Wrapping them re-breaks it silently.

### Month pager — `umd-shell-pagination` is NOT in the styles package

The pattern is real (see <https://today.umd.edu/tags/athletics>) but **its CSS ships nowhere this project loads**. All eight `web-styles-library` bundles were searched for `pagin|pager|page-num|prev|next|load-more`: zero hits, and no `umd-shell-*` rule of any kind. That family belongs to the CMS shell layer; `critical.css` carries only its utility-nav and person-grid members. The design system's own pagination is a different thing entirely — `packages/feeds/source/states/pagination.ts` builds a centred "Load more" `<button>` styled `umd-action-outline`.

So the pager here restates `umd-shell-pagination` from the **live computed styles**, the same situation as `critical.css` §23's `umd-filter-*`. Measured and matched: 8px gaps, centred wrapper, `2px solid #000` current, `1px solid #E6E6E6` page boxes, 40×40 black steppers going `#E6E6E6` when disabled, 16px white chevron rotated 180° for prev.

**Pages are numbered, and page N is the Nth month the data covers** — so stepping a page steps a month. The boxes stay the source's fixed 40×40 (they hold digits) and the window is first · … · prev · current · next · … · last, the same shape as the source's `1 2 3 4 5 … 18`, clamped to `YM_MIN`/`YM_MAX` — the same clamp that stops the control-bar arrows walking off into empty months. A month-labelled variant ("Apr 2026" in each box, boxes grown with `min-width` + padding) was tried and reverted: it was far too heavy for what is a page stepper.

The month is not lost for non-visual users — it rides in the `aria-label` ("View page 1 of 27, April 2026") and in the nav's `sr-only` line ("Page 5 of 27, August 2026").

Page actions are `<button data-goto="YYYY-MM">`, not `<a href>` — there is no per-month URL on a client-side page.

`matchFacets()` is kept separate from the date window for the same reason: both views filter the same faceted set and then apply their own window, so switching views never re-derives the facets.

A day click in the mini calendar sets the same cursor at day granularity. The mini calendar carries **no month nav of its own** — the control bar owns the month, and two sets of arrows for one value invites them to drift.

### Mini month calendar (`.cal-mini`)

Recreated from <https://calendar.umd.edu>'s right rail by measuring the live computed styles, not by guessing: `#FAFAFA` panel at `24px 14px`, two `repeat(7, 1fr)` grids with a `1px` gutter, square cells from `padding-bottom: 100%` on a zero-height box, `12px`/`800` numerals absolutely centred, `#F1F1F1` for out-of-month cells, `#454545` text for past days.

- **The source's only "this day has events" cue is `text-decoration: underline` on the numeral.** No dot, no badge — diffing every computed property between a `data-hasevents="true"` and `="false"` cell turns up exactly that one difference. Reproduced as-is. Assert on the computed `textDecorationLine` of `.num`, not on the attribute.
- **The selected-day ring is an inset `box-shadow`, not the source's `border`.** A real border on a `padding-bottom: 100%` box is added outside the zero content height and knocks the cell out of square. `box-shadow: inset 0 0 0 2px` paints in the same place with no layout cost.
- **Cells are `<button disabled>`, not `<a>`.** There is no per-day URL here, so days with no matching events are genuinely inert and should be out of the tab order.
- **`data-hasevents` reflects the facet filters but NOT the from-date.** Otherwise the grid goes blank the moment the list scrolls past a month, which is precisely when it is useful. This is why `renderMini()` is handed `faceted`, not `shown`.
- **It changes role when the layout wraps.** Below 1020px the rail stops being a narrow column beside the list and becomes a band across the page, so it centres (`margin: var(--umd-space-xl) auto`), grows to `600px`, and takes 40px of air top and bottom. Cells go from 48px to 81px.
- **The numeral size is a CONTAINER query, not a media query** — `.cal-rail` carries `container-type: inline-size` and the step-up is `@container (min-width: 480px)`, 12px (`--umd-font-size-min`) to 18px (`--umd-font-size-lg`). A media query was tried first and was wrong: at a **760px viewport the rail is still at its full 600px** (the horizontal lock leaves the room), so `@media (min-width:768px) and (max-width:1019px)` switched the type back down while the cells were still 81px. The rail's width is the only thing that matters here, so ask about that directly. Verified by driving the rail through 340 / 479 / 480 / 600 / 327px and reading the computed size at each: 12 / 12 / 18 / 18 / 12.
- **The step-up rule must come AFTER the base `.cal-mini-days p, .cal-day` rule.** The selectors are identical, so specificity ties and source order decides — placed before it, the query loses silently. It did, on the first attempt, and only a computed-style check caught it.

### Tokens: this page declares no colour or spacing values of its own

Everything comes from `tokens.min.css` (TEMPLATE links it second, so the custom properties are live before any page rule runs).

- **Spacing:** `--umd-space-sm` 16, `-md` 24, `-lg` 32, `-xl` 40, `-3xl` 56. The control-bar arrows are `var(--umd-space-lg)` square with a `var(--umd-space-xs)` glyph at desktop.
- **Type scale where it steps:** `--umd-font-size-min` 12 → `--umd-font-size-lg` 18 for the mini-calendar numerals.
- **Colour:** all ten in use are `--umd-color-*` — `red`, `gold`, `white`, `black`, `gray-darker`, `gray-dark`, `gray-medium-a-a`, `gray-light`, `gray-lighter`, `gray-lightest`. **Zero hex literals remain in the page `<style>` block.** (The inlined `critical.css` above it is TEMPLATE's, copied verbatim, and is not ours to touch.)

Two things this sweep settled:

- **A local `:root { --umd-red: #e21833 }` alias is gone.** It was a hand-rolled duplicate of `--umd-color-red` behind a different name, which is exactly how a page drifts off the palette. Don't reintroduce a page-level colour variable — use the DS token directly.
- **`#767676` became `--umd-color-gray-medium-a-a` (`#757575`).** A deliberate 1/255 shift on the muted greys (per-event counts, past dates in the grid, grid cell times) to land on the DS's AA-compliant grey rather than a near-miss of it.

**Custom properties cross the shadow boundary,** so the Upcoming-cards border injection uses `var(--umd-color-gray-light)` inside the shadow root and resolves against the host. Verified: the injected `.layout-block-stacked-container` computes `1px solid rgb(230,230,230)`.

### Upcoming Events — and the bordered-event-card gap

The page-bottom block reproduces the live page's "Upcoming Events": a three-up grid of **bordered, image-less event cards**. It is **static**, rendered at build time from the next six events on or after today — it deliberately ignores the filters, the month cursor and the view toggle, so it needs no JS and ships as real HTML. (The live version is hand-curated and had gone stale — it was still showing March 2025 Terrapin Tours against an August 2026 date. Deriving it keeps it honest.)

**There is no bordered event card in the design system.** Worth stating plainly, because the capability *looks* like it should be there:

| Layer | Border support |
|---|---|
| `card.block()` (elements) | **yes** — takes `hasBorder` |
| `umd-element-card` / `umd-element-article` | **yes** — `card/_model.ts` reads `Attributes.isVisual.bordered` and passes `hasBorder` |
| `umd-element-event` | **no** — `card/event.ts` has its own `createComponent` that never reads it |

`data-visual-bordered="true"` on `umd-element-event` is therefore **inert**: it does not throw, it does not warn, it simply does nothing — the worst failure mode. Confirmed by A/B against the same shadow node, not by reading source alone:

| probe | `.layout-block-stacked-container` border | `.layout-block-stacked-text` padding |
|---|---|---|
| `umd-element-card` `data-visual-bordered="true"` | `1px solid rgb(230,230,230)` | `24px` |
| `umd-element-card` (no attribute) | `0px none` | `0px` |
| `umd-element-event` `data-visual-bordered="true"` | **`0px none`** | **`0px`** |
| `umd-element-event` `data-visual-border="true"` (legacy) | **`0px none`** | **`0px`** |

Console is clean in every case (only the pre-existing `process is not defined` pair from the CDN bundle).

**Run this probe in a clean room, not on a project page.** Two ways to get a false result:

1. `cdn.js` registers lazily, so an element absent from the DOM is simply `undefined` — a probe on the wrong page returns "no shadow root" and reads as a failure that isn't one.
2. A page that already styles or shadow-injects cards can confound either arm.

The result above was taken on a throwaway page carrying **nothing but the nine CDN stylesheets and `cdn.js`** — no page CSS, no injections, both elements registered. (Its only `<style>` tag is a keyframes block `cdn.js` inserts itself.) That page was deleted after the run; recreate it rather than testing against a project page.

The registry entry lists only `data-display`, `data-theme`, `data-visual-transparent`, `data-visual-time`. **Upstream candidate:** wire `hasBorder` through `card/event.ts` the way `_model.ts` already does.

The border is therefore a page-level shadow injection reproducing exactly what `hasBorder` renders on card-standard — `1px solid #E6E6E6` on `.layout-block-stacked-container`, `24px` padding on `.layout-block-stacked-text`. It is driven by page content, not chrome, so it lives in the page (see "Chrome vs. page-level shadow injections").

**Where the date sign actually appears** — measured, because the rule is not what the slot list suggests:

| `data-display` | `dateSign` passed by `card/event.ts`? | needs an image? | result |
|---|---|---|---|
| *(default block)* | **no** | — | **never a date sign, even with an image** |
| `feature` | yes | **yes** — the sign rides on the image (`assets.image.background({dateSign})`) | sign only when an image is slotted |
| `promo` | yes | yes (the variant needs one regardless) | sign |
| `list` | yes | **no** — `createCompositeCardList` pushes `makeDateColumn` in its own `if (dateSign)` branch, independent of `if (image)` | **sign with or without an image** |

So dropping `slot="image"` from these cards costs nothing: the default block never had a sign to lose. The date rides in the event meta row instead, which is what the live page's cards do.

One related gotcha for the **list** cards used in the main view: `makeDateColumn` carries `createMediaQuery('max-width', breakpointValues.large.min, { display: 'none' })`, so the list date sign is **hidden below the large breakpoint**. Verified at 375px — the wrapper computes `display: none` while the meta row still reads "Thu. Aug 20", so it degrades cleanly. Don't "fix" it.

Card heights stay uniform per row (measured 394/394/394 and 340/340/340 at 1280px).

Grid is `umd-layout-grid-gap-three` (32px gap), stepped to 2-up between 768 and 1019px and 1-up below, since the DS class is 3-up at every width.

The heading is the **tailwing** treatment — `umd-text-line-trailing-light` (aka `umd-tailwing-right-headline[theme="light"]`), the same 14px uppercase label-with-trailing-rule the filter band uses for "FILTER EVENTS". It **requires a `<span>` child** and an explicit `background-color` on the `<h2>`: the span masks the rule with `background-color: inherit`, so a transparent heading lets the rule run straight through the text. `umd-element-section-intro-wide` was used first and replaced — its 40px headline outweighed a closing block.

### Month grid

- **Grid lines are the 1px `gap` showing through a gray-light backdrop**, not per-cell borders — nothing to collapse, and no double line at the seams. Cells paint white on top; leading/trailing blanks paint gray-lightest (the live grid's `.empty-date`) and carry no number.
- **The weekday header row is black with white labels**, and each `.cal-wd` carries `box-shadow: 0 0 0 1px var(--umd-color-black)`. That bleed is load-bearing: the same 1px `gap` that draws the grid lines would otherwise cut the header into seven black chips separated by light seams. The shadow fills each cell's own gutters so the row reads as one solid band. Verified the gaps are still 1px structurally while the row paints continuous.
- **Cells list their events.** The live grid's cells contain only a date number — a day with events is pixel-identical to an empty one, and `data-hasevents`/`data-hasmodal` drive nothing visible (verified by diffing every computed property between the two states; the only difference is 38px of bottom padding). Not reproduced. Each cell prints up to `CELL_LIMIT` (3) linked titles with their times, then a **"+N more"** toggle using the same `.is-collapsed` / `.cal-*-extra` idiom as the programs rail's "Show all".
- **Below 768px the toggle is hidden and the page is list-only.** A seven-column grid with content in the cells cannot be done honestly at 375px. The live site agrees by omission — its `umd-calendar-grid` measures 0×0 at that width. Between 768 and 1019px cells drop to 130px with 12px titles (93px columns at 768).
- Row heights stay uniform within a week and grow only when a day actually holds three items — verify by grouping cells on `getBoundingClientRect().top` and asserting one distinct height per row.

### `umd-element-event` — two attribute traps, both silent

- **A missing `end-date-iso` prints `undefined` into the event meta.** `createDateRow` derives `isMultiDay` from `startDay != endDay || startMonth != endMonth` and `createTimeText` from `startTime != endTime` (`packages/elements/source/atomic/events/meta.ts`). With the slot absent both end values are `undefined`, both comparisons are true, and a single-point event renders **`Thu. Aug 20 - undefined. undefined undefined`** and **`3:00pm - undefined`**. The registry documents `end-date-iso` as optional; in practice it is required for anything that is not a range. Fix: repeat the start stamp in `end-date-iso`. Both comparisons then go false and the meta collapses to the single date and time. **Verify with `card.shadowRoot.textContent.includes('undefined')`** — nothing throws and the date sign is correct either way, so the page looks fine until you read a card.
- **`data-visual-time` is opt-OUT, not opt-in.** `Attributes.isVisual.showTime` passes `defaultValue: true` (`packages/model/source/attributes/checks.ts`), so omitting the attribute *shows* the time — an all-day deadline renders **`12:00am`**. The registry describes it as "Show time in the event meta display", which reads as opt-in. Emit it explicitly on every card: `"true"` for timed events, `"false"` for all-day ones.
- **The `<time>` slot is read from `textContent`, not `datetime`.** `parseDateFromElement` calls `Date.parse(element.textContent)` and never touches the attribute. Put a parseable stamp in the element's text (this page writes the ISO string in both places); the light-DOM `<time>` measures 0×0 once the component upgrades, so the raw stamp never shows.
- **Slot names are `start-date-iso` / `end-date-iso`.** The component's own JSDoc says `date-start-iso`; `Slots.name.DATE_START_ISO` resolves to `start-date-iso`. Wrong names fail silently — `extractEventData` returns null and the component renders an empty `<div>`.
- **The divider between consecutive list events is upstream.** `web-components.min.css` ships `umd-element-event[data-display="list"] + umd-element-event[data-display="list"] { margin-top:24px; padding-top:24px; border-top:1px solid #E6E6E6 }`. Write no page CSS for it — including across a re-render, since the sibling selector applies to injected markup too.

### No scrollbars anywhere

Carried over from the programs rail (`d152be2`) and preserved through the relayout: nothing on this page scrolls except the page. Assert it directly — no element inside the explorer `<section>` should have `overflow-y: auto|scroll` *and* `scrollHeight > clientHeight`.

## Colour: every page is on DS tokens

`tokens.min.css` is TEMPLATE's second `<link>`, so `--umd-color-*` is live before any page rule runs. **No page in this repo declares a colour of its own.** Verified across all ten: zero bare hex in page CSS, inline `style=""` attributes, or shadow-injection strings.

**One form only: `var(--umd-color-x)`.** No hex fallbacks. `build-colleges-schools.py` used to write `var(--umd-color-x, #HEX)` to guard against `tokens.min.css` failing to load, and all 29 were removed: if that stylesheet is unreachable then so are the other eight bundles and `cdn.js`, and the page has no components and no layout — a correct border colour is not the problem at that point. Four of those fallbacks had also silently drifted from their token values (`gray-medium, #C1C1C1`; `gray-lightest, #F1F1F1` ×2; `gray-light, #DCDCDC`), which is the maintenance cost the form was buying.

### Hand-rolled CSS removed because the DS already ships it

Order of preference on this project: **DS component (registry) → styles-package class/token → hand-rolled CSS, last resort.** An audit comparing every class we define against the 264 the styles package ships turned up three duplicates:

| removed from | rule | shipped by |
|---|---|---|
| `build-programs.py`, `build-calendar.py` | `.sr-only` | `accessibility.min.css` |
| `pages/admissions.html` | `umd-element-card-overlay.size-large { min-height:320px; 560px @768px }` | `web-components.min.css` — and `critical.css` §16 had **already retired the same rule upstream**, so the page copy was stale twice over |
| `pages/admissions.html` | `.umd-text-rich-advanced .text-black { color:#000 }` | `critical.css` §6 ships this exact selector |

The `.text-black` one is worth noting as an audit gap: a comparison of "classes we define" against "classes the styles package ships" will **not** catch it, because `.text-black` is a `critical.css` utility, not a styles-package one. Duplicates of `critical.css` rules need their own check.

Verified after removal: `.sr-only` still computes `position:absolute; width:1px; height:1px; overflow:hidden` with nothing leaking (60 instances on the calendar, 1 on programs), and the admissions overlay cards still compute `min-height: 560px` at desktop.

The other class-name collisions the audit found are **legitimate and should stay** — they are scoped overrides, not redefinitions: `.pf-body .umd-field-checkbox-wrapper`, `.pf-pill-cluster.umd-text-cluster-pill`, `#cal-filters .umd-text-line-trailing-light`, `.wta-section > .umd-layout-space-horizontal-larger`, `#search-form .umd-filter-search-row`. Each adjusts a DS class in one context; none restates it.

## Search field: underlined, not boxed (`pages/search/`)

`critical.css` §23 styles `.umd-filter-search-row` as a **boxed** field — white ground, `1px #c0c0c0` border with the right side removed, butted against a `44x44` solid-red submit. That is right in a filter band, where the search sits beside select boxes and should match them.

On `pages/search/` it is the only control on the page and the whole reason the page exists, so `#search-form` restyles it as a single **underlined** field: transparent ground, one `1px #242424` rule under the entire row, and the design system's own magnifier (`web-icons-library/dist/search.js`, verbatim) as a plain `#242424` glyph rather than a red button. The `44x44` hit area is kept; only its red ground goes.

Focus moves to the row: `:focus-within` turns the rule Maryland red and adds `box-shadow: 0 1px 0` to reach 2px **without reflow** (a border-width change would shift the row a pixel — measured, the row stays 45px either way). The input's own `outline` is cleared, because §23's 2px red box draws around a field that no longer has edges.

**Scoped to `#search-form` deliberately.** Promote to a `critical.css` variant only when a second page wants it. Today nothing else is affected: the calendar band has no search row, and the representatives directory uses its own `.reps-search-row` and keeps the boxed treatment.

### `.umd-text-rich-advanced` vs. the utilities on a heading

Column headings on `pages/admissions.html` are `<p class="text-black umd-sans-extralarge-bold">` **inside** a `.umd-text-rich-advanced` block. Two utilities are in play, from two different places:

| utility | ships in | what beats it |
|---|---|---|
| `.text-black` | **`critical.css` §6** — explicitly "not in upstream tokens or typography bundles" | `.umd-text-rich-advanced *  { color:#454545 }` (§7) |
| `.umd-sans-extralarge-bold` | `typography.min.css` (styles package) | `.umd-text-rich-advanced > * { font-size:18px }` (§7) |

Both §7 rules are (0,1,0) — the same specificity as the utilities — but later in the file, so they win on order.

- **The colour half needs no page CSS.** `critical.css` §6 already ships `.umd-text-rich-advanced .text-black { color:#000 }` for exactly this collision. A duplicate of that rule sat in the page and has been removed. Verified all four `.text-black` elements still compute `rgb(0,0,0)`.
- **The size half is still needed**, and the reason is upstream, not local. `element.min.css` ships both halves of the collision itself:

  ```css
  :is(.umd-text-rich-advanced,.umd-rich-text) > * { font-size: 18px; margin-top: 24px }
  :is(.umd-text-rich-advanced,.umd-rich-text) *   { color: #454545 }
  ```

  Both are (0,1,0), and **`element.min.css` loads after `typography.min.css`**, so a bare typography utility on a direct child can never win on its own — whichever size you pick. The page's `.umd-text-rich-advanced > .umd-sans-extralarge-bold` bump is the correct fix, not a workaround. Note the pin is by *position*, not tag: an `<h2>` inside rich text is 18px too unless something outranks it.

**Heading sizes come from the typography package**, and all three sit there already:

| want | class | behaviour |
|---|---|---|
| 18px | `umd-sans-large` | flat 18px/700 |
| 22px | `umd-sans-larger` / `-bold` | ramps 18 → 22px |
| 32px | `umd-sans-extralarge` / `-bold` | ramps 22 → 32px |

These headings use `extralarge-bold`, so the page rules restore that ramp above 650px; below 650px they agree with the 18px pin.

**The markup was wrong, and that was the real bug.** "Tuition & Aid" and "Important Dates" were `<p class="text-black umd-sans-extralarge-bold">` — styled as section titles but not marked up as them, while every other section title on the page is an `<h2>`. Both are now `<h2>`; the CSS is class-based so nothing moved (measured 32px/700/`rgb(0,0,0)` before and after), and the document outline no longer skips two sections.

An earlier revision of this file described the 18px base as a stale copy of the utility's old value. That was wrong: `.umd-sans-extralarge-bold`'s 22px base is never in play, because the `> *` pin is 18px regardless.

**Stale comment in `critical.css` §7** (submodule, not fixed here): it says "upstream only colors list content `#454545`; we force it on all descendants." Upstream has since caught up — `element.min.css` ships the `*` colour rule — so §7's colour delta is now a duplicate.

### Four colours had no exact token

| was | now | why |
|---|---|---|
| `#767676` | `--umd-color-gray-medium-a-a` (`#757575`) | facet counts / muted meta — 1/255 shift onto the DS's AA-compliant grey |
| `#444444` | `--umd-color-gray-dark` (`#454545`) | tuition rule — 1/255 |
| `#DCDCDC` | `--umd-color-gray-light` (`#E6E6E6`) | a lone `.cs-major` divider; every other divider in that file already used gray-light |
| `#D3D3D3` | `--umd-color-gray-medium` (`#7F7F7F`) | `.az-off`, the dimmed A–Z letters. `#D3D3D3` is 1.3:1 on white — failing regardless. `#7F7F7F` is 4.6:1. The active/inactive distinction survives because it is carried by **hue** (active letters are Maryland red), not lightness. |

### Two traps found doing this

- **`build-colleges-schools.py` appends its page CSS to the *first* `<style>` block**, alongside the verbatim `critical.css`. Every other generator emits a separate block. Any audit that treats "block 0 = TEMPLATE, don't touch" silently skips 7KB of page CSS on that one page — this sweep missed it twice before catching it.
- **Don't bulk-replace hex inside a file that already uses the fallback form.** Doing so turns `var(--token, #hex)` into `var(--token, var(--token))` — self-referential and pointless. Mask the fallbacks (and CSS comments, and `&#NNNN;` entities) before substituting.

To re-verify after any colour change, resolve tokens back to values and diff the multiset per page against `git show HEAD:<page>`; every difference should be one of the four above.

## Shared chrome (`shared/` + `scripts/build-chrome.py`)

The site chrome — header stack, footer, its CSS companions, and its shadow injection — was copy-pasted into all seven pages, with the CSS living in a different place from the markup. That split caused two silent regressions while building `pages/academics/colleges-schools.html` (unstyled utility nav; scroll-top falling back to the DS `right:40px; bottom:10vh`), so it is now extracted.

- **Source of truth is `shared/`**: `header.html`, `footer.html`, `chrome.css`, `chrome-scripts.html`. `scripts/_chrome.py` wraps each in `SHARED:<key>:START` / `:END` markers; `scripts/build-chrome.py` splices them into every page in `pages/`. The two page generators emit the identical blocks via the same module, so running any of the three converges — no ordering dependency. `--check` exits non-zero if a page is stale.
- **Migration is content-located, not marker-dependent.** On a page with no markers the script finds the existing chrome by content and wraps it, so a new page needs no setup. A zero-width insertion slot (chrome CSS before `</head>`, chrome scripts before `</body>`) must emit its own trailing newline — without it the block runs straight into the following tag (`<!-- SHARED:chrome-css:END --></head>`).
- **Only chrome-driven injections are shared.** `shared/chrome-scripts.html` holds just the nav-header logo width. The pathway aspect-ratio, banner-promo stacked-actions, call-to-action and card-overlay injections are driven by page **content** and stay with the page — verified by usage: `student-life.html` has zero `umd-element-pathway` and correctly carries no pathway injection.
- **Two drifts were normalised**, both confirmed with the user rather than assumed: the footer logo now points at `admissions.html` on all seven pages (it was `https://admissions.umd.edu/` on six and `/` on one, so clicking it left the prototype for production, while the header logo was already relative), and `admissions.html` gained the `line-height: 1.25` on utility links that the other six already had.
- **Scroll-to-top stays opt-in** (only the two long directory pages use the element), but its pin lives in `shared/chrome.css` so it is styled consistently wherever it appears.

### Known remaining drift — the inlined `critical.css` block

`build-chrome.py` deliberately does **not** touch the inlined critical block. Against the current `page-builder/TEMPLATE.html`: `programs.html` is in sync; `colleges-schools.html` differs only by its own appended page CSS; the four other hand-authored pages differ only by the §11 `:has()` gate; and **`admissions.html` carries two intentional page-specific edits inside that block** — an extra `.umd-layout-background-full-dark-no-bottom` utility, and a `:not(.quote-with-chevron)` exclusion on the dark→light transition selector.

Those two are why a blanket refresh from TEMPLATE would be wrong — it would silently clobber them. Rendering is unaffected by the §11 lag either way, because `shared/chrome.css` sets the flat-link `gap: 24px` explicitly on every page. Refreshing critical blocks is a separate task that has to preserve the `admissions.html` edits.

### Pre-existing, not introduced

`pages/admissions.html` has ~64px of horizontal overflow at 1440px. Measured on the pre-migration file as well (64px before, 63px after), so it is unrelated to the chrome extraction.

**Do not "fix" it — it is the hero-grid animation's start state.** `umd-element-hero-grid` runs a scroll-driven animation (`animation-timeline: view()` on a sticky `.hero-grid-layout` inside a `300vh` container):

```css
@keyframes grid-columns {
  0%   { grid-template-columns: 20% 60% 20%; }
  100% { grid-template-columns: 0px 100% 0px; gap: 0px; }
}
```

The side columns are **designed** to sit past the viewport edge and slide away while the centre image expands to full width. The 64px is `2 × column-gap`, left over from percentage tracks summing to 100%; the component accepts it, and `critical.css` §21's `body { overflow-x: clip }` already suppresses the scrollbar, so nothing is user-visible.

**A `grid-template-columns` override with `!important` freezes the animation.** Important author declarations beat animations in the cascade, so the columns never move and the hero silently stops working — it still *looks* correct at rest, which is why this was once attempted, "verified" against static measurements, and only caught when someone scrolled. If the overflow ever genuinely needs containing, use `overflow-x: clip` on the host (leaves `grid-template-columns` alone) and confirm the sweep still runs first — note §21's warning that `overflow-x: hidden`, unlike `clip`, creates a scroll container and breaks scroll-driven animations.

**Verifying any scroll-driven animation here:** `animation-timeline` advances at frame time, so calling `getComputedStyle` immediately after `window.scrollTo` in the same task returns stale values and *everything* reads as frozen. Scroll in one step, read in a separate one. Check `getAnimations()[0].timeline.currentTime` and `matchMedia('(prefers-reduced-motion: reduce)')` before concluding an animation is broken.

---

## `pages/admissions.html` was renamed to `pages/index.html` (2026-08-31)

The site home now sits at `pages/index.html`, so GitHub Pages serves it at
`/admissions-design/pages/` and the project matches the convention in
`page-builder/CLAUDE.md` (a section's landing page is its `index.html`).

**Entries above still name `pages/admissions.html`.** They are a record of what
was true when each was written and have deliberately not been rewritten — the
same reason version numbers in `critical.css` comments are left as tombstones.
Read them as referring to this file.

The header and footer logos now link to `{{ROOT}}pages/` rather than the file.
The directory form is what `chrome.py`'s `_self_hrefs` matches against both
spellings, so the home page still gets `data-selected` in the drawer.

---

## `umd-element-person-hero` — two things the registry does not tell you (2026-08-31)

Both found building `pages/admission-representatives/<slug>.html` (see
`briefs/admission-representatives.md`). They matter to any future page that
uses this component, which is the DS's only "profile page" hero.

### 1. `slot="association"` is silently dropped

`registry-person.json` lists `association` ("Department or unit") as a slot on
all three person components. `umd-element-person-hero` **does not render it**.

The component does not project the profile content through `<slot>` at all — it
reads the light DOM and rebuilds a text lockup inside its shadow root, and that
lockup reads only `name` and `job-title`:

```html
<div class="person-hero-text">
  <div class="umd-text-line-adjustent-inset">
    <h1 class="umd-campaign-large">Abigail Trice</h1>
    <p class="umd-sans-medium">Senior Coordinator of Admissions and Rural Recruitment</p>
  </div>
</div>
```

Verified against the rendered shadow tree in `cdn.js@1.18.12`. `image`, `email`
and `actions` *are* picked up (into `.umd-person-hero-image-container`);
`association` is not. Do not emit it — it is dead markup, and its absence is
invisible until someone looks for the unit name and cannot find it.

The same clone-don't-slot behaviour is why **page CSS cannot style the name,
job title, email or actions** on this component. Anything cosmetic there needs
a shadow injection, not a stylesheet rule.

### 2. `slot="breadcrumb"` takes a `umd-element-breadcrumb`, and the registry's example markup for it is wrong

Two mistakes are easy to make here, and the component only warns about the first.

**The slot validates.** Putting a hand-rolled `<nav>` (or anything else) in it
logs, and renders unstyled light-DOM links in browser-default blue:

```
[UMD-DS:umd-element-person-hero] Slot validation failed
  Slot "breadcrumb" contains invalid elements. Allowed: umd-element-breadcrumb
```

`registry-person.json`'s "do not also render a standalone
`umd-element-breadcrumb`" means **put it in this slot** rather than separately
on the page — not that the slot takes raw markup.

**Then use RULES.md's paths markup, not the registry's.**
`registry-navigation.json` documents `slot="paths"` as an ordered list:

```html
<!-- WRONG — registry-navigation.json's example -->
<ol slot="paths"><li><a href="/">Home</a></li><li aria-current="page">This page</li></ol>
```

The DS draws its separators with `.breadcrumb-path + *::before`, so the paths
must be **adjacent siblings**. Wrapping each in its own `<li>` gives every
anchor a container to itself, the selector never matches, and the trail renders
as one run-on string — `HomeAdmission RepresentativesAbigail Trice`, no
separators, no spacing. `RULES.md` § "Breadcrumb" has the correct form, and
`RULES.md` outranks the registry in the source-of-truth hierarchy:

```html
<umd-element-breadcrumb slot="breadcrumb">
  <div slot="paths">
    <a href="/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
    <a href="/section"><span>Section Name</span></a>
    <p aria-label="Current Page"><span>Current Page Title</span></p>
  </div>
</umd-element-breadcrumb>
```

Each label needs its own `<span>` — that is the element the hover underline
animates (`background-size: 200% 2px` sliding gray→red).

**Getting it right means no page CSS at all.** The breadcrumb component clones
`slot="paths"` into its own shadow root and styles it there (`.breadcrumb-path`,
grey `#757575`, slanted 1px separators). An earlier revision of this page hand-
styled a light-DOM `<nav>` with a `.rep-breadcrumb` rule set; all of it was
deleted once the markup was correct.

**Querying it is confusing.** person-hero clones the breadcrumb into a second
`slot="breadcrumb-copy"` for its mobile layout, and the clone comes **first** in
document order. So `document.querySelector('umd-element-breadcrumb')` returns
the mobile one, which is `display: none` and measures 0×0 at desktop — easy to
misread as "the breadcrumb is broken". Select on the slot:

```js
Array.from(document.querySelectorAll('umd-element-breadcrumb'))
     .find(b => b.getAttribute('slot') === 'breadcrumb')
```

---

## `umd-element-person` styles a linked and an unlinked name identically (2026-08-31)

`<a slot="name">` and `<p slot="name">` both render as
`.person-name.umd-sans-larger` — black, 700 weight, no underline, no hover
state. There is no built-in affordance telling a reader which cards go
somewhere.

That is right for a directory where every card links. It is wrong for a
**partial** one, which is what `pages/admission-representatives/index.html` is
while only six of 24 reps have profile pages. The name is cloned into the
shadow root (same behaviour as person-hero above), so this needs an injection:

```js
'a.person-name{text-decoration:none}' +
'a.person-name:hover,a.person-name:focus-visible' +
'{text-decoration:underline;text-underline-offset:3px;' +
'text-decoration-thickness:2px;color:var(--umd-color-red,#e21833)}'
```

Scoped to `a.person-name`, so it is inert on cards whose name is a `<p>`. It
fixes the hover state, not the resting one — a partial directory still shows
eighteen names that look identical to the six that work. The real resolution is
to generate the rest.

---

## `umd-element-person` re-renders ADDITIVELY when it reconnects (2026-08-31)

Take an `umd-element-person` out of the DOM and put it back, and the component
appends a **second** `.person-block` to its shadow root instead of replacing the
first. The card then draws the same person twice and doubles in height —
measured 389px → 694px after a single detach/reattach, with the shadow root
holding `[STYLE, DIV.person-block, STYLE, STYLE, DIV.person-block]`.

This bites any list that re-renders by moving existing nodes:

```js
grid.replaceChildren.apply(grid, matches.slice(0, n));   // WRONG
```

`replaceChildren` re-inserts the nodes that were **already** on screen, so on
`pages/admission-representatives/search.html` one "Load More" click did this to
every visible card at once and the grid appeared to repeat its rows.

### `display: none` is NOT the alternative

The obvious fix — leave every card in the DOM and hide non-matches — breaks the
border grid. `layout.min.css` draws the top border by DOM position:

```css
:is(.umd-layout-grid-border-four):not(:has(>:last-child:nth-child(4))) > *:nth-child(1),
… > *:nth-child(2), … > *:nth-child(3), … > *:nth-child(4) { border-top: 1px solid #E6E6E6 }
```

`:nth-child` counts children, not visible ones. Filter the first four cards out
and the top border stays stranded on hidden cells while the visible first row
has none.

### The fix: never reconnect a card

Render from **captured markup**, so every card is a new element that upgrades —
and therefore renders — exactly once:

```js
// once, at init: outerHTML on an upgraded umd-element-person serialises its
// LIGHT DOM only (the shadow root is not included), so this round-trips the
// original markup, data-* attributes and all.
var ALL = Array.prototype.map.call(grid.children, el => ({html: el.outerHTML, …}));

function append(from, to) {                 // build fresh, never reuse
  var holder = document.createElement('div');
  holder.innerHTML = ALL.slice(from, to).map(r => r.html).join('');
  while (holder.firstElementChild) grid.appendChild(holder.firstElementChild);
}
```

Two consequences worth keeping:

- **Load More must only APPEND the delta**, never repaint the whole slice — the
  cards already on screen are correct and must be left alone.
- **Any shadow injection has to be re-runnable.** Cards built after load never
  saw the one-shot `customElements.whenDefined(...)` pass, so the
  `a.person-name` hover injection is exposed as `window.umdInjectPersonLinkCss()`
  with a per-element `data-person-link-css-done` guard and called after every
  append.

Elements created by `innerHTML` on a **detached** container do not upgrade until
they are connected, which is what makes this safe: they render once, on append.

---

## Tables: the hook is `.umd-text-rich-advanced`, not a table class (2026-09-09)

Found while building an interior page whose body was one large table. The
source markup wrapped it in a `.umd-text-rich-table` / `-scroll` / `-total`
class family. **None of those class names exist** — not in
`web-styles-library`, not in `critical.css`, not anywhere in the page-builder.
The table shipped with browser-default borders and nothing errored to say so.

The real hook is the rich-text wrapper. `element.min.css` styles tables
*descended from* `.umd-text-rich-advanced` (or `.umd-rich-text`):

```css
:is(.umd-text-rich-advanced, .umd-rich-text) table {
  border-collapse: collapse; display: block; overflow-x: auto;
  table-layout: fixed; max-width: 100%;
}
… table) thead th   { background: #F1F1F1; color: #000; text-align: left }
… table) tbody tr   { border-top: 1px solid #E6E6E6 }
… table) tr:nth-child(even) { background: #FAFAFA }
… table) th, … td   { padding: 24px; vertical-align: top }
```

So a **plain `<table>` inside a `.umd-text-rich-advanced` div** is fully
styled with zero page CSS; a `<table>` outside one is unstyled. Do not
hand-roll table classes — check for a rich-text ancestor first.

`thead th` keeps its black text because `:is(:is(.umd-text-rich-advanced,…)
table) thead th` out-specifies §7's `.umd-text-rich-advanced * { color: #454545 }`.
Body cells do take #454545, which is correct — they are body copy.

Three things upstream leaves open, for whenever a table lands in this project again:

- **width.** `display: block` is what gives the table its mobile scroll, but it
  also makes the table shrink-to-fit instead of filling the content column.
  `width: 100%` restores the full-width reading; `table-layout: fixed` then
  splits the data columns evenly.
- **a summary/total row.** No upstream hook, and any override has to beat
  `tr:nth-child(even)` — so the selector has to be doubled with `:nth-child(even)`.
- **keyboard access.** Upstream makes the *table itself* the scroll container,
  so a table that overflows needs `tabindex="0"` or it is unreachable by
  keyboard (WCAG 2.1.1). Put the tabindex on the `<table>` rather than on a
  wrapping `role="region"` div, so the element keeps its table role and its
  `<caption>` keeps naming it.

## `<ol>` in `.umd-text-rich-advanced` is fully styled — do not "fix" it (2026-09-10)

Worth stating because the computed styles look broken and are not. Upstream sets
`list-style-type: none !important` on `<ol>` inside the rich-text wrapper, so a
`getComputedStyle` probe reports no marker and the obvious reaction is to add
`list-style: decimal` back. Don't — the marker is drawn as a `::before`
pseudo-element instead:

```css
:is(… ol, …) > li::before {
  content: counter(item);
  border-right: 1px solid #E21833;   /* the UMD numbered-list red rule */
  padding-right: 8px;
  position: absolute; right: calc(100% - 32px);
}
```

That red rule beside the numeral is the design-system treatment, and the
`!important` means a page-level `list-style` cannot win anyway — it only breaks
the `padding-left: 40px` the pseudo-element is positioned against. A nested
`<ul>` inside an `<ol>` is handled the same way (`content: "•"`). A plain
`<ol>` in a `.umd-text-rich-advanced` div needs **no page CSS at all**. See
`pages/tuition/frederick-douglass-scholarship.html`.

## `umd-element-banner-promo` cannot stack actions — the injection was cargo (2026-09-10)

Removed from all 11 pages that carried it, plus `scripts/build-programs.py` and
`scripts/build-representatives.py`, on 2026-09-10. What it claimed to do was
not a thing the component does.

The component reads the slot with **`querySelector`** — singular — and hands
that one element straight through:

```js
JG = ({actions}) => actions
  ? new F(actions).withClassName("banner-promo-actions").withStyles({element:{
      "@container (max-width: …)": {marginTop: sm},
      "@container (min-width: …)": {maxWidth: "30%", marginLeft: md}}}).build()
  : null
```

Three consequences, none of them obvious from the markup:

1. **There is no multi-action layout.** The component stamps
   `.banner-promo-actions` onto whatever single element you slot and gives it
   `max-width: 30%; margin-left: 24px` — no display, no flex, no gap. Anything
   beyond one action is the page's own problem.
2. **`class="banner-promo-actions"` in page markup is redundant** — the
   component applies that class itself. Ours is left in place only because it
   is what `critical.css` §12 styles if the component never upgrades.
3. **`critical.css` §12 is dead for the upgraded component.** banner-promo
   *clones* `slot="text"` and `slot="actions"` into its shadow root rather than
   projecting them through a real `<slot>`, so a light-DOM class cannot reach
   the rendered copies. The originals stay in the document at 0×0. §12 is left
   alone here because `critical.css` lives in the shared page-builder submodule
   and the rule is a plausible no-JS fallback — but it is not what styles the
   promo you see.

**Measuring the light-DOM originals is a trap.** They are still queryable and
still report computed styles — default-blue links, 0×0 boxes — none of which is
what renders. Always reach through `el.shadowRoot` when checking a banner promo.

Removing the injection changed nothing visually: the actions box measures
155×44 at the same coordinates with `display: block` as it did with the
injected column flex, because there is only ever one action in it.

## `umd-element-media-inline` — `slot="text"` is what turns on wrapping (2026-09-10)

`data-layout-alignment="right"` on its own does nothing. The component picks its
mode from which slots are present:

| Slots | Mode |
|---|---|
| `image` | standard — image full width |
| `image` + `caption` | caption — image full width, credit line beneath |
| `image` + `text` | **wrapped** — image floats, copy wraps around it |

So floating an image right means moving the body copy *inside* the component as
`<div class="umd-text-rich-advanced" slot="text">`, not leaving it in a sibling
div. The caption floats with the image rather than staying under the whole
block. Unlike banner-promo, this component projects `slot="text"` through a real
`<slot>`, so the light-DOM copy stays live and page CSS does reach it.

Verified at 1280px: image and caption both flush to the content column's right
edge (371px of 775px), every line of copy stopping short of the float. At 375px
the float collapses to stacked, which is the design system's own behaviour.
See `pages/tuition/frederick-douglass-scholarship.html`.
