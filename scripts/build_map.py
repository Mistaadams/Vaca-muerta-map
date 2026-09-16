#!/usr/bin/env python3
"""Rebuild index.html from the Neuquén provincial GeoServer.

Usage:
  python scripts/build_map.py            # fetch live WFS, simplify, render index.html
  python scripts/build_map.py --offline  # render from data/*.json without fetching

Requires: requests, shapely, pyproj  (pip install -r scripts/requirements.txt)
"""
import argparse, json, sys, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WFS = "https://hidrocarburos.energianeuquen.gob.ar/geoserver/Hidrocarburos/wfs"
KEEP = ["ID_NQN","NOMBRE","TIPO_AREA","TITULAR","PARTICIPAC","OPERADOR","SUP_LEGAL","SIGLA","INI_CONTRATO","FIN_CONTRATO","NORMA_LEGAL"]
TARGETS = ["LOMA JARILLOSA ESTE","PUESTO SILVA OESTE","BAJADA DEL PALO OESTE","BAJADA DEL PALO ESTE"]

def fetch(layer):
    import requests
    r = requests.get(WFS, params={"service":"WFS","version":"1.0.0","request":"GetFeature","typeName":layer,
                                  "outputFormat":"application/json","srsName":"EPSG:4326"}, timeout=120)
    r.raise_for_status()
    return r.json()

def simplify(fc, keys, tol):
    from shapely.geometry import shape, mapping, MultiPolygon
    out = []
    for f in fc["features"]:
        g = shape(f["geometry"]).simplify(tol, preserve_topology=True)
        if g.geom_type == "Polygon":
            g = MultiPolygon([g])
        coords = [[[[round(x,5), round(y,5)] for x,y in ring] for ring in [poly.exterior.coords, *[i.coords for i in poly.interiors]]] for poly in g.geoms]
        out.append({"type":"Feature","properties":{k: f["properties"].get(k) for k in keys},
                    "geometry":{"type":"MultiPolygon","coordinates":coords}})
    return {"type":"FeatureCollection","features":out}

def neighbours(areas):
    from shapely.geometry import shape
    geoms = {f["properties"]["NOMBRE"]: shape(f["geometry"]) for f in areas["features"]}
    props = {f["properties"]["NOMBRE"]: f["properties"] for f in areas["features"]}
    nb = {}
    for t in TARGETS:
        if t not in geoms: continue
        g = geoms[t].buffer(0.002)
        nb[t] = [[n, props[n]["OPERADOR"], props[n]["TIPO_AREA"]] for n, h in geoms.items() if n != t and g.intersects(h)]
    return nb

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--offline", action="store_true"); a = ap.parse_args()
    if a.offline:
        d = json.loads((DATA/"neuquen_areas_simplified.json").read_text(encoding="utf-8"))
    else:
        areas = simplify(fetch("Hidrocarburos:Areas"), KEEP, 0.00015)
        vm = simplify(fetch("Hidrocarburos:VM_Distribucion_Fluidos"), ["Nombre","Observacio"], 0.0005)
        d = {"areas": areas, "vm": vm}
        (DATA/"neuquen_areas_simplified.json").write_text(json.dumps(d, separators=(",",":"), ensure_ascii=False), encoding="utf-8")
    extras = json.loads((DATA/"extras.json").read_text(encoding="utf-8"))
    extras["neighbours"] = neighbours(d["areas"])
    (DATA/"extras.json").write_text(json.dumps(extras, separators=(",",":"), ensure_ascii=False), encoding="utf-8")
    tpl = (ROOT/"scripts"/"template.html").read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    body = (tpl.replace("__DATA__", json.dumps(d, separators=(",",":"), ensure_ascii=False))
               .replace("__EXTRAS__", json.dumps(extras, separators=(",",":"), ensure_ascii=False))
               .replace("pulled 2026‑09‑16", f"pulled {today}"))
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="Neuquén hydrocarbon blocks by operator, Vaca Muerta fluid windows, GeoPark and Vista blocks highlighted.">'
            '</head><body style="margin:0;height:100vh">' + body + "</body></html>")
    (ROOT/"index.html").write_text(html, encoding="utf-8")
    print(f"index.html written ({len(html):,} bytes), {len(d['areas']['features'])} areas, {today}")

if __name__ == "__main__":
    main()
