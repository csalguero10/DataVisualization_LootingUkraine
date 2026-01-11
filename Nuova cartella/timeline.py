import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("default")

# -----------------------
# CONFIG
# -----------------------
YEAR_MIN = 2014
YEAR_MAX = None  # e.g. 2025
OUTFILE = "timeline_cultural_harm_vs_acled.png"  # save in repo (e.g. /docs/assets/)

# -----------------------
# LOAD DATA
# -----------------------
URL_STOLEN = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/main/data_stolen/stolen_objects_ukraine_cleaned.csv"
URL_UNESCO = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/main/raw_data/unesco_damage_sites.csv"
URL_ACLED  = "https://media.githubusercontent.com/media/csalguero10/DisperseArt_InformationVisualization/bc92f709426671effb51f96261de4a53e2ac7b1b/processed_data/acled_clean.csv"

stolen = pd.read_csv(URL_STOLEN)
unesco = pd.read_csv(URL_UNESCO)
acled  = pd.read_csv(URL_ACLED, sep=";")

# -----------------------
# YEARS: STOLEN (incident year) + UNESCO
# -----------------------
# stolen: prefer incident year, fallback to year_for_timeline
stolen_year = pd.to_numeric(stolen.get("year_incident"), errors="coerce")
stolen_year = stolen_year.fillna(pd.to_numeric(stolen.get("year_for_timeline"), errors="coerce"))
stolen_year = stolen_year.where((stolen_year >= 1900) & (stolen_year <= 2100))

# unesco: parse "Date of damage (first reported)"
unesco_date = pd.to_datetime(unesco.get("Date of damage (first reported)"), errors="coerce")
unesco_year = unesco_date.dt.year

# filter range
if YEAR_MIN is not None:
    stolen_year = stolen_year.where(stolen_year >= YEAR_MIN)
    unesco_year = unesco_year.where(unesco_year >= YEAR_MIN)
if YEAR_MAX is not None:
    stolen_year = stolen_year.where(stolen_year <= YEAR_MAX)
    unesco_year = unesco_year.where(unesco_year <= YEAR_MAX)

stolen_counts = stolen_year.dropna().astype(int).value_counts().sort_index()
unesco_counts = unesco_year.dropna().astype(int).value_counts().sort_index()

# -----------------------
# ACLED: year + 2 contexts
# -----------------------
acled_tmp = acled.copy()
acled_tmp["ACLED_Date"] = pd.to_datetime(acled_tmp["ACLED_Date"], errors="coerce")
acled_tmp["ACLED_Year"] = acled_tmp["ACLED_Date"].dt.year

if YEAR_MIN is not None:
    acled_tmp = acled_tmp[acled_tmp["ACLED_Year"] >= YEAR_MIN]
if YEAR_MAX is not None:
    acled_tmp = acled_tmp[acled_tmp["ACLED_Year"] <= YEAR_MAX]

# Context buckets
destruction_types = {"Explosions/Remote violence", "Battles"}
occupation_types  = {"Violence against civilians", "Strategic developments"}

acled_destruct = acled_tmp[acled_tmp["ACLED_EventType"].isin(destruction_types)]
acled_occup    = acled_tmp[acled_tmp["ACLED_EventType"].isin(occupation_types)]

acled_destruct_counts = acled_destruct["ACLED_Year"].value_counts().sort_index()
acled_occup_counts    = acled_occup["ACLED_Year"].value_counts().sort_index()

# -----------------------
# ALIGN YEARS (common axis)
# -----------------------
all_years = sorted(
    set(stolen_counts.index)
    | set(unesco_counts.index)
    | set(acled_destruct_counts.index)
    | set(acled_occup_counts.index)
)

stolen_aligned = stolen_counts.reindex(all_years, fill_value=0)
unesco_aligned = unesco_counts.reindex(all_years, fill_value=0)
acled_destruct_aligned = acled_destruct_counts.reindex(all_years, fill_value=0)
acled_occup_aligned    = acled_occup_counts.reindex(all_years, fill_value=0)

# -----------------------
# PLOT (dual y-axis)
# -----------------------
fig, ax1 = plt.subplots(figsize=(14, 6))

# Left axis (cultural harm)
ax1.plot(
    all_years,
    stolen_aligned.values,
    marker="o",
    color="red",
    label="Stolen objects"
)
ax1.plot(all_years, unesco_aligned.values, marker="o", label="UNESCO damaged sites")
ax1.set_xlabel("Year")
ax1.set_ylabel("Count (cultural datasets)")
ax1.grid(alpha=0.3)

# Right axis (ACLED)
ax2 = ax1.twinx()
ax2.plot(
    all_years,
    acled_destruct_aligned.values,
    linestyle="--",
    alpha=0.6,
    label="ACLED destruction context (remote violence & battles)"
)

ax2.plot(
    all_years,
    acled_occup_aligned.values,
    linestyle="--",
    alpha=0.6,
    label="ACLED occupation & coercion context"
)

ax2.set_ylabel("Count (ACLED events)")



# Title (message, not description)
ax1.set_title("Cultural harm intensifies with war, but persists under occupation")

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig(OUTFILE, dpi=200)
plt.show()

print("Saved:", OUTFILE)
print("ACLED destruction total:", int(acled_destruct_aligned.sum()))
print("ACLED occupation total:", int(acled_occup_aligned.sum()))
