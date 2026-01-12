import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from matplotlib.lines import Line2D


# geopandas stack
import geopandas as gpd

plt.style.use("default")

# -----------------------
# CONFIG
# -----------------------
YEAR_MIN = 2022
USE_BBOX = True
ADD_ACLED = True
ACLED_YEAR_MIN = 2022
ACLED_MODE = "two_layers"  # "two_layers" recommended

OUTFILE = "map_plus_bar_2022.png"

URL_STOLEN = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/main/stolen_objects_ukraine_cleaned.csv"
URL_UNESCO = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/main/raw_data/unesco_damage_sites.csv"
URL_ACLED  = "https://media.githubusercontent.com/media/csalguero10/DisperseArt_InformationVisualization/bc92f709426671effb51f96261de4a53e2ac7b1b/processed_data/acled_clean.csv"

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

COLOR_STOLEN = "red"
COLOR_UNESCO = "tab:blue"

# -----------------------
# HELPERS
# -----------------------
def in_ukraine_bbox(lat, lon):
    return (lat >= 44) & (lat <= 53.8) & (lon >= 22) & (lon <= 41.5)

def extract_lat_lon(gmaps_url):
    """Parse lat/lon from Google Maps link if needed."""
    if pd.isna(gmaps_url):
        return (np.nan, np.nan)
    s = str(gmaps_url)

    m = re.search(r"[?&]q=([-0-9.]+)\s*,\s*([-0-9.]+)", s)
    if m:
        return (float(m.group(1)), float(m.group(2)))

    m = re.search(r"@([-0-9.]+)\s*,\s*([-0-9.]+)", s)
    if m:
        return (float(m.group(1)), float(m.group(2)))

    return (np.nan, np.nan)

def normalize_region_name(region):
    if not isinstance(region, str):
        return np.nan
    r = region.lower()

    if "kherson" in r:
        return "kherson"
    if "crimea" in r:
        return "crimea"
    if "donetsk" in r:
        return "donetsk"
    if "luhansk" in r:
        return "luhansk"
    if "kharkiv" in r:
        return "kharkiv"
    if "odesa" in r:
        return "odesa"
    if "mykolaiv" in r:
        return "mykolaiv"
    if "kyiv" in r:
        return "kyiv"
    if "zaporizh" in r:
        return "zaporizhzhya"

    return np.nan

def region_from_coords(lat, lon):
    """Very rough proxy clusters (as in your Colab)."""
    if pd.isna(lat) or pd.isna(lon):
        return np.nan

    # Kherson region (museum cluster)
    if 46.4 <= lat <= 46.8 and 32.4 <= lon <= 32.8:
        return "kherson"

    # Crimea
    if 44.5 <= lat <= 45.8 and 33.5 <= lon <= 36.5:
        return "crimea"

    # Donetsk
    if 47.5 <= lat <= 48.5 and 36.5 <= lon <= 38.5:
        return "donetsk"

    return np.nan

# -----------------------
# LOAD DATA
# -----------------------
print("Loading datasets...")
stolen = pd.read_csv(URL_STOLEN)
unesco = pd.read_csv(URL_UNESCO)
acled  = pd.read_csv(URL_ACLED, sep=";")
print("✓ stolen:", stolen.shape, "| unesco:", unesco.shape, "| acled:", acled.shape)

# -----------------------
# UNESCO PREP: year + coords + region
# -----------------------
unesco = unesco.copy()

unesco["UNESCO_Date"] = pd.to_datetime(unesco.get("Date of damage (first reported)"), errors="coerce")
unesco["UNESCO_Year"] = unesco["UNESCO_Date"].dt.year

# region clean
if "Region" in unesco.columns:
    unesco["Region_clean"] = unesco["Region"].astype(str).str.strip().str.lower()
else:
    unesco["Region_clean"] = np.nan

unesco["Region_norm"] = unesco["Region_clean"].apply(normalize_region_name)

# coords
if "Geo location" in unesco.columns:
    coords = unesco["Geo location"].astype(str).str.split(",", expand=True)
    if coords.shape[1] >= 2:
        unesco["LAT"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        unesco["LON"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")
    else:
        unesco["LAT"] = np.nan
        unesco["LON"] = np.nan
else:
    # if your file already has LAT/LON, keep them; else NaN
    if "LAT" not in unesco.columns:
        unesco["LAT"] = np.nan
    if "LON" not in unesco.columns:
        unesco["LON"] = np.nan

# filter year
if YEAR_MIN is not None:
    unesco = unesco[unesco["UNESCO_Year"] >= YEAR_MIN]

# -----------------------
# STOLEN PREP: year + coords + region proxy
# -----------------------
stolen = stolen.copy()

# year (incident preferred)
stolen_year = pd.to_numeric(stolen.get("year_incident"), errors="coerce")
stolen_year = stolen_year.fillna(pd.to_numeric(stolen.get("year_for_timeline"), errors="coerce"))
stolen["year_clean_num"] = stolen_year.where((stolen_year >= 1900) & (stolen_year <= 2100))

# coords: use latitude_num/longitude_num if present, else parse google_maps_link
if ("latitude_num" in stolen.columns) and ("longitude_num" in stolen.columns):
    stolen["latitude_num"] = pd.to_numeric(stolen["latitude_num"], errors="coerce")
    stolen["longitude_num"] = pd.to_numeric(stolen["longitude_num"], errors="coerce")
elif ("latitude" in stolen.columns) and ("longitude" in stolen.columns):
    stolen["latitude_num"] = pd.to_numeric(stolen["latitude"], errors="coerce")
    stolen["longitude_num"] = pd.to_numeric(stolen["longitude"], errors="coerce")
elif "google_maps_link" in stolen.columns:
    latlon = stolen["google_maps_link"].apply(lambda x: pd.Series(extract_lat_lon(x)))
    stolen["latitude_num"] = pd.to_numeric(latlon[0], errors="coerce")
    stolen["longitude_num"] = pd.to_numeric(latlon[1], errors="coerce")
else:
    stolen["latitude_num"] = np.nan
    stolen["longitude_num"] = np.nan

# filter year
if YEAR_MIN is not None:
    stolen = stolen[stolen["year_clean_num"] >= YEAR_MIN]

# bbox sanity
stolen = stolen[
    stolen["latitude_num"].between(-90, 90) &
    stolen["longitude_num"].between(-180, 180)
]

# region proxy (cluster)
stolen["Region_proxy"] = stolen.apply(
    lambda r: region_from_coords(r["latitude_num"], r["longitude_num"]),
    axis=1
)

# -----------------------
# ACLED PREP (for map background)
# -----------------------
acled_map = acled.copy()
acled_map["ACLED_Date"] = pd.to_datetime(acled_map.get("ACLED_Date"), errors="coerce")
acled_map["ACLED_Year"] = acled_map["ACLED_Date"].dt.year

if ACLED_YEAR_MIN is not None:
    acled_map = acled_map[acled_map["ACLED_Year"] >= ACLED_YEAR_MIN]

# require coords
acled_map = acled_map.dropna(subset=["ACLED_Lat", "ACLED_Lon"]).copy()
acled_map["ACLED_Lat"] = pd.to_numeric(acled_map["ACLED_Lat"], errors="coerce")
acled_map["ACLED_Lon"] = pd.to_numeric(acled_map["ACLED_Lon"], errors="coerce")

# bbox filter
if USE_BBOX:
    acled_map = acled_map[in_ukraine_bbox(acled_map["ACLED_Lat"], acled_map["ACLED_Lon"])]

gdf_acled_destruct = None
gdf_acled_occup = None
gdf_acled_all = None

if ADD_ACLED:
    if ACLED_MODE == "two_layers":
        acled_destruct = acled_map[acled_map["ACLED_EventType"].isin(["Explosions/Remote violence", "Battles"])].copy()
        acled_occup = acled_map[acled_map["ACLED_EventType"].isin(["Violence against civilians", "Strategic developments"])].copy()

        gdf_acled_destruct = gpd.GeoDataFrame(
            acled_destruct,
            geometry=gpd.points_from_xy(acled_destruct["ACLED_Lon"], acled_destruct["ACLED_Lat"]),
            crs="EPSG:4326"
        )
        gdf_acled_occup = gpd.GeoDataFrame(
            acled_occup,
            geometry=gpd.points_from_xy(acled_occup["ACLED_Lon"], acled_occup["ACLED_Lat"]),
            crs="EPSG:4326"
        )
        print("ACLED destruct:", len(gdf_acled_destruct), "| ACLED occup:", len(gdf_acled_occup))
    else:
        gdf_acled_all = gpd.GeoDataFrame(
            acled_map,
            geometry=gpd.points_from_xy(acled_map["ACLED_Lon"], acled_map["ACLED_Lat"]),
            crs="EPSG:4326"
        )
        print("ACLED total:", len(gdf_acled_all))

# -----------------------
# BUILD GDFs FOR UNESCO + STOLEN
# -----------------------
unesco_pts = unesco.dropna(subset=["LAT", "LON"]).copy()
unesco_pts["LAT"] = pd.to_numeric(unesco_pts["LAT"], errors="coerce")
unesco_pts["LON"] = pd.to_numeric(unesco_pts["LON"], errors="coerce")
unesco_pts = unesco_pts.dropna(subset=["LAT", "LON"])

stolen_pts = stolen.dropna(subset=["latitude_num", "longitude_num"]).copy()

if USE_BBOX:
    unesco_pts = unesco_pts[in_ukraine_bbox(unesco_pts["LAT"], unesco_pts["LON"])]
    stolen_pts = stolen_pts[in_ukraine_bbox(stolen_pts["latitude_num"], stolen_pts["longitude_num"])]

gdf_unesco = gpd.GeoDataFrame(
    unesco_pts,
    geometry=gpd.points_from_xy(unesco_pts["LON"], unesco_pts["LAT"]),
    crs="EPSG:4326"
)
gdf_stolen = gpd.GeoDataFrame(
    stolen_pts,
    geometry=gpd.points_from_xy(stolen_pts["longitude_num"], stolen_pts["latitude_num"]),
    crs="EPSG:4326"
)

# -----------------------
# REGION SUMMARY (for bar chart)
# -----------------------
unesco_region_counts = (
    unesco.dropna(subset=["Region_norm"])
    .groupby("Region_norm").size()
    .reset_index(name="damaged_sites")
)

stolen_region_counts = (
    stolen.dropna(subset=["Region_proxy"])
    .groupby("Region_proxy").size()
    .reset_index(name="stolen_objects")
)

region_summary = pd.merge(
    unesco_region_counts,
    stolen_region_counts,
    left_on="Region_norm",
    right_on="Region_proxy",
    how="outer"
)

region_summary["damaged_sites"] = region_summary["damaged_sites"].fillna(0).astype(int)
region_summary["stolen_objects"] = region_summary["stolen_objects"].fillna(0).astype(int)

region_summary["Region_label"] = (
    region_summary["Region_norm"].astype("string")
    .fillna(region_summary["Region_proxy"].astype("string"))
)

region_summary = region_summary.dropna(subset=["Region_label"])

# -----------------------
# WORLD CONTEXT (neighbors)
# -----------------------
world = gpd.read_file(NE_URL).to_crs("EPSG:4326")

name_col = "NAME" if "NAME" in world.columns else ("name" if "name" in world.columns else None)
if name_col is None:
    raise ValueError("Natural Earth: cannot find a country name column.")

ukraine_poly = world[world[name_col] == "Ukraine"].copy()
if len(ukraine_poly) == 0:
    raise ValueError("Ukraine polygon not found in Natural Earth file.")

ukr_geom = ukraine_poly.geometry.iloc[0]

minx, miny, maxx, maxy = ukr_geom.bounds
padx, pady = 6.0, 4.0
xlim = (minx - padx, maxx + padx)
ylim = (miny - pady, maxy + pady)
context = world.cx[xlim[0]:xlim[1], ylim[0]:ylim[1]].copy()

# -----------------------
# PLOT: MAP + BAR
# -----------------------
df = region_summary.copy()
df["total"] = df["damaged_sites"] + df["stolen_objects"]
df = df.sort_values("total", ascending=False)

regions = df["Region_label"].astype(str)
damaged = df["damaged_sites"].values
stolen_counts = df["stolen_objects"].values

fig = plt.figure(figsize=(16, 8))
gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.0], wspace=0.12)

ax_map = fig.add_subplot(gs[0, 0])
ax_bar = fig.add_subplot(gs[0, 1])

# MAP
context.plot(ax=ax_map, color="#f2f2f2", edgecolor="#666666", linewidth=0.6)
ukraine_poly.plot(ax=ax_map, color="white", edgecolor="black", linewidth=1.1)

if ADD_ACLED:
    if ACLED_MODE == "two_layers":
        if gdf_acled_destruct is not None:
            gdf_acled_destruct.plot(ax=ax_map, markersize=2, alpha=0.05, color="#7fc97f")
        if gdf_acled_occup is not None:
            gdf_acled_occup.plot(ax=ax_map, markersize=2, alpha=0.05, color="#fdae61")
    else:
        if gdf_acled_all is not None:
            gdf_acled_all.plot(ax=ax_map, markersize=2, alpha=0.05)

gdf_unesco.plot(ax=ax_map, markersize=30, alpha=0.85, color=COLOR_UNESCO)
gdf_stolen.plot(ax=ax_map, markersize=40, alpha=0.85, color=COLOR_STOLEN, 
                edgecolor="black", linewidth=0.25)

legend_handles = [
    Line2D([0], [0], marker="o", linestyle="None",
           markerfacecolor="#7fc97f", markeredgecolor="#7fc97f",
           markersize=8, label="ACLED: destruction context"),
    Line2D([0], [0], marker="o", linestyle="None",
           markerfacecolor="#fdae61", markeredgecolor="#fdae61",
           markersize=8, label="ACLED: occupation/coercion context"),
    Line2D([0], [0], marker="o", linestyle="None",
           markerfacecolor=COLOR_UNESCO, markeredgecolor=COLOR_UNESCO,
           markersize=8, label="UNESCO damaged sites"),
    Line2D([0], [0], marker="o", linestyle="None",
           markerfacecolor=COLOR_STOLEN, markeredgecolor="black",
           markersize=8, label="Stolen objects"),
]

leg = ax_map.legend(handles=legend_handles, loc="lower left", frameon=True)
leg.get_frame().set_alpha(0.9)

ax_map.set_xlim(*xlim)
ax_map.set_ylim(*ylim)
ax_map.set_xlabel("Longitude")
ax_map.set_ylabel("Latitude")
ax_map.grid(alpha=0.2)

# BAR

x = np.arange(len(regions))
width = 0.38
ax_bar.bar(x - width/2, damaged, width, label="UNESCO damaged sites", color=COLOR_UNESCO)
ax_bar.bar(x + width/2, stolen_counts, width, label="Stolen objects", color=COLOR_STOLEN)

ax_bar.set_xticks(x)
ax_bar.set_xticklabels(regions, rotation=45, ha="right")
ax_bar.set_ylabel("Count")
ax_bar.set_title(f"Destruction vs Looting by Region (Year ≥ {YEAR_MIN})")
ax_bar.grid(axis="y", alpha=0.25)
ax_bar.legend(loc="upper right", frameon=True)

fig.suptitle(f"Cultural harm locations and regional asymmetry (Year ≥ {YEAR_MIN})", y=0.98)

plt.tight_layout()
plt.savefig(OUTFILE, dpi=200, bbox_inches="tight")
plt.show()

print("Saved:", OUTFILE)
