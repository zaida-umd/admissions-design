# Admissions Rich Text Patterns

> ## ⚠️ ARCHIVED — 2026-09-18
>
> **The restyled table described here is no longer on `main`.** Dev feedback
> was that the interior-page work could not be implemented as built, so both
> pages using it (`tuition/cost-of-attendance.html` and
> `how-to-apply/english-language-proficiency.html`) were removed, along with
> `scripts/rich_text.py` and `styles/rich-text-table.css`.
>
> This file is kept as the **design record** — it is the reasoning behind the
> treatment, not a description of the current tree. Nothing here is importable
> today. Recover the implementation with
> `git checkout archive/interior-pages -- scripts/rich_text.py styles/rich-text-table.css`.

Project-owned reusable content functions that extend the shared Page Builder
without changing its `page-builder/` submodule.

## Responsive Rich Text Table

Use `scripts.rich_text.render_rich_text_table()` for structured tabular content
inside an Admissions interior page. The function produces a semantic table,
keyboard-focusable horizontal-scroll wrapper, accessible caption and optional
footnotes.

Add the shared stylesheet to the page `<head>`. Adjust the relative path for the
page depth:

```html
<link rel="stylesheet" href="../../styles/rich-text-table.css">
```

Example:

```python
from scripts.rich_text import render_rich_text_table, rich_text_table_header

table_html = render_rich_text_table(
    caption="Estimated cost of attendance",
    region_label="Estimated cost of attendance table",
    headers_html=(
        rich_text_table_header("Cost category", screen_reader_only=True),
        rich_text_table_header("Maryland Residents", second_line="(In-State)"),
        rich_text_table_header("Nonresidents", second_line="(Out-of-State)"),
    ),
    rows_html=(
        ("Tuition<sup>2</sup> &amp; Fees<sup>3</sup>", "$12,008", "$41,974"),
        ("TOTAL EST. COST OF ATTENDANCE", "$32,408", "$62,374"),
    ),
    total_row_indices=(1,),
    footnotes_html=(
        "<em>Footnote copy.</em>",
        '<em>More details are available on the </em><a href="/policy">policy page</a>.',
    ),
)
```

The stylesheet provides the established Cost of Attendance treatment:

- full-width table with a 680px minimum and horizontal overflow on narrow screens;
- black 71px header with white 18px bold text;
- 16px padding on all header and body cells;
- left-aligned columns and tabular numerals;
- 64px body rows, 1px dividers and alternating white / `#fafafa` zebra stripes;
- optional bold total rows selected with `total_row_indices`.

### Footnotes carry no page-owned CSS

`footnotes_html` renders as `<li><small>…</small></li>` inside a plain
`.umd-text-rich-advanced` `<ul>`, and **every bit of its styling comes from the
design system** — `element.min.css` already ships

```css
:is(.umd-text-rich-advanced,.umd-rich-text) small { font-size:14px; line-height:1.28em; }
:is(.umd-text-rich-advanced,.umd-rich-text) a     { /* black → red gradient underline */ }
:is(…) ul li + li                                 { margin-top:16px; }
```

so `<small>` gets the 14px, the bullets, the 16px item spacing and the animated
link underline for nothing. There is no footnote rule in
`styles/rich-text-table.css`, and there should not be one.

There used to be. `.umd-text-rich-table-footnotes` was 52 lines that re-declared
`font-size: 14px` on five different selectors to fight the 18px rich-text
cascade, and copied the DS link rule verbatim. `<small>` is the design system's
own answer to that cascade, so the whole block was redundant — and one line of
it never worked at all: `list-style: disc` loses to the DS's
`list-style-type: none !important` (which draws a `•` pseudo-element instead),
so its `padding-left: 22px` was only ever stacking on top of the `li`'s own
24px.

**Spacing above the block is markup, not CSS.** The DS gives a rich-text `ul`
`margin-top: 24px`, but only against a sibling *inside the same* rich-text div —
two adjacent `.umd-text-rich-advanced` divs give each other 0. So:

- footnotes **directly after the table** get 32px from
  `.umd-text-rich-table-scroll`'s `margin-bottom`, which is what the renderer
  emits;
- footnotes **after a paragraph** (as on `cost-of-attendance.html`) must go in
  *that paragraph's* div, where the DS's own 24px applies.

Do not add a `margin-top` rule to get this — measured 24px and 32px respectively
at 1280px.

`headers_html`, `rows_html`, and `footnotes_html` intentionally accept trusted
HTML fragments so authored content can contain links, emphasis and superscript
markers. Never pass user-submitted HTML to those arguments.

By default, the first cell in each row is emitted as a semantic row header.
Pass `row_headers=False` when every column contains equivalent data, such as a
multi-column alphabetical country list.
