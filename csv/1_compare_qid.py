"""
uso l4r e lista unesco per confrontare qid se hanno gli stessi --> spoiler non ne hanno. good job unesco.
"""

import pandas as pd
import csv

def read_csv_with_semicolon(filepath):
    """Legge un CSV con separatore punto e virgola"""
    return pd.read_csv(filepath, delimiter=';', encoding='utf-8')

def read_csv_with_comma(filepath):
    """Legge un CSV con separatore virgola"""
    return pd.read_csv(filepath, delimiter=',', encoding='utf-8')

def extract_qids_from_dataframe(df, qid_column):
    """Estrae tutti i QID unici da un dataframe"""
    qids = set()
    for qid in df[qid_column].dropna().unique():
        # Pulisci il QID se necessario (rimuovi spazi, ecc.)
        qid_clean = str(qid).strip()
        if qid_clean.startswith('Q') and qid_clean[1:].isdigit():
            qids.add(qid_clean)
    return qids

def find_matches():
    # Percorsi dei file (modifica questi percorsi se necessario)
    csv1_path = 'DisperseArt_InformationVisualization/raw_data/unesco_ukraine_lists_qid.csv'  # File con separatore ;
    csv2_path = 'DisperseArt_InformationVisualization/csv/cultural_damage_wikidata_enriched_improved.csv'  # File con separatore ,
    
    # Leggi i file CSV
    print("Leggo i file CSV...")
    try:
        df1 = read_csv_with_semicolon(csv1_path)
        df2 = read_csv_with_comma(csv2_path)
    except FileNotFoundError as e:
        print(f"Errore: {e}")
        print("Assicurati che i file CSV siano nella stessa directory dello script")
        return
    
    # Nomi delle colonne QID
    # Nel primo file: colonna 'QID'
    # Nel secondo file: colonna 'wikidata_id'
    qid_col1 = 'QID'
    qid_col2 = 'wikidata_id'
    
    print(f"File 1 colonne disponibili: {list(df1.columns)}")
    print(f"File 2 colonne disponibili: {list(df2.columns)}")
    print()
    
    # Estrai QID
    print("Estrazione QID...")
    qids1 = extract_qids_from_dataframe(df1, qid_col1)
    qids2 = extract_qids_from_dataframe(df2, qid_col2)
    
    print(f"Trovati {len(qids1)} QID unici nel file UNESCO")
    print(f"Trovati {len(qids2)} QID unici nel file cultural sites")
    
    # Trova intersezioni
    matches = qids1.intersection(qids2)
    
    print(f"\nTrovati {len(matches)} QID che matchano:")
    print("=" * 80)
    
    # Mostra i match con dettagli
    if matches:
        for qid in sorted(matches):
            print(f"\nQID: {qid}")
            
            # Info dal file UNESCO
            unesco_rows = df1[df1[qid_col1] == qid]
            if not unesco_rows.empty:
                print("  Dal file UNESCO:")
                for _, row in unesco_rows.iterrows():
                    print(f"    • ID: {row.get('id', 'N/A')}")
                    print(f"    • Nome: {row.get('name', 'N/A')}")
                    print(f"    • Categoria: {row.get('category', 'N/A')}")
            
            # Info dal file cultural sites
            cultural_rows = df2[df2[qid_col2] == qid]
            if not cultural_rows.empty:
                print("  Dal file Cultural Sites:")
                for _, row in cultural_rows.iterrows():
                    print(f"    • Site: {row.get('site', 'N/A')}")
                    print(f"    • Nome: {row.get('name', 'N/A')}")
                    print(f"    • Alt Name: {row.get('altName', 'N/A')}")
                    print(f"    • Etichetta Wikidata: {row.get('wikidata_label', 'N/A')}")
            
            print("-" * 80)
    
    # Salva i risultati in un file
    if matches:
        save_results(df1, df2, matches, qid_col1, qid_col2)
    
    # Mostra QID unici per file
    if len(matches) < max(len(qids1), len(qids2)):
        print("\n\nQID unici per file:")
        print("=" * 80)
        
        # QID solo nel file UNESCO
        only_in_unesco = qids1 - qids2
        if only_in_unesco:
            print(f"\nQID solo nel file UNESCO ({len(only_in_unesco)}):")
            for qid in sorted(only_in_unesco)[:20]:  # Mostra solo i primi 20
                print(f"  {qid}")
            if len(only_in_unesco) > 20:
                print(f"  ... e altri {len(only_in_unesco) - 20}")
        
        # QID solo nel file cultural sites
        only_in_cultural = qids2 - qids1
        if only_in_cultural:
            print(f"\nQID solo nel file Cultural Sites ({len(only_in_cultural)}):")
            for qid in sorted(only_in_cultural)[:20]:  # Mostra solo i primi 20
                print(f"  {qid}")
            if len(only_in_cultural) > 20:
                print(f"  ... e altri {len(only_in_cultural) - 20}")

def save_results(df1, df2, matches, qid_col1, qid_col2):
    """Salva i risultati dettagliati in un file CSV"""
    output_rows = []
    
    for qid in sorted(matches):
        # Prendi tutte le righe corrispondenti da entrambi i file
        unesco_rows = df1[df1[qid_col1] == qid]
        cultural_rows = df2[df2[qid_col2] == qid]
        
        # Per ogni combinazione di righe
        for _, unesco_row in unesco_rows.iterrows():
            for _, cultural_row in cultural_rows.iterrows():
                output_rows.append({
                    'QID': qid,
                    'UNESCO_ID': unesco_row.get('id', ''),
                    'UNESCO_Name': unesco_row.get('name', ''),
                    'UNESCO_Category': unesco_row.get('category', ''),
                    'Cultural_Site_ID': cultural_row.get('site', '').split('/')[-1] if isinstance(cultural_row.get('site'), str) else '',
                    'Cultural_Site_Name': cultural_row.get('name', ''),
                    'Cultural_Site_AltName': cultural_row.get('altName', ''),
                    'Cultural_Site_Wikidata_Label': cultural_row.get('wikidata_label', ''),
                    'Cultural_Site_Instance_Of': cultural_row.get('instance_of_label', ''),
                    'UNESCO_Location': unesco_row.get('location', ''),
                    'Cultural_Site_Oblast': cultural_row.get('oblast', ''),
                    'UNESCO_Description': str(unesco_row.get('description', ''))[:200] + '...'  # Prima 200 caratteri
                })
    
    # Crea dataframe e salva
    output_df = pd.DataFrame(output_rows)
    output_file = 'qid_matches.csv'
    output_df.to_csv(output_file, index=False, encoding='utf-8', sep=';')
    print(f"\nRisultati dettagliati salvati in: {output_file}")
    
    # Salva anche un sommario
    summary = pd.DataFrame({
        'QID': list(matches),
        'Match_Type': 'Both files'
    })
    summary_file = 'qid_matches_summary.csv'
    summary.to_csv(summary_file, index=False, encoding='utf-8', sep=';')
    print(f"Sommario salvato in: {summary_file}")

if __name__ == "__main__":
    print("=" * 80)
    print("CONFRONTO QID TRA FILE CSV")
    print("=" * 80)
    
    find_matches()
    
    print("\n" + "=" * 80)
    print("ANALISI COMPLETATA")
    print("=" * 80)