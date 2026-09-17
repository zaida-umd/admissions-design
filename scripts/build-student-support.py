#!/usr/bin/env python3
"""Build the Student Support & Safety interior page.

Source copy: https://admissions.umd.edu/student/student-support
Component rationale: briefs/student-support.md

Run after editing this file or shared chrome:
    python3 scripts/build-student-support.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chrome


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "page-builder", "TEMPLATE.html")
OUT = os.path.join(REPO, "pages", "student-life", "student-support.html")
TITLE = (
    "Student Support & Safety — Undergraduate Admissions | "
    "University of Maryland"
)


template = open(TEMPLATE, encoding="utf-8").read()
template_lines = template.split("\n")
critical_end = next(
    index for index, line in enumerate(template_lines) if line.strip() == "</style>"
)
head = _chrome.with_robots("\n".join(template_lines[:critical_end]))
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, count=1)

pin = re.search(r"web-components-library@([\d.]+)/dist/cdn\.js", template)
assert pin, "TEMPLATE.html has no web-components-library cdn.js pin"

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
  <style>
    @media (min-width: 768px) {
      .student-support-media .student-support-safety-image {
        object-position: center 10%;
      }
    }

    .student-support-media {
      aspect-ratio: 4 / 3;
      overflow: hidden;
    }

    .student-support-media img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    /* The zig-zag pattern's third rule (LAYOUT-PATTERNS.md): the inlined
       critical CSS gives <hr> no border, so a bare <hr> inside a rich-text
       block needs one. Its 32px above/below spacing comes from the wrapper.

       The rule sits BELOW the heading, as the first child of the body
       rich-text block, and not above it as hr.umd-text-divider. The image
       column alternates by DOM order, so at 375px the <figure> stacks first
       on alternating blocks; a rule above the heading then lands between the
       photo and its own headline and the photo reads as the previous
       section's tail. Heading-then-rule keeps them grouped. */
    .umd-layout-grid-gap-two .umd-text-rich-advanced hr {
      border: 0; border-top: 1px solid #000; height: 0;
    }

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
        <p slot="eyebrow">Student Life</p>
        <img slot="image" src="../../images/shared/interior-hero-pattern.png" alt="" />
        <h1 slot="headline">Student Support &amp; Safety</h1>
      </umd-element-hero-minimal>
    </section>

    <div class="umd-layout-space-horizontal-normal umd-layout-space-vertical-interior">
      <umd-element-breadcrumb>
        <div slot="paths">
          <a href="../../pages/" aria-label="Return Home"><span aria-hidden="true">Home</span></a>
          <a href="../../pages/student-life/"><span>Student Life</span></a>
          <p aria-label="Current Page"><span>Student Support &amp; Safety</span></p>
        </div>
      </umd-element-breadcrumb>
    </div>

    <div class="umd-layout-space-horizontal-normal">
      <div id="umd-shell-content">
        <section class="umd-layout-space-vertical-interior">
          <p class="umd-sans-larger-bold text-black page-lede">Safety is the shared responsibility of each campus community member. We know that students thrive in a community they feel safe and supported in and continue to work toward a safer and more secure community.</p>
        </section>

        <section class="umd-layout-space-vertical-interior">
          <div class="umd-layout-grid-gap-two">
            <figure class="umd-layout-alignment-block-stacked student-support-media">
              <img src="../../images/student-life/student-support-academics.jpg" alt="Students sitting around a table in an engineering lab." />
            </figure>
            <div>
              <h2 class="umd-layout-space-vertical-headline-large text-black umd-sans-extralarge-bold">Academics</h2>
              <div class="umd-text-rich-advanced">
                <hr>
                <ul>
                  <li>Tutoring services</li>
                  <li><a href="https://careers.umd.edu/" target="_blank" rel="noopener noreferrer">Career Center</a> - Whether you’re looking to gain experience through an internship, fine tune your resume, practice your interviewing skills or evaluate a job offer, the Career Center has you covered. You’ll receive support at every stage of your career development and will be prepared to pursue a meaningful career path through high-quality services, resources and instruction.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section class="umd-layout-space-vertical-interior">
          <div class="umd-layout-grid-gap-two">
            <div>
              <h2 class="umd-layout-space-vertical-headline-large text-black umd-sans-extralarge-bold">Wellness</h2>
              <div class="umd-text-rich-advanced">
                <hr>
                <ul>
                  <li><a href="https://health.umd.edu/prospective-students" target="_blank" rel="noopener noreferrer">University Health Center</a> - Provides high-quality, cost-effective health care and wellness programs in order to promote the health of the university community and support academic success.</li>
                  <li><a href="https://www.counseling.umd.edu/aboutus/" target="_blank" rel="noopener noreferrer">Counseling Center</a> - Provides comprehensive support services that promote the personal, social and academic success of UMD students.</li>
                  <li><a href="https://recwell.umd.edu/" target="_blank" rel="noopener noreferrer">Recreation &amp; Wellness</a> - Creates a culture of wellness where all members of the university community thrive. Recreation is for everyone and there is something for everyone at RecWell.</li>
                </ul>
              </div>
            </div>
            <figure class="umd-layout-alignment-block-stacked student-support-media">
              <img src="../../images/student-life/student-support-wellness.jpg" alt="Front door to the health center." />
            </figure>
          </div>
        </section>

        <section class="umd-layout-space-vertical-interior">
          <div class="umd-layout-grid-gap-two">
            <figure class="umd-layout-alignment-block-stacked student-support-media">
              <img class="student-support-safety-image" src="../../images/student-life/safety@2x.jpg" alt="Safety" />
            </figure>
            <div>
              <h2 class="umd-layout-space-vertical-headline-large text-black umd-sans-extralarge-bold">Safety</h2>
              <div class="umd-text-rich-advanced">
                <hr>
                <p>Call University Police at 911 or (301) 405-3555. If you ever see a situation involving fighting between partners or groups, threatening actions or statements, screams, suspicious persons or behavior, weapons, etc., do not hesitate to call police immediately. Then, call your Service Desk or CA.</p>
                <ul>
                  <li>Blue Light Program</li>
                  <li>Police Escorts</li>
                  <li>Opt-in Safety Alerts</li>
                  <li>UID Only Accessibility</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section class="umd-layout-space-vertical-interior">
          <h2 class="umd-layout-space-vertical-interior-child text-black umd-sans-extralarge-bold">Transportation &amp; Parking</h2>
          <div class="umd-text-rich-advanced">
            <p>Whether you live on campus or off, the Department of Transportation Services makes it easy to get around. Shuttle-UM buses operate several campus-based routes and serve a six-mile radius beyond, taking students to Metro station, shops, restaurants and more than two dozen apartment communities. All you need to ride Shuttle-UM is your student ID. It’s also a snap to travel to Washington, D.C., Baltimore and local airports by using Metrorail and MARC trains.</p>
            <p>If you’re living off campus, permits for campus parking are available for purchase from the Department of Transportation Services.</p>
            <ul>
              <li><a href="https://transportation.umd.edu/shuttle-um" target="_blank" rel="noopener noreferrer">Shuttle-UM</a> - DOTS provides routes that circulate around campus, commuter routes to neighboring communities and Park &amp; Ride routes that can be tracked on the Transit app. Students can also use the NITE Ride evening service to get around campus when shuttle routes are not operating.</li>
              <li><a href="https://transportation.umd.edu/bikeumd-escooters" target="_blank" rel="noopener noreferrer">BikeUMD</a> - Students can bring their own bike to campus or rent one from the RecWell Bike Shop. Community members can also utilize the shared mobility system provided by VEO in partnership with the City of College Park and University Park.</li>
              <li><a href="https://transportation.umd.edu/sustainable-transportation/local-regional-transit" target="_blank" rel="noopener noreferrer">Local &amp; Regional Transit</a> - College Park connects to many local and regional transit options that make many destinations easily accessible. It’s also a snap to travel to Washington, D.C., Baltimore and local airports by using <a href="https://www.wmata.com/service/rail/" target="_blank" rel="noopener noreferrer">Metrorail</a> and <a href="https://mta.maryland.gov/marc-train" target="_blank" rel="noopener noreferrer">MARC</a> trains.</li>
              <li><a href="https://transportation.umd.edu/parking" target="_blank" rel="noopener noreferrer">Parking</a> - Flexible parking permit options are available for each individual working, living and learning situation. If you are going to have a car on campus, you will need a parking permit. Permits can be purchased on the Department of Transportation Services website.</li>
            </ul>
          </div>
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
for key in ("chrome-css", "gate", "header", "footer", "chrome-scripts"):
    body = body.replace(f"@@CHROME:{key}@@", _chrome.block(key, OUT))

output = head + "\n" + body
assert "@@" not in output, "unreplaced build token"
assert output.count("<umd-element-hero-minimal") == 1
assert 'src="../../images/shared/interior-hero-pattern.png" alt=""' in output
assert "<umd-element-nav-slider" not in output
assert output.count('<div class="umd-layout-grid-gap-two">') == 3
assert output.count('<figure class="umd-layout-alignment-block-stacked student-support-media">') == 3
# The figure is a DIRECT grid child — never wrapped in a rich-text div.
assert '<div class="umd-text-rich-advanced">\n              <figure' not in output
assert "aspect-ratio: 4 / 3" in output
assert output.count('<div>') == 3
assert output.count('<h2 class="umd-layout-space-vertical-headline-large text-black umd-sans-extralarge-bold">') == 3
# The rule is the FIRST CHILD of the body rich-text block, below the heading —
# the shared zig-zag treatment (LAYOUT-PATTERNS.md canonical). A rule above the
# heading breaks the figure-first mobile stack; see the CSS comment.
assert output.count('</h2>\n              <div class="umd-text-rich-advanced">\n                <hr>') == 3
assert 'student-support-title-rule' not in output
assert 'student-support-copy' not in output
assert output.count("umd-element-banner-promo") >= 1
assert "Let's stay in touch! <a href=\"https://apply.umd.edu/register/request-info\"" in output
assert output.count('href="https://apply.umd.edu/register/request-info"') == 2
assert '>Join the List</a>' in output
assert '>Join the Mailing List</a> or <a href="https://admissions.umd.edu/connect">Connect</a>!' in output
banner_start = output.index("<umd-element-banner-promo>")
shell_start = output.index('<div id="umd-shell-content"')
shell_end = output.index("</div>\n    </div>\n  </main>", shell_start)
assert shell_start < banner_start < shell_end
assert '<div id="umd-shell-content">' in output
for heading in ("Academics", "Wellness", "Safety", "Transportation &amp; Parking"):
    assert f">{heading}</h2>" in output
for image in (
    "student-support-academics.jpg",
    "student-support-wellness.jpg",
    "safety@2x.jpg",
):
    assert image in output
assert '../../pages/student-life/student-support.html" data-selected' in output
assert "https://admissions.umd.edu/student/student-support" not in output
# The page lede is a PARAGRAPH, not a heading. umd-sans-large gives it 18px/700
# in place; wrapping a multi-sentence lede in <h2> puts a paragraph in the
# document outline and makes screen-reader heading navigation announce the whole
# thing. Matches tuition/frederick-douglass-scholarship.html.
assert '<p class="umd-sans-larger-bold text-black page-lede">' in output
# The lede must sit OUTSIDE .umd-text-rich-advanced or its size class is inert.
assert 'umd-sans-large text-black' not in output
assert '<div class="umd-text-rich-advanced">\n          ' + '<p class="umd-sans-larger-bold text-black page-lede">' not in output
assert '<h2 class="umd-sans-large' not in output
assert '<h2 class="umd-sans-larger-bold text-black page-lede"' not in output
assert '<html lang="en">' in output
assert (
    f"web-components-library@{pin.group(1)}/dist/cdn.js" in output
), "generated component CDN URL is missing its version separator"

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    handle.write(output)

print(os.path.relpath(OUT, REPO))
