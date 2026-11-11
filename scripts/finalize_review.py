"""Validate saved November evidence and rebuild reports without changing provenance.

Use --import-captures only after explicitly recording a new browser capture set.
Screenshot dates and hashes must already be supplied by that capture process.
"""
import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'reports/typography-audit'
OWNED = {'folio', 'atelier', 'nocturne', 'tufte', 'zephyr-reading', 'simplex-reading', 'pulse-reading', 'litera-reading', 'darkly-reading'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-captures', action='store_true',
                        help='Explicitly accept newly recorded captures and their source inputs')
    parser.add_argument('--review-date', type=date.fromisoformat,
                        help='Date of an explicit new capture import, in America/New_York')
    parser.add_argument('--fresh-themes', nargs='+', choices=sorted(OWNED), default=sorted(OWNED),
                        help='Themes freshly captured in this batch; other recorded captures are retained')
    args = parser.parse_args()
    captures = json.loads((AUDIT / 'current-captures.json').read_text())
    foundations = json.loads((AUDIT / 'foundations-measurements.json').read_text())
    captures = [r for r in captures if r['page'] != 'foundations'] + foundations
    assert len(captures) == 126
    keys = [(r['id'], r['mode'], r['page'], r['viewportName']) for r in captures]
    assert len(set(keys)) == len(keys)
    assert {r['id'] for r in captures} == OWNED
    assert all(r['fontStatus'] == 'loaded' and r['settleMilliseconds'] >= 40 for r in captures)
    shots = json.loads((AUDIT / 'current-screenshots.json').read_text())
    assert len(shots) == 126 and len({s['file'] for s in shots}) == 126
    for shot in shots:
        file = AUDIT / shot['file']
        assert shot['sha256'] == hashlib.sha256(file.read_bytes()).hexdigest(), f'Screenshot changed: {file}'
        assert datetime.fromisoformat(shot['capturedAt']).tzinfo, f'Missing capture timezone: {file}'
    pins = json.loads((ROOT / 'theme-sources.json').read_text())
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['vendor/themes', 'vendor/bootswatch', 'vendor/bootstrap'] for p in sorted((ROOT / folder).rglob('*')) if p.is_file()}
    evidence_files = [AUDIT / name for name in ['current-captures.json', 'foundations-measurements.json', 'current-screenshots.json']]
    fixture_files = sorted((ROOT / 'example').glob('*.qmd')) + [ROOT / 'example/bridge.html', ROOT / 'example/_smalldocs.yml']
    evidence_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence_files + fixture_files}
    metadata_path = AUDIT / 'metadata.json'
    if args.import_captures:
        assert args.review_date, '--review-date is required for a new capture import'
        fresh = set(args.fresh_themes)
        recorded_today = {r['id'] for r in captures if datetime.fromisoformat(r['capturedAt']).astimezone(ZoneInfo('America/New_York')).date() == args.review_date}
        assert recorded_today == fresh, 'Fresh theme list must match capture dates'
        assert all(datetime.fromisoformat(r['capturedAt']).astimezone(ZoneInfo('America/New_York')).date() == args.review_date for r in captures if r['id'] in fresh), 'Each fresh theme needs its complete dated capture batch'
        baseline_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        if fresh != OWNED:
            def committed(path):
                return subprocess.check_output(['git', 'show', f'{baseline_commit}:{path}'], cwd=ROOT)
            prior = json.loads(committed('reports/typography-audit/metadata.json'))
            assert prior['smalldocs_version'] == importlib.metadata.version('smalldocs'), 'Renderer changed: recapture all owned themes'
            prior_fixtures = {p: digest for p, digest in prior['evidence_hashes'].items() if p.startswith('example/')}
            current_fixtures = {p: digest for p, digest in evidence_hashes.items() if p.startswith('example/')}
            assert prior_fixtures == current_fixtures, 'Shared fixture set changed: recapture all owned themes'
            retained = lambda r: r['id'] not in fresh
            for filename, current in [('current-captures.json', captures), ('current-screenshots.json', shots), ('foundations-measurements.json', foundations)]:
                path = f'reports/typography-audit/{filename}'
                old_bytes = committed(path)
                assert hashlib.sha256(old_bytes).hexdigest() == prior['evidence_hashes'][path], f'Committed baseline provenance mismatch: {filename}'
                assert list(filter(retained, json.loads(old_bytes))) == list(filter(retained, current)), f'Retained evidence changed: {filename}'
            def retained_sources(mapping):
                return {p: digest for p, digest in mapping.items() if not any(p.startswith(f'vendor/themes/{name}/') for name in fresh)}
            assert retained_sources(prior['source_hashes']) == retained_sources(hashes), 'Retained source assets changed: include affected themes in the recapture'
            assert [p for p in prior['theme_sources'] if p['name'] not in fresh] == [p for p in pins if p['name'] not in fresh], 'Retained source pins changed'
        fresh_type = sum(r['id'] in fresh and r['page'] in {'typography', 'code'} for r in captures)
        fresh_controls = sum(r['id'] in fresh and r['page'] == 'components' for r in captures)
        fresh_foundations = sum(r['id'] in fresh and r['page'] == 'foundations' for r in captures)
        metadata = dict(date=args.review_date.isoformat(), gallery='https://rahuldave.com/elegant-themes/', themes=38, mode_variants=51,
        prose_and_code_observations=204, desktop_components_observations=51, foundation_observations=36,
        fresh_themes=sorted(fresh), fresh_prose_and_code_observations=fresh_type,
        fresh_components_observations=fresh_controls, fresh_foundation_observations=fresh_foundations,
        retained_prose_and_code_observations=204-fresh_type, retained_components_observations=51-fresh_controls,
        capture_dates=sorted({datetime.fromisoformat(r['capturedAt']).astimezone(ZoneInfo('America/New_York')).date().isoformat() for r in captures}),
        desktop_css_viewport=[1280, 844], mobile_css_viewport=[390, 844], screenshot_crop_css_pixels=650,
        mobile_method='Actual 390px iframe; CSS reflow, not physical-device emulation',
        settling='Await document.fonts.ready, two animation frames, then declared CSS transition duration plus 40ms',
        smalldocs_version=importlib.metadata.version('smalldocs'), bootstrap_version='5.3.8',
        method='The nine-theme November10 capture is supplemented by an explicit dated repair batch. Unchanged owned theme captures and October stock/native/original baselines are retained with their dates. Fixed rubric weights, bands, and judgment anchors; lower paired mode total wins.',
        baseline_gallery_commit='69c7339c', baseline_archive='history/2026-10-16/',
        source_hashes=hashes, evidence_hashes=evidence_hashes, theme_sources=pins, previous_review_commit=baseline_commit, public_sources=['https://practicaltypography.com/', 'https://refactoringui.com/'],
        scope='SmallDocs reading specimens. Foundation intended pairs and rendered roles supplement scores. Quarto validation is upstream evidence; no fresh Quarto score, physical projection, device, or comprehensive accessibility certification.')
        # Full baseline identity is recorded in the preserved review-history file.
        metadata['baseline_gallery_commit'] = subprocess.check_output(['git', 'rev-parse', '69c7339'], cwd=ROOT, text=True).strip()
        metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')
        print('Imported explicitly recorded capture provenance; screenshot dates were preserved.')
    else:
        metadata = json.loads(metadata_path.read_text())
        assert metadata['source_hashes'] == hashes, 'Theme inputs changed: record fresh browser evidence before importing it'
        assert metadata['theme_sources'] == pins, 'Theme pins changed: record fresh browser evidence before importing it'
        assert metadata['evidence_hashes'] == evidence_hashes, 'Saved evidence or fixtures changed: recapture and explicitly import it'
        assert metadata['smalldocs_version'] == importlib.metadata.version('smalldocs'), 'Renderer version changed: recapture before recalculating'
    # Derived files are written only after validating all recorded evidence.
    for filename, pages in [('measurements.json', {'typography', 'code'}), ('controls.json', {'components'})]:
        old = [r for r in json.loads((AUDIT / filename).read_text()) if r['id'] not in OWNED]
        fresh = [r for r in captures if r['page'] in pages]
        (AUDIT / filename).write_text(json.dumps(old + fresh, indent=2) + '\n')
    for script in ['foundations.py', 'build_reports.py']:
        subprocess.run([sys.executable, str(AUDIT / script)], check=True, cwd=ROOT)
    current = {r['id']: r for r in json.loads((AUDIT / 'scores.json').read_text())}
    previous = json.loads((AUDIT / 'previous-scores.json').read_text())
    for row in previous:
        if row['id'] not in OWNED:
            assert (row['typography'], row['design']['total']) == (current[row['id']]['typography'], current[row['id']]['design']['total']), row['id']
    print('All 29 unchanged designs retain exactly their previous scores.')


if __name__ == '__main__':
    main()
