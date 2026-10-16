"""Check the generated inventory and local HTML/CSS assets before publication."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "example/_site"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('src','href') and value:
                self.refs.append(value)


def main():
    data = (OUTPUT / 'site_libs/gallery/themes.js').read_text()
    themes = json.loads(data.removeprefix('window.THEME_LIBRARY = ').rstrip(';\n'))
    assert len(themes) == 38
    assert {t['id'] for t in themes if t['group']=='custom'} == {'folio','atelier','nocturne','tufte','folio-original','atelier-original','nocturne-original'}
    assert len([t for t in themes if t['group']=='bootswatch']) == 25
    assert not any('ac215' in json.dumps(t).lower() for t in themes)
    assert len([t for t in themes if t['group']=='refined']) == 5
    assert len([t for t in themes if t.get('comparison')]) == 16
    assert not list(OUTPUT.rglob('*.pdf')), 'PDF must never enter the public output'
    for f in OUTPUT.rglob('*'):
        if f.suffix in ('.html','.json','.txt'):
            assert '/Users/rahul/Attic' not in f.read_text(), f
    audit = OUTPUT / 'typography-audit'
    for filename, count in [('measurements.json',184),('controls.json',46)]:
        records = json.loads((audit / filename).read_text())
        keys = [(r['id'],r['mode'],r.get('page'),r.get('viewportName')) for r in records]
        assert len(records) == count and len(keys) == len(set(keys)), filename
    missing = []
    for file in OUTPUT.rglob('*'):
        if file.suffix not in ('.html','.css'):
            continue
        if file.suffix == '.html':
            parser = Links()
            parser.feed(file.read_text())
            refs = parser.refs
        else:
            refs = [m[1] for m in re.findall(r'url\(\s*([\'"]?)(.*?)\1\s*\)',file.read_text())]
        for ref in refs:
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
                continue
            target = file.parent / unquote(parsed.path)
            if not target.exists():
                missing.append(f'{file.relative_to(OUTPUT)}: {ref}')
    assert not missing, '\n'.join(missing)
    for theme in themes:
        for page in ('index.html','typography.html','code.html','components.html'):
            assert (OUTPUT / 'previews' / theme['id'] / page).is_file()
    print('Verified 38 themes, 152 specimen pages, and all local HTML/CSS assets. AC215 is excluded.')


if __name__ == '__main__':
    main()
