import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

plt.style.use("default")

# -----------------------
# LOAD UNESCO
# -----------------------
URL_UNESCO = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/main/raw_data/unesco_damage_sites.csv"
unesco = pd.read_csv(URL_UNESCO)
OUTFILE = "unesco_types_and_periods.png"
plt.savefig(OUTFILE, dpi=200, bbox_inches="tight")


# -----------------------
# BASIC COLUMNS
# -----------------------
unesco["site_type"] = (
    unesco["Type of damanged site"]
    .astype(str)
    .str.lower()
    .str.strip()
)

unesco["title_en"] = unesco["Title of the damage site in English"].astype(str)

# -------------------------
# 1) REMOVE "REGION HEADER" ROWS (fake rows)
# Some files have region headers in an unnamed col.
# We'll try both patterns (title_en and unnamed col).
# -------------------------
region_header_pattern = r"^\s*\d+\s+site(?:s)?\s+in\s+(?:the\s+)?.+?\s+region\s*$"

mask_header_title = unesco["title_en"].str.strip().str.match(
    region_header_pattern, flags=re.IGNORECASE, na=False
)

# Sometimes headers are in "Unnamed: 0"
mask_header_unnamed = pd.Series(False, index=unesco.index)
if "Unnamed: 0" in unesco.columns:
    mask_header_unnamed = (
        unesco["Unnamed: 0"].astype(str).str.strip()
        .str.match(region_header_pattern, flags=re.IGNORECASE, na=False)
    )

mask_header = mask_header_title | mask_header_unnamed
unesco_clean = unesco.loc[~mask_header].copy()

# -------------------------
# 2) Recode type (clean semantic mapping)
# -------------------------
def recode_type(row):
    raw = row.get("site_type", "")
    title = str(row.get("title_en", "")).lower()

    # religious
    if any(k in title for k in ["church", "cathedral", "chapel", "monastery", "house of prayer"]):
        return "religious site"

    # theatre / cultural institution
    if any(k in title for k in ["theatre", "theater", "concert hall", "house of culture", "philharmonic"]):
        return "theatre / cultural institution"

    # education
    if any(k in title for k in ["academy", "university", "conservatory", "school"]):
        return "education"

    # museums / libraries / archives
    if ("museum" in title) or ("gallery" in title):
        return "museum"
    if "library" in title:
        return "library"
    if "archive" in title:
        return "archive"

    # archaeological
    if "archaeological" in title:
        return "archaeological site"

    # normalize raw
    if isinstance(raw, str):
        raw = raw.strip().lower()

        # whitelist known UNESCO labels
        if raw in ["religious site", "museum", "library", "archive", "monument", "archaeological site", "education"]:
            return raw

        if "building of historical" in raw:
            return "building of historical and/or artistic interest"

        # infer historical/artistic if title says so
        if "architectural" in title and "monument of local importance" in title:
            return "building of historical and/or artistic interest"

        if raw == "other":
            return "other"

        if raw != "" and raw != "nan":
            return raw

    # fallback
    if "architectural" in title and "monument of local importance" in title:
        return "building of historical and/or artistic interest"

    return "other"


unesco_clean["site_type_clean"] = unesco_clean.apply(recode_type, axis=1)

# Optional dedup (same title + region + date)
DEDUP = True
if DEDUP and ("Region" in unesco_clean.columns) and ("Date of damage (first reported)" in unesco_clean.columns):
    unesco_clean["dedup_key"] = (
        unesco_clean["title_en"].str.lower().str.strip()
        + " | " + unesco_clean["Region"].astype(str).str.lower().str.strip()
        + " | " + unesco_clean["Date of damage (first reported)"].astype(str).str.strip()
    )
    before = len(unesco_clean)
    unesco_clean = unesco_clean.drop_duplicates(subset=["dedup_key"], keep="first").copy()
    print("Dedup removed:", before - len(unesco_clean))

# Remove nan-like types
unesco_clean = unesco_clean[
    unesco_clean["site_type_clean"].notna() &
    (unesco_clean["site_type_clean"].astype(str).str.lower() != "nan")
].copy()

# Counts (types)
type_counts = unesco_clean["site_type_clean"].value_counts().sort_values(ascending=True)

# -------------------------
# 3) PERIODS — extract construction year
# -------------------------
def extract_year_extended(text):
    if pd.isna(text):
        return np.nan
    s = str(text).strip().lower()

    # ranges like "1851–1852" or "1851-1852" -> first year
    m = re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\s*[–-]\s*(1[0-9]{3}|20[0-2][0-9])\b", s)
    if m:
        return float(m.group(1))

    # explicit year
    m = re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", s)
    if m:
        return float(m.group(1))

    # centuries approximation
    if ("xix" in s) or ("19th century" in s) or ("19 century" in s):
        return 1850.0
    if ("xviii" in s) or ("18th century" in s) or ("18 century" in s):
        return 1750.0
    if ("xxi" in s) or ("21st century" in s) or ("21 century" in s):
        return 2010.0
    if ("xx" in s) or ("20th century" in s) or ("20 century" in s):
        return 1950.0

    return np.nan


if "Year of construction" in unesco_clean.columns:
    unesco_clean["year_built_num_ext"] = unesco_clean["Year of construction"].apply(extract_year_extended)
else:
    unesco_clean["year_built_num_ext"] = np.nan

unesco_clean["year_built_num_ext"] = unesco_clean["year_built_num_ext"].where(
    (unesco_clean["year_built_num_ext"] >= 800) & (unesco_clean["year_built_num_ext"] <= 2025)
)

def historical_period_ua(year):
    if pd.isna(year):
        return np.nan
    y = int(year)

    if y <= 1054:
        return "Kyivan Rus’ (839–1054)"
    elif y <= 1200:
        return "Galicia–Volhynia & fragmentation (1054–1200)"
    elif y <= 1600:
        return "Mongol & multi-power domination (1239–1600)"
    elif y <= 1764:
        return "Cossack Hetmanate (1648–1764)"
    elif y <= 1917:
        return "Russian Empire (1764–1917)"
    elif y <= 1921:
        return "Early Independence (1917–1921)"
    elif y <= 1991:
        return "Soviet period (1921–1991)"
    else:
        return "Independent Ukraine (1991–2025)"

unesco_clean["historical_period_new"] = unesco_clean["year_built_num_ext"].apply(historical_period_ua)

order_new = [
    "Kyivan Rus’ (839–1054)",
    "Galicia–Volhynia & fragmentation (1054–1200)",
    "Mongol & multi-power domination (1239–1600)",
    "Cossack Hetmanate (1648–1764)",
    "Russian Empire (1764–1917)",
    "Early Independence (1917–1921)",
    "Soviet period (1921–1991)",
    "Independent Ukraine (1991–2025)",
]

period_counts = (
    unesco_clean.dropna(subset=["historical_period_new"])
    .groupby("historical_period_new")
    .size()
    .reindex(order_new)  # keep timeline order
    .dropna()
    .astype(int)
)

period_counts = period_counts.sort_index(key=lambda s: [order_new.index(x) for x in s])

# Coverage print
total = len(unesco_clean)
parsed = int(unesco_clean["year_built_num_ext"].notna().sum())
print(f"Coverage (construction year parsed): {parsed}/{total} ({parsed/total*100:.1f}%)")

# -------------------------
# 4) ONE FIGURE — two panels
# -------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19, 6))
fig.subplots_adjust(wspace=0.55)

# --- Left: Types ---
ax1.barh(type_counts.index.astype(str), type_counts.values)
ax1.set_title("Damaged sites by type (UNESCO)")
ax1.set_xlabel("Number of damaged sites")
ax1.grid(axis="x", alpha=0.25)
ax1.invert_yaxis()

maxv1 = max(type_counts.values) if len(type_counts) else 1
for i, v in enumerate(type_counts.values):
    ax1.text(v + maxv1 * 0.01, i, str(int(v)), va="center")

# --- Right: Periods (short labels) ---
period_labels_short = [p.split(" (")[0] for p in period_counts.index.astype(str)]

ax2.barh(period_labels_short, period_counts.values)
ax2.set_title("Damaged sites by historical period (UNESCO)")
ax2.set_xlabel("Number of damaged sites")
ax2.grid(axis="x", alpha=0.25)
ax2.invert_yaxis()
ax2.tick_params(axis="y", labelsize=10)

maxv2 = max(period_counts.values) if len(period_counts) else 1
for i, v in enumerate(period_counts.values):
    ax2.text(v + maxv2 * 0.01, i, str(int(v)), va="center")

fig.suptitle("What gets damaged: heritage categories and historical layers", y=1.03, fontsize=16)
plt.tight_layout()

OUTFILE = "unesco_types_and_periods.png"
plt.savefig(OUTFILE, dpi=200, bbox_inches="tight")
plt.show()
print("Saved:", OUTFILE)

