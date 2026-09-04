# UMD "Experts" page — filter / listing pattern

Reverse-engineered from <https://umdrightnow.umd.edu/experts> (source pulled 2026-07-28).

Sources examined (downloaded and grepped, not just WebFetch):
- Page HTML: `https://umdrightnow.umd.edu/experts`
- `/umdrn/experts.CGKabBVQ.js` — page controller (init, filter orchestration, render)
- `/umdrn/shared/experts.utils.C1Poeg_3.js` — the pure filter function + per-expert search-index builder
- `/umdrn/experts.F4mVBRTN.css` and `/umdrn/news-release-index.AR7EkBAY.css` — filter/list styling

## Headline answers

- **There is NO alphabet (A–Z) jump nav on this page.** Nothing in the HTML, JS, or CSS references letters, `charAt`, `scrollIntoView`, or per-letter grouping. Results are a flat, last-name-sorted grid of cards — not grouped by letter. (If we want an alphabet nav on our page, we are *adding* a pattern, not copying one from here.)
- **Filtering is 100% client-side.** On load the JS fetches the entire expert dataset once (GraphQL `POST /api/experts`, paged 500 at a time until exhausted), holds it in memory, and filters that in-memory array. No page reload, no per-keystroke network request. The URL query string is updated via `history.replaceState` purely for shareable/bookmarkable links — it does **not** drive a reload.
- **Filter controls that exist:** (1) a free-text **Search** input, and (2) three collapsible **checkbox groups** — "Colleges, Schools & Campus Units", "Areas of Expertise", "Topics". Plus a Filter/submit button, a Reset button, and removable "Filtered by:" **pills** above the results. The Topics group is dynamically narrowed to topics related to whichever Expertise checkboxes are ticked.
- **"Load More" is client-side paging** of the already-filtered array (page size 9), not a network fetch.

## Filter UX summary

A visitor lands on the page and sees the full expert list (sorted by last name) render into a 3-column card grid after a brief loader. On the left (desktop ≥1020px) is a filter rail titled **REFINE**; on mobile it collapses behind a "Filter" toggle button. The visitor can:

- Type in the **Search** box — results filter live as they type (debounced ~300ms) by substring-matching a precomputed per-person search index (name + org titles + campus units, diacritics stripped, lowercased).
- Expand any of the three **checkbox groups** and tick terms. Ticking Expertise terms also live-rebuilds the Topics group to only relevant topics. Applying filters is AND *across* groups, OR *within* a group.
- See active filters as removable **pills** ("Filtered by: …") with a "Clear all" link; each pill's × removes just that constraint.
- Click **Load More** to reveal the next 9 matches.
- **Reset / Clear filters** to return to the full list.

A results status line (`aria-live="polite"`) announces "Displaying N of M results" for screen readers.

## HTML structure (key skeleton, real class/id names)

The listing container is `#umdrn-search`. Two `<form>`s exist: the REFINE rail (`#umdrn-filters-form`, checkboxes) and a compact search-only form (`#umdrnExpertsFilter`). Both are plain GET forms as a no-JS fallback (`action="…/experts" method="get"`), but JS calls `preventDefault()` and handles everything in-memory.

```html
<!-- LEFT RAIL: REFINE (checkbox filter groups) -->
<div id="umdrn-filters">
  <h2 class="umd-tailwing-right-headline"><span>REFINE</span></h2>
  <form id="umdrn-filters-form">
    <div class="umdrn-filters-form-content">
      <!-- one .umdrn-filters-group per category, injected by JS after data loads -->
      <div class="umdrn-filters-group" data-filter-group="expertise">
        <button class="umdrn-fieldset-toggle" aria-expanded="false">
          <span>Areas of Expertise</span>          <!-- ± toggle via ::before/::after -->
        </button>
        <div class="umdrn-fieldset-container" data-expanded="false" aria-hidden="true" inert>
          <fieldset>
            <label class="umd-field-checkbox-wrapper">
              <input type="checkbox" name="filters" value="<term-id>" data-slug="<slug>">
              <span>Term title</span>
            </label>
            <!-- … more terms … -->
          </fieldset>
        </div>
      </div>
      <!-- groups: data-filter-group="unit" | "expertise" | "topic" -->
    </div>
    <div class="umdrn-filters-actions">
      <button id="umdrn-filter-button"  type="submit">Filter</button>
      <button id="umdrn-reset-button"   type="reset">Reset</button>
    </div>
  </form>

  <!-- mobile-only toggle that shows/hides the rail -->
  <button id="umdrn-filter-expand-button" aria-owns="umdrn-filters-form" aria-expanded="true">
    <span>Filter</span> <svg>…</svg>
  </button>

  <!-- compact search-only form (name/expertise quick search) -->
  <form id="umdrnExpertsFilter" data-search-type="experts">
    <input type="text" id="umd-shell-form-search-input-experts" name="search" placeholder="Search">
    <button type="submit" id="umd-shell-form-search-submit-experts">…</button>
    <button type="reset"  id="umd-shell-form-reset-experts">Clear filters</button>
  </form>
</div>

<!-- RESULTS -->
<p id="umdrn-results-status" role="status" aria-live="polite">Displaying 9 of 300 results</p>

<section id="umdrn-news-results" data-loading="true">
  <div class="umdrn-news-results-loader"><span class="umd-animation-loader-dots"></span></div>

  <!-- active-filter pills, unhidden when filters are set -->
  <div id="umdrn-results-filters" class="umd-text-cluster-pill umdrn-news-filtered-by" hidden></div>

  <p id="umdrn-experts-empty" class="umdrn-news-empty">Loading…</p>

  <!-- the card grid; cards injected here -->
  <section id="umdrn-experts-results-grid"
           class="umdrn-experts-results umd-grid-three-border"
           data-display="block"></section>
</section>

<div class="umdrn-experts-load-more">
  <button type="button" id="umdrn-experts-load-more">Load More</button>
</div>
```

Pill markup produced by JS for the "Filtered by:" bar:

```html
<div class="umdrn-news-filtered-by" >
  <p>Filtered by:</p>
  <a class="umdrn-news-filter-pill" href="?…" data-remove-id="<term-id>"
     aria-label="Remove <term> filter">Term title <span aria-hidden="true">×</span></a>
  <a class="umdrn-news-filter-pill" href="?…" data-remove-search="true">Search: “foo” <span>×</span></a>
  <a class="umdrn-news-filter-clear" href="?…">Clear all</a>
</div>
```

### Key identifiers to reuse / mirror

| Purpose | Selector |
|---|---|
| Listing wrapper | `#umdrn-search` |
| Checkbox filter form | `#umdrn-filters-form` |
| One collapsible group | `.umdrn-filters-group[data-filter-group="…"]` |
| Group toggle button | `.umdrn-fieldset-toggle` (`aria-expanded`) |
| Group body (animates height) | `.umdrn-fieldset-container` (`data-expanded`, `inert`) |
| Checkbox row | `.umd-field-checkbox-wrapper` + `input[name="filters"][value=<id>]` |
| Search input | `input[name="search"]` (`#umd-shell-form-search-input-experts`) |
| Results grid | `#umdrn-experts-results-grid` |
| Loading state host | `#umdrn-news-results[data-loading="true|false"]` |
| Active-filter pill | `.umdrn-news-filter-pill` (`data-remove-id` / `data-remove-search`) |
| Clear-all link | `.umdrn-news-filter-clear` |
| Status line | `#umdrn-results-status` (`aria-live="polite"`) |
| Load more | `#umdrn-experts-load-more` |

## CSS (relevant rules)

Note there is **no alphabet-nav CSS** to copy. The reusable pieces are: the collapsible group accordion (±-icon toggle + height transition), the checkbox fieldset, the removable pills, and the loading→reveal transition.

### Collapsible filter group (accordion with ± toggle)

```css
.umdrn-filters-group { border-bottom: 1px solid #000; margin-bottom: 24px; }
.umdrn-filters-group:last-of-type { border-bottom: 0; margin-bottom: 0; }

.umdrn-filters-group > button {
  cursor: pointer; display: flex; position: relative;
  justify-content: space-between; align-items: flex-start;
  gap: 16px; width: 100%; margin-bottom: 24px; transition: color .5s;
}
.umdrn-filters-group > button span { white-space: normal; text-align: left; line-height: 1.2; }
.umdrn-filters-group > button:hover,
.umdrn-filters-group > button:focus { color: #e21833; }

/* the "+" / "−" indicator: two bars, one rotated 90deg (=+), un-rotated when open */
.umdrn-filters-group > button::before,
.umdrn-filters-group > button::after {
  content: ""; display: block; position: absolute;
  top: calc(50% - 1px); right: 0;
  width: 12px; height: 2px; background-color: #000; transition: transform .5s;
}
.umdrn-filters-group > button::after { transform: rotate(90deg); }
.umdrn-filters-group > button[aria-expanded=true]::before { transform: rotate(-180deg); }
.umdrn-filters-group > button[aria-expanded=true]::after  { transform: rotate(0); }

/* body height animates 0 -> auto (JS sets an explicit px height mid-transition) */
.umdrn-filters-group .umdrn-fieldset-container {
  display: block; height: 0; overflow: hidden; transition: height .5s;
}
.umdrn-filters-group .umdrn-fieldset-container[data-expanded=true] { height: auto; }
.umdrn-filters-group .umdrn-fieldset-container fieldset {
  display: flex; flex-direction: column; gap: 32px;
  max-height: 500px; overflow-y: auto; padding: 0 0 24px;
  transition: margin .75s ease-in-out;
}
.umdrn-filters-group .umdrn-fieldset-container fieldset legend,
.umdrn-filters-group .umdrn-fieldset-container fieldset label { margin: 0; }
```

### Whole-rail collapse (mobile) + actions

```css
#umdrn-filters-form { display: block; height: auto; overflow: visible; transition: height .5s ease-in; }
#umdrn-filters-form[data-expanded=false] { height: 0; overflow: hidden; }
#umdrn-filters-form .umdrn-filters-form-content { padding: 16px 0; }
#umdrn-filters-form .umdrn-filters-actions {
  display: flex; flex-wrap: wrap; align-items: center;
  justify-content: flex-end; gap: 24px; margin-top: 16px;
}

/* rail is a fixed-width sidebar on desktop, full-width stacked on mobile */
@media (max-width:1019px){ #umdrn-search #umdrn-filters { width:100%; min-width:0; max-width:none; } }
@media (min-width:1020px){ #umdrn-search #umdrn-filters { width:28%; min-width:260px; max-width:420px; } }
@media (max-width:1019px){ #umdrn-search { display:block; } }
@media (min-width:1020px){ #umdrn-search { display:flex; justify-content:space-between; gap:64px; } }
@media (max-width:1019px){ #umdrn-search #umdrn-filter-expand-button { display:flex; } }
@media (min-width:1020px){ #umdrn-search #umdrn-filter-expand-button { display:none; } }
```

### Active-filter pills

```css
.umdrn-news-filtered-by { margin-top: 16px; }
.umdrn-news-filtered-by .umdrn-news-filter-pill {
  display: inline-flex; align-items: center; gap: .25em;
  white-space: normal; word-break: break-word; max-width: 100%;
}
.umdrn-news-filtered-by span[aria-hidden=true] { display: inline-block; line-height: 1; } /* the × */
.umdrn-news-filtered-by .umdrn-news-filter-clear {
  display: inline; border: 0; background: unset; color: inherit;
  padding: 0 0 0 8px; white-space: nowrap;
  text-decoration: underline; text-decoration-color:#e6e6e6; text-decoration-thickness:1px;
  text-underline-offset:.12em;
}
```

### Loading → reveal transition

```css
#umdrn-news-results[data-loading=true] { min-height: 240px; }
.umdrn-news-results-loader {
  position: absolute; inset: 0; z-index: 2;
  display: flex; justify-content: center; align-items: center;
  background-color: #fff; color: #454545; opacity: 1; transition: opacity .3s;
}
.umdrn-news-results-loader[aria-hidden=true] { opacity: 0; pointer-events: none; }
/* while loading, the grid/empty/pagination are collapsed & invisible; revealed when data-loading=false */
#umdrn-news-results[data-loading=true] #umdrn-experts-results-grid,
#umdrn-news-results[data-loading=true] .umdrn-news-empty {
  opacity: 0; max-height: 0; overflow: hidden;
}
```

### Card grid

The grid uses the design-system class `umd-grid-three-border` and a container-query for card padding (24 → 32 → 48px as the container widens). List mode is toggled via `#umdrn-experts-results-grid[data-display=list]`.

```css
#umdrn-search .umdrn-experts-results { margin-top: 64px; }
#umdrn-search .umd-grid-three-border {
  --umdrn-expert-card-padding: 24px;
  container: umd-shell-person-grid-helper / inline-size;
}
@container umd-shell-person-grid-helper (width>=650px)  { #umdrn-search .umd-grid-three-border{--umdrn-expert-card-padding:32px} }
@container umd-shell-person-grid-helper (width>=1024px) { #umdrn-search .umd-grid-three-border{--umdrn-expert-card-padding:48px} }
```

## JS logic

Config (from `experts.CGKabBVQ.js`): page size `m = 9`, API fetch page `h = 500`, search debounce `g = 300ms`, desktop breakpoint `_ = 1020px`. State: `S` = all experts (fetched once, sorted by last name), `C` = current filtered array, `w` = current visible count (starts at 9).

### 1. The pure filter function (the important bit)

From `experts.utils.C1Poeg_3.js` (function `y`, imported into the controller as `u`). Called as `C = u(S, searchString, {expertise, units, topics})`:

```js
// e = all experts, t = raw search string, n = { expertise:Set-ish, units, topics } of selected ids
const filterExperts = (e, t, n) => {
  const r = t.trim().toLowerCase();          // normalized search text
  const i = new Set(n.expertise);            // selected expertise ids
  const a = new Set(n.units);                // selected unit/college ids
  const o = new Set(n.topics);               // selected topic ids
  const s = i.size > 0, c = a.size > 0, l = o.size > 0;

  return e.filter(exp => !(
    (r && !exp.searchIndex?.includes(r))                        ||  // text: substring of precomputed index
    (s && !relatedExpertiseIds(exp).some(id => i.has(id)))      ||  // expertise: OR within group
    (c && !unitsOf(exp).some(u => u.id && a.has(u.id)))         ||  // units:     OR within group
    (l && !exp.topics?.some(tp => tp.id && o.has(tp.id)))           // topics:    OR within group
  ));
};
```

Algorithm in plain English: keep an expert **iff** it passes every *active* constraint. A group with no selections is skipped. Text search is a case-insensitive `includes()` against a **precomputed per-expert `searchIndex` string** (built at load time from first/last name + organization titles + campus units, NFD-normalized with diacritics stripped, lowercased, space-joined). So constraints are **AND across the four dimensions, OR within each checkbox group** — and search is plain substring, not fuzzy/tokenized.

### 2. Orchestration on every change (`Y` in the controller)

```js
const applyFilters = () => {
  const search  = searchInput?.value ?? "";
  const checked = collectCheckedFilterIds();     // Set of ticked input[name="filters"] values
  const groups  = splitByType(checked);          // { expertise, units, topics }
  C = filterExperts(S, search, groups);          // recompute filtered array
  w = 9;                                          // reset visible count to first page
  renderActiveFilterPills(search, checked);       // build/update "Filtered by:" bar
  render();                                        // paint first 9 cards
  syncUrl(search, checked);                        // history.replaceState — shareable URL, NO reload
};
```

Triggers wired in `init` (`$`):
- Search input → `input` event, **debounced 300ms** → `applyFilters()`.
- Either form → `submit` → `preventDefault()` + `applyFilters()`.
- Checkbox form → `change`; if an **expertise** box changed, it rebuilds the **Topics** group (`G`) to only topics whose `relatedExpertiseIds` intersect the checked expertise, then filters.
- Reset buttons → clear inputs/checkboxes → `applyFilters()`.
- Pill clicks (`de`, delegated on `document`): a `.umdrn-news-filter-clear` resets everything; a `.umdrn-news-filter-pill` unchecks the box named by its `data-remove-id` (or clears search if `data-remove-search`) then re-filters.

### 3. Render + "Load More" paging (`V` / `B` / `fe`)

```js
const computeVisible = () => {                    // B()
  const total = C.length;
  const shown = Math.min(w, total);
  status.textContent = `Displaying ${shown} of ${total} results`;
  loadMoreBtn.style.display = (shown < total) ? "inline-flex" : "none";
  if (total === 0) { showEmptyState("No Results Found"); return null; }
  return shown;
};

const render = () => {                             // V()
  const shown = computeVisible();
  if (!shown) return;
  resultsContainer.replaceChildren(
    ...C.slice(0, shown).map(exp => buildCard(exp, "card"))   // rebuild DOM from data
  );
  setLoading(false);
};

loadMoreBtn.addEventListener("click", () => { w += 9; render(); });   // fe(): +9 visible, re-render
```

So "Load More" simply grows `w` by 9 and re-renders a bigger slice of the **already-filtered in-memory array** — no network call.

### 4. Data load (once, up front)

```js
// POST /api/experts (GraphQL), paged 500 at a time until a short page is returned
// then: S = experts.sort(byLastName); build id→title maps for expertise/units/topics;
//       inject the .umdrn-filters-group checkbox groups; applyFilters() to paint initial list.
```

## Implications for replicating on our page

- If we want the **UMD look** (left REFINE rail, ±-toggle accordion groups, checkbox facets, removable pills, Load More), the CSS above is directly liftable and the filter algorithm is ~20 lines of vanilla JS over an in-memory array. No framework needed.
- If we specifically want an **A–Z alphabet nav**, this page does **not** provide one — we'd design it ourselves. The natural fit given this architecture: bucket the sorted array by `lastName[0]`, render sticky letter headings, and make the A–Z bar either (a) scroll-to the matching heading, or (b) act as a fourth OR-filter dimension. UMD does neither today.
- Reusable class names if we want to stay consistent with UMD's naming: `.umdrn-filters-group`, `.umdrn-fieldset-toggle`, `.umdrn-fieldset-container`, `.umd-field-checkbox-wrapper`, `.umdrn-news-filter-pill`, `.umdrn-news-filter-clear`. Note these belong to UMD's `umdrn` site CSS, not the vendored `page-builder/` design system — check `page-builder/registry/` before assuming any are available here.

---

# Appendix: The SEARCH BAR (lift-it-directly reference)

Everything needed to replicate the prominent "Search" bar (the `#umdrnExpertsFilter` compact form), self-contained. The bar is deceptively simple: a **flex row** wrapping a **full-width bare `<input>`** (styled by a global `input{}` element rule, NOT by any id/class) plus a **fixed 44×44px red submit button** whose look is entirely Tailwind utility classes. There is no `.umd-shell-form-container` or `#umd-shell-form-search-input-experts` CSS anywhere — the input inherits its whole box from the global `input{}` rule.

## 1. Exact HTML markup

Trimmed to the search bar itself (from the page HTML). The `<form>` carries UMD's "highlight card" layout classes; the actual bar is the inner `.flex.gap-min.items-center` row.

```html
<div class="umd-shell-form-container">
  <a href="#umd-shell-person-list" class="umd-skip-content">
    <span class="sr-only">Skip search form</span><span>Skip to Content</span>
  </a>

  <form id="umdrnExpertsFilter"
        class="umd-layout-background-highlight-light umd-layout-grid-gap-stacked"
        action="https://umdrightnow.umd.edu/experts" method="get"
        data-site="umdrn" data-search-type="experts">

    <div class="umd-layout-grid-inline-stretch">
      <h2 class="umd-text-line-trailing-light"><span>Filter Experts</span></h2>
      <button type="reset" id="umd-shell-form-reset-experts"
              class="umd-sans-smaller umd-animation-line-slide-graydark-red"
              aria-label="Clear and reset search">
        <span aria-hidden="true">Clear filters</span>   <!-- JS renames to "Clear Search" -->
      </button>
    </div>

    <div class="">
      <div class="flex gap-min items-center">                <!-- THE BAR ROW -->
        <label for="umd-shell-form-search-input-experts" class="sr-only">Search</label>

        <input type="text" id="umd-shell-form-search-input-experts"
               name="search" value="" placeholder="Search" />

        <button type="submit" id="umd-shell-form-search-submit-experts"
                class="aspect-square bg-red flex justify-center items-center
                       hover:bg-redDark focus:bg-redDark h-[44px] w-[44px]
                       transition-colors duration-500"
                aria-label="Submit search">
          <svg class="fill-white h-[20px] w-[20px]" aria-hidden="true" title="Search"
               width="96" height="96" viewBox="0 0 96 96" fill="none"
               xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd"
              d="M79.3401 42.2306C79.3401 54.1438 69.6826 63.8013 57.7694 63.8013C45.8562 63.8013 36.1987 54.1438 36.1987 42.2306C36.1987 30.3174 45.8562 20.6599 57.7694 20.6599C69.6826 20.6599 79.3401 30.3174 79.3401 42.2306ZM91 42.2306C91 60.5833 76.1222 75.4612 57.7694 75.4612C51.3447 75.4612 45.3458 73.6379 40.2619 70.4806L24.2216 86.5209H5L30.2245 60.8255C26.6351 55.5189 24.5388 49.1195 24.5388 42.2306C24.5388 23.8778 39.4167 9 57.7694 9C76.1222 9 91 23.8778 91 42.2306Z" />
          </svg>
        </button>
      </div>
    </div>
  </form>
</div>
```

Notes:
- The `<label>` is visually hidden (`.sr-only`) — the placeholder `"Search"` is the only visible label.
- The input has **no class**; every visible style comes from the global `input{}` rule below.
- `type="text"` (not `type="search"`), so the `[type=search]` reset does not apply.

## 2. All CSS that styles the bar (verbatim, with source file noted)

### A. The input box — global `input{}` element rules — **`main.css`**

```css
/* main.css — reset (base), then the real box */
button,input,optgroup,select,textarea{font-feature-settings:inherit;font-variation-settings:inherit;font-family:inherit;font-size:100%;font-weight:inherit;line-height:inherit;letter-spacing:inherit;color:inherit;margin:0;padding:0}

/* main.css — typography applied to every input */
input{class-name:umd-field-input;font-family:Interstate,Helvetica,Arial,Verdana,sans-serif;font-size:14px;line-height:1.375em}

/* main.css — THE box: border, radius(none), padding, height(from padding+line-height), bg, full width */
input{color:#000;cursor:text;outline-offset:1px;text-overflow:ellipsis;background-color:#fff;border:1px solid #e6e6e6;width:100%;padding:12px 16px;transition:border .5s ease-in-out,color .5s ease-in-out;display:block;position:relative}

/* main.css — focus state (adds a black bottom border) */
input:focus,input:focus-within{border-bottom:1px solid #000}

/* main.css — placeholder color (note: a generic gray-400 rule is overridden by #757575) */
input::placeholder,textarea::placeholder{opacity:1;color:#9ca3af}
input::placeholder{color:#757575}

/* main.css — responsive input font-size bumps */
@media (min-width:480px){ input{font-size:16px;line-height:1.375em} }
@media (min-width:650px){ input{font-size:calc(14px + .16vw)} }
@media (min-width:1024px){ input{font-size:16px;line-height:1.375em} }
```

There is **no `border-radius`** declared → the input is square-cornered (0px). Effective height ≈ 14px line + 24px vertical padding + 2px border ≈ 40px at base, matching the 44px button closely.

### B. The 44×44 red submit button — Tailwind utilities — **`main.css`**

```css
/* main.css */
.flex{display:flex}
.aspect-square{aspect-ratio:1}
.items-center{align-items:center}
.justify-center{justify-content:center}
.bg-red{--tw-bg-opacity:1;background-color:rgb(226 24 51/var(--tw-bg-opacity,1))}          /* #e21833 */
.hover\:bg-redDark:hover,.focus\:bg-redDark:focus{--tw-bg-opacity:1;background-color:rgb(169 0 7/var(--tw-bg-opacity,1))}  /* #a90007 */
.h-\[44px\]{height:44px}
.w-\[44px\]{width:44px}
.transition-colors{transition-property:color,background-color,border-color,text-decoration-color,fill,stroke;transition-duration:.15s;transition-timing-function:cubic-bezier(.4,0,.2,1)}
.duration-500{transition-duration:.5s}
```

### C. The search icon (svg inside the button) — **`main.css`**

```css
/* main.css */
.fill-white{fill:#fff}
.h-\[20px\]{height:20px}
.w-\[20px\]{width:20px}
```

### D. The bar row wrapper — **`main.css`**

```css
/* main.css — the flex row holding input + button */
.flex{display:flex}
.gap-min{gap:8px}
.items-center{align-items:center}
```

### E. The reset / "Clear filters" button — **`main.css` + `umdApp.css`**

```css
/* main.css — text size */
.umd-sans-smaller{font-family:Interstate,Helvetica,Arial,Verdana,sans-serif;font-size:14px;line-height:1.28em}
@media (min-width:650px){ .umd-sans-smaller{font-size:calc(12px + .16vw)} }
@media (min-width:1024px){ .umd-sans-smaller{font-size:14px;line-height:1.28em} }

/* umdApp.css — animated underline that slides gray-dark -> red on hover/focus */
.umd-animation-line-slide-graydark-red{position:relative;text-decoration:none}
.umd-animation-line-slide-graydark-red>*:not(svg):not(.sr-only){display:inline;position:relative;background-image:linear-gradient(to left,#454545 50%,#e21833 50%,#e21833);background-position:right bottom;background-repeat:no-repeat;background-size:200% 2px;transition:background .5s}
.umd-animation-line-slide-graydark-red:hover>*:not(svg):not(.sr-only),.umd-animation-line-slide-graydark-red:focus>*:not(svg):not(.sr-only){background-position:left bottom;background-size:200% 2px}
```

### F. The form "highlight card" wrapper (optional — the gray panel + red left rule around the whole bar) — **`main.css`**

```css
/* main.css */
.umd-layout-background-highlight-light{border-left:2px solid #e21833;padding:24px;background-color:#f1f1f1}
@media (min-width:768px){ .umd-layout-background-highlight-light{padding:32px} }
@media (min-width:1024px){ .umd-layout-background-highlight-light{padding:56px} }
.umd-layout-grid-gap-stacked{grid-gap:24px;grid-template-columns:1fr;display:grid}
@media (min-width:1024px){ .umd-layout-grid-gap-stacked{grid-gap:40px} }
```

### G. Screen-reader-only label — **`main.css`**

```css
/* main.css */
.sr-only{clip:rect(0,0,0,0);white-space:nowrap;border-width:0;width:1px;height:1px;margin:-1px;padding:0;position:absolute;overflow:hidden}
```

## Minimal lift (if you want ONLY the bar, no framework)

Collapse the utilities into plain rules — this reproduces the bar exactly:

```css
.search-bar { display:flex; gap:8px; align-items:center; }
.search-bar input {
  flex:1; width:100%; display:block;
  font-family:Interstate,Helvetica,Arial,Verdana,sans-serif;
  font-size:16px; line-height:1.375em;                 /* 14px below 480px */
  color:#000; background:#fff; border:1px solid #e6e6e6; border-radius:0;
  padding:12px 16px; cursor:text; text-overflow:ellipsis; outline-offset:1px;
  transition:border .5s ease-in-out, color .5s ease-in-out;
}
.search-bar input::placeholder { color:#757575; opacity:1; }
.search-bar input:focus { border-bottom:1px solid #000; }
.search-bar button {                                    /* submit */
  flex:none; width:44px; height:44px; aspect-ratio:1;
  display:flex; align-items:center; justify-content:center;
  background:#e21833; border:0; cursor:pointer;
  transition:background-color .5s;
}
.search-bar button:hover, .search-bar button:focus { background:#a90007; }
.search-bar button svg { width:20px; height:20px; fill:#fff; }
```

Palette: red `#e21833`, red-dark (hover) `#a90007`, border gray `#e6e6e6`, placeholder gray `#757575`, panel bg `#f1f1f1`.
