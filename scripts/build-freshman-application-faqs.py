#!/usr/bin/env python3
"""Build the Freshman Application FAQs interior page.

Source copy: https://admissions.umd.edu/apply/freshman-application-faqs
Component rationale: briefs/freshman-application-faqs.md
Content data:       briefs/freshman-application-faqs-data.json

Run after editing this file, the data file, or the shared chrome:
    python3 scripts/build-freshman-application-faqs.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "page-builder", "TEMPLATE.html")
DATA = os.path.join(REPO, "briefs", "freshman-application-faqs-data.json")
OUT = os.path.join(REPO, "pages", "how-to-apply", "freshman-application-faqs.html")
TITLE = (
    "Freshman Application FAQs — Undergraduate Admissions | "
    "University of Maryland"
)

# The source breadcrumb is Home / Application FAQs / Freshman Application FAQs.
# The parent now resolves to the local Application FAQs listing page.
# The eyebrow repeats the last breadcrumb link, per CLAUDE.md.
PARENT_LABEL = "Application FAQs"
PARENT_HREF = "application-faqs.html"


data = json.load(open(DATA, encoding="utf-8"))

template = open(TEMPLATE, encoding="utf-8").read()
template_lines = template.split("\n")
critical_end = next(
    index for index, line in enumerate(template_lines) if line.strip() == "</style>"
)
head = _chrome.with_robots("\n".join(template_lines[:critical_end]))
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, count=1)

pin = re.search(r"web-components-library@([\d.]+)/dist/cdn\.js", template)
assert pin, "TEMPLATE.html has no web-components-library cdn.js pin"


def render_sections(sections):
    """One <section> per FAQ group: level-2 heading + a stack of accordion items.

    The heading carries umd-layout-space-vertical-interior-child for its 32px
    margin-BOTTOM; the section's own *-interior class spaces the groups apart.
    Every item starts closed — the source renders all 39 panels
    aria-expanded="false".
    """
    out = []
    for section in sections:
        items = []
        for item in section["items"]:
            items.append(
                '        <umd-element-accordion-item>\n'
                f'          <p slot="headline">{item["question"]}</p>\n'
                '          <div slot="text">\n'
                '            <div class="umd-text-rich-advanced">\n'
                f'              {item["answer_html"]}\n'
                '            </div>\n'
                '          </div>\n'
                '        </umd-element-accordion-item>'
            )
        out.append(
            '        <section class="umd-layout-space-vertical-interior">\n'
            '          <h2 class="umd-layout-space-vertical-interior-child '
            f'text-black umd-sans-larger-bold">{section["heading"]}</h2>\n'
            + "\n".join(items)
            + "\n        </section>"
        )
    return "\n\n".join(out)


faq_markup = render_sections(data["sections"])
image = data["image"]

body = r'''    /* LEDE. umd-sans-larger-bold is FLUID — 18px at 375, ~21.8 at 768, 22.5
       around 900, 22 at 1024+ — and it renders that scale ONLY outside
       .umd-text-rich-advanced, which pins every direct child to
       `font-size: 18px`. That pin is why the lede used to be umd-sans-large
       (already 18px, so the pin took nothing from it) and why ANY larger size
       class inside the block is a silent no-op — swapping the class in place
       changes nothing. The lede is therefore a bare <p> in the section, not a
       child of a rich-text block.

       The 960px cap replaces the measure the wrapper was supplying
       (element.min.css caps p/ul/ol at 960px in place). It is NOT the old
       .interior-lede 800px cap and must not drift back to it.

       The adjacency rule supplies the gap when body copy follows the lede
       directly; it is inert where the lede sits alone in its section. Both
       rules are byte-identical on every page that has a lede — do not rename
       them per page. */
    .page-lede { max-width: 960px; }
    .page-lede + .umd-text-rich-advanced { margin-top: 24px; }
  </style>

  <script src="https://unpkg.com/@universityofmaryland/web-components-library@@@PIN@@/dist/cdn.js"></script>
@@CHROME:chrome-css@@
@@CHROME:gate@@
</head>
<body>
@@CHROME:header@@

  <main id="main-content">
    <section>
      <umd-element-hero-minimal data-theme="dark">
        <p slot="eyebrow">@@PARENT_LABEL@@</p>
        <img slot="image" src="../../images/shared/interior-hero-pattern.png" alt="" />
        <h1 slot="headline">@@PAGE_TITLE@@</h1>
      </umd-element-hero-minimal>
    </section>

    <div class="umd-layout-space-horizontal-normal umd-layout-space-vertical-interior">
      <umd-element-breadcrumb>
        <div slot="paths">
          <a href="../../pages/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
          <a href="../../pages/how-to-apply/"><span>How To Apply</span></a>
          <a href="@@PARENT_HREF@@"><span>@@PARENT_LABEL@@</span></a>
          <p aria-label="Current Page"><span>@@PAGE_TITLE@@</span></p>
        </div>
      </umd-element-breadcrumb>
    </div>

    <div class="umd-layout-space-horizontal-normal">
      <div id="umd-shell-content">
        <section class="umd-layout-space-vertical-interior">
          @@LEDE@@
        </section>

        <!-- The source's umd-image-caption data-size="full" carries no caption
             text, so this is media-inline in standard mode: slot="image" only,
             full content width (OVERRIDES.md § umd-element-media-inline). -->
        <section class="umd-layout-space-vertical-interior">
          <umd-element-media-inline>
            <img slot="image" src="@@IMAGE_SRC@@" alt="@@IMAGE_ALT@@" />
          </umd-element-media-inline>
        </section>

@@FAQ_SECTIONS@@

        <section class="umd-layout-space-vertical-interior">
          <umd-element-banner-promo>
            <h2 slot="headline">There is a lot more to learn about UMD</h2>
            <p slot="text">Let's stay in touch! <a href="https://apply.umd.edu/register/request-info" target="_blank" rel="noopener">Join the Mailing List</a> or <a href="https://admissions.umd.edu/connect">Connect</a>!</p>
            <div slot="actions" class="banner-promo-actions">
              <umd-element-call-to-action data-display="primary">
                <a href="https://apply.umd.edu/register/request-info" target="_blank" rel="noopener">Join the List</a>
              </umd-element-call-to-action>
            </div>
          </umd-element-banner-promo>
        </section>

      </div>
    </div>
  </main>

@@CHROME:footer@@

  <script>
    customElements.whenDefined('umd-element-banner-promo').then(() => {
      document.querySelectorAll('umd-element-banner-promo').forEach(el => {
        const style = document.createElement('style');
        style.textContent = '.banner-promo-actions{display:flex!important;flex-direction:column!important;align-items:flex-end!important;gap:8px!important}';
        el.shadowRoot && el.shadowRoot.appendChild(style);
      });
    });
  </script>

@@CHROME:chrome-scripts@@
</body>
</html>
'''

body = body.replace("@@PIN@@", pin.group(1))
body = body.replace("@@PAGE_TITLE@@", data["title"])
body = body.replace("@@PARENT_LABEL@@", PARENT_LABEL)
body = body.replace("@@PARENT_HREF@@", PARENT_HREF)
body = body.replace("@@LEDE@@", data["lede_html"].replace(
    "<p>", '<p class="umd-sans-larger-bold text-black page-lede">', 1))
body = body.replace("@@IMAGE_SRC@@", image["src"])
body = body.replace("@@IMAGE_ALT@@", image["alt"])
body = body.replace("@@FAQ_SECTIONS@@", faq_markup)
for key in ("chrome-css", "gate", "header", "footer", "chrome-scripts"):
    body = body.replace(f"@@CHROME:{key}@@", _chrome.block(key, OUT))

output = head + "\n" + body
assert "@@" not in output, "unreplaced build token"

# Structural assertions read the page's own <main>, not the whole file: the
# critical CSS in <head> names layout classes, and the chrome regions carry
# their own locks.
main_markup = output[output.index('<main id="main-content">'):output.index("</main>")]

# --- Layout B, the "wide interior" style -----------------------------------
# The source page's <main> has no nav and no aside, so this page has no sidebar
# and sits in the -normal lock. Both the breadcrumb and the content lock use it.
assert main_markup.count('class="umd-layout-space-horizontal-normal') == 2
assert "umd-layout-space-columns-left" not in main_markup
assert "umd-element-nav-slider" not in main_markup
assert 'id="umd-shell-sidebar-container"' not in main_markup
# No 800px cap: that is Layout A's column width, not a Layout B measure. The
# design system's own 960px rich-text rule handles the reading measure here.
assert '<div id="umd-shell-content">' in main_markup
assert "max-w-[800px]" not in main_markup
assert "umd-layout-space-horizontal-larger" not in main_markup
assert "umd-element-section-intro-wide" not in main_markup

# --- Shared interior hero ---------------------------------------------------
assert main_markup.count("<umd-element-hero-minimal") == 1
assert "<umd-element-hero " not in main_markup
assert 'src="../../images/shared/interior-hero-pattern.png" alt=""' in output
assert f'<p slot="eyebrow">{PARENT_LABEL}</p>' in output
# The eyebrow repeats the breadcrumb's last link, which is the page's parent.
assert main_markup.count(f'<span>{PARENT_LABEL}</span>') == 1
assert f'<a href="{PARENT_HREF}"><span>{PARENT_LABEL}</span></a>' in output

# --- Headings ---------------------------------------------------------------
# Every source heading is headline-four-san-serif (24px) -> level 2. No level 1
# and no level 3 appear on this page.
assert main_markup.count('umd-sans-larger-bold">') == len(data["sections"])
assert "umd-sans-extralarge-bold" not in main_markup
assert "umd-sans-large-bold" not in output, "umd-sans-large-bold is not a real class"
# Slotted headings are styled by component shadow CSS; a size class there is inert.
assert not re.search(r'slot="headline"[^>]*class="umd-sans', main_markup)
assert not re.search(r'class="umd-sans[^"]*"[^>]*slot="headline"', main_markup)

# --- The lede is a PARAGRAPH, not a heading ---------------------------------
assert '<p class="umd-sans-larger-bold text-black page-lede">' in main_markup
assert main_markup.count('text-black page-lede') == 1
# The lede must sit OUTSIDE .umd-text-rich-advanced or its size class is inert.
assert 'umd-sans-large text-black' not in main_markup
assert '<h2 class="umd-sans-large' not in main_markup

# --- Accordion --------------------------------------------------------------
expected_items = sum(len(s["items"]) for s in data["sections"])
assert expected_items == 39, expected_items
assert main_markup.count("<umd-element-accordion-item>") == expected_items
assert main_markup.count("</umd-element-accordion-item>") == expected_items
# All 39 panels are aria-expanded="false" on the source: none opens on load.
assert 'data-visual-open' not in main_markup
# Question in slot="headline", answer in slot="text" wrapped in rich text.
assert main_markup.count('<p slot="headline">') == expected_items
assert main_markup.count('<div slot="text">') == expected_items
for _section in data["sections"]:
    heading = ('<h2 class="umd-layout-space-vertical-interior-child '
               f'text-black umd-sans-larger-bold">{_section["heading"]}</h2>')
    assert main_markup.count(heading) == 1, _section["heading"]

# --- Image ------------------------------------------------------------------
# Standard mode: slot="image" alone renders full width. A caption or text slot
# would switch the component into caption or wrapped mode, which the source is
# not doing.
assert main_markup.count("<umd-element-media-inline>") == 1
assert 'slot="caption"' not in main_markup
assert 'slot="text" class=' not in main_markup
assert f'src="{image["src"]}"' in main_markup
assert image["alt"] and f'alt="{image["alt"]}"' in main_markup

# --- Page closer ------------------------------------------------------------
assert main_markup.count("umd-element-banner-promo") >= 1
banner_start = output.index("<umd-element-banner-promo>")
shell_start = output.index('<div id="umd-shell-content">')
shell_end = output.index("</div>\n    </div>\n  </main>", shell_start)
assert shell_start < banner_start < shell_end

# --- Chrome and indexing ----------------------------------------------------
assert '<html lang="en">' in output
assert 'name="robots" content="noindex, nofollow"' in output
assert 'name="googlebot" content="noindex, nofollow"' in output
assert f"web-components-library@{pin.group(1)}/dist/cdn.js" in output

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    handle.write(output)

print(os.path.relpath(OUT, REPO))
