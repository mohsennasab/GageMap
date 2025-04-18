import geopandas as gpd
import requests
from shapely.geometry import Point
from utils.map import generate_map

def process_shapefile_and_find_stations(zip_path):
    # Step 1: Read shapefile
    gdf = gpd.read_file(f"zip://{zip_path}")
    area = gdf.unary_union
    # Get original shape in lat/lon (EPSG:4326) for mapping
    area_latlon = gpd.GeoSeries([area], crs=gdf.crs).to_crs(epsg=4326)[0]

    gdf_proj = gpd.GeoSeries([area], crs=gdf.crs).to_crs(epsg=3857)
    buffered_area = gdf_proj.buffer(32187)[0]
    buffered_area_latlon = gpd.GeoSeries([buffered_area], crs="EPSG:3857").to_crs(epsg=4326)[0]

    # Step 2: Get bounding box
    minx, miny, maxx, maxy = buffered_area_latlon.bounds
    bbox = f"{minx},{miny},{maxx},{maxy}"
    print(f"Querying USGS for bounding box: {bbox}")

    # Step 3: Query USGS API in RDB format
    def fetch_sites():
        url = "https://waterservices.usgs.gov/nwis/site/"
        # Round coordinates to 4 decimal places
        rounded_bbox = ",".join([f"{float(x):.4f}" for x in bbox.split(",")])

        params = {
            "format": "rdb",
            "bBox": rounded_bbox,
            "parameterCd": "00060"
            # NOTE: We are omitting hasDataTypeCd to avoid 400 errors
        }

        r = requests.get(url, params=params)
        print(f"Requesting USGS with: {r.url}")

        if r.status_code != 200:
            print(f"[ERROR] USGS API failed. Status code: {r.status_code}")
            return []

        lines = r.text.splitlines()
        sites = []

        for line in lines:
            if line.startswith("#") or line.startswith("agency_cd") or line.startswith("5s"):
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            site = {
                "siteCode": parts[1],
                "siteName": parts[2],
                "latitude": float(parts[4]),
                "longitude": float(parts[5]),
                "has_daily": True,  # mark all as daily for now
                "has_instant": False  # optionally update this later
            }
            sites.append(site)

        return sites


    sites = fetch_sites()


    if not sites:
        print("[ERROR] No station data could be retrieved from USGS.")
        return [], "data/stations.txt", "<p>Failed to retrieve station data from USGS.</p>"


    stations = {}
    for site in sites:
        sid = site["siteCode"]
        stations[sid] = {
            "id": sid,
            "name": site["siteName"],
            "latitude": site["latitude"],
            "longitude": site["longitude"],
            "has_daily": site["has_daily"],
            "has_instant": site["has_instant"]
        }


    print(f"Total USGS stations found in bounding box: {len(stations)}")

    filtered = []
    for s in stations.values():
        pt = Point(s["longitude"], s["latitude"])
        if pt.within(area_latlon):
            filtered.append(s)


    print(f"Stations within buffered area: {len(filtered)}")

    # Step 5: Write to TXT
    txt_path = "data/stations.txt"
    with open(txt_path, "w") as f:
        for s in filtered:
            f.write(f"Station ID: {s['id']}\n")
            f.write(f"Name: {s['name']}\n")
            f.write(f"Location: {s['latitude']:.5f}, {s['longitude']:.5f}\n")
            f.write(f"Daily Data: {'Yes' if s['has_daily'] else 'No'}\n")
            f.write(f"Instantaneous Data: {'Yes' if s['has_instant'] else 'No'}\n\n")

    map_html = generate_map(list(stations.values()), area_latlon, filtered)
    return filtered, txt_path, map_html
