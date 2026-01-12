import pandas as pd
import numpy as np
from datetime import datetime
import os

PATH_ACLED = "DisperseArt_InformationVisualization/raw_data/ACLED Data_2025-12-21.csv"
OUT_DIR    = "DisperseArt_InformationVisualization/processed_data"
OUT_PATH   = os.path.join(OUT_DIR, "acled_clean.csv")

def clean_acled_data(path):
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8", on_bad_lines="skip", engine="python")
        df.columns = df.columns.str.strip()

        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        df = df[df['event_date'] >= datetime(2014, 1, 1)]

        # Filtro tipi di evento (Includiamo Violence against civilians per il Looting)
        include_events = [
            "Explosions/Remote violence",
            "Battles",
            "Violence against civilians",
            "Strategic developments"
        ]
        df = df[df['event_type'].isin(include_events)]

        df = df.dropna(subset=['event_date', 'latitude', 'longitude']).copy()

        df = df.rename(columns={
            'event_date': 'ACLED_Date',
            'latitude': 'ACLED_Lat',
            'longitude': 'ACLED_Lon',
            'event_type': 'ACLED_EventType',
            'sub_event_type': 'ACLED_SubEvent',
            'notes': 'ACLED_Notes'
        })

        return df
    except Exception as e:
        print(f"Error processing ACLED data: {e}")
        return pd.DataFrame()

df_acled_clean = clean_acled_data(PATH_ACLED)

if not df_acled_clean.empty:
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    
    df_acled_clean.to_csv(OUT_PATH, index=False, sep=";")
    print(f"ACLED Dataset Cleaned: {df_acled_clean.shape[0]} events processed.")
    print(f"File salvato con successo in: {OUT_PATH}")
else:
    print("Errore: Il DataFrame è vuoto, niente da salvare.")

df_acled_clean.head(3)