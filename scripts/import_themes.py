"""Import clean, committed upstream extensions and record exact source identities."""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['folio', 'atelier', 'nocturne', 'tufte', 'zephyr-reading', 'simplex-reading', 'pulse-reading', 'litera-reading', 'darkly-reading']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--themes', nargs='+', choices=NAMES, default=NAMES,
                        help='Import only these reviewed themes; leave other source pins unchanged')
    names = parser.parse_args().themes
    sources = json.loads((ROOT / 'theme-sources.json').read_text())
    for name in names:
        repo = ROOT.parent / ('smalldocs-' + name)
        if not repo.exists():
            repo = ROOT.parent.parent / ('smalldocs-' + name)
        assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo), f'Dirty source: {repo}'
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        prefix = f'_extensions/{name}/'
        archive = subprocess.check_output(['git', 'archive', commit, prefix], cwd=repo)
        target = ROOT / 'vendor/themes' / name
        shutil.rmtree(target)
        target.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar:
                if member.isfile():
                    relative = Path(member.name).relative_to(prefix)
                    assert '..' not in relative.parts
                    dest = target / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(tar.extractfile(member).read())
        manifest = (target / 'foundations.json').read_bytes()
        assert manifest == (repo / 'src/foundations.json').read_bytes()
        record = next(s for s in sources if s['name'] == name)
        record.update(commit=commit, foundations_sha256=hashlib.sha256(manifest).hexdigest())
        print(name, commit, record['foundations_sha256'])
    (ROOT / 'theme-sources.json').write_text(json.dumps(sources, indent=2) + '\n')


if __name__ == '__main__':
    main()
