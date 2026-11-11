"""Redirecciones 301 del sitio nuevo con el plugin Redirection.

  python scripts/redirecciones.py generar    -> data/redirection_import.csv (para Herramientas > Redirection > Importar)
  python scripts/redirecciones.py verificar  -> comprueba que cada URL antigua responda 301 al destino correcto
                                                y guarda data/redirecciones_verificacion.csv

Formato del plugin: source,target,regex,code,type (comas, sin encabezado, UTF-8 sin BOM).
Ref: https://redirection.me/support/import-export/
"""
import csv
import os
import sys
from urllib.parse import urljoin

from wp_client import new

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "redirecciones.csv")
OUT = os.path.join(ROOT, "data", "redirection_import.csv")
VERIF = os.path.join(ROOT, "data", "redirecciones_verificacion.csv")


def load():
    with open(SRC, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["source"].strip()]
    for r in rows:
        for k in ("source", "target"):
            if not r[k].startswith("/"):
                sys.exit(f"Ruta inválida en redirecciones.csv ({k}): {r[k]}")
    sources = [r["source"] for r in rows]
    dup = {s for s in sources if sources.count(s) > 1}
    if dup:
        sys.exit(f"Orígenes duplicados en redirecciones.csv: {dup}")
    loops = {r["source"] for r in rows} & {r["target"] for r in rows}
    if loops:
        sys.exit(f"Un destino también es origen (cadena/bucle): {loops}")
    return rows


def generar():
    rows = load()
    site = new()
    problemas = []
    for r in rows:
        resp = site.s.get(site.base + r["target"], allow_redirects=False, timeout=60)
        if resp.status_code != 200:
            problemas.append(f"  destino {r['target']} responde {resp.status_code}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        for r in rows:
            w.writerow([r["source"], r["target"], 0, 301, "url"])
    print(f"Generado {os.path.relpath(OUT, ROOT)} con {len(rows)} redirecciones 301.")
    pendientes = [r for r in rows if "confirmar" in r["accion"].lower() or "revisar" in r["accion"].lower()]
    for r in pendientes:
        print(f"  PENDIENTE de confirmar: {r['source']} -> {r['target']} ({r['accion']})")
    if problemas:
        print("ATENCIÓN, destinos que no responden 200:")
        print("\n".join(problemas))
        sys.exit(1)


def verificar():
    rows = load()
    site = new()
    results, ok = [], 0
    for r in rows:
        expected = site.base + r["target"]
        resp = site.s.get(site.base + r["source"], allow_redirects=False, timeout=60)
        location = urljoin(site.base + r["source"], resp.headers.get("Location", ""))
        final = site.s.get(location, timeout=60) if resp.is_redirect else None
        good = (resp.status_code == 301 and location == expected
                and final is not None and final.status_code == 200 and not final.history)
        ok += good
        results.append({
            "source": r["source"], "esperado": r["target"], "codigo": resp.status_code,
            "location": location if resp.is_redirect else "",
            "destino_final": final.status_code if final is not None else "",
            "resultado": "OK" if good else "FALLA",
        })
        print(f"{'OK   ' if good else 'FALLA'} {resp.status_code} {r['source']} -> {location if resp.is_redirect else '-'}")
    with open(VERIF, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)
    print(f"\n{ok}/{len(rows)} redirecciones correctas. Detalle en {os.path.relpath(VERIF, ROOT)}")
    sys.exit(0 if ok == len(rows) else 1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"generar": generar, "verificar": verificar}.get(cmd, lambda: sys.exit(__doc__))()
