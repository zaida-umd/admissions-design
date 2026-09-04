#!/usr/bin/env python3
"""Regenerate an interest page, e.g. pages/academics/interest-engineering-technology.html.

Sources
  briefs/interests-data.json          editorial copy per interest (hero, intro,
                                      pathway copy + images, careers list, the
                                      curated college slugs)
  briefs/programs-data.json           203 programs; the majors grid is every
                                      program whose `interests` facet contains
                                      this page's interest title
  briefs/colleges-schools-data.json   13 colleges; supplies desc + image for the
                                      three curated college cards
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Usage:
    python3 scripts/build-interest.py                        # all slugs in the JSON
    python3 scripts/build-interest.py engineering-technology # one slug

Adding an interest is a data edit, not a code edit: add a slug block to
briefs/interests-data.json and re-run. Do not hand-edit the generated HTML -
it is overwritten wholesale.
"""
import json, os, re, sys
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
INTERESTS = os.path.join(REPO, 'briefs/interests-data.json')
PROGRAMS = os.path.join(REPO, 'briefs/programs-data.json')
COLLEGES = os.path.join(REPO, 'briefs/colleges-schools-data.json')
OUTDIR = os.path.join(REPO, 'pages', 'academics')
DEPTH = _chrome.depth_of(os.path.join(OUTDIR, 'x.html'))   # -> '../../'


def e(s):
    return _html.escape(s, quote=True)


def plain(desc):
    """Strip tags, THEN unescape entities, THEN collapse whitespace.

    Order-sensitive, and identical to build-programs.py's helper so both pages
    render the same program description byte-for-byte. Any other order leaves a
    stray double space where a tag was, or lets "&amp;" survive as-is.
    """
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', '', desc or ''))).strip()


# ---------------------------------------------------------------- head
# Everything before TEMPLATE's closing </style> is the inlined critical.css
# block, copied verbatim (page-builder/CLAUDE.md: never trim it). Boundaries are
# located by CONTENT, not line number -- TEMPLATE grows whenever critical.css
# does, and hardcoded indices break silently on the next upstream edit.
tpl = open(TEMPLATE, encoding='utf-8').read().split('\n')
crit_end = next(i for i, l in enumerate(tpl) if l.strip() == '</style>')
head_close = next(i for i, l in enumerate(tpl) if l.strip() == '</head>' and i > crit_end)
HEAD_TOP = _chrome.with_robots('\n'.join(tpl[:crit_end]))
# </style> .. cdn.js, WITHOUT </head> -- the shared chrome-CSS block is emitted
# after it (so it wins at equal specificity) and this file closes </head> itself.
HEAD_TAIL_OPEN = '\n'.join(tpl[crit_end:head_close])
assert 'cdn.js' in HEAD_TAIL_OPEN, 'TEMPLATE head is missing the cdn.js script tag'

# ---------------------------------------------------------------- page CSS
PAGE_CSS = '''
    /* ============================================================
       25. INTEREST PAGE — majors grid + careers list
       Two page-specific needs on top of the DS components:
       a 4-up grid for the (text-only) major cards, and a two-column
       list for the careers bullets inside the pathway text slot.
       ============================================================ */

    /* --- majors list ------------------------------------------
       NO page CSS for the majors. They are the DS card-list pattern exactly as
       RULES.md §33 documents it: a plain stack of
       umd-element-card[data-display="list"] inside a
       umd-layout-space-horizontal-small (992px) lock. The separator between
       cards is the DS's own adjacent-sibling rule in web-components.min.css:

         umd-element-card[data-display="list"] + umd-element-card[data-display="list"]
           { margin-top: 24px; padding-top: 24px; border-top: 1px solid #E6E6E6 }

       That rule is why this must NOT go in a border grid. An earlier revision
       put these cards in umd-layout-grid-border-two with
       umd-shell-person-grid-helper, and the two separator systems fought:
       the sibling rule overrode the helper's 48px padding-top back to 24px on
       every card but the first, and its 24px margin-top opened bands that the
       cells' own borders do not paint -- while the border grid's continuous
       left border ran straight through them. Net effect was misaligned first
       row, uneven top padding, and rules on the left that stopped on the right.
       Stacked in one column, the same rule is exactly the list separator this
       section wants.

       Also note data-visual-bordered has NO effect on data-display="list" --
       measured, zero bordered nodes in that variant's shadow tree.

       The careers list is likewise unstyled: it is the plain rich-text <ul>
       the source page uses, single-column, bullets from the DS. */
'''


def outpath(slug):
    return os.path.join(OUTDIR, f'interest-{slug}.html')


def render(slug, data, programs, colleges_by_slug):
    out = outpath(slug)          # the chrome is rendered for this exact page
    interest = data['interest']
    hero, intro = data['hero'], data['intro']
    majors_copy, careers = data['majors'], data['careers']

    # -------------------------------------------------------- majors
    matched = sorted(
        (p for p in programs if any(i['title'] == interest for i in p['interests'])),
        key=lambda p: p['title'])
    if not matched:
        raise SystemExit(f'{slug}: no programs tagged "{interest}" -- check the '
                         f'`interest` value against programs-data.json')

    cards = []
    for p in matched:
        types = ' / '.join(t['title'] for t in p['types'])
        name = e(p['title'])
        head = (f'<a href="{e(p["titleLink"])}" target="_blank" rel="noopener">{name}</a>'
                if p['titleLink'] else name)
        cards.append(f'''        <umd-element-card data-display="list" class="interest-major">
          <p slot="eyebrow">{e(types)}</p>
          <h3 slot="headline">{head}</h3>
          <p slot="text" class="interest-major-desc">{e(plain(p["description"]))}</p>
        </umd-element-card>''')
    cards_html = '\n'.join(cards)

    # -------------------------------------------------------- colleges
    # Curated per interest, mirroring the live page's three cards -- NOT every
    # college represented in `matched`. Fail loudly on a bad slug rather than
    # silently dropping a card.
    college_cards = []
    for cslug in data['colleges']:
        c = colleges_by_slug.get(cslug)
        if c is None:
            raise SystemExit(f'{slug}: unknown college slug "{cslug}" -- '
                             f'valid: {", ".join(sorted(colleges_by_slug))}')
        college_cards.append(f'''        <umd-element-card data-visual-image-aligned="true">
          <a slot="image" href="{e(c['url'])}" target="_blank" rel="noopener"><img src="{e(c['image'])}" alt="{e(c['alt'])}" loading="lazy" /></a>
          <p slot="eyebrow">{e(c['abbr'])}</p>
          <h3 slot="headline"><a href="{e(c['url'])}" target="_blank" rel="noopener">{e(c['name'])}</a></h3>
          <p slot="text">{e(c['desc'])}</p>
        </umd-element-card>''')
    colleges_html = '\n'.join(college_cards)

    careers_items = '\n'.join(
        f'            <li>{e(i)}</li>' for i in careers['items'])

    title = (f'{_html.unescape(data["title"])} — Undergraduate Admissions '
             f'| University of Maryland')
    head_top = HEAD_TOP.replace(
        '<title>{{PAGE_TITLE}} — {{SITE_NAME}} | University of Maryland</title>',
        f'<title>{e(title)}</title>')
    if '{{' in head_top:
        raise SystemExit('unreplaced placeholder in head: '
                         + re.findall(r'\{\{\w+\}\}', head_top)[0])

    # -------------------------------------------------------- assemble
    # Chrome (header, footer, chrome CSS, chrome scripts) comes from shared/ via
    # _chrome.py, so this page and build-chrome.py's hand-authored pages emit
    # byte-identical blocks. The pathway aspect-ratio injection IS emitted here
    # because this page has two umd-element-pathway instances; the banner-promo,
    # call-to-action and card-overlay injections are not (no such elements).
    return f'''{head_top}
{HEAD_TAIL_OPEN}

  <!-- Page CSS gets its OWN style block, after cdn.js -- it is deliberately
       NOT appended to the inlined critical.css above. tools/inline-critical.py
       rewrites the FIRST style block in a file and leaves later ones alone, so
       page CSS sitting inside that block is (a) invisible to --check, which
       then reports the page as permanently stale, and (b) DELETED the moment
       the tool is run over pages/. Cascade order is unchanged: critical <
       page CSS < chrome CSS, exactly as when this sat at the tail of the
       critical block. (No literal style tag in this comment on purpose -- the
       repo's tooling finds these blocks by regex.) -->
  <style>{PAGE_CSS}  </style>
{_chrome.block('chrome-css', out)}
{_chrome.block('gate', out)}
</head>
<body>

{_chrome.block('header', out)}

  <!-- 3. HERO — small background, left-aligned text -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small">
      <img slot="image" src="{e(hero['image'])}" alt="{e(hero['alt'])}" />
      <h1 slot="headline">{hero['headline']}</h1>
      <div slot="text"><p>{hero['text']}</p></div>
      <div slot="actions">
        <umd-element-call-to-action data-display="primary">
          <a href="programs.html">Explore All Programs</a>
        </umd-element-call-to-action>
      </div>
    </umd-element-hero>
  </section>

  <!-- 4. INTRO — the interior-page lockup used on how-to-apply.html and
       colleges-schools.html: narrow -small lock, rule, uppercase lead,
       rich-text body. Deliberately NOT a pathway. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black" style="text-transform:uppercase;">{intro['lead']}</p>
      <div class="umd-text-rich-advanced">
        <p>{intro['text']}</p>
      </div>
    </div>
  </section>

  <!-- 5. RELATED MAJORS — pathway carries the headline + copy, the DS card-list
       stack follows it inside the same section (RULES §33: standalone card list
       takes the umd-layout-space-horizontal-small 992px lock).
       {len(matched)} programs tagged "{interest}".

       The pathway wrapper takes umd-layout-vertical-landing (120px desktop),
       NOT -child (48px): the pathway and the grid are two components stacked
       in one section, not a section-intro and the content it introduces. The
       -child gap belongs on a section intro -- see the colleges section below,
       where it is what produces the required 48px. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-vertical-landing">
      <umd-element-pathway data-layout-image-position="{e(majors_copy['imagePosition'])}">
        <img slot="image" src="{e(majors_copy['image'])}" alt="{e(majors_copy['alt'])}" />
        <h2 slot="headline">{majors_copy['headline']}</h2>
        <div slot="text">
          <p>{majors_copy['text']}</p>
        </div>
      </umd-element-pathway>
    </div>
    <div class="umd-layout-space-horizontal-small">
      <div class="interest-majors-grid">

{cards_html}

      </div>
    </div>
  </section>

  <!-- 6. CAREERS — dark overlay pathway, image opposite the majors pathway.
       data-display="overlay" data-theme="dark" is self-contained: it paints its
       own black panel inside the content lock, so NO umd-layout-background-full-dark
       wrapper (OVERRIDES.md § "Overlay pathway as a dark editorial block").
       The list is the source page's plain rich-text <ul>, single column. -->
  <section class="umd-layout-vertical-landing">
    <umd-element-pathway data-display="overlay" data-theme="dark"
                         data-layout-image-position="{e(careers['imagePosition'])}">
      <img slot="image" src="{e(careers['image'])}" alt="{e(careers['alt'])}" />
      <h2 slot="headline">{careers['headline']}</h2>
      <div slot="text">
        <ul class="interest-careers-list">
{careers_items}
        </ul>
      </div>
    </umd-element-pathway>
  </section>

  <!-- 7. RELATED COLLEGES & SCHOOLS — 3-up DS cards, curated in
       briefs/interests-data.json. Page ends here: the live page repeats the
       majors grid below this point, which is a bug, not a section. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <umd-element-section-intro class="umd-layout-vertical-landing-child">
        <h2 slot="headline">Related Colleges &amp; Schools</h2>
      </umd-element-section-intro>
      <div class="umd-layout-grid-gap-three" data-animation="off">

{colleges_html}

      </div>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right (pin lives in shared/chrome.css) -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

{_chrome.block('footer', out)}

{_chrome.block('chrome-scripts', out)}

  <!-- Pathway shadow injection — page-content-driven (OVERRIDES.md).
       Emitted because this page uses umd-element-pathway.

       1:1 image crop. Selector is the project's documented one
       (.pathway-image-container / .image-container /
       .umd-asset-image-wrapper-scaled) — verified against the live shadow tree
       in cdn.js@1.18.12. The component exposes no CSS variable or ::part hook
       for the image container. Load-bearing on the overlay variant, not just
       cosmetic: overlay lays its image out as a grid column, so without the cap
       a tall source drives the height of the whole component. -->
  <script>
  (function () {{
    var CSS = '.pathway-image-container,.image-container,' +
              '.umd-asset-image-wrapper-scaled' +
              '{{aspect-ratio:1/1 !important;height:auto !important;}}' +
              '.pathway-image-container img,.image-container img' +
              '{{object-fit:cover;width:100%;height:100%;}}';
    function inject(el) {{
      if (!el.shadowRoot || el.dataset.pathwayCssDone) return;
      var s = document.createElement('style');
      s.textContent = CSS;
      el.shadowRoot.appendChild(s);
      el.dataset.pathwayCssDone = '1';
    }}
    function run() {{
      document.querySelectorAll('umd-element-pathway').forEach(inject);
    }}
    if (window.customElements) {{
      customElements.whenDefined('umd-element-pathway').then(function () {{
        run();
        setTimeout(run, 300);
      }});
    }}
    document.addEventListener('DOMContentLoaded', run);
  }})();
  </script>

  <!-- NO description clamp. Program descriptions run 250-875 characters and
       every one displays in full: truncating a program's description is a
       content decision, not a layout one, and this page is the reader's index
       of what a major actually is. An earlier revision shadow-injected a
       4-line -webkit-line-clamp here; it is deliberately gone. Row heights are
       evened out by umd-layout-grid-child-fill-height on each card instead, so
       a long description makes its row taller rather than getting cut. -->

  <!-- Canonical grid-entry animations (page-builder/CLAUDE.md: never inline). -->
  <script src="../../page-builder/scripts/grid-animations.js"></script>

</body>
</html>
'''


def main():
    interests = json.load(open(INTERESTS, encoding='utf-8'))
    programs = json.load(open(PROGRAMS, encoding='utf-8'))['data']['programsEntries']
    colleges_by_slug = {c['slug']: c
                        for c in json.load(open(COLLEGES, encoding='utf-8'))}

    slugs = sys.argv[1:] or [k for k in interests if not k.startswith('_')]
    for slug in slugs:
        if slug not in interests:
            raise SystemExit(f'unknown interest slug "{slug}" -- valid: '
                             + ', '.join(k for k in interests if not k.startswith('_')))
        page = render(slug, interests[slug], programs, colleges_by_slug)
        out = outpath(slug)
        # Image paths in interests-data.json are repo-root-relative behind
        # {{ROOT}}, like the chrome's; resolve them for this page's depth.
        page = page.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)
        open(out, 'w', encoding='utf-8').write(page)
        print('wrote', out, len(page.split(chr(10))), 'lines')


if __name__ == '__main__':
    main()
