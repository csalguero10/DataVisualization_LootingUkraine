import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patheffects import withStroke

def create_modern_waffle_chart():
    # Dati
    protected_sites = 42
    damaged_sites = 387
    total_sites = protected_sites + damaged_sites
    
    # Calcola le percentuali
    protected_pct = (protected_sites / total_sites) * 100
    damaged_pct = (damaged_sites / total_sites) * 100
    
    # Colori moderni nello stile del sito linked
    colors = {
        'protected': '#FFB81C',  # Giallo brillante
        'damaged': '#0056B8',    # Blu intenso
        'accent': '#DC241F',     # Rosso per accenti
        'light_bg': '#F8F9FA',   # Grigio molto chiaro
        'dark_text': '#1A1A1A',  # Quasi nero per testo
        'medium_text': '#666666', # Grigio per testo secondario
        'grid': '#E8EAED'        # Grigio chiarissimo per griglia
    }
    
    # Crea figura con sfondo chiaro
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), 
                                   gridspec_kw={'width_ratios': [2, 1]},
                                   facecolor='white')
    
    # === PARTE 1: WAFFLE CHART ===
    # Parametri del waffle chart
    rows = 10
    cols = 10
    total_tiles = rows * cols
    
    # Calcola quanti quadratini per ogni categoria
    protected_tiles = int((protected_sites / total_sites) * total_tiles)
    damaged_tiles = total_tiles - protected_tiles
    
    # Disegna il waffle chart
    for i in range(rows):
        for j in range(cols):
            tile_index = i * cols + j
            
            if tile_index < protected_tiles:
                color = colors['protected']
            else:
                color = colors['damaged']
            
            # Quadratino con angoli arrotondati
            rect = mpatches.FancyBboxPatch(
                (j, rows - i - 1),
                0.85, 0.85,  # Più spazio tra i quadratini
                boxstyle="round,pad=0.02",
                facecolor=color,
                edgecolor='white',
                linewidth=2
            )
            ax1.add_patch(rect)
    
    # Configura assi del waffle chart
    ax1.set_xlim(0, cols)
    ax1.set_ylim(0, rows)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # === PARTE 2: INFOGRAFICA TESTO ===
    # Sfondo per la parte testo
    ax2.set_facecolor(colors['light_bg'])
    
    # Titolo principale
    title_text = ax2.text(0.5, 0.9, 'PROTECTION\nGAP', 
                         transform=ax2.transAxes,
                         ha='center', va='center',
                         fontsize=36, fontweight='bold',
                         color=colors['dark_text'],
                         linespacing=1.2)
    
    # Effetto sul titolo
    title_text.set_path_effects([withStroke(linewidth=3, foreground='white')])
    
    # Sottotitolo
    subtitle = f'{protected_sites:,} UNESCO Protected\n{damaged_sites:,} Sites Damaged'
    ax2.text(0.5, 0.75, subtitle,
            transform=ax2.transAxes,
            ha='center', va='top',
            fontsize=18,
            color=colors['medium_text'],
            linespacing=1.5)
    
    # Statistiche
    stats_y = 0.6
    stat_spacing = 0.08
    
    # Statistica protetti
    ax2.text(0.1, stats_y, 'PROTECTED', 
            transform=ax2.transAxes,
            fontsize=14, fontweight='bold',
            color=colors['dark_text'])
    
    ax2.text(0.7, stats_y, f'{protected_pct:.1f}%', 
            transform=ax2.transAxes,
            fontsize=24, fontweight='bold',
            color=colors['protected'],
            ha='right')
    
    # Statistica danneggiati
    ax2.text(0.1, stats_y - stat_spacing, 'DAMAGED', 
            transform=ax2.transAxes,
            fontsize=14, fontweight='bold',
            color=colors['dark_text'])
    
    ax2.text(0.7, stats_y - stat_spacing, f'{damaged_pct:.1f}%', 
            transform=ax2.transAxes,
            fontsize=24, fontweight='bold',
            color=colors['damaged'],
            ha='right')
    
    # Barra di separazione
    separator = mpatches.Rectangle((0.05, 0.45), 0.9, 0.005,
                                 transform=ax2.transAxes,
                                 facecolor=colors['grid'])
    ax2.add_patch(separator)
    
    # Insight
    insight_text = (
        'UNESCO World Heritage designation\n'
        'provides legal protection but\n'
        'offers no physical shield against\n'
        'direct attacks in conflict zones.'
    )
    
    ax2.text(0.5, 0.35, insight_text,
            transform=ax2.transAxes,
            ha='center', va='top',
            fontsize=14,
            color=colors['medium_text'],
            linespacing=1.4)
    
    # Fonte dati
    source_text = 'Data: UNESCO Protected Lists & Damage Reports\nAnalysis: DispersArt Project'
    ax2.text(0.5, 0.05, source_text,
            transform=ax2.transAxes,
            ha='center', va='bottom',
            fontsize=10,
            color=colors['medium_text'],
            alpha=0.7,
            linespacing=1.3)
    
    # Rimuovi bordi dalla parte testo
    ax2.axis('off')
    
    # Aggiungi bordo decorativo attorno a tutto
    fig.patch.set_linewidth(2)
    fig.patch.set_edgecolor(colors['grid'])
    
    plt.tight_layout()
    return fig, (ax1, ax2)

# Crea e mostra il grafico
if __name__ == "__main__":
    fig, axes = create_modern_waffle_chart()
    
    # Salva in alta qualità
    fig.savefig('modern_protection_gap_chart.png', 
                dpi=300, 
                bbox_inches='tight', 
                facecolor='white',
                edgecolor='none')
    
    plt.show()
    
    print("Infografica creata con successo!")
    print("File salvato come: modern_protection_gap_chart.png")
    print("\n" + "="*50)
    print("VISUALIZATION SUMMARY:")
    print("="*50)
    print(f"• UNESCO Protected Sites: {42:,}")
    print(f"• Damaged Cultural Sites: {387:,}")
    print(f"• Protection Gap Ratio: {42/(42+387)*100:.1f}% protected vs {387/(42+387)*100:.1f}% damaged")
    print("="*50)