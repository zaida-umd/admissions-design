#!/usr/bin/env python3
"""Regenerate the admission-representatives landing page and the rep bio pages.

Sources
  briefs/representatives-data.json    page copy + all 24 reps (name, position,
                                      headshot, "Favorite Maryland Moment" bio,
                                      territory list, and a `page` flag)
  page-builder/TEMPLATE.html          <head> + inlined critical.css (verbatim)
  shared/ (via scripts/_chrome.py)    header stack, footer, chrome CSS,
                                      chrome shadow injections

Outputs
  pages/admission-representatives/index.html    the landing page (all 24 reps)
  pages/admission-representatives/<slug>.html   one per rep with "page": true

Usage:
    python3 scripts/build-representatives.py                  # landing + every flagged rep
    python3 scripts/build-representatives.py ebony-freeman    # one rep, no landing

Why the bios are pages, not modals
  The live site renders each rep as a <umd-person-modal> that lazy-loads the
  bio from its CMS on click. The design system has no modal component, and
  nothing in it projects an arbitrary content payload over the page. It does
  have umd-element-person-hero -- explicitly "a person profile landing page",
  with its own breadcrumb slot -- so a rep's bio becomes a real URL instead.
  That is a better outcome than the modal anyway: the bios become linkable,
  crawlable and back-button-able.

Adding a rep's page is a data edit, not a code edit: flip "page" to true in
briefs/representatives-data.json and re-run. Do not hand-edit the generated
HTML -- it is overwritten wholesale.
"""
import json, os, re, sys
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, 'page-builder/TEMPLATE.html')
DATA = os.path.join(REPO, 'briefs/representatives-data.json')
OUTDIR = os.path.join(REPO, 'pages', 'admission-representatives')
DEPTH = _chrome.depth_of(os.path.join(OUTDIR, 'x.html'))   # -> '../../'

CONTACT_EMAIL = 'ApplyMaryland@umd.edu'


def e(s):
    return _html.escape(s or '', quote=True)


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
# Shared by the landing page and the bio pages so the two never drift. The
# brand-chevron block is copied from pages/how-to-apply/index.html deliberately:
# it is the project's established "eyebrow lockup + chevron" intro treatment,
# and the animation's own hardcoded 100vw/50vw internals are what force the
# host to span the full width rather than be sized.
PAGE_CSS = '''
    /* ============================================================
       26. ADMISSION REPRESENTATIVES — intro lockup + rep pages
       ============================================================ */

    /* --- intro lockup with brand chevron (landing page) --------
       Same treatment as how-to-apply/index.html and tuition/index.html:
       rule, uppercase eyebrow, rich text, with the brand animation
       riding behind it and overlapping ~180px up into the hero.
       The animation hardcodes its inner container to width:100vw /
       height:50vw and anchors chevrons to right:0, so the host must
       span full width -- sizing or clipping it does not work. */
    .reps-intro-section {
      position: relative;
      overflow: visible;
      z-index: 100;
    }

    .reps-intro-content {
      position: relative;
      z-index: 2;
    }

    .reps-chevron {
      position: absolute;
      top: -180px;
      left: 0;
      right: 0;
      bottom: -80px;
      pointer-events: none;
      z-index: 1;
      overflow: visible;
    }

    .reps-chevron > umd-element-brand-logo-animation {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      display: block;
    }

    @media (max-width: 1023px) {
      .reps-chevron { display: none; }
    }

    /* --- rep grid ----------------------------------------------
       No grid CSS of its own. The cards are the documented border-grid
       pattern exactly as LAYOUT-PATTERNS.md describes it:
       umd-layout-grid-border-four + class="umd-shell-person-grid-helper"
       on every umd-element-person host (that class is the container-query
       target -- without it the 24/32/48px cell padding never applies).
       Partial rows are handled by critical.css §19's :not(:has(...)) rules,
       so 24 reps in a 4-up grid needs no filler markup.

       The one thing added: the grid's own left/right border is drawn by
       layout.min.css against the cell edge, and a headshot sitting flush
       in a 24px cell reads as unaligned next to a name that wraps to two
       lines. umd-layout-grid-child-fill-height equalises the cells so the
       job-title baselines line up across a row. */

    /* --- search page: filter form ------------------------------
       The CMS person-index template (omc.umd.edu/people) is built almost
       entirely from design-system classes that ARE in our bundles:
       umd-layout-background-highlight-light (grey panel + red left rule),
       umd-layout-grid-gap-stacked / -two, umd-layout-grid-inline-stretch,
       umd-text-line-trailing-light, umd-field-select-wrapper, umd-field-input,
       umd-action-outline, umd-skip-content, sr-only.

       What is NOT in our bundles, and is therefore reproduced below:
         - the `umd-shell-*` classes (shellcraft site CSS, not the DS)
         - the Tailwind utilities the template leans on for the search row
           (flex, gap-min, items-center, aspect-square, bg-red, h-[44px])
       Measured against the loaded bundles, not assumed. The rules below are
       the "minimal lift" from briefs/experts-filter.md, which documents this
       same search bar on the experts page. */
    .reps-search-row {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .reps-search-row input { flex: 1; }
    /* 44x44 red submit, matching the template's Tailwind box exactly. */
    .reps-search-submit {
      flex: none;
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--umd-color-red, #e21833);
      border: 0;
      cursor: pointer;
      transition: background-color .5s;
    }
    .reps-search-submit:hover,
    .reps-search-submit:focus-visible { background: #a90007; }
    .reps-search-submit svg { width: 20px; height: 20px; fill: #fff; }

    /* Gap between the results grid and whatever follows it.

       The DS vertical rhythm classes are margin-BOTTOM only -- measured,
       umd-layout-vertical-landing is `margin-bottom: 120px; margin-top: 0`
       (the same thing CLAUDE.md notes about -child, and it holds for the
       parent class too). The grid's own wrapper is a bare
       umd-layout-space-horizontal-larger with no vertical class, so nothing
       separated it from the next block and both the Load More button and the
       trailing copy sat flush against the last row of cards.

       Putting the space on the WRAPPER rather than on either follower is what
       makes it hold in both states: Load More is display:none when every match
       is already shown, so a margin on that section would vanish with it and
       the copy would jump back up against the grid the moment a filter
       narrowed the results. Followers have margin-top: 0, so there is no
       collapsing to reason about -- the gap is exactly this value. */
    .reps-results-wrap { margin-bottom: 80px; }

    /* Results count + empty state. The template's .umd-shell-pagination-results
       is site CSS, not DS, so the type is set here. */
    .reps-results-status {
      font-size: 14px;
      color: var(--umd-color-gray-dark, #757575);
      margin-top: 24px;
    }
    .reps-empty { padding: 48px 0; text-align: center; }
    .reps-load-more { display: flex; justify-content: center; }
    /* JS hides this when every match is already on screen; without JS the
       whole set is rendered, so the button has nothing to do and stays gone. */
    .reps-load-more[hidden] { display: none; }

    /* --- territory list (bio pages) ----------------------------
       The territories are a plain list, but a rep can cover nine of them
       (Abigail Trice) or none at all, so a single column runs long and a
       fixed multi-column grid leaves a ragged hole. Columns that fill on
       width keep both ends honest. */
    .rep-regions-list {
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px 32px;
    }
    @media (min-width: 650px) {
      .rep-regions-list { grid-template-columns: repeat(2, 1fr); }
    }
    @media (min-width: 1024px) {
      .rep-regions-list { grid-template-columns: repeat(3, 1fr); }
    }
    .rep-regions-list li {
      border-top: 1px solid var(--umd-color-gray-light, #e6e6e6);
      padding-top: 12px;
    }
'''


# ---------------------------------------------------------------- helpers
def head_for(title):
    head = HEAD_TOP.replace(
        '<title>{{PAGE_TITLE}} — {{SITE_NAME}} | University of Maryland</title>',
        '<title>%s</title>' % e(title))
    if '{{' in head.replace(_chrome.ROOT_TOKEN, ''):
        raise SystemExit('unreplaced placeholder in head: '
                         + re.findall(r'\{\{\w+\}\}', head)[0])
    return head


def landing_path():
    return os.path.join(OUTDIR, 'index.html')


def rep_path(slug):
    return os.path.join(OUTDIR, '%s.html' % slug)


def mailto(person):
    """Everyone routes through the shared inbox.

    The live site publishes no individual addresses -- it asks the reader to
    email ApplyMaryland@umd.edu with their city and state in the subject. The
    subject line is prefilled with the rep's name so the office can route it,
    which is the same instruction the source page gives in prose.
    """
    return 'mailto:%s?subject=%s' % (
        CONTACT_EMAIL,
        _html.escape('Student Inquiry for %s' % person['name'], quote=True).replace(' ', '%20'))


# ---------------------------------------------------------------- cards
def region_slug(region):
    """Stable option value for a territory. Only has to round-trip, not be pretty."""
    return re.sub(r'[^a-z0-9]+', '-', region.lower()).strip('-')


def person_card(p, filterable=False):
    """One grid cell. Identical markup on the index and the search page.

    `filterable` adds the data-* the search page's JS reads. The attributes are
    inert everywhere else, but they are only emitted where they are used so the
    index's markup stays exactly what it was.
    """
    # A rep with a bio page gets their name as the link into it; a rep without
    # one gets the same name as plain text. Both render through the same slot,
    # so the grid stays visually uniform either way -- the only difference is
    # whether the name is actionable.
    if p['page']:
        name = ('<a href="%s.html" slot="name"><span>%s</span></a>'
                % (e(p['slug']), e(p['name'])))
    else:
        name = '<p slot="name">%s</p>' % e(p['name'])

    data = ''
    if filterable:
        # Precomputed lowercase search index -- name + position + territories,
        # matched with a plain substring test (the same approach the UMD
        # experts page uses; see briefs/experts-filter.md). Doing it here keeps
        # the per-keystroke work to one String.includes per card.
        idx = ' '.join([p['name'], p['position']] + p['regions']).lower()
        data = ('\n          data-regions="%s" data-search="%s"'
                % (e('|'.join(region_slug(r) for r in p['regions'])), e(idx)))

    return ('''        <umd-element-person class="umd-shell-person-grid-helper umd-layout-grid-child-fill-height"%s>
          <img slot="image" src="%s" alt="%s" loading="lazy" />
          %s
          <p slot="job-title">%s</p>
        </umd-element-person>'''
            % (data, e(p['image']), e(p['alt']), name, e(p['position'])))


# ---------------------------------------------------------------- landing
def render_landing(doc):
    out = landing_path()
    page, people = doc['page'], doc['people']
    hero, intro, grid, promo = page['hero'], page['intro'], page['grid'], page['promo']

    cards_html = '\n'.join(person_card(p) for p in people)

    intro_paras = '\n'.join('        <p>%s</p>' % t for t in intro['paragraphs'])

    return '''%(head)s
%(head_tail)s

  <!-- Page CSS gets its OWN style block, after cdn.js -- it is deliberately
       NOT appended to the inlined critical.css above. tools/inline-critical.py
       rewrites the FIRST style block in a file and leaves later ones alone, so
       page CSS sitting inside that block is (a) invisible to --check, which
       then reports the page as permanently stale, and (b) DELETED the moment
       the tool is run over pages/. Cascade order is unchanged: critical <
       page CSS < chrome CSS, exactly as when this sat at the tail of the
       critical block. (No literal style tag in this comment on purpose -- the
       repo's tooling finds these blocks by regex.) -->
  <style>%(css)s  </style>
%(chrome_css)s
%(gate)s
</head>
<body>

%(header)s

  <!-- 3. HERO — small background, centred text (matches how-to-apply/index.html
       and personas/prospective-students.html; the section landings that lead
       with a directory rather than a pathway stack use the centred variant). -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small" data-layout-text="center">
      <img slot="image" src="%(hero_img)s" alt="%(hero_alt)s" />
      <h1 slot="headline">%(hero_headline)s</h1>
      <div slot="text"><p>%(hero_text)s</p></div>
    </umd-element-hero>
  </section>

  <!-- 4. WE'RE HERE FOR YOU — the project's eyebrow lockup + brand chevron,
       same treatment as how-to-apply/index.html § "Get to Know Our Process".
       The source page's instruction to click a photo is rewritten to point at
       the profile pages, since this recreation has no modals. -->
  <section class="umd-layout-vertical-landing reps-intro-section">
    <div class="reps-chevron" aria-hidden="true">
      <umd-element-brand-logo-animation></umd-element-brand-logo-animation>
    </div>
    <div class="umd-layout-space-horizontal-small reps-intro-content">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black" style="text-transform:uppercase;">%(intro_lead)s</p>
      <div class="umd-text-rich-advanced">
%(intro_paras)s
      </div>
    </div>
  </section>

  <!-- 5. THE REPS — DS border grid, 4-up. Every host carries
       umd-shell-person-grid-helper (critical.css §19 container-query target);
       %(n)d reps, %(n_pages)d of them linked to a profile page. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <!-- include-separator draws the DS's red vertical accent above the
           headline (and adds the top padding it needs). Boolean attribute --
           presence enables it, so it takes no value. -->
      <umd-element-section-intro include-separator class="umd-layout-vertical-landing-child">
        <h2 slot="headline">%(grid_headline)s</h2>
      </umd-element-section-intro>
      <div class="umd-layout-grid-border-four">

%(cards)s

      </div>
    </div>
  </section>

  <!-- 6. JOIN THE MAILING LIST — banner promo -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <umd-element-banner-promo>
        <p slot="eyebrow">%(promo_eyebrow)s</p>
        <h2 slot="headline">%(promo_headline)s</h2>
        <p slot="text">%(promo_text)s</p>
        <div slot="actions" class="banner-promo-actions">
          <umd-element-call-to-action data-display="primary">
            <a href="%(promo_href)s">%(promo_cta)s</a>
          </umd-element-call-to-action>
        </div>
      </umd-element-banner-promo>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right (pin lives in shared/chrome.css) -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

%(footer)s

%(chrome_scripts)s

%(promo_script)s

%(person_link_script)s

  <!-- Canonical grid-entry animations (page-builder/CLAUDE.md: never inline). -->
  <script src="%(root)spage-builder/scripts/grid-animations.js"></script>

</body>
</html>
''' % dict(
        head=head_for('%s — Undergraduate Admissions | University of Maryland' % page['title']),
        css=PAGE_CSS,
        head_tail=HEAD_TAIL_OPEN,
        chrome_css=_chrome.block('chrome-css', out),
        gate=_chrome.block('gate', out),
        header=_chrome.block('header', out),
        footer=_chrome.block('footer', out),
        chrome_scripts=_chrome.block('chrome-scripts', out),
        promo_script=BANNER_PROMO_SCRIPT,
        person_link_script=PERSON_LINK_SCRIPT,
        hero_img=e(hero['image']), hero_alt=e(hero['alt']),
        hero_headline=hero['headline'], hero_text=hero['text'],
        intro_lead=intro['lead'], intro_paras=intro_paras,
        grid_headline=grid['headline'],
        promo_eyebrow=promo['eyebrow'], promo_headline=promo['headline'],
        promo_text=promo['text'], promo_href=e(promo['ctaHref']),
        promo_cta=promo['ctaLabel'],
        cards=cards_html, n=len(people),
        n_pages=sum(1 for p in people if p['page']),
        root=_chrome.ROOT_TOKEN,
    )


# umd-element-person renders <a slot="name"> and <p slot="name"> IDENTICALLY --
# same .person-name.umd-sans-larger class, same black, same 700 weight, no
# underline (measured in cdn.js@1.18.12). That is right for the finished page,
# where every rep has a profile and the whole grid is uniform, but it leaves a
# linked name with no hover affordance at all. The name is CLONED into the
# shadow root rather than slotted, so page CSS cannot reach it.
PERSON_LINK_SCRIPT = '''  <!-- Person-card link affordance — page-content-driven (OVERRIDES.md).
       umd-element-person styles a linked and an unlinked name the same; this
       gives the linked ones an underline on hover/focus so the card reads as
       actionable. Scoped to `a.person-name`, so it is inert on the cards whose
       rep has no profile page yet.

       Exposed as a re-runnable function, not a one-shot pass: the search page
       builds fresh cards on every filter, and those need the injection too. The
       per-element flag keeps repeat calls from stacking <style> nodes. -->
  <script>
    window.umdInjectPersonLinkCss = function () {
      document.querySelectorAll('umd-element-person').forEach(el => {
        if (!el.shadowRoot || el.dataset.personLinkCssDone) return;
        const style = document.createElement('style');
        style.textContent =
          'a.person-name{text-decoration:none}' +
          'a.person-name:hover,a.person-name:focus-visible' +
          '{text-decoration:underline;text-underline-offset:3px;' +
          'text-decoration-thickness:2px;color:var(--umd-color-red,#e21833)}';
        el.shadowRoot.appendChild(style);
        el.dataset.personLinkCssDone = '1';
      });
    };
    customElements.whenDefined('umd-element-person')
      .then(() => window.umdInjectPersonLinkCss());
  </script>'''


# The banner-promo injection is page-content-driven (OVERRIDES.md), so it ships
# with the page that has the element rather than with shared/.
BANNER_PROMO_SCRIPT = '''  <!-- Banner-promo shadow injection — page-content-driven (OVERRIDES.md).
       banner-promo reprojects slot="actions" into its shadow root under
       .banner-promo-actions with no gap when the actions stack. -->
  <script>
    customElements.whenDefined('umd-element-banner-promo').then(() => {
      document.querySelectorAll('umd-element-banner-promo').forEach(el => {
        const style = document.createElement('style');
        style.textContent = '.banner-promo-actions{display:flex!important;flex-direction:column!important;align-items:flex-end!important;gap:8px!important}';
        el.shadowRoot && el.shadowRoot.appendChild(style);
      });
    });
  </script>'''


# ---------------------------------------------------------------- search page
SEARCH_ICON = ('<svg aria-hidden="true" width="96" height="96" viewBox="0 0 96 96" '
               'fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" '
               'clip-rule="evenodd" d="M79.3401 42.2306C79.3401 54.1438 69.6826 63.8013 '
               '57.7694 63.8013C45.8562 63.8013 36.1987 54.1438 36.1987 42.2306C36.1987 '
               '30.3174 45.8562 20.6599 57.7694 20.6599C69.6826 20.6599 79.3401 30.3174 '
               '79.3401 42.2306ZM91 42.2306C91 60.5833 76.1222 75.4612 57.7694 '
               '75.4612C51.3447 75.4612 45.3458 73.6379 40.2619 70.4806L24.2216 '
               '86.5209H5L30.2245 60.8255C26.6351 55.5189 24.5388 49.1195 24.5388 '
               '42.2306C24.5388 23.8778 39.4167 9 57.7694 9C76.1222 9 91 23.8778 91 '
               '42.2306Z" /></svg>')

# Page size, matching the template's data-limit="8" on #umd-shell-person-gallery.
PAGE_SIZE = 8


def territory_options(people):
    """<optgroup>ed <option>s for every territory any rep covers.

    56 territories over 24 reps, and all but one are covered by exactly one
    person. A flat 56-item list is a lot to scroll, and the data already
    carries its own grouping: "Maryland - Kent County", "New York - Upstate".
    Splitting on " - " gives Maryland (25), New York (6), New Jersey (3),
    Virginia (3), Pennsylvania (2); the 17 entries with no prefix (states,
    International, the two D.C. school systems) fall into one trailing group.
    """
    groups, loose = {}, []
    for r in sorted({r for p in people for r in p['regions']}):
        head, sep, tail = r.partition(' - ')
        (groups.setdefault(head, []).append((tail, r)) if sep else loose.append(r))

    out = []
    for head in sorted(groups):
        # A lone "X - Y" is not worth a group of one; fold it back in.
        if len(groups[head]) == 1:
            loose.append(groups[head][0][1])
            continue
        out.append('            <optgroup label="%s">' % e(head))
        for label, full in groups[head]:
            out.append('              <option value="%s">%s</option>'
                       % (e(region_slug(full)), e(label)))
        out.append('            </optgroup>')
    if loose:
        out.append('            <optgroup label="States &amp; Regions">')
        for r in sorted(loose):
            out.append('              <option value="%s">%s</option>'
                       % (e(region_slug(r)), e(r)))
        out.append('            </optgroup>')
    return '\n'.join(out)


def render_search(doc):
    out = os.path.join(OUTDIR, 'search.html')
    page, people = doc['page'], doc['people']
    hero, intro, promo = page['hero'], page['intro'], page['promo']

    cards_html = '\n'.join(person_card(p, filterable=True) for p in people)
    intro_paras = '\n'.join('        <p>%s</p>' % t for t in intro['paragraphs'])

    return '''%(head)s
%(head_tail)s

  <!-- Page CSS gets its OWN style block, after cdn.js -- it is deliberately
       NOT appended to the inlined critical.css above. tools/inline-critical.py
       rewrites the FIRST style block in a file and leaves later ones alone, so
       page CSS sitting inside that block is (a) invisible to --check, which
       then reports the page as permanently stale, and (b) DELETED the moment
       the tool is run over pages/. Cascade order is unchanged: critical <
       page CSS < chrome CSS, exactly as when this sat at the tail of the
       critical block. (No literal style tag in this comment on purpose -- the
       repo's tooling finds these blocks by regex.) -->
  <style>%(css)s  </style>
%(chrome_css)s
%(gate)s
</head>
<body>

%(header)s

  <!-- 3. HERO — identical to index.html (same image, copy, and centred small
       variant). The two pages are the same directory in two presentations, so
       the hero deliberately does not differentiate them. -->
  <section class="umd-layout-vertical-landing">
    <umd-element-hero data-layout-height="small" data-layout-text="center">
      <img slot="image" src="%(hero_img)s" alt="%(hero_alt)s" />
      <h1 slot="headline">%(hero_headline)s</h1>
      <div slot="text"><p>%(hero_text)s</p></div>
    </umd-element-hero>
  </section>

  <!-- 4. FILTER — the CMS person-index template's form, rebuilt from the DS
       classes our bundles actually carry (see page CSS §26 for what had to be
       reproduced). Structure mirrors omc.umd.edu/people: a highlight panel
       holding a heading + reset on one row, then the term dropdown and the
       search bar in a two-up grid.

       No "Please select a valid option." error <p>. That exists on the CMS
       page because its dropdown is populated from a taxonomy that can go
       stale; ours is generated from the same JSON that renders the cards, so
       an invalid option cannot occur.

       The form is progressive enhancement: it POSTs nowhere and has no
       no-JS fallback endpoint, so it is hidden until the script confirms it
       can run. Without JS the full set of %(n)d reps renders below, which is
       the correct fallback for a directory. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <a href="#reps-results" class="umd-skip-content">
        <span class="sr-only">Skip search form</span><span>Skip to Content</span>
      </a>
      <form id="reps-filter" class="umd-layout-background-highlight-light umd-layout-grid-gap-stacked" hidden>
        <div class="umd-layout-grid-inline-stretch">
          <h2 class="umd-text-line-trailing-light"><span>Filter Representatives</span></h2>
          <button type="reset" id="reps-reset" class="umd-sans-smaller umd-animation-line-slide-graydark-red"
                  aria-label="Clear and reset search">
            <span aria-hidden="true">Clear filters</span>
          </button>
        </div>

        <div class="umd-layout-grid-gap-two">
          <div>
            <label for="reps-territory" class="sr-only">Filter by Territory</label>
            <div class="umd-field-select-wrapper">
              <select id="reps-territory" name="territory">
                <option value="">All Territories</option>
%(options)s
              </select>
            </div>
          </div>

          <div class="reps-search-row">
            <label for="reps-search" class="sr-only">Search</label>
            <input type="text" id="reps-search" name="search" class="umd-field-input"
                   placeholder="Search by name or title" autocomplete="off" />
            <button type="submit" class="reps-search-submit" aria-label="Submit search">%(icon)s</button>
          </div>
        </div>
      </form>

      <p class="reps-results-status" id="reps-status" role="status" aria-live="polite"></p>
    </div>
  </section>

  <!-- 5. RESULTS — the same umd-layout-grid-border-four and the same
       umd-element-person cards as index.html, server-rendered in full. The
       script takes a copy of these %(n)d nodes on init and thereafter owns the
       grid's children, so a filtered view is a real re-render rather than
       hidden cells: critical.css §19's partial-row rules key off :nth-child,
       and display:none-ing a card leaves it in the count and paints the
       borders wrong. -->
  <div class="umd-layout-space-horizontal-larger reps-results-wrap">
    <section id="reps-results" class="umd-layout-grid-border-four">

%(cards)s

    </section>
    <p class="reps-empty" id="reps-empty" hidden>No representatives match those filters.</p>
  </div>

  <section class="umd-layout-vertical-landing reps-load-more" id="reps-load-more" hidden>
    <button type="button" class="umd-action-outline" id="reps-load-more-button">Load More</button>
  </section>

  <!-- 6. WE'RE HERE FOR YOU — the index's intro copy, moved to the FOOT of the
       page. The CMS person-index template has no rich-text region above the
       filter, so on this page the copy cannot lead; below the results it still
       answers "how do I actually reach these people".

       No brand chevron here. On index.html that animation is positioned to
       overlap ~180px UP into the hero above it; at the bottom of the page it
       has nothing to bite into and would instead ride over the results grid. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black" style="text-transform:uppercase;">%(intro_lead)s</p>
      <div class="umd-text-rich-advanced">
%(intro_paras)s
      </div>
    </div>
  </section>

  <!-- 7. JOIN THE MAILING LIST — banner promo -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-larger">
      <umd-element-banner-promo>
        <p slot="eyebrow">%(promo_eyebrow)s</p>
        <h2 slot="headline">%(promo_headline)s</h2>
        <p slot="text">%(promo_text)s</p>
        <div slot="actions" class="banner-promo-actions">
          <umd-element-call-to-action data-display="primary">
            <a href="%(promo_href)s">%(promo_cta)s</a>
          </umd-element-call-to-action>
        </div>
      </umd-element-banner-promo>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right (pin lives in shared/chrome.css) -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

%(footer)s

%(chrome_scripts)s

%(promo_script)s

%(person_link_script)s

%(filter_script)s

  <!-- NO grid-animations.js on this page. The canonical script animates grid
       children in on first reveal; here the grid's children are replaced on
       every keystroke, so each filter would re-trigger the entry animation and
       the results would flicker. index.html keeps it. -->

</body>
</html>
''' % dict(
        head=head_for('Search Admission Representatives — Undergraduate Admissions '
                      '| University of Maryland'),
        css=PAGE_CSS,
        head_tail=HEAD_TAIL_OPEN,
        chrome_css=_chrome.block('chrome-css', out),
        gate=_chrome.block('gate', out),
        header=_chrome.block('header', out),
        footer=_chrome.block('footer', out),
        chrome_scripts=_chrome.block('chrome-scripts', out),
        promo_script=BANNER_PROMO_SCRIPT,
        person_link_script=PERSON_LINK_SCRIPT,
        filter_script=FILTER_SCRIPT % {'page_size': PAGE_SIZE},
        hero_img=e(hero['image']), hero_alt=e(hero['alt']),
        hero_headline=hero['headline'], hero_text=hero['text'],
        options=territory_options(people),
        icon=SEARCH_ICON,
        cards=cards_html, n=len(people),
        intro_lead=intro['lead'], intro_paras=intro_paras,
        promo_eyebrow=promo['eyebrow'], promo_headline=promo['headline'],
        promo_text=promo['text'], promo_href=e(promo['ctaHref']),
        promo_cta=promo['ctaLabel'],
    )


# Client-side filtering over the server-rendered cards. Same shape as the UMD
# experts page's controller (briefs/experts-filter.md): one in-memory list, AND
# across dimensions, a plain substring test for the text, and Load More as
# client-side paging of the already-filtered list -- no network at any point.
#
# It renders from CAPTURED MARKUP rather than by moving the original nodes
# around. umd-element-person re-renders ADDITIVELY when it reconnects: taking a
# card out of the DOM and putting it back leaves a second .person-block in its
# shadow root, so the card draws the same person twice and doubles in height
# (389px -> 694px, measured). replaceChildren() re-inserts the cards that were
# already on screen, so one Load More click did that to every visible card --
# the grid appeared to repeat its rows.
#
# Hiding non-matches with display:none instead is NOT the fix. layout.min.css
# draws the grid's top border with
#   :is(.umd-layout-grid-border-four):not(:has(>:last-child:nth-child(4))) > *:nth-child(1..4)
# which counts DOM position, not what is visible -- filter the first four cards
# out and the top border stays on the hidden cells while the visible first row
# has none.
#
# So: never reconnect a card. Every render builds new elements from the pristine
# markup captured at init, and Load More only ever APPENDS the delta, leaving
# the cards already on screen untouched.
FILTER_SCRIPT = '''  <!-- Filter controller — page-content-driven, this page only. -->
  <script>
  (function () {
    var PAGE = %(page_size)d;
    var form = document.getElementById('reps-filter');
    var grid = document.getElementById('reps-results');
    var status = document.getElementById('reps-status');
    var empty = document.getElementById('reps-empty');
    var more = document.getElementById('reps-load-more');
    var moreBtn = document.getElementById('reps-load-more-button');
    var termSel = document.getElementById('reps-territory');
    var searchIn = document.getElementById('reps-search');
    if (!form || !grid) return;

    // Capture each card's markup once, up front. outerHTML on an upgraded
    // umd-element-person serialises its LIGHT DOM only -- the shadow root is
    // not included -- so this round-trips the original markup, data-* and all.
    var ALL = Array.prototype.map.call(grid.children, function (el) {
      return {
        html: el.outerHTML,
        regions: (el.getAttribute('data-regions') || '').split('|'),
        search: el.getAttribute('data-search') || ''
      };
    });
    var shown = 0;
    var matches = ALL;

    // The form does nothing without this script, so it ships hidden and is
    // revealed only now.
    form.hidden = false;

    function filtered() {
      var term = termSel.value;
      var q = searchIn.value.trim().toLowerCase();
      return ALL.filter(function (rec) {
        if (term && rec.regions.indexOf(term) === -1) return false;
        if (q && rec.search.indexOf(q) === -1) return false;
        return true;
      });
    }

    // Build fresh elements for matches[from..to). They upgrade -- and therefore
    // render -- exactly once, when they are appended here.
    function append(from, to) {
      if (to <= from) return;
      var holder = document.createElement('div');
      holder.innerHTML = matches.slice(from, to).map(function (r) { return r.html; }).join('');
      while (holder.firstElementChild) grid.appendChild(holder.firstElementChild);
      // Freshly built cards need the hover injection too.
      if (window.umdInjectPersonLinkCss) window.umdInjectPersonLinkCss();
    }

    function paint(target, rebuild) {
      if (rebuild) { grid.replaceChildren(); shown = 0; }
      append(shown, target);
      shown = target;
      var total = matches.length;
      empty.hidden = total !== 0;
      grid.hidden = total === 0;
      more.hidden = shown >= total;
      status.textContent = total
        ? 'Showing ' + shown + ' of ' + total + ' representative' + (total === 1 ? '' : 's')
        : 'No representatives match those filters.';
    }

    function apply() {
      matches = filtered();
      paint(Math.min(PAGE, matches.length), true);
    }

    // Debounced so a fast typist does not force a rebuild per keystroke.
    var t;
    searchIn.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(apply, 200);
    });
    termSel.addEventListener('change', apply);
    form.addEventListener('submit', function (ev) { ev.preventDefault(); clearTimeout(t); apply(); });
    // Reset fires BEFORE the fields clear, so read them on the next tick.
    form.addEventListener('reset', function () { setTimeout(apply, 0); });
    // Grow only: the cards already on screen are correct and are left alone.
    moreBtn.addEventListener('click', function () {
      paint(Math.min(shown + PAGE, matches.length), false);
    });

    apply();
  })();
  </script>'''


# ---------------------------------------------------------------- bio page
def render_rep(doc, person):
    out = rep_path(person['slug'])

    # Bio section. Absent for the five reps whose CMS entry carries no
    # "Favorite Maryland Moment" -- the section disappears entirely rather than
    # rendering an empty heading.
    bio_html = ''
    if person['bio']:
        bio_html = '''
  <!-- 4. BIO — the source modal's "Favorite Maryland Moment". Narrow -small
       lock and the same rule + uppercase eyebrow lockup the interior pages use. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black" style="text-transform:uppercase;">%s</p>
      <div class="umd-text-rich-advanced">
        <p>%s</p>
      </div>
    </div>
  </section>
''' % (e(person['bioHeadline'] or 'Favorite Maryland Moment'), e(person['bio']))

    # Territory section. Also conditional: nine of the reps are office-wide
    # roles (director, scholarships, Shady Grove) with no geography attached.
    regions_html = ''
    if person['regions']:
        items = '\n'.join('          <li>%s</li>' % e(r) for r in person['regions'])
        regions_html = '''
  <!-- 5. TERRITORIES — the modal's region list. Columns fill on width
       (page CSS §26); a rep can cover one territory or nine. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <hr style="border:none;border-top:1px solid var(--umd-color-black);margin:0 0 24px 0;" />
      <p class="umd-sans-large mb-md text-black" style="text-transform:uppercase;">Territories</p>
      <ul class="rep-regions-list">
%s
      </ul>
    </div>
  </section>
''' % items

    return '''%(head)s
%(head_tail)s

  <!-- Page CSS gets its OWN style block, after cdn.js -- it is deliberately
       NOT appended to the inlined critical.css above. tools/inline-critical.py
       rewrites the FIRST style block in a file and leaves later ones alone, so
       page CSS sitting inside that block is (a) invisible to --check, which
       then reports the page as permanently stale, and (b) DELETED the moment
       the tool is run over pages/. Cascade order is unchanged: critical <
       page CSS < chrome CSS, exactly as when this sat at the tail of the
       critical block. (No literal style tag in this comment on purpose -- the
       repo's tooling finds these blocks by regex.) -->
  <style>%(css)s  </style>
%(chrome_css)s
%(gate)s
</head>
<body>

%(header)s

  <!-- 3. PERSON HERO — the DS's own profile-page hero. It owns the breadcrumb
       (registry-person.json: "do not also render a standalone
       umd-element-breadcrumb"), so this page has none of its own. -->
  <section class="umd-layout-vertical-landing">
    <umd-element-person-hero>
      <!-- The slot takes a umd-element-breadcrumb, NOT a bare <nav>: the
           component validates its slots and logs 'Slot "breadcrumb" contains
           invalid elements. Allowed: umd-element-breadcrumb' for anything
           else. registry-person.json's "do not also render a standalone
           umd-element-breadcrumb" means put it HERE rather than separately on
           the page -- not that the slot takes hand-rolled markup.

           The paths markup is RULES.md §"Breadcrumb", not the <ol>/<li>
           shown in registry-navigation.json. The registry example is wrong:
           the DS draws its separators with `.breadcrumb-path + *::before`, so
           the paths have to be ADJACENT SIBLINGS. Wrapping each in its own
           <li> gives every anchor a container to itself, the selector never
           matches, and the trail renders as one run-on string
           ("HomeAdmission RepresentativesAbigail Trice"). Flat <a> siblings
           plus a <p> for the current page -- each with its own <span>, which
           is what the hover underline animates. -->
      <umd-element-breadcrumb slot="breadcrumb">
        <div slot="paths">
          <a href="%(root)spages/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
          <a href="index.html"><span>Admission Representatives</span></a>
          <p aria-label="Current Page"><span>%(name)s</span></p>
        </div>
      </umd-element-breadcrumb>
      <img slot="image" src="%(image)s" alt="%(alt)s" />
      <h1 slot="name">%(name)s</h1>
      <p slot="job-title">%(position)s</p>
      <!-- NO slot="association". registry-person.json lists it, but
           umd-element-person-hero silently drops it: the component rebuilds
           its text lockup from the light DOM and only reads name + job-title
           (verified against the rendered shadow tree in cdn.js@1.18.12). The
           unit name would have been dead markup, so it is not emitted. -->
      <!-- The email slot IS the contact action -- no slot="actions" CTA.
           Both pointed at the same mailto, so the button restated the link
           directly above it. The visible text is "Email <first name>" rather
           than the address; the aria-label still names the actual inbox, so
           the destination is not lost for a screen reader. -->
      <a slot="email" href="%(mailto)s" aria-label="Email %(first)s at %(email)s"><span>Email %(first)s</span></a>
    </umd-element-person-hero>
  </section>
%(bio)s%(regions)s
  <!-- 6. BACK TO THE DIRECTORY — the only navigation off this page, and the
       thing the modal used to give for free by closing. -->
  <section class="umd-layout-vertical-landing">
    <div class="umd-layout-space-horizontal-small">
      <umd-element-call-to-action data-display="secondary">
        <a href="index.html">All Admission Representatives</a>
      </umd-element-call-to-action>
    </div>
  </section>

  <!-- SCROLL TO TOP — fixed 24px from viewport bottom-right (pin lives in shared/chrome.css) -->
  <umd-element-scroll-top data-layout-fixed="true"></umd-element-scroll-top>

%(footer)s

%(chrome_scripts)s

</body>
</html>
''' % dict(
        head=head_for('%s — Undergraduate Admissions | University of Maryland' % person['name']),
        css=PAGE_CSS,
        head_tail=HEAD_TAIL_OPEN,
        chrome_css=_chrome.block('chrome-css', out),
        gate=_chrome.block('gate', out),
        header=_chrome.block('header', out),
        footer=_chrome.block('footer', out),
        chrome_scripts=_chrome.block('chrome-scripts', out),
        name=e(person['name']), position=e(person['position']),
        image=e(person['image']), alt=e(person['alt']),
        mailto=mailto(person), email=CONTACT_EMAIL,
        first=e(person['name'].split()[0]),
        bio=bio_html, regions=regions_html,
        root=_chrome.ROOT_TOKEN,
    )


# ---------------------------------------------------------------- main
def write(path, text):
    # Image and cross-section paths in the data file are repo-root-relative
    # behind {{ROOT}}, like the chrome's; resolve them for this page's depth.
    text = text.replace(_chrome.ROOT_TOKEN, '../' * DEPTH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
    print('wrote', os.path.relpath(path, REPO), len(text.split('\n')), 'lines')


def main():
    doc = json.load(open(DATA, encoding='utf-8'))
    by_slug = {p['slug']: p for p in doc['people']}

    if sys.argv[1:]:
        for slug in sys.argv[1:]:
            if slug not in by_slug:
                raise SystemExit('unknown rep slug "%s" -- valid: %s'
                                 % (slug, ', '.join(sorted(by_slug))))
            write(rep_path(slug), render_rep(doc, by_slug[slug]))
        return

    write(landing_path(), render_landing(doc))
    write(os.path.join(OUTDIR, 'search.html'), render_search(doc))
    for p in doc['people']:
        if p['page']:
            write(rep_path(p['slug']), render_rep(doc, p))


if __name__ == '__main__':
    main()
