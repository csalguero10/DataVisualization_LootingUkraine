import pandas as pd
import altair as alt

# --- 1. CONFIGURAZIONE URL ---
URL_RED_LIST = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/refs/heads/main/raw_data/red_list.csv"
URL_STOLEN = "https://raw.githubusercontent.com/csalguero10/DisperseArt_InformationVisualization/refs/heads/main/data_stolen/stolen_objects_ukraine_cleaned.csv"

def generate_cultural_theft_chart():
    # --- 2. CARICAMENTO DATI ---
    try:
        df_r = pd.read_csv(URL_RED_LIST)
        df_s = pd.read_csv(URL_STOLEN)
    except Exception as e:
        print(f"Errore nel caricamento dei dati: {e}")
        return

    # --- 3. LOGICA DI NORMALIZZAZIONE ---
    def normalize_final(cat):
        cat = str(cat).lower().strip()
        if 'painting' in cat: return 'DIPINTI'
        if 'archaeological' in cat: return 'ARCHEOLOGIA'
        if 'icon' in cat: return 'ICONE'
        if 'manuscripts' in cat or 'books' in cat: return 'LIBRI / MANOSCRITTI'
        if 'religious' in cat: return 'OGGETTI RELIGIOSI'
        return 'ALTRO / VARIE'

    df_r['cat_clean'] = df_r['category'].apply(normalize_final)
    df_s['cat_clean'] = df_s['category'].apply(normalize_final)

    # --- 4. CALCOLO PERCENTUALI ---
    # Definiamo l'ordine delle categorie che vogliamo mostrare (escludendo ALTRO / VARIE)
    categorie_principali = ['DIPINTI', 'ARCHEOLOGIA', 'ICONE', 'LIBRI / MANOSCRITTI', 'OGGETTI RELIGIOSI']
    
    # Calcoliamo le percentuali per Red List
    red_counts = df_r['cat_clean'].value_counts(normalize=False).reset_index()
    red_counts.columns = ['Categoria', 'Conteggio']
    
    # Calcoliamo le percentuali per Furti Reali
    stolen_counts = df_s['cat_clean'].value_counts(normalize=False).reset_index()
    stolen_counts.columns = ['Categoria', 'Conteggio']
    
    # Creiamo un DataFrame completo con tutte le categorie principali
    red_data = []
    stolen_data = []
    
    for cat in categorie_principali:
        # Red List
        red_row = red_counts[red_counts['Categoria'] == cat]
        if not red_row.empty:
            red_total = red_counts['Conteggio'].sum()
            red_pct = red_row['Conteggio'].iloc[0] / red_total
        else:
            red_pct = 0.0
        
        red_data.append({
            'Categoria': cat,
            'Percentuale': red_pct,
            'Percentuale_Testo': f"{red_pct:.1%}",
            'Tipo': 'Red List (Previsione UNESCO)'
        })
        
        # Furti Reali
        stolen_row = stolen_counts[stolen_counts['Categoria'] == cat]
        if not stolen_row.empty:
            stolen_total = stolen_counts['Conteggio'].sum()
            stolen_pct = stolen_row['Conteggio'].iloc[0] / stolen_total
        else:
            stolen_pct = 0.0
        
        stolen_data.append({
            'Categoria': cat,
            'Percentuale': stolen_pct,
            'Percentuale_Testo': f"{stolen_pct:.1%}",
            'Tipo': 'Furti Reali (Dati sul campo)'
        })
    
    df_finale = pd.DataFrame(red_data + stolen_data)
    
    print("Dati generati:")
    print(df_finale)
    print("\nSommario:")
    for cat in categorie_principali:
        red_val = df_finale[(df_finale['Categoria'] == cat) & (df_finale['Tipo'] == 'Red List (Previsione UNESCO)')]['Percentuale'].iloc[0]
        stolen_val = df_finale[(df_finale['Categoria'] == cat) & (df_finale['Tipo'] == 'Furti Reali (Dati sul campo)')]['Percentuale'].iloc[0]
        print(f"{cat}: Red List={red_val:.1%}, Furti Reali={stolen_val:.1%}")

    # --- 5. COSTRUZIONE GRAFICO (Verticale, Dark Mode, Layered) ---
    
    # Base comune per i layer
    base = alt.Chart(df_finale).encode(
        x=alt.X('Categoria:N', 
                title=None, 
                axis=alt.Axis(labelAngle=0, labelPadding=10, labelColor='white'),
                sort=categorie_principali),
        xOffset='Tipo:N',
        color=alt.Color('Tipo:N', 
                        scale=alt.Scale(
                            domain=['Red List (Previsione UNESCO)', 'Furti Reali (Dati sul campo)'],
                            range=['#FF3131', '#318CE7'] # Rosso e Blu
                        ),
                        legend=alt.Legend(orient="top", title=None))
    )

    # Layer 1: Le barre verticali (senza asse Y)
    bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=40).encode(
        y=alt.Y('Percentuale:Q', 
                title=None,
                axis=None,
                scale=alt.Scale(domain=[0, df_finale['Percentuale'].max() * 1.15]))
    )

    # Layer 2: Testo ALL'INTERNO della barra (centrato verticalmente)
    text_inside = base.mark_text(
        align='center',
        baseline='middle',
        color='white',
        fontWeight='bold',
        fontSize=16,  # Font più grande per le percentuali
        dy=-10
    ).encode(
        y=alt.Y('Percentuale:Q'),
        text=alt.Text('Percentuale_Testo:N')
    )

    # Unione dei layer principali
    final_chart = (bars + text_inside).properties(
        width=800,
        height=500,
        title={
            "text": "IL DIVARIO DELLA PROTEZIONE",
            "subtitle": [
                "Rosso: Priorità accademiche Red List | Blu: Realtà logistica dei saccheggi",
                "Fonte: ICOM Red List & Ministry of Culture of Ukraine"
            ],
            "fontSize": 24,
            "subtitleFontSize": 14,
            "anchor": "start",
            "dy": -20
        }
    ).configure(
        background='#000000'
    ).configure_view(
        strokeWidth=0,
        fill='#000000'
    ).configure_axis(
        domain=False,
        grid=False,
        labelColor='white',
        titleColor='white'
    ).configure_axisX(
        labelFontSize=13,
        labelFontWeight='bold'
    ).configure_legend(
        labelColor='white',
        titleColor='white',
        labelFontSize=12
    ).configure_title(
        color='white',
        subtitleColor='#aaaaaa'
    )

    # --- 6. SALVATAGGIO HTML ---
    output_name = "visualizzazione_redlist_verticale.html"
    final_chart.save(output_name)
    print(f"\n✓ Successo! File generato: {output_name}")
    print(f"  - Categorie mostrate: {len(categorie_principali)}")

if __name__ == "__main__":
    generate_cultural_theft_chart()