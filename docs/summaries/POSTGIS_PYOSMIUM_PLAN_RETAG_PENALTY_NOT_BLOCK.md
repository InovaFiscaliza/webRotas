Great—here’s the **“penalty, not block”** variant using PostGIS to *decide* which ways to penalize, PyOsmium to *embed a tag* on those ways, and a tiny tweak to OSRM’s `car.lua` so those tagged ways get a **huge speed penalty** (i.e., they’re still usable if there’s no alternative, but the router will strongly avoid them).

---

# 1) In PostGIS: select penalized ways (and a severity)

```sql
-- Assumes classic osm2pgsql schema with planet_osm_line
-- and your avoid polygons in avoid_zones(geom)
WITH zones AS (
  SELECT ST_UnaryUnion(geom) AS g FROM avoid_zones
),
routable AS (
  SELECT osm_id, way, highway
  FROM planet_osm_line
  WHERE osm_id > 0
    AND highway IS NOT NULL
    AND highway NOT IN ('footway','path','cycleway','steps','bridleway')
)
SELECT r.osm_id,
       CASE
         WHEN ST_Covers(z.g, r.way)        THEN 0.02  -- inside: extreme penalty
         WHEN ST_Intersects(r.way, z.g)     THEN 0.10  -- touching: strong penalty
         ELSE 1.00
       END AS penalty_factor
INTO TEMP TABLE penalized_ways
FROM routable r, zones z
WHERE ST_Intersects(r.way, z.g);

-- Only keep rows that actually need a penalty (< 1.0):
DELETE FROM penalized_ways WHERE penalty_factor >= 1.0;

\copy (SELECT osm_id, penalty_factor FROM penalized_ways ORDER BY osm_id)
  TO '/tmp/penalized_way_ids.csv' WITH (FORMAT csv, HEADER true)
```

This writes a CSV like:

```
osm_id,penalty_factor
123456,0.02
234567,0.10
...
```

---

# 2) In PyOsmium: *retag* those ways (don’t drop them)

We’ll embed two tags that OSRM can see during `osrm-extract`:

* `avoid_zone=yes`
* `avoid_factor=<0.02 or 0.10, etc.>`

```python
#!/usr/bin/env python3
# tag_penalties.py
import argparse, csv
import pyosmium as osm

def load_penalties(csv_path):
    factors = {}
    with open(csv_path, newline="") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            factors[int(row["osm_id"])] = float(row["penalty_factor"])
    return factors

class PenaltyTagger(osm.SimpleHandler):
    def __init__(self, writer, factors):
        super().__init__()
        self.wr = writer
        self.factors = factors

    def node(self, n):      self.wr.add_node(n)
    def relation(self, r):  self.wr.add_relation(r)

    def way(self, w):
        f = self.factors.get(w.id)
        if f is None:
            self.wr.add_way(w)
            return
        mw = osm.osm.mutable.Way(w)
        tags = {t.k: t.v for t in w.tags}
        tags["avoid_zone"] = "yes"
        # Store a bounded, numeric factor string (defensive)
        tags["avoid_factor"] = f"{max(0.01, min(f, 0.99)):.4f}"
        mw.tags = [osm.osm.Tag(k, v) for k, v in tags.items()]
        self.wr.add_way(mw)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_pbf")
    ap.add_argument("penalties_csv")   # /tmp/penalized_way_ids.csv
    ap.add_argument("out_pbf")
    args = ap.parse_args()

    penalties = load_penalties(args.penalties_csv)
    r = osm.io.Reader(args.in_pbf)
    w = osm.io.Writer(args.out_pbf)
    osm.apply(r, PenaltyTagger(w, penalties))
    w.close(); r.close()

if __name__ == "__main__":
    main()
```

Run:

```bash
python tag_penalties.py planet-latest.osm.pbf /tmp/penalized_way_ids.csv planet-penalized.osm.pbf
```

---

# 3) Tell OSRM to **slow down** tagged ways (profile tweak)

Routing in OSRM is driven by **edge `weight`**, which (for car) is derived from the **speed** you set in the Lua profile. Setting a *much lower speed* on tagged ways massively increases the weight, so OSRM avoids them unless necessary. (OSRM’s docs and issues confirm that `weight` decides the path; changing profile speeds changes weight/duration. ([GitHub][1]))

Make a copy of the default `car.lua` (matching your OSRM version), and add a tiny hook **after** the standard handlers run. For modern profiles that expose `process_way(profile, way, result, relations)`:

```lua
-- car_avoid.lua (copy of car.lua with a small patch)

-- ... keep all original requires and setup ...

function process_way(profile, way, result, relations)
  -- Run the stock pipeline:
  local data = WayHandlers.get_data(way)             -- already in car.lua
  local handlers = WayHandlers.get_handlers(profile) -- already in car.lua
  WayHandlers.run(profile, way, result, data, handlers, relations)

  -- === Penalty hook (our addition) ===
  local az = way:get_value_by_key('avoid_zone')
  if az == 'yes' then
    local f = tonumber(way:get_value_by_key('avoid_factor')) or 0.05
    -- bound factor to something sane
    if f < 0.01 then f = 0.01 end
    if f > 0.99 then f = 0.99 end

    -- Penalize by reducing speeds (km/h) -> increases weight/duration
    if result.forward_mode ~= mode.inaccessible and result.forward_speed and result.forward_speed > 0 then
      result.forward_speed  = math.max(1, result.forward_speed  * f)
    end
    if result.backward_mode ~= mode.inaccessible and result.backward_speed and result.backward_speed > 0 then
      result.backward_speed = math.max(1, result.backward_speed * f)
    end
    -- Optional (and version-dependent): you can also scale result.weight if your profile sets it explicitly.
    -- Routing uses 'weight'; most car.lua compute weight from speed, so speed scaling is usually enough.
  end
end
```

> If your OSRM image uses the **older** `way_function(way, result)` style profile, apply the same `avoid_zone/avoid_factor` check at the end of that function and scale `result.forward_speed`/`result.backward_speed`.

Rebuild with your patched profile and **the penalized PBF**:

```bash
docker run --rm -v "$PWD:/data" ghcr.io/project-osrm/osrm-backend \
  osrm-extract -p /opt/car_avoid.lua /data/planet-penalized.osm.pbf
docker run --rm -v "$PWD:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/planet-penalized.osrm
docker run --rm -v "$PWD:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/planet-penalized.osrm
```

Now any way with `avoid_zone=yes` will be treated as **painfully slow** (factor 0.02 → ~50× slower), making OSRM skirt around your polygons whenever possible.

---

## Why this works (and references)

* OSRM’s **routing decision** uses edge **`weight`**; for car, weight is derived from speed in the Lua profile. Slashing speed → large weight → strong avoidance. ([GitHub][1])
* Longstanding guidance from OSRM maintainers: “add a tag and **set the speed very low** in the profile” to de-prefer/avoid roads. ([GitHub][2])

---

## Tweaks you might like

* **Graduated penalties**: keep the numeric `avoid_factor` from PostGIS so you can differentiate “inside zone” vs “edge touch”.
* **Profile isolation**: keep your stock `car.lua`; create `car_avoid.lua` with just this hook to make maintenance trivial across OSRM upgrades.
* **QA**: In PostGIS, inspect a quick sample of penalized ways (`SELECT * FROM planet_osm_line WHERE osm_id IN (...)`) and visualize your zones + ways to confirm.

[1]: https://github.com/Project-OSRM/osrm-backend/issues/5469?utm_source=chatgpt.com "osrm profile: weight for distance ? · Issue #5469"
[2]: https://github.com/Project-OSRM/osrm-backend/issues/1313?utm_source=chatgpt.com "Feature Request: Avoiding roads · Issue #1313"
