"""Build a portable comparison gallery and identical SmallDocs specimens."""
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from smalldocs.site import build

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "example/_site"

CUSTOM = [
    {"id":"folio", "name":"Folio", "group":"custom", "description":"Folio uses cream paper, forest green, and Caslon headings. The Close Reading book catalog (CRBooks) inspired the design.", "type":"Caslon · Source Serif 4 · IBM Plex Mono", "colors":["#f8f4eb","#254f38","#9d442b"], "paired":True},
    {"id":"atelier", "name":"Atelier", "group":"custom", "description":"Atelier uses chalk white and deep teal, with modern sans-serif type.", "type":"DM Sans · IBM Plex Mono", "colors":["#fbfcfa","#176a70","#253e42"], "paired":True},
    {"id":"nocturne", "name":"Nocturne", "group":"custom", "description":"Light mode uses pearl paper. Dark mode uses midnight ink and warm brass.", "type":"Source Serif 4 · DM Sans · IBM Plex Mono", "colors":["#1c2030","#e2bd82","#ede8de"], "paired":True},
    {"id":"tufte", "name":"Tufte", "group":"custom", "description":"Tufte uses ET Book, cream paper, and italic headings. It was the starting point for this collection.", "type":"ET Book · Consolas / Menlo", "colors":["#fffff8","#111111","#7a1c1c"], "paired":True},
    {"id":"bootstrap", "name":"Bootstrap", "group":"bootstrap", "description":"Bootstrap provides the baseline component styles. The gallery includes light and dark previews.", "type":"System sans · System monospace", "colors":["#ffffff","#0d6efd","#212529"], "paired":True},
]
# Preserve the original snapshots alongside the revised custom themes.
for t in CUSTOM[:3]:
    t['name'] += ' · Refined'
    t['revision'] = 'refined'
    t['comparison'] = t['id']
for original in list(CUSTOM[:3]):
    t = dict(original)
    t.update(id=original['id']+'-original', name=original['id'].title()+' · Original', revision='original', description='Original version, preserved before the reading refinement. '+original['description'])
    CUSTOM.append(t)
CUSTOM[0].update(
    description='Folio uses Source Serif 4 for prose and headings, DM Sans for controls, and IBM Plex Mono for code. Libre Caslon Display is an optional display face. The Close Reading book catalog (CRBooks) inspired its cream and forest-green palette.',
    type='Source Serif 4 · DM Sans · IBM Plex Mono · Optional Caslon',
)
for base, family, colors in [
 ('zephyr','Inter',['#ffffff','#3459e6','#495057']),
 ('simplex','Open Sans',['#fcfcfc','#b81d0e','#212529']),
 ('pulse','System sans',['#ffffff','#593196','#444444']),
 ('litera','Georgia',['#ffffff','#2557a0','#343a40']),
 ('darkly','Lato',['#222222','#8db9e8','#eeeeee'])]:
    CUSTOM.append(dict(id=base+'-reading',name=base.title()+' Reading',group='refined',description='A light and dark reading version of '+base.title()+', with defined type sizes, spacing, named color uses, and readable controls.',type=family+' · IBM Plex Mono',colors=colors,paired=True,revision='refined',comparison=base))


DESCRIPTIONS = {
    "cerulean":"Soft blue and a familiar interface.", "cosmo":"Clean lines and Source Sans.",
    "cyborg":"Black surfaces with bright cyan accents.", "darkly":"Deep charcoal and colorful details.",
    "flatly":"Flat surfaces and generous spacing.", "journal":"Journal-style typography and expressive headings.",
    "litera":"An editorial page built around the prose.", "lumen":"Light surfaces with fine shadows.",
    "lux":"Spaced capitals and stark contrast.", "materia":"Material-inspired controls and clean type.",
    "minty":"Mint and coral with rounded edges.", "morph":"Raised-style panels on a pale blue background.",
    "pulse":"Purple accents and clear hierarchy.", "quartz":"Violet, translucency, and glass-like panels.",
    "sandstone":"Earthy colors and compact labels.", "simplex":"Small touches of red on a clean page.",
    "sketchy":"Hand-drawn rules and playful type.", "slate":"Steel gray and subtle gradients.",
    "solar":"A deep teal background with warm accents.", "spacelab":"Cool gray with blue details.",
    "superhero":"Midnight blue and warm orange.", "united":"Warm orange and Ubuntu type.",
    "vapor":"Neon pastels on a purple background.", "yeti":"An open page with clean lines.",
    "zephyr":"Light shadows and blue accents.",
}


def variable(css, name):
    return re.search(r"--bs-" + name + r":([^;}]+)", css)[1]


def themes():
    result = [dict(t) for t in CUSTOM]
    for t in result:
        foundation = ROOT / 'vendor/themes' / t['id'] / 'foundations.json'
        if foundation.exists():
            f = json.loads(foundation.read_text())
            t['foundation'] = f"previews/{t['id']}/site_libs/themes/{t['id']}/foundations.json"
            t['nativeMode'] = f['nativeMode']
            t['profile'] = f['typography']['profiles']['reading']
        if t["group"] in ("custom", "refined"):
            repo = t["id"].removesuffix("-original")
            t["guide"] = f"theme-guide.html#{repo}"
            t["source"] = f"https://github.com/rahuldave/smalldocs-{repo}"
            t["demo"] = f"https://rahuldave.com/smalldocs-{repo}/"
            t["install"] = f"smalldocs add rahuldave/smalldocs-{repo}"
            if t["id"].endswith("-original"):
                t["source"] += "/tree/before-reading-redesign-2026-10-16"
                t["install"] += "@before-reading-redesign-2026-10-16"
        else:
            t.update(source="https://github.com/twbs/bootstrap", demo="https://getbootstrap.com/docs/5.3/", install="theme: bootstrap", guide="theme-guide.html#bootstrap")
    for file in sorted((ROOT / "vendor/bootswatch").glob("*.css")):
        name = file.name.split('.')[0]
        css = file.read_text()
        family = variable(css,"font-sans-serif").split(',')[0].strip('"')
        if family in ("system-ui", "-apple-system"):
            family = "System sans"
        result.append({"id":name,"name":name.title(),"group":"bootswatch","description":DESCRIPTIONS[name],"type":family + " · Original Bootswatch type", "colors":[variable(css,"body-bg"),variable(css,"primary"),variable(css,"body-color")], "paired":False,"source":f"https://bootswatch.com/{name}/", "demo":f"https://bootswatch.com/{name}/", "install":f"theme: {name}"})
    for t in result:
        t.setdefault("guide", "theme-guide.html#bootswatch")
        if t["id"] in ("zephyr","simplex","pulse","litera","darkly"):
            t.update(comparison=t["id"], revision="original")
    return result


def main():
    library = themes()
    scores_file = ROOT / 'reports/typography-audit/scores.json'
    if scores_file.exists():
        scores = {t['id']:t for t in json.loads(scores_file.read_text())}
        for t in library:
            t['typeScore'] = scores[t['id']]['typography']
            t['designScore'] = scores[t['id']]['design']['total']
            row = scores[t['id']]
            t['reviewFlagged'] = bool(row.get('foundationFlags')) or any(c['failures'] for c in row['design']['contexts']) or any(
                m['metrics']['syntaxContrast'] < 4.5 or any(m['metrics'][k][0] < 4.5 for k in ['bodyContrast', 'linkContrast', 'inlineContrast'])
                for m in row['modes'])
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for t in library:
        name = t["id"]
        stage = ROOT / ".build" / name
        if stage.exists():
            shutil.rmtree(stage)
        shutil.copytree(ROOT / "example", stage, ignore=shutil.ignore_patterns("_site", "_extensions"))
        cfg = yaml.safe_load((stage / "_smalldocs.yml").read_text())
        cfg["website"]["title"] = t["name"]
        cfg["website"]["site-url"] = f"https://rahuldave.com/elegant-themes/previews/{name}/"
        if t["group"] in ("custom", "refined"):
            shutil.copytree(ROOT / "vendor/themes" / name, stage / "_extensions" / name)
            cfg["theme"] = name
        elif name == "bootstrap":
            out = stage / "_extensions/native-bootstrap"
            out.mkdir(parents=True)
            bs = (ROOT / "vendor/bootstrap/bootstrap.min.css").read_text()
            bs = re.sub(r"/\*# sourceMappingURL=.*?\*/", "", bs)
            dark = subprocess.check_output([sys.executable,str(ROOT / "scripts/dark_root.py"),str(ROOT / "vendor/bootstrap/bootstrap.min.css")],text=True)
            (out / "bootstrap.css").write_text(bs)
            (out / "bootstrap-dark.css").write_text(bs + '\n' + dark)
            (out / "smalldocs.yml").write_text('css:\n  light: bootstrap.css\n  dark: bootstrap-dark.css\n')
            cfg["theme"] = "native-bootstrap"
        else:
            (stage / "styles").mkdir()
            shutil.copy2(ROOT / f"vendor/bootswatch/{name}.min.css",stage / f"styles/{name}.min.css")
            cfg["theme"] = f"styles/{name}.min.css"
        (stage / "_smalldocs.yml").write_text(yaml.safe_dump(cfg,sort_keys=False))
        with contextlib.redirect_stderr(io.StringIO()):
            site = build(stage)
        if site.warnings:
            raise RuntimeError(f"{name}: {site.warnings}")
        shutil.copytree(stage / "_site", OUTPUT / "previews" / name)
        foundation = ROOT / 'vendor/themes' / name / 'foundations.json'
        if foundation.exists():
            shutil.copy2(foundation, OUTPUT / 'previews' / name / 'site_libs/themes' / name / 'foundations.json')
            for notice in foundation.parent.rglob('*'):
                if notice.is_file() and re.search(r'license|licence|ofl|copyright', notice.name, re.I):
                    destination = OUTPUT / 'previews' / name / 'site_libs/themes' / name / notice.relative_to(foundation.parent)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(notice, destination)
        print(f"Rendered {t['name']}",flush=True)
    assets = OUTPUT / "site_libs/gallery"
    assets.mkdir(parents=True)
    shutil.copytree(ROOT / "vendor/fonts",assets / "fonts")
    for source, dest in (("index.html",OUTPUT / "index.html"),("using-themes.html",OUTPUT / "using-themes.html"),("theme-guide.html",OUTPUT / "theme-guide.html"),("theme-guide.css",assets / "theme-guide.css"),("gallery.css",assets / "gallery.css"),("gallery.js",assets / "gallery.js")):
        shutil.copy2(ROOT / "src" / source,dest)
    (assets / "themes.js").write_text("window.THEME_LIBRARY = " + json.dumps(library,ensure_ascii=False) + ";\n")
    # Reports are plain HTML and our own evidence, copied using an explicit export.
    reports = ROOT / 'reports'
    if reports.exists():
        shutil.copytree(reports, OUTPUT, dirs_exist_ok=True)
    (OUTPUT / '.nojekyll').touch()
    print(f"Built {len(library)} designs in {OUTPUT}")


if __name__ == "__main__":
    main()
