"""Shared site chrome — single source for every build script in this repo.

The chrome lives in shared/ as four files:

    shared/header.html          header stack (nav-utility +
                                navigation-header with the project nav items)
    shared/footer.html          visual footer
    shared/chrome.css           CSS companions the chrome markup depends on
    shared/chrome-scripts.html  chrome-driven shadow injections

`block(key)` wraps one of them in SHARED:<key>:START / :END markers.
scripts/build-chrome.py splices those blocks into hand-authored pages;
scripts/build-programs.py and scripts/build-colleges-schools.py emit the same
blocks when generating their pages. Because both paths render byte-identical
output, running any of the three converges — no ordering dependency.

Markup, CSS, and scripts are deliberately in ONE module. Splitting them is what
caused the original bug: a page took the chrome markup from a sibling and its
<head> from TEMPLATE.html, silently dropping the CSS companions.

Depth
    Pages live at more than one depth under pages/ (pages/admissions.html but
    also pages/academics/programs.html), so the chrome cannot hard-code `../`.
    Every path in shared/header.html and shared/footer.html is written
    repo-root-relative behind a `{{ROOT}}` token, and `payload`/`block` expand
    it to the right number of `../` for the page being written.

    `payload`/`block` therefore take the OUTPUT PAGE PATH, not a depth --
    `depth_of()` derives the depth from it, and the drawer needs the path
    itself (see below). `depth_of(path)` is still public for callers that
    resolve {{ROOT}} in their own body markup.

Contextual drawer
    The mobile drawer in shared/header.html is one shared blob, but it has to
    open on the section the reader is already in. The DS drives that from two
    attributes -- `data-active` on the children-slides group, `data-selected`
    on the current link -- so `_mark_current` stamps them per page, matching
    the page's own path against the drawer's hrefs while they are still
    {{ROOT}}-relative. The section is the page's directory under pages/, which
    is why the drawer's data-child-ref values ARE those directory names.

    Only the DRAWER:START/END region is stamped. The desktop nav deliberately
    carries no current-page state.
"""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(REPO, 'shared')

_START = '  <!-- SHARED:%s:START — generated from shared/%s; do not edit here -->'
_END = '  <!-- SHARED:%s:END -->'

# key -> (source file, wrapper applied to the file's contents)
_REGIONS = {
    'header':         ('header.html',         lambda s: s),
    'footer':         ('footer.html',          lambda s: s),
    'chrome-css':     ('chrome.css',           lambda s: '  <style>\n' + s + '\n  </style>'),
    'chrome-scripts': ('chrome-scripts.html',  lambda s: s),
    # The access gate is head content and self-contained (its own <style> and
    # <script>), so it is a region like any other. It MUST be a region rather
    # than a one-off splice: it was originally inserted by hand, and the next
    # run of build-programs.py / build-calendar.py silently dropped it -- both
    # pages sat ungated on main until this was wired up.
    'gate':           ('gate.html',            lambda s: s),
}


ROOT_TOKEN = '{{ROOT}}'


# TEMPLATE.html carries no robots meta -- it is the generic page-builder
# skeleton, and whether a page should be indexed is a project decision, not a
# design-system one. Every page in THIS repo is a prototype, so none of them
# should surface in search. The googlebot line is a belt-and-braces duplicate:
# a robots.txt is only read from the HOST root, and a GitHub Pages project
# site is served from /<repo>/, so a robots.txt in this repo would never be
# fetched -- the meta is the only mechanism that actually applies there.
# Hand-written pages carry the meta in their own head; the generated pages get
# it here so a rebuild cannot silently drop it.
ROBOTS_META = ('<meta name="robots" content="noindex, nofollow">\n'
               '  <meta name="googlebot" content="noindex, nofollow">')


def with_robots(head):
    """Insert the noindex meta right after the viewport meta. Idempotent."""
    if 'name="robots"' in head:
        return head
    m = re.search(r'^(\s*)<meta name="viewport"[^>]*>[^\n]*$', head, re.M)
    assert m, 'TEMPLATE head has no viewport meta to anchor the robots meta to'
    return head[:m.end()] + '\n' + m.group(1) + ROBOTS_META + head[m.end():]


def depth_of(path):
    """How many `../` a page at `path` needs to reach the repo root."""
    rel = os.path.relpath(os.path.abspath(path), REPO)
    return len(rel.replace(os.sep, '/').split('/')) - 1


def _resolve(text, depth):
    return text.replace(ROOT_TOKEN, '../' * depth)


_DRAWER_START = '<!-- DRAWER:START'
_DRAWER_END = '<!-- DRAWER:END -->'


def _rel(page):
    """`page` as a repo-relative, forward-slash path."""
    return os.path.relpath(os.path.abspath(page), REPO).replace(os.sep, '/')


def _self_hrefs(rel):
    """The {{ROOT}}-relative hrefs that mean "the page being written".

    A section landing page is linked as the directory (pages/tuition/), never
    as pages/tuition/index.html, so both spellings count as self.
    """
    hrefs = {ROOT_TOKEN + rel}
    if rel.endswith('/index.html'):
        hrefs.add(ROOT_TOKEN + rel[:-len('index.html')])
    return hrefs


def _mark_current(text, rel):
    """Stamp data-active / data-selected on the drawer for one page.

    Runs BEFORE {{ROOT}} is resolved, so hrefs are still comparable to `rel`
    without knowing the page's depth. A page in no section (pages/admissions.html)
    or in a section with no drawer group (pages/calendar/) simply matches
    nothing and the drawer opens at its top level -- which is correct.
    """
    start = text.find(_DRAWER_START)
    if start == -1:
        return text
    end = text.index(_DRAWER_END, start) + len(_DRAWER_END)
    drawer = text[start:end]

    parts = rel.split('/')
    section = parts[1] if parts[0] == 'pages' and len(parts) > 2 else None
    if section:
        drawer = drawer.replace(
            '<div data-parent-ref="%s">' % section,
            '<div data-parent-ref="%s" data-active>' % section)

    for href in _self_hrefs(rel):
        # The closing quote is part of the needle so that pages/academics/
        # does not also match pages/academics/programs.html.
        drawer = drawer.replace('<a href="%s"' % href,
                                '<a href="%s" data-selected' % href)

    return text[:start] + drawer + text[end:]


def _read(name):
    with open(os.path.join(SHARED, name), encoding='utf-8') as fh:
        return fh.read().rstrip('\n')


def source_file(key):
    return _REGIONS[key][0]


# Regions whose source file may legitimately be deleted. shared/gate.html says
# so in its own header ("DELETE THIS FILE on a project that should be public --
# the inliner skips a region whose source file is absent"), so removing it has
# to strip the block rather than crash every build script.
_OPTIONAL = {'gate'}


def present(key):
    """Does this region have a source file? Always true except for _OPTIONAL."""
    return os.path.exists(os.path.join(SHARED, source_file(key)))


def payload(key, page):
    """The region's content, without markers, rendered for the page at `page`.

    `page` is the output path (absolute or repo-relative): it fixes both the
    {{ROOT}} depth and, for the header, which drawer entries are current.
    """
    src, wrap = _REGIONS[key]
    text = wrap(_read(src))
    if key == 'header':
        text = _mark_current(text, _rel(page))
    return _resolve(text, depth_of(page))


def block(key, page):
    """The region's content wrapped in its SHARED:<key> markers.

    An _OPTIONAL region with no source file renders as the empty string, which
    is what strips it: build-chrome.py replaces the marked span with this, and
    the generators substitute it for their @@CHROME:<key>@@ slot.
    """
    if key in _OPTIONAL and not present(key):
        return ''
    return '\n'.join([_START % (key, source_file(key)), payload(key, page), _END % key])


def keys():
    return list(_REGIONS)
