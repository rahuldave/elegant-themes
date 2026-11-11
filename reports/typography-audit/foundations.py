"""Supplementary foundation checks, separate from the two fixed 100-point rubrics."""
import hashlib
import json
from pathlib import Path

from analyze import contrast, contrast_range

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def hex_color(value):
    return [int(value[i:i + 2], 16) for i in (1, 3, 5)] + [1]


def pair(a, b):
    return contrast(hex_color(a), hex_color(b))


def main():
    measurements = json.loads((ROOT / 'foundations-measurements.json').read_text())
    pins = json.loads((REPO / 'theme-sources.json').read_text())
    results = []
    for pin in pins:
        path = REPO / 'vendor/themes' / pin['name'] / 'foundations.json'
        if not path.exists():
            continue
        assert hashlib.sha256(path.read_bytes()).hexdigest() == pin['foundations_sha256']
        foundation = json.loads(path.read_text())
        for mode, data in foundation['modes'].items():
            checks = []
            def check(label, value, minimum, kind):
                checks.append(dict(label=label, ratio=round(value, 3), minimum=minimum, passes=value + 1e-8 >= minimum, kind=kind))
            def role(name):
                return data['swatches'][data['roles'][name]]
            for fg in ['ink', 'muted', 'accent-text', 'secondary-text', 'code-ink']:
                for bg in ['paper', 'panel', 'code']:
                    check(f'{fg} on {bg}', pair(role(fg), role(bg)), 5, 'source-pair')
            for fg in data['roles']:
                if fg.startswith('syntax-'):
                    check(f'{fg} on code', pair(role(fg), role('code')), 5, 'syntax-pair')
            for fg, bg in [('button-ink', 'primary-fill'), ('primary-hover-ink', 'primary-hover-fill'), ('selected-ink', 'selected-fill')]:
                check(f'{fg} on {bg}', pair(role(fg), role(bg)), 4.5, 'source-pair')
            for edge in ['focus', 'control-boundary']:
                for bg in ['paper', 'panel', 'code']:
                    check(f'{edge} against {bg}', pair(role(edge), role(bg)), 3, 'source-pair')
            for name, state in data['states'].items():
                check(f'{name} text on fill', pair(state['ink'], state['fill']), 5, 'source-pair')
                check(f'{name} boundary on fill', pair(state['boundary'], state['fill']), 3, 'source-pair')
            browser = []
            for record in [r for r in measurements if r['id'] == pin['name'] and r['mode'] == mode]:
                profile = foundation['typography']['profiles']['reading']
                errors = []
                expected = {'foundation-prose': profile['body'], 'foundation-metadata': profile['metadata'], 'foundation-primary': profile['ui']}
                for id, size in expected.items():
                    actual = float(record['elements'][id]['style']['fontSize'].removesuffix('px'))
                    if abs(actual - size) > .05:
                        errors.append(f'{id}: {actual}px, expected {size}px')
                actual_code = float(record['code']['style']['fontSize'].removesuffix('px'))
                if abs(actual_code - profile['code']) > .05:
                    errors.append(f'Code: {actual_code}px, expected {profile["code"]}px')
                if record['documentWidth'] > record['viewport']['width'] + 1:
                    errors.append('Horizontal page overflow')
                if record['fontStatus'] != 'loaded':
                    errors.append('Fonts still loading')
                if record['rootSize'] != '16px':
                    errors.append('Default root differs from 16px reference')
                semantic = record['semantics']
                if not (semantic['disabled'] and semantic['invalid'] == 'true' and semantic['describedBy'] == 'foundation-error' and semantic['current'] == 'page'):
                    errors.append('Fixture semantics missing')
                ratios = []
                for id in ['foundation-prose', 'foundation-metadata', 'foundation-primary', 'foundation-secondary', 'foundation-outline', 'foundation-disabled', 'foundation-error', 'foundation-selected']:
                    element = record['elements'][id]
                    value = contrast_range(element, record)[0]
                    # Disabled text is deliberately included as a usability check,
                    # not presented as a normative WCAG requirement.
                    ratios.append(dict(label=id, ratio=value, minimum=4.5, passes=value >= 4.5))
                for state in record['states']:
                    value = contrast_range(state, record)[0]
                    ratios.append(dict(label=state['state'] + ' action', ratio=value, minimum=4.5, passes=value >= 4.5))
                browser.append(dict(viewport=record['viewportName'], profileErrors=errors, renderedText=ratios, loadedFonts=record['loadedFonts']))
            results.append(dict(id=pin['name'], mode=mode, commit=pin['commit'], sourceChecks=checks, browser=browser))
    (ROOT / 'foundations-checks.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Foundation contexts:', len(results))
    print('Source pair flags:', sum(not c['passes'] for r in results for c in r['sourceChecks']))
    print('Profile flags:', [(r['id'], r['mode'], b['viewport'], b['profileErrors']) for r in results for b in r['browser'] if b['profileErrors']])
    print('Rendered text flags:', [(r['id'], r['mode'], b['viewport'], [(c['label'], c['ratio']) for c in b['renderedText'] if not c['passes']]) for r in results for b in r['browser'] if any(not c['passes'] for c in b['renderedText'])])


if __name__ == '__main__':
    main()
