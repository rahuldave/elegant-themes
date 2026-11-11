# Elegant themes

Elegant themes compares 38 designs for SmallDocs, a Python website generator. The designs have 51 variants across color modes. A variant is one design in one available light or dark mode. The collection includes nine current themes that we maintain, three original custom snapshots, all 25 unchanged Bootswatch themes, and native Bootstrap. Eight original/current pairs remain in the gallery. All specimens use identical content.

Bootstrap supplies the base website components. Bootswatch supplies alternative styles for those components.

Start with [the live site](https://rahuldave.com/elegant-themes/) or its [before/after view](https://rahuldave.com/elegant-themes/?group=comparisons). [Install or update a theme](https://rahuldave.com/elegant-themes/using-themes.html), replace an older Atelier copy, or restore it. The [theme handbook](https://rahuldave.com/elegant-themes/theme-guide.html) documents each theme, its configuration, and optional recipes for title labels. Current custom themes omit fixed title labels. The original snapshots and pinned `v0.2.0` release retain them.

The four HTML reports are the typography assessment, visual design assessment, typography principles, and UI design principles. They were refreshed on 10 November 2026, with a three-theme color repair and focused recapture on 11 November. The typography and visual design rubrics are unchanged and assess all nine current themes we maintain in both modes. The October reports and evidence are preserved at [history/2026-10-16](https://rahuldave.com/elegant-themes/history/2026-10-16/).

The supplementary Foundations specimen compares intended foreground/background color pairs with actual component behavior. In the gallery's Specimen menu, choose States & foundations. The sources are [Butterick’s Practical Typography](https://practicaltypography.com/) and [Refactoring UI](https://refactoringui.com/). Scores are this review's interpretation, not endorsements. No proprietary book PDF, extracts, or illustrations are included.

## Build and publish

To build and check the site, install uv, Python 3.11 or later, and Node.js. Run the commands below from this repository's root. The built site is written to `example/_site/`. The last command below publishes the built output to GitHub Pages.

```sh
uv sync
uv run python scripts/build.py
uv run python scripts/check.py
uv run smalldocs publish gh-pages example --no-render
```

`src/` holds the comparison interface. `vendor/themes/` contains fixed compiled themes, including the preserved originals, and `theme-sources.json` records their revisions. Installable refined themes and editable sources live in their independent `rahuldave/smalldocs-*` repositories, linked on every card. Bootswatch originals remain bundled in SmallDocs.

`reports/` contains the four reports and the measurement data and browser screenshots selected for public release. The build copies these static files directly into the site. Generated output lives on `gh-pages`, and authored source lives on `main`.

## November findings and reproducibility

The current themes use 18 to 20px prose, 16px code and interface text, and prose leading of 1.60. Leading is the distance between lines relative to text size. Each theme's foundation file names its design settings, including colors for specific uses in both light and dark modes. The fixed Butterick rubric deducts eight points for leading. The report records that tradeoff with the original scoring bands.

The 11 November follow-up repairs the dark secondary action in Pulse Reading, the selected navigation in Litera Reading, and weak light syntax colors in Darkly Reading. Typography, spacing, and shape are unchanged, including 1.60 prose leading. Before/after evidence remains at `history/2026-11-10/`.

`scripts/import_themes.py` imports clean committed extensions from sibling source repositories and records their exact revisions and hashes of foundation files. It does not modify the theme repositories. The browser capture set contains 72 prose/code observations, 18 desktop control observations, and 36 supplementary observations of design settings.

The 11 November repair replaces 42 of the 126 browser captures/screenshots. For three themes in both modes, it replaces 24 prose/code observations, 6 control observations, and 12 observations of design settings. Six of the themes we maintain did not change. They retain their 10 November observations. The review also retains unchanged baseline observations.

`reports/typography-audit/capture.html` measures the specimens in a real browser. CUA, the browser automation used for this review, controls the browser after you serve the built site. The capture page waits for fonts and declared color transitions. These scripts do not start a headless browser.

`just review` validates the saved observations, fixture and source hashes, screenshot inventory, renderer version, and baseline scores before recalculating the reports. It preserves capture dates and stops if the saved evidence has changed. First, record a fresh browser capture set and its screenshot dates and hashes. Then use `uv run python scripts/finalize_review.py --import-captures --review-date YYYY-MM-DD --fresh-themes THEME ...` to associate that set with the current source inputs. Recalculation uses the saved evidence and does not take new browser measurements.

`scripts/check.py` checks all 190 specimen pages and excludes private AC215 and proprietary PDFs.

The documentation covers all nine paired formats for SmallDocs and Quarto, another publishing tool. It records fixed source commits, manifest versions and Git tags, optional title labels, and named design roles. It also covers an optional local preset for tighter line spacing. Reading profiles set document sizes. Applications can use separate presentation profiles without enlarging document navigation. Elegant themes is a [smallish.dev](https://smallish.dev/) project.
