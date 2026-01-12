import requests
import pandas as pd
import re
import os
from rdflib import Dataset

PATH_L4R_TRIG_URL = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/refs/heads/main/raw_data/https___linked4resilience.eu_graphs_cultural-site-damage-events.trig"

LOCAL_TRIG_PATH = "cultural-site-damage-events.trig"
OUTPUT_DIR = "DisperseArt_InformationVisualization/processed_data"
OUTPUT_FILE = "cultural_damage_L4R2.csv"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

def download_file(url, local_path):
    """Scarica il file .trig se non è già presente localmente."""
    if not os.path.exists(local_path):
        print(f"Downloading knowledge graph from GitHub...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print("Download complete.")
        except Exception as e:
            print(f"Error during download: {e}")
            return False
    return True

def extract_linked4resilience_data(path):
    """Analizza il file TriG ed estrae i metadati tramite SPARQL."""
    if not os.path.exists(path):
        print(f"Error: File {path} not found.")
        return pd.DataFrame()

    print("Parsing TriG file (this may take a moment)...")
    g = Dataset()
    g.parse(path, format="trig")
    print(f"✓ Parsed {len(g)} triples.")

    query = """
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX schema: <https://schema.org/>
    PREFIX vocab: <https://linked4resilience.eu/vocab/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?site ?name ?address ?observationYear ?comment ?wikiUA ?newsLink ?wkt
    WHERE {
      GRAPH ?g {
        ?site geo:hasGeometry ?geom .
        ?geom geo:asWKT ?wkt .
        OPTIONAL { ?site schema:name ?name . }
        OPTIONAL { ?site schema:address ?address . }
        OPTIONAL { ?site schema:observationTime ?observationYear . }
        OPTIONAL { ?site rdfs:comment ?comment . }
        OPTIONAL { ?site vocab:wikipediaUkrainian ?wikiUA . }
        OPTIONAL { ?site vocab:wasMentionedIn ?newsLink . }
      }
    }
    """

    results = g.query(query)
    extracted_records = []

    for row in results:
        # Regex per estrarre Lat/Lon dal formato WKT: "POINT(lon lat)"
        wkt_text = str(row["wkt"])
        lon, lat = None, None
        coord_match = re.search(r"POINT\s*\(\s*([-0-9\.]+)\s+([-0-9\.]+)\s*\)", wkt_text, flags=re.IGNORECASE)
        if coord_match:
            lon, lat = float(coord_match.group(1)), float(coord_match.group(2))

        extracted_records.append({
            "URI": str(row["site"]),
            "Site_Name": str(row["name"]) if row["name"] else None,
            "Address": str(row["address"]) if row["address"] else None,
            "Observation_Year": str(row["observationYear"]) if row["observationYear"] else None,
            "Comment": str(row["comment"]) if row["comment"] else None,
            "Wiki_UA_Link": str(row["wikiUA"]) if row["wikiUA"] else None,
            "News_Link": str(row["newsLink"]) if row["newsLink"] else None,
            "Latitude": lat,
            "Longitude": lon
        })

    return pd.DataFrame(extracted_records)

def main():
    if download_file(PATH_L4R_TRIG_URL, LOCAL_TRIG_PATH):

        df = extract_linked4resilience_data(LOCAL_TRIG_PATH)

        if not df.empty:
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
            print(f"Success! Saved {len(df)} records to: {OUTPUT_PATH}")
            print("\nPreview:")
            print(df.head())
        else:
            print("Error: No data extracted.")

if __name__ == "__main__":
    main()