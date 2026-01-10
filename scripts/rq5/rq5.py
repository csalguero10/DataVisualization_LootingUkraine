#!/usr/bin/env python
"""
Waffle chart UNESCO protection vs damaged cultural sites L4R

sono siti che sono sttai distrutti e forse avrebbero potuto essere protetti con unesco dato che abbiamo visto funziona.
"""

import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------

# numero di colonne del waffle (modificalo per cambiare il “layout”)
GRID_COLUMNS = 30

# ordine e colori delle categorie nel waffle
CATEGORY_ORDER = [
    "Protected: World Heritage",
    "Destroyed: Religious",
    "Destroyed: Museums",
    "Destroyed: Libraries",
    "Destroyed: Other Historic",
]

CATEGORY_COLORS = {
    "Protected: World Heritage": "#f4d03f",   # giallo
    "Destroyed: Religious": "#b03a2e",        # rosso mattone
    "Destroyed: Museums": "#e67e22",          # arancione
    "Destroyed: Libraries": "#95a5a6",        # grigio
    "Destroyed: Other Historic": "#c0392b",   # rosso scuro
}

# disabilito il limite di righe di Altair (qui non serve ma è comodo)
alt.data_transformers.disable_max_rows()


# -----------------------------
# Funzioni di utilità
# -----------------------------

def load_paths_from_argv():
    """Legge i path da riga di comando o usa i default."""
    protected_path = sys.argv[1] if len(sys.argv) > 1 else "raw_data/unesco_ukraine_lists.csv"
    damaged_path = sys.argv[2] if len(sys.argv) > 2 else "raw_data/unesco_damage_sites.csv"
    output_html = sys.argv[3] if len(sys.argv) > 3 else "unesco_protection_waffle.html"
    return Path(protected_path), Path(damaged_path), Path(output_html)


def count_protected_sites(df_protected: pd.DataFrame) -> int:
    """
    Conta i siti UNESCO 'World Heritage List' in Ucraina.
    Adatta il filtro se usi una logica diversa.
    """
    # filtro di base: solo righe della World Heritage List
    mask = df_protected["category"].str.strip() == "World Heritage List"

    # se vuoi limitarti solo ai siti con 'Ukraine' nel campo location:
    # mask &= df_protected["location"].fillna("").str.contains("Ukraine", case=False)

    protected_sites = df_protected.loc[mask, "name"].dropna().unique()
    return len(protected_sites)


def map_damage_type_to_category(type_str: str) -> str:
    """
    Mappa il campo 'Type of damanged site' alla categoria del waffle.

    Qui faccio una mappatura molto semplice basata su parole chiave.
    Puoi raffinarla se hai categorie più pulite nel CSV.
    """
    if not isinstance(type_str, str):
        return "Destroyed: Other Historic"

    t = type_str.lower()

    if "religious" in t or "church" in t or "cathedral" in t or "lavra" in t or "monastery" in t:
        return "Destroyed: Religious"
    if "museum" in t:
        return "Destroyed: Museums"
    if "library" in t:
        return "Destroyed: Libraries"

    # tutto il resto
    return "Destroyed: Other Historic"


def count_damaged_by_category(df_damaged: pd.DataFrame) -> dict:
    """
    Conta i siti danneggiati per categoria (religious / museums / libraries / other).
    Considera solo le righe con 'Include or not (Yes/No)' == Yes.
    """
    include_col = "Include or not (Yes/No)"
    type_col = "Type of damanged site"

    # normalizzo la colonna Include/Yes
    mask_yes = (
        df_damaged[include_col]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
    )

    df_included = df_damaged.loc[mask_yes].copy()

    # mappo il tipo in categoria waffle
    df_included["waffle_category"] = df_included[type_col].apply(
        map_damage_type_to_category
    )

    counts = df_included["waffle_category"].value_counts().to_dict()

    # mi assicuro che tutte le categorie ci siano, anche se con 0
    for cat in CATEGORY_ORDER:
        counts.setdefault(cat, 0)

    return counts


def build_waffle_dataframe(protected_count: int, damaged_counts: dict) -> pd.DataFrame:
    """
    Costruisce un DataFrame con una riga per quadratino del waffle,
    e coordinate (x, y) della griglia.
    """
    rows = []
    idx = 0

    # 1) protetti
    for _ in range(protected_count):
        rows.append({"idx": idx, "category": "Protected: World Heritage"})
        idx += 1

    # 2) danneggiati per categoria
    for cat in CATEGORY_ORDER:
        if cat == "Protected: World Heritage":
            continue
        for _ in range(damaged_counts.get(cat, 0)):
            rows.append({"idx": idx, "category": cat})
            idx += 1

    df = pd.DataFrame(rows)

    # coordinate griglia
    df["x"] = df["idx"] % GRID_COLUMNS
    df["y"] = df["idx"] // GRID_COLUMNS

    # invertiamo l'asse y per avere la prima riga in alto
    max_y = df["y"].max()
    df["y"] = max_y - df["y"]

    return df


def build_chart(df_waffle: pd.DataFrame, protected_count: int, damaged_total: int) -> alt.Chart:
    """
    Crea il waffle chart Altair.
    """
    title_text = f"PROTECTION GAP: {protected_count} Protected vs {damaged_total} Destroyed"
    subtitle_text = "Each square is one cultural site"

    chart = (
        alt.Chart(df_waffle)
        .mark_square(size=90)
        .encode(
            x=alt.X("x:O", axis=None),
            y=alt.Y("y:O", axis=None),
            color=alt.Color(
                "category:N",
                legend=alt.Legend(title=None),
                scale=alt.Scale(
                    domain=CATEGORY_ORDER,
                    range=[CATEGORY_COLORS[c] for c in CATEGORY_ORDER],
                ),
            ),
            tooltip=["category:N"],
        )
        .properties(
            width=650,
            height=650,
            title=alt.TitleParams(
                text=title_text,
                subtitle=[subtitle_text],
                anchor="middle",
            ),
        )
    )

    return chart


# -----------------------------
# Main
# -----------------------------

def main():
    protected_path, damaged_path, output_html = load_paths_from_argv()

    # carico i CSV
    df_protected = pd.read_csv(protected_path, encoding="utf-8")
    df_damaged = pd.read_csv(damaged_path, encoding="utf-8")

    # 1) conteggio siti protetti (UNESCO World Heritage in Ucraina)
    protected_count = count_protected_sites(df_protected)

    # 2) conteggio siti danneggiati per categoria
    damaged_counts = count_damaged_by_category(df_damaged)
    damaged_total = sum(
        count
        for cat, count in damaged_counts.items()
        if cat != "Protected: World Heritage"
    )

    # 3) costruzione DataFrame per waffle
    df_waffle = build_waffle_dataframe(protected_count, damaged_counts)

    # 4) creazione grafico
    chart = build_chart(df_waffle, protected_count, damaged_total)

    # 5) salvataggio HTML
    chart.save(output_html)
    print(f"Waffle chart salvato in: {output_html}")


if __name__ == "__main__":
    main()
