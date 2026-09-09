# Shared path remappings for design-project wrapper commands

Every slash command in this repo wraps a recipe from `page-builder/.claude/commands/`. The source recipes assume the page-builder repo is the working directory. Apply these remappings before executing the source recipe.

This repo is one instance of a design-project repo (e.g. admissions, academics, engineering). The slash commands are project-agnostic — read `CLAUDE.md` for the specific project's identity, reference page, logo paths, and output folder names.

## Reads — page-builder resources

| In source recipe | Read here |
|---|---|
| `TEMPLATE.html` | `page-builder/TEMPLATE.html` |
| `RULES.md` | `page-builder/RULES.md` |
| `LAYOUT-PATTERNS.md` | `page-builder/LAYOUT-PATTERNS.md` |
| `REQUIRED-CSS.md` | `page-builder/REQUIRED-CSS.md` |
| `registry/...` | `page-builder/registry/...` |
| `styles/critical.css` | `page-builder/styles/critical.css` |
| `images/images-index.json` | `page-builder/images/images-index.json` |
| `OVERRIDES.md` (generic shadow injections) | `page-builder/OVERRIDES.md` — also read this repo's local `OVERRIDES.md`; the local one wins on conflict |

## Writes — current design-project repo

| In source recipe | Write here |
|---|---|
| `examples/{slug}.html` (landing) | `pages/{slug}.html` |
| `test/{slug}.html` (sample) | `pages/{slug}.html` |
| Hardcoded `/Users/.../design-system-page-builder/examples/{slug}.html` | `pages/{slug}.html` |
| OVERRIDES harvest step | Update this repo's `OVERRIDES.md`, NOT the submodule's |

The page-builder is a submodule — never write inside `page-builder/` from this repo.

## Image refs in generated HTML

| Asset type | Path in generated HTML |
|---|---|
| Shared library: `large/`, `small/`, `medium/` (campus, people, events, default) | `../page-builder/images/large/...`, `../page-builder/images/small/...`, `../page-builder/images/medium/...` |
| Shared icons | `../page-builder/images/icons/...` |
| Project logos | See `CLAUDE.md` for this project's header logo, footer logo, and onerror fallback paths (typically `../images/logos/...`) |
| Page-specific photography | `../images/{page-slug}/...` (create the folder if needed) |

## Header & footer chrome

Every page within this design project renders the same chrome. Copy it verbatim from this project's **reference page**, which is named in `CLAUDE.md` under "Shared chrome and reference pages."

If `CLAUDE.md` declares a reference page (e.g. `pages/academics.html`), copy from that file:

- The full header stack — typically `umd-element-navigation-utility` + `umd-element-navigation-header` (with this project's logo and nav items)
- The footer block — typically `umd-element-footer data-display="visual"` (with this project's footer logo and image)
- End-of-body shadow-injection scripts (e.g. pathway aspect ratio, banner-promo gap, nav-header logo width)

Use the reference page's exact logo paths, nav item set, and footer image — do not substitute or reorder.

If no reference page exists yet (i.e. this is the first page in a fresh design-project repo), the page you're about to build **becomes** the reference. Establish the chrome intentionally and update `CLAUDE.md` to record header/nav/logo/footer choices for subsequent pages.

Do not invent new chrome. The shared chrome lives inline in each page until it is extracted to `shared/` partials in a future task.
