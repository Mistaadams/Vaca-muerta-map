# Vaca Muerta Land Map

Interactive map of Neuquén province hydrocarbon areas coloured by operator, with the Vaca Muerta fluid windows overlaid and four blocks highlighted: **Loma Jarillosa Este** and **Puesto Silva Oeste** (GeoPark) and **Bajada del Palo Oeste / Este** (Vista Energy, with PAD 30 / PAD 31 well locations).

`index.html` is fully self‑contained (data embedded, no backend) — it can be served from GitHub Pages or any static host.

## Publish on GitHub Pages
1. Push this repo to GitHub.
2. **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder = `/ (root)`.
3. The page is live at `https://<user-or-org>.github.io/<repo>/` within a minute or two. Add a custom domain (e.g. `maps.shearfrac.com`) in the same settings panel with a CNAME record.

## Data
| File | Content |
|---|---|
| `data/neuquen_areas_simplified.json` | 245 hydrocarbon areas (WGS84, simplified to ~15 m) + 5 Vaca Muerta fluid‑window polygons |
| `data/extras.json` | Vista PAD 30 / PAD 31 wells (converted from POSGAR 94 Faja 2, EPSG:22182) and adjacency lists for the highlighted blocks |

Source: Subsecretaría de Energía, Minería e Hidrocarburos de la Provincia del Neuquén — GeoServer WFS layers `Hidrocarburos:Areas` and `Hidrocarburos:VM_Distribucion_Fluidos` (<https://hidrocarburos.energianeuquen.gob.ar/gis>). Neuquén province only; Río Negro / Mendoza / La Pampa acreage is not included.

## Refreshing
```bash
pip install -r scripts/requirements.txt
python scripts/build_map.py          # pulls live WFS data and rewrites index.html
python scripts/build_map.py --offline  # re-render from data/ without fetching
```
`.github/workflows/refresh.yml` runs the same build on the 1st of each month (and on demand via *Actions → Run workflow*) and commits `index.html` if the provincial layer changed.

## Editing the map
Styling, colours, operator short names and the highlighted‑block list live in `scripts/template.html`; rebuild with `--offline` after editing.
