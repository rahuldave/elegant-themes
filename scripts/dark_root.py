"Print Bootstrap's dark colour mode as the page's own: the [data-bs-theme=dark] variables on :root, and each [data-bs-theme=dark] X rule as X."
import re, sys
css = open(sys.argv[1], encoding="utf-8").read()
out = ["\n/* ---------------------------------------------------------------- Bootstrap's dark colour mode, on the whole page, as Bootswatch's dark themes do */"]
block = re.search(r"\[data-bs-theme=dark\]\{(color-scheme:dark[^}]*)\}", css).group(1)
out.append(":root,[data-bs-theme=light]{" + block + "}")
for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    sel = sel.rpartition(";")[2]
    items = [s for s in sel.split(",") if s.startswith("[data-bs-theme=dark] ")]
    if items:
        out.append(",".join(s.removeprefix("[data-bs-theme=dark] ") for s in items) + "{" + body + "}")
print("\n".join(out))
