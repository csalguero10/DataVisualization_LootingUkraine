import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
GEOJSON_PATH = r"stolen vs damaged\geoBoundaries-UKR-ADM1-all\geoBoundaries-UKR-ADM1.geojson"
OUT_HTML = "ukraine_oblast_hover_map_dropdown.html"

# ============================================================
# INPUT DATA
# ============================================================
region_summary = pd.DataFrame(
    [
        {"Region_label": "crimea",        "damaged_sites": 0,  "stolen_objects": 556},
        {"Region_label": "donetsk",       "damaged_sites": 89, "stolen_objects": 0},
        {"Region_label": "kharkiv",       "damaged_sites": 56, "stolen_objects": 0},
        {"Region_label": "kherson",       "damaged_sites": 16, "stolen_objects": 1296},
        {"Region_label": "kyiv",          "damaged_sites": 40, "stolen_objects": 0},
        {"Region_label": "luhansk",       "damaged_sites": 34, "stolen_objects": 0},
        {"Region_label": "mykolaiv",      "damaged_sites": 10, "stolen_objects": 0},
        {"Region_label": "odesa",         "damaged_sites": 49, "stolen_objects": 0},
        {"Region_label": "zaporizhzhya",  "damaged_sites": 13, "stolen_objects": 0},
    ]
)

iso_map = {
    "crimea": "UA-43",
    "donetsk": "UA-14",
    "kharkiv": "UA-63",
    "kherson": "UA-65",
    "kyiv": "UA-32",
    "luhansk": "UA-09",
    "mykolaiv": "UA-48",
    "odesa": "UA-51",
    "zaporizhzhya": "UA-23",
}

df = region_summary.copy()
df["Region_label"] = df["Region_label"].astype(str).str.strip().str.lower()
df["shapeISO"] = df["Region_label"].map(iso_map)

df["damaged_sites"] = pd.to_numeric(df["damaged_sites"], errors="coerce").fillna(0).astype(float)
df["stolen_objects"] = pd.to_numeric(df["stolen_objects"], errors="coerce").fillna(0).astype(float)

df["total"] = df["damaged_sites"] + df["stolen_objects"]
df["pct_stolen"] = np.where(df["total"] > 0, df["stolen_objects"] / df["total"] * 100.0, 0.0)

# LOG SCALE to avoid "all blue" because of outliers
df["total_log"] = np.log10(1.0 + df["total"])

# ============================================================
# LOAD GEOJSON + build a reference table
# ============================================================
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    ukr_geo = json.load(f)

geo_rows = []
for feat in ukr_geo["features"]:
    props = feat.get("properties", {})
    geo_rows.append({
        "shapeISO": props.get("shapeISO"),
        "shapeName": props.get("shapeName"),
    })
geo_df = pd.DataFrame(geo_rows).dropna(subset=["shapeISO"]).drop_duplicates("shapeISO")

# full coverage: all oblast from geojson + your data (0 if missing)
df_full = geo_df.merge(df, on="shapeISO", how="left")
for c in ["damaged_sites", "stolen_objects", "total", "pct_stolen", "total_log"]:
    df_full[c] = pd.to_numeric(df_full[c], errors="coerce").fillna(0).astype(float)

# debug
print(df_full.sort_values("total", ascending=False).head(12)[
    ["shapeISO","shapeName","total","stolen_objects","damaged_sites","pct_stolen","total_log"]
])
print("total min/max:", df_full["total"].min(), df_full["total"].max())
print("total_log min/max:", df_full["total_log"].min(), df_full["total_log"].max())

# hover text (always shows the real counts + pct)
hover = (
    df_full["shapeName"].astype(str)
    + "<br>ISO: " + df_full["shapeISO"].astype(str)
    + "<br>Stolen: " + df_full["stolen_objects"].astype(int).astype(str)
    + "<br>Damaged: " + df_full["damaged_sites"].astype(int).astype(str)
    + "<br>Total: " + df_full["total"].astype(int).astype(str)
    + "<br>pct_stolen: " + df_full["pct_stolen"].map(lambda v: f"{v:.1f}%")
)

# ============================================================
# METRICS FOR DROPDOWN (important: proper ranges)
# ============================================================
metrics = {
    "Total (log scale)": ("total_log", 0.0, float(df_full["total_log"].max() if df_full["total_log"].max() > 0 else 1.0), "log10(1+total)"),
    "Damaged sites": ("damaged_sites", 0.0, float(df_full["damaged_sites"].max() if df_full["damaged_sites"].max() > 0 else 1.0), "damaged"),
    "Stolen objects": ("stolen_objects", 0.0, float(df_full["stolen_objects"].max() if df_full["stolen_objects"].max() > 0 else 1.0), "stolen"),
    "pct_stolen (0–100)": ("pct_stolen", 0.0, 100.0, "% stolen"),
}

default_label = "Total (log scale)"
default_col, default_min, default_max, default_cbtitle = metrics[default_label]

# ============================================================
# PLOT
# ============================================================
fig = go.Figure(
    go.Choropleth(
        geojson=ukr_geo,
        locations=df_full["shapeISO"],
        featureidkey="properties.shapeISO",
        z=df_full[default_col],
        zmin=default_min,
        zmax=default_max,
        colorscale="Plasma",
        marker_line_color="black",
        marker_line_width=0.6,
        hovertemplate="%{text}<extra></extra>",
        text=hover,
        colorbar_title=default_cbtitle,
    )
)

# dropdown buttons
buttons = []
for label, (col, mn, mx, cbtitle) in metrics.items():
    buttons.append(
        dict(
            label=label,
            method="restyle",
            args=[{
                "z": [df_full[col]],
                "zmin": [mn],
                "zmax": [mx],
                "colorbar.title": [cbtitle],
            }],
        )
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    title="Destruction vs Looting by Oblast (hover for details)",
    margin=dict(l=0, r=0, t=60, b=0),
    updatemenus=[dict(
        type="dropdown",
        x=0.02, y=0.98,
        xanchor="left", yanchor="top",
        buttons=buttons
    )],
)

fig.write_html(OUT_HTML, include_plotlyjs=True)
print("Saved:", OUT_HTML)
