import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from .stats_module import get_raster_stats, save_stats_to_csv

def visualize_raster(file_path, ax, no_data_value=65533, hist_output_dir=None):
    """
    Carica il raster e lo visualizza sul subplot ax,
    SENZA salvare o chiudere la figura.
    Se hist_output_dir non è None, genera anche l'istogramma del raster.
    """
    with rasterio.open(file_path) as src:
        data = src.read(1).astype(float)

        # Gestione NoData
        if src.nodata is not None:
            data[data == src.nodata] = np.nan
        data[data == no_data_value] = np.nan

        # Se tutto NoData, esci e stampi avviso
        if np.isnan(data).all():
            ax.set_title(f"{os.path.basename(file_path)} - ALL NODATA")
            ax.axis('off')
            return
        
        # Plot del raster
        cax = ax.imshow(data, cmap='viridis', interpolation='none')
        ax.set_title(os.path.basename(file_path))
        plt.colorbar(cax, ax=ax, orientation='vertical', label='Value')

        # Eventuale istogramma
        if hist_output_dir is not None:
            os.makedirs(hist_output_dir, exist_ok=True)
            valid_data = data[~np.isnan(data)].ravel()
            plt.figure()
            plt.hist(valid_data, bins=50, color='blue', alpha=0.7)
            plt.title(f"Histogram - {os.path.basename(file_path)}")
            plt.xlabel('Value')
            plt.ylabel('Frequency')
            hist_path = os.path.join(hist_output_dir, f"{os.path.basename(file_path)}_hist.png")
            plt.savefig(hist_path, bbox_inches='tight')
            plt.close()
            print(f"Saved histogram to {hist_path}")

def compare_rasters(file_paths, output_dir, comparison_title):
    """
    Crea un'unica figura con subplots affiancati per
    visualizzare side-by-side i raster di file_paths.
    Calcola statistiche di base e le salva su file CSV.
    """
    import matplotlib.pyplot as plt  # per sicurezza, import locale

    fig, axes = plt.subplots(1, len(file_paths), figsize=(6*len(file_paths), 6))
    if len(file_paths) == 1:
        axes = [axes]

    stats_list = []

    for ax, file_path in zip(axes, file_paths):
        with rasterio.open(file_path) as src:
            data = src.read(1).astype(float)
            if src.nodata is not None:
                data[data == src.nodata] = np.nan
            data[data == 65533] = np.nan

        # Visualizzazione
        visualize_raster(
            file_path, 
            ax, 
            hist_output_dir=os.path.join(output_dir, "histograms")
        )
        
        # Calcolo statistiche
        stats = get_raster_stats(data)
        stats_list.append({
            "filename": os.path.basename(file_path),
            **stats
        })

    # Salvataggio figure
    fig.suptitle(comparison_title, fontsize=16)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{comparison_title}.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved comparison visualization to {out_path}")

    # Salvataggio CSV con statistiche
    csv_filename = f"{comparison_title}_stats.csv"
    csv_path = os.path.join(output_dir, "stats", csv_filename)
    save_stats_to_csv(csv_path, stats_list)

    print(f"Saved CSV stats to {csv_path}")

# Come interpretare i plot di compare_rasters:
# - Ogni subplot mostra un anno/dataset differente.
# - Confronta visivamente la distribuzione spaziale e la colorbar.
# - A colpo d’occhio, puoi vedere quale anno ha valori più alti o più bassi.
# - Sotto la cartella "histograms" trovi gli istogrammi dettagliati.
# - Nel CSV in "stats" trovi min, max, mean, median per ogni raster.
