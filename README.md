# Elegant themes

A public comparison of 38 SmallDocs designs, including eight original/refined pairs, all 25 unchanged Bootswatch themes, Tufte and native Bootstrap. Start with [the live site](https://rahuldave.com/elegant-themes/) or its [before/after view](https://rahuldave.com/elegant-themes/?group=comparisons). All specimens use identical content. [Install or update a theme](https://rahuldave.com/elegant-themes/using-themes.html), including how to replace an older Atelier copy or restore it.

The [theme handbook](https://rahuldave.com/elegant-themes/theme-guide.html) documents each theme, configuration, and optional title label recipes. Current custom themes omit fixed title labels; the original snapshots and pinned `v0.2.0` release retain them.

Four linked HTML reports explain the fixed typography and visual design rubrics, show measurements, and provide original illustrated guides. The sources are [Butterick’s Practical Typography](https://practicaltypography.com/) and [Refactoring UI](https://refactoringui.com/). Scores are this review’s interpretation, not endorsements. No proprietary book PDF, extracts, or illustrations are included.

## Build

```sh
uv sync
uv run python scripts/build.py
uv run python scripts/check.py
uv run smalldocs publish gh-pages example --no-render
```

`src/` holds the comparison interface, `vendor/themes/` contains pinned compiled themes including the preserved originals, and `theme-sources.json` records their revisions. Installable refined themes and editable sources live in their independent `rahuldave/smalldocs-*` repositories, linked on every card. Bootswatch originals remain bundled in SmallDocs.

`reports/` contains the four reports and a safe, explicit selection of our measurement data and browser screenshots. The build copies these static files directly into the site. Generated output lives on `gh-pages`; authored source lives on `main`.
