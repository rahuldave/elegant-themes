# Elegant themes

A public comparison of 38 SmallDocs designs and 51 mode variants: nine current owned themes, three original custom snapshots, all 25 unchanged Bootswatch themes, and native Bootstrap. Eight original/current pairs remain in the gallery. Start with [the live site](https://rahuldave.com/elegant-themes/) or its [before/after view](https://rahuldave.com/elegant-themes/?group=comparisons). All specimens use identical content. [Install or update a theme](https://rahuldave.com/elegant-themes/using-themes.html), including how to replace an older Atelier copy or restore it.

The [theme handbook](https://rahuldave.com/elegant-themes/theme-guide.html) documents each theme, configuration, and optional title label recipes. Current custom themes omit fixed title labels; the original snapshots and pinned `v0.2.0` release retain them.

The four HTML reports were refreshed on 10 November 2026. The same typography and visual design rubrics now assess all nine current owned themes in both modes. The October reports and evidence are preserved at [history/2026-10-16](https://rahuldave.com/elegant-themes/history/2026-10-16/). A new supplementary Foundations specimen distinguishes intended palette pairs from actual component behavior. The sources are [Butterick’s Practical Typography](https://practicaltypography.com/) and [Refactoring UI](https://refactoringui.com/). Scores are this review’s interpretation, not endorsements. No proprietary book PDF, extracts, or illustrations are included.

## Build

```sh
uv sync
uv run python scripts/build.py
uv run python scripts/check.py
uv run smalldocs publish gh-pages example --no-render
```

`src/` holds the comparison interface, `vendor/themes/` contains pinned compiled themes including the preserved originals, and `theme-sources.json` records their revisions. Installable refined themes and editable sources live in their independent `rahuldave/smalldocs-*` repositories, linked on every card. Bootswatch originals remain bundled in SmallDocs.

`reports/` contains the four reports and a safe, explicit selection of our measurement data and browser screenshots. The build copies these static files directly into the site. Generated output lives on `gh-pages`; authored source lives on `main`.

## November findings and reproducibility

The new themes use 1.60 prose leading, 18–20px prose, 16px code/interface roles,
and paired semantic foundations. The fixed Butterick rubric deducts eight leading
points; the report preserves that tradeoff instead of changing the bands.
Remaining flags are Pulse Reading's dark secondary action, Litera Reading's
selected navigation pill, and a Darkly Reading light syntax color. Source-pair
checks pass; those rendered components still need repair upstream.

`scripts/import_themes.py` imports clean committed extensions from sibling source
repositories and records their exact revisions and foundation hashes. It does not
modify the theme repositories. The fresh capture matrix contains 72 prose/code,
18 desktop control, and 36 supplementary foundation observations; unchanged
baseline observations are retained explicitly. `reports/typography-audit/capture.html`
is the real-browser measurement harness, driven through CUA after serving the
built site. It awaits fonts and declared color transitions. No headless browser
is launched by these scripts.

`just review` validates the saved observations, fixture and source hashes,
screenshot inventory, renderer version, and baseline scores before recalculating
the reports. It preserves capture dates and refuses changed evidence. After
explicitly recording a fresh browser capture set and its screenshot dates/hashes,
use `uv run python scripts/finalize_review.py --import-captures` to associate it
with the current source inputs. Recalculation never takes new browser measurements.
`scripts/check.py` checks
all 190 specimen pages and excludes private AC215 and proprietary PDFs.

The documentation covers all nine paired SmallDocs/Quarto formats, fixed source
commits, the difference between manifest versions and Git tags, optional title
labels, semantic roles, and a denser local reading preset. The reading and
presentation profiles stay separate. This is a [smallish.dev](https://smallish.dev/)
project.
