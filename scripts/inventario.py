"""Inventario y comparativo de contenido entre el sitio antiguo y el nuevo.

Genera en data/:
  inventario_old.csv / inventario_new.csv  -> todo el contenido de cada sitio
  comparativo.csv                         -> qué URL antigua existe o falta en el nuevo
  imagenes_sin_alt_new.csv                -> imágenes del sitio nuevo sin texto alternativo
"""
import csv
import html
import os
import re
from urllib.parse import urlparse

from wp_client import new, old

TYPES = ["pages", "posts", "portafolio"]
OUT = os.path.join(os.path.dirname(__file__), "..", "data")


def clean(text):
    return html.unescape(re.sub(r"<[^>]+>", " ", text or "")).strip()


def inventory(site):
    rows = []
    for t in TYPES:
        for it in site.get_all(t):
            content = clean(it.get("content", {}).get("rendered"))
            rows.append({
                "tipo": t,
                "id": it["id"],
                "estado": it.get("status", "publish"),
                "slug": it["slug"],
                "path": urlparse(it["link"]).path,
                "titulo": clean(it["title"]["rendered"]),
                "extracto": clean(it.get("excerpt", {}).get("rendered"))[:200],
                "palabras": len(content.split()),
                "modificado": it.get("modified"),
                "url": it["link"],
            })
    return rows


def write(name, rows):
    if not rows:
        return
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    o, n = old(), new()
    inv_old, inv_new = inventory(o), inventory(n)
    write("inventario_old.csv", inv_old)
    write("inventario_new.csv", inv_new)

    by_path = {r["path"]: r for r in inv_new}
    by_slug = {r["slug"]: r for r in inv_new}
    comp = []
    for r in inv_old:
        match = by_path.get(r["path"]) or by_slug.get(r["slug"])
        comp.append({
            "tipo": r["tipo"],
            "titulo_old": r["titulo"],
            "path_old": r["path"],
            "path_new": match["path"] if match else "",
            "estado": "igual" if match and match["path"] == r["path"]
            else "cambió URL (redirigir 301)" if match else "FALTA en nuevo",
        })
    write("comparativo.csv", comp)

    media = n.get_all("media")
    write("imagenes_sin_alt_new.csv", [
        {"id": m["id"], "archivo": m["source_url"], "titulo": clean(m["title"]["rendered"])}
        for m in media if not m.get("alt_text")
    ])

    print(f"Antiguo: {len(inv_old)} contenidos | Nuevo: {len(inv_new)} contenidos")
    for estado in ("igual", "cambió URL (redirigir 301)", "FALTA en nuevo"):
        print(f"  {estado}: {sum(c['estado'] == estado for c in comp)}")
    print(f"Imágenes sin alt en nuevo: {sum(1 for m in media if not m.get('alt_text'))}/{len(media)}")
    print(f"Autenticado: antiguo={o.status()} | nuevo={n.status()}")
    if not (o.auth and n.auth):
        print("AVISO: sin autenticación el inventario NO incluye borradores ni contenido privado.")


if __name__ == "__main__":
    main()
