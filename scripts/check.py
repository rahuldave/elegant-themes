"""Check the generated inventory and local HTML/CSS assets before publication."""
import json
import hashlib
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
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'id' and value:
                self.ids.add(value)
            if name in ('src','href') and value:
                self.refs.append(value)


def main():
    data = (OUTPUT / 'site_libs/gallery/themes.js').read_text()
    themes = json.loads(data.removeprefix('window.THEME_LIBRARY = ').rstrip(';\n'))
    assert len(themes) == 38
    assert sum(2 if t['paired'] else 1 for t in themes) == 51
    assert {t['id'] for t in themes if t['group']=='custom'} == {'folio','atelier','nocturne','tufte','folio-original','atelier-original','nocturne-original'}
    assert len([t for t in themes if t['group']=='bootswatch']) == 25
    assert not any('ac215' in json.dumps(t).lower() for t in themes)
    assert len([t for t in themes if t['group']=='refined']) == 5
    assert len([t for t in themes if t.get('comparison')]) == 16
    handbook = Links()
    handbook.feed((OUTPUT / 'theme-guide.html').read_text())
    for theme in themes:
        guide = urlsplit(theme['guide'])
        assert (OUTPUT / guide.path).is_file(), theme['id']
        assert guide.fragment in handbook.ids, theme['id']
    for ref in handbook.refs:
        if ref.startswith('#'):
            assert ref[1:] in handbook.ids, ref
    assert not list(OUTPUT.rglob('*.pdf')), 'PDF must never enter the public output'
    for f in OUTPUT.rglob('*'):
        if f.suffix in ('.html','.json','.txt'):
            assert '/Users/rahul/Attic' not in f.read_text(), f
    audit = OUTPUT / 'typography-audit'
    for filename, count in [('measurements.json',204),('controls.json',51),('foundations-measurements.json',36)]:
        records = json.loads((audit / filename).read_text())
        keys = [(r['id'],r['mode'],r.get('page'),r.get('viewportName')) for r in records]
        assert len(records) == count and len(keys) == len(set(keys)), filename
    metadata = json.loads((audit / 'metadata.json').read_text())
    for path, digest in metadata['source_hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    for path, digest in metadata['evidence_hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    owned = {p['name'] for p in metadata['theme_sources'] if p.get('foundations_sha256')}
    assert len(owned) == 9
    assert all(t['paired'] for t in themes if t['id'] in owned)
    sources = json.loads((ROOT / 'theme-sources.json').read_text())
    assert sources == metadata['theme_sources']
    checks = json.loads((audit / 'foundations-checks.json').read_text())
    assert len(checks) == 18
    assert all(c['passes'] for r in checks for c in r['sourceChecks'])
    assert all(not b['profileErrors'] for r in checks for b in r['browser'])
    assert all(c['passes'] for r in checks for b in r['browser'] for c in b['renderedText']), 'A repaired foundation component still fails'
    shots = json.loads((audit / 'current-screenshots.json').read_text())
    assert len(shots) == 126
    for shot in shots:
        assert hashlib.sha256((audit / shot['file']).read_bytes()).hexdigest() == shot['sha256'], shot['file']
    previous = {t['id']: t for t in json.loads((audit / 'previous-scores.json').read_text())}
    for theme in json.loads((audit / 'scores.json').read_text()):
        if theme['id'] in owned:
            assert all(m['scores']['leading'] == 12 for m in theme['modes']), 'Owned prose leading must remain1.60'
            assert all(m['metrics']['syntaxContrast'] >= 4.5 for m in theme['modes']), theme['id']
        if theme['id'] not in owned:
            assert theme['typography'] == previous[theme['id']]['typography']
            assert theme['design']['total'] == previous[theme['id']]['design']['total']
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
        for page in ('index.html','typography.html','code.html','components.html','foundations.html'):
            assert (OUTPUT / 'previews' / theme['id'] / page).is_file()
    print('Verified 38 themes, 51 mode variants, 190 specimen pages, 126 dated screenshots, source hashes, frozen baseline scores, and local HTML/CSS assets. AC215 is excluded.')


if __name__ == '__main__':
    main()
