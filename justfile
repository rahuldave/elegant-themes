default:
    @just --list

build:
    uv run python scripts/build.py

check:
    node --check src/gallery.js
    uv run python scripts/check.py

serve: build
    uv run python -m http.server 8432 --directory example/_site --bind 127.0.0.1

publish: build check
    uv run smalldocs publish gh-pages example --no-render
