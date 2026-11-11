"""Texto alternativo (alt) de las imágenes del sitio nuevo.

  python scripts/alt_imagenes.py contexto  -> data/alt_contexto.csv: cada imagen con archivo, título, tipo y páginas donde se usa
  python scripts/alt_imagenes.py dry-run   -> muestra los cambios de data/alt_propuesto.csv (alt actual -> propuesto)
  python scripts/alt_imagenes.py aplicar   -> respalda en data/backup/ y aplica por la API (pide confirmación escrita)

data/alt_propuesto.csv (id, archivo, alt_propuesto) es el archivo revisado que se aplica.
"""
import csv
import datetime
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urljoin, urlparse

from wp_client import new

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
CONTEXTO = os.path.join(DATA, "alt_contexto.csv")
PROPUESTO = os.path.join(DATA, "alt_propuesto.csv")
BACKUP = os.path.join(DATA, "backup")

UPLOAD_RE = re.compile(r"""(?:https?:)?//[^\s"'()<>]*?/wp-content/uploads/[^\s"'()<>,]+|/wp-content/uploads/[^\s"'()<>,]+""")
CSS_RE = re.compile(r"""<link[^>]+href=["']([^"']+/elementor/css/[^"']+\.css[^"']*)["']""")


def key(url):
    """Nombre base del archivo sin tamaño (-300x200), -scaled ni extensión."""
    name = os.path.basename(urlparse(url).path).lower()
    name = re.sub(r"\.(webp|avif)$", "", name)  # LiteSpeed puede servir archivo.jpg.webp
    name = re.sub(r"\.[a-z0-9]+$", "", name)
    return re.sub(r"(-\d+x\d+|-scaled|-e\d{10,})+$", "", name)


def pages(site):
    with open(os.path.join(DATA, "inventario_new.csv"), encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f) if r["estado"] == "publish"]


def contexto():
    site = new()
    media = site.get_all("media")
    usos = defaultdict(set)
    for p in pages(site):
        html = site.s.get(p["url"], timeout=60).text.replace("\\/", "/")
        found = set(UPLOAD_RE.findall(html))
        for css in set(CSS_RE.findall(html)):  # fondos de secciones de Elementor
            css_url = urljoin(p["url"], css.replace("&#038;", "&"))
            found |= set(UPLOAD_RE.findall(site.s.get(css_url, timeout=60).text))
        for u in found:
            usos[key(u)].add(f"{p['titulo']} ({p['path']})")
    rows = []
    for m in media:
        k = key(m["source_url"])
        rows.append({
            "id": m["id"],
            "tipo_mime": m.get("mime_type", ""),
            "archivo": os.path.basename(urlparse(m["source_url"]).path),
            "titulo": re.sub(r"<[^>]+>", "", m["title"]["rendered"]),
            "alt_actual": m.get("alt_text", ""),
            "adjunto_a": m.get("post") or "",
            "n_paginas": len(usos.get(k, ())),
            "paginas": " | ".join(sorted(usos.get(k, ()))),
            "url": m["source_url"],
        })
    with open(CONTEXTO, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    usadas = sum(1 for r in rows if r["n_paginas"])
    print(f"{len(rows)} archivos en la biblioteca; {usadas} aparecen en páginas públicas. -> {os.path.relpath(CONTEXTO, ROOT)}")


def load_propuesto():
    with open(PROPUESTO, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["alt_propuesto"].strip()]
    for r in rows:
        if len(r["alt_propuesto"]) > 125:
            sys.exit(f"alt demasiado largo (>125) en id {r['id']}")
    return rows


def plan(site):
    actuales = {m["id"]: m for m in site.get_all("media")}
    cambios = []
    for r in load_propuesto():
        m = actuales.get(int(r["id"]))
        if m is None:
            print(f"  OMITIDO id {r['id']}: ya no existe")
            continue
        if m.get("alt_text", "") != r["alt_propuesto"]:
            cambios.append((m, r["alt_propuesto"]))
    return cambios


def dry_run():
    site = new()
    cambios = plan(site)
    for m, alt in cambios:
        print(f"[{m['id']}] {os.path.basename(m['source_url'])}\n    '{m.get('alt_text', '')}' -> '{alt}'")
    print(f"\nDRY-RUN: {len(cambios)} imágenes cambiarían. No se escribió nada. Autenticado: {site.status()}")


def aplicar():
    site = new()
    site.require_auth()
    cambios = plan(site)
    if not cambios:
        return print("Nada que aplicar.")
    os.makedirs(BACKUP, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(BACKUP, f"media_alt_{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([{"id": m["id"], "source_url": m["source_url"], "alt_text": m.get("alt_text", "")}
                   for m, _ in cambios], f, ensure_ascii=False, indent=1)
    print(f"Respaldo: {os.path.relpath(path, ROOT)} ({len(cambios)} imágenes)")
    if input(f"Escribe APLICAR para actualizar {len(cambios)} imágenes en {site.base}: ") != "APLICAR":
        return print("Cancelado.")
    for m, alt in cambios:
        res = site.update("media", m["id"], {"alt_text": alt})
        print(f"  OK {m['id']}" if res.get("alt_text") == alt else f"  REVISAR {m['id']}")
    print("Listo. Purga la caché de LiteSpeed para ver los alt en el HTML.")


def restaurar(path):
    site = new()
    site.require_auth()
    with open(path, encoding="utf-8") as f:
        for it in json.load(f):
            site.update("media", it["id"], {"alt_text": it["alt_text"]})
            print(f"  restaurado {it['id']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "restaurar" and len(sys.argv) > 2:
        restaurar(sys.argv[2])
    else:
        {"contexto": contexto, "dry-run": dry_run, "aplicar": aplicar}.get(cmd, lambda: sys.exit(__doc__))()
