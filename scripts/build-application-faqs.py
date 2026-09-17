#!/usr/bin/env python3
"""Build Application FAQs from the source inventory in briefs/application-faqs-data.json."""

import json
import re
from html import escape
from pathlib import Path

import _chrome


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pages/how-to-apply/application-faqs.html"
data = json.loads((ROOT / "briefs/application-faqs-data.json").read_text())
template = (ROOT / "page-builder/TEMPLATE.html").read_text()
style_close = template.index("</style>")
head = template[:template.rindex("\n", 0, style_close) + 1]
head = _chrome.with_robots(head)
head = re.sub(
    r"<title>.*?</title>",
    "<title>Application FAQs — Undergraduate Admissions | University of Maryland</title>",
    head,
    count=1,
)
pin = re.search(r"web-components-library@([\d.]+)/dist/cdn\.js", template).group(1)


# Byte-identical to the block on every other page that has a lede — do not
# rename these rules per page.
LEDE_CSS = """\
    /* LEDE. umd-sans-larger-bold is FLUID — 18px at 375, ~21.8 at 768, 22.5
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

       The adjacency rule supplies the gap where body copy follows the lede
       directly — as it does here — since the block's own
       `> *:first-child { margin-top: 0 }` would otherwise zero it. */
    .page-lede { max-width: 960px; }
    .page-lede + .umd-text-rich-advanced { margin-top: 24px; }
"""


def card(item):
    """Adjacent list cards use the design system's own separators and spacing."""
    image = item["image"]
    href = escape(item["href"], quote=True)
    return f'''          <umd-element-card data-display="list" data-theme="light" data-visual-image-aligned="true">
            <img slot="image" src="{escape(image['src'], quote=True)}" alt="{escape(image['alt'], quote=True)}" loading="lazy" />
            <h2 slot="headline"><a href="{href}">{escape(item['title'])}</a></h2>
            <div slot="text">{item['description_html']}</div>
            <div slot="actions">
              <umd-element-call-to-action data-display="secondary">
                <a href="{href}" aria-label="{escape(item['cta_label'], quote=True)}">{escape(item['cta'])}</a>
              </umd-element-call-to-action>
            </div>
          </umd-element-card>'''


cards = "\n".join(card(item) for item in data["items"])
lede = data["lede_html"].replace(
    '<p>', '<p class="umd-sans-larger-bold text-black page-lede">', 1)
body = f'''{LEDE_CSS}  </style>
  <script src="https://unpkg.com/@universityofmaryland/web-components-library@{pin}/dist/cdn.js"></script>
@@CHROME:chrome-css@@
@@CHROME:gate@@
</head>
<body>
@@CHROME:header@@

  <main id="main-content">
    <section>
      <umd-element-hero-minimal data-theme="dark">
        <p slot="eyebrow">How To Apply</p>
        <h1 slot="headline">Application FAQs</h1>
        <img slot="image" src="../../images/shared/interior-hero-pattern.png" alt="" />
      </umd-element-hero-minimal>
    </section>

    <div class="umd-layout-space-horizontal-normal umd-layout-space-vertical-interior">
      <umd-element-breadcrumb>
        <div slot="paths">
          <a href="../../pages/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
          <a href="../../pages/how-to-apply/"><span>How To Apply</span></a>
          <p aria-label="Current Page"><span>Application FAQs</span></p>
        </div>
      </umd-element-breadcrumb>
    </div>

    <div class="umd-layout-space-horizontal-normal">
      <div id="umd-shell-content">
        <section class="umd-layout-space-vertical-interior">
          {lede}
          <div class="umd-text-rich-advanced">
            {data['body_html']}
          </div>
        </section>

        <section class="umd-layout-space-vertical-interior" aria-label="Application resources">
{cards}
        </section>

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
@@CHROME:chrome-scripts@@
</body>
</html>
'''
for key in _chrome.keys():
    token = f"@@CHROME:{key}@@"
    assert token in body, f"Missing chrome region: {key}"
    body = body.replace(token, _chrome.block(key, str(OUT)))
output = head + body
assert "@@" not in output

# --- The lede is a PARAGRAPH, and it sits OUTSIDE the rich-text block --------
# Inside .umd-text-rich-advanced a size class is INERT, not wrong: the block
# pins every direct child to 18px, so the page looks fine and measures wrong.
# Only an assertion catches it.
assert '<p class="umd-sans-larger-bold text-black page-lede">' in output
assert output.count("text-black page-lede") == 1
assert "umd-sans-large text-black" not in output
assert '<h2 class="umd-sans-large' not in output
assert ".page-lede { max-width: 960px; }" in output
OUT.write_text(output)
print(OUT.relative_to(ROOT))
