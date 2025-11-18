Below is a pragmatic “DB-in-the-middle” workflow: **use PostGIS to decide what to cut**, then **rewrite the OSM PBF** (retag or drop) with a tiny PyOsmium pass driven by the list of way IDs you found in PostGIS. It’s simple, fast, and avoids the hassles of exporting OSM from PostGIS.

---

# 1) Load OSM into PostGIS (with tags)

Use `osm2pgsql` (flex or classic) so you have a `planet_osm_line` (or your flex-mapped road table) with OSM **way IDs** and geometries.

```bash
# Example (classic schema, keeps tags in hstore):
osm2pgsql \
  --create \
  --database osm \
  --username postgres \
  --hstore \
  --latlong \
  --number-processes 8 \
  planet-latest.osm.pbf
```

Relevant columns (classic):

* `planet_osm_line(osm_id bigint, way geometry(LineString,4326), tags hstore, highway text, …)`
  Note: `osm_id > 0` are **ways**; relations often come negative.

---

# 2) Load your avoid zones into PostGIS

GeoJSON → `avoid_zones(geom geometry(MultiPolygon,4326))`.

```sql
CREATE TABLE IF NOT EXISTS avoid_zones(geom geometry(MultiPolygon,4326));
-- One-liner via ogr2ogr:
-- ogr2ogr -f PostgreSQL PG:"dbname=osm user=postgres" avoid_zones.geojson -nln avoid_zones -nlt MULTIPOLYGON -lco GEOM_TYPE=geography
-- If you used geography above, adapt the ST_ calls to ::geometry.
CREATE INDEX IF NOT EXISTS idx_avoid_zones_geom ON avoid_zones USING GIST(geom);
ANALYZE avoid_zones;
```

---

# 3) Find the affected ways (car routing example)

This returns **OSM way IDs** that intersect any forbidden polygon and look “car-routable”.

```sql
-- Optional: define what you consider "car-routable"
WITH routable AS (
  SELECT osm_id, way, highway, tags
  FROM planet_osm_line
  WHERE highway IS NOT NULL
    AND highway NOT IN ('footway','path','cycleway','steps','bridleway')
    AND osm_id > 0   -- keep only ways
),
zones AS (
  SELECT ST_UnaryUnion(geom) AS g FROM avoid_zones
)
SELECT r.osm_id
INTO TEMP TABLE blocked_way_ids
FROM routable r, zones z
WHERE ST_Intersects(r.way, z.g);

CREATE INDEX ON blocked_way_ids(osm_id);
```

Export the IDs to a text file (one per line) for the cutter:

```sql
\copy (SELECT osm_id FROM blocked_way_ids ORDER BY osm_id) TO '/tmp/blocked_way_ids.txt' WITH (FORMAT csv, HEADER false);
```

---

# 4) Rewrite the PBF (retag or drop) with PyOsmium

This pass is **pure ID-based**—no Shapely needed. It clones each way; if the way ID is in your blocked set, it either **drops** it or **adds restrictive tags** (e.g., `access=no`, `motor_vehicle=no`) so OSRM’s `car.lua` rejects it.

```python
#!/usr/bin/env python3
# cut_by_id.py
import argparse
import pyosmium as osm

def load_blocklist(path):
    ids = set()
    with open(path, 'r') as f:
        for line in f:
            s = line.strip()
            if s:
                ids.add(int(s))
    return ids

class IdBasedRewriter(osm.SimpleHandler):
    def __init__(self, writer, drop_ids, mode="retag", what="car"):
        super().__init__()
        self.w = writer
        self.drop_ids = drop_ids
        self.mode = mode   # "drop" | "retag"
        self.what = what   # "car" | "bike" | "foot"

    def node(self, n):      self.w.add_node(n)
    def relation(self, r):  self.w.add_relation(r)

    def way(self, w):
        if w.id in self.drop_ids:
            if self.mode == "drop":
                return  # omit this way entirely
            else:
                mw = osm.osm.mutable.Way(w)
                tags = {t.k: t.v for t in w.tags}
                if self.what == "car":
                    tags.setdefault("access", "no")
                    tags.setdefault("motor_vehicle", "no")
                elif self.what == "bike":
                    tags.setdefault("bicycle", "no")
                elif self.what == "foot":
                    tags.setdefault("foot", "no")
                tags["avoid_zone"] = "true"
                mw.tags = [osm.osm.Tag(k, v) for k, v in tags.items()]
                self.w.add_way(mw)
                return
        # passthrough
        self.w.add_way(w)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_pbf")
    ap.add_argument("blocked_ids_txt")
    ap.add_argument("out_pbf")
    ap.add_argument("--mode", choices=["drop","retag"], default="retag")
    ap.add_argument("--what", choices=["car","bike","foot"], default="car")
    args = ap.parse_args()

    block_ids = load_blocklist(args.blocked_ids_txt)
    r = osm.io.Reader(args.in_pbf)
    w = osm.io.Writer(args.out_pbf)

    h = IdBasedRewriter(w, block_ids, mode=args.mode, what=args.what)
    osm.apply(r, h)

    w.close()
    r.close()

if __name__ == "__main__":
    main()
```

Run it:

```bash
python cut_by_id.py planet-latest.osm.pbf /tmp/blocked_way_ids.txt planet-cut.osm.pbf \
  --mode retag --what car
```

Then rebuild OSRM:

```bash
docker run --rm -v $PWD:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/planet-cut.osm.pbf
docker run --rm -v $PWD:/data osrm/osrm-backend osrm-partition /data/planet-cut.osrm
docker run --rm -v $PWD:/data osrm/osrm-backend osrm-customize /data/planet-cut.osrm
```

---

## Variations you might want

* **Hard split at polygon boundaries** (surgical cuts):

  * In PostGIS, pre-split with `ST_Split`/`ST_Difference` to determine the *segments* to block vs. keep, then produce **two ID lists**: segments-to-keep and segments-to-block. Because OSM ways are atomic, you’ll still need an OSM-side splitter if you want to split a single OSM way into multiple OSM ways. In practice for OSRM, **retagging the whole way** is usually sufficient.

* **Multi-profile control**:

  * Generate separate ID lists per profile (e.g., `blocked_car_ids.txt`, `blocked_bike_ids.txt`) and run the cutter once per output PBF to produce per-profile datasets, or teach the cutter to apply different tags by reading a CSV with `way_id,profile`.

* **Speed penalties instead of outright block**:

  * OSRM doesn’t ingest per-way external speeds at query time, so for reliable “avoid” you either remove or retag. If you’re customizing `car.lua`, you could add logic to read a special tag like `avoid_zone=yes` and set speed to 0 / weight to inf, which this cutter already adds by default.

---

## Why this route?

Doing the *spatial* decision in PostGIS is delightful (rich ops, easy QA), but exporting a **correct** OSM change back out of PostGIS (with versioning, references, etc.) is painful. The hybrid approach keeps PostGIS where it shines and uses a deterministic, streaming PyOsmium rewrite to produce the final `.osm.pbf` OSRM needs.
