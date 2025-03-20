import streamlit as st
import os
import rasterio
import numpy as np
import csv
import matplotlib.pyplot as plt

import sys
import os
# Add the current directory (or a specific directory) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# or if the modules are in a subfolder 'analysis_tools':
sys.path.insert(0, os.path.join(current_dir, 'analysis_tools'))



def compare_rasters_in_groups(file_paths, out_dir, base_title):
    """
    Divide the list of files into groups of 3 and visualize them side-by-side.
    """
    for i in range(0, len(file_paths), 3):
        group = file_paths[i:i+3]
        if group:
            group_title = f"{base_title} (Group {i//3 + 1})"
            compare_rasters(group, out_dir, group_title)

def run_analysis():
    # Define directories
    climate_data_dir = 'Datasets_Hackathon/Climate_Precipitation_Data'
    population_data_dir = 'Datasets_Hackathon/Gridded_Population_Density_Data'
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)

    # 1. List files for climate data and population data
    climate_files = sorted([
        os.path.join(climate_data_dir, f)
        for f in os.listdir(climate_data_dir)
        if f.endswith('.tif')
    ])
    population_files = sorted([
        os.path.join(population_data_dir, f)
        for f in os.listdir(population_data_dir)
        if f.endswith('.tif')
    ])

    # 2. Visualize and compare files in groups of 3 (these functions should save images)
    compare_rasters_in_groups(climate_files, output_dir, "Climate Data Comparison")
    compare_rasters_in_groups(population_files, output_dir, "Population Data Comparison")

    # 3. Difference analysis: Calculate difference between two rasters (example: 2020 and 2010)
    difference_out = os.path.join(output_dir, "2020_minus_2010.tif")
    raster_difference(
        file_path1=os.path.join(climate_data_dir, "2010R.tif"),
        file_path2=os.path.join(climate_data_dir, "2020R.tif"),
        output_tif_path=difference_out
    )

    # Read the difference raster and save values to CSV
    with rasterio.open(difference_out) as src:
        diff_data = src.read(1)
        diff_data[diff_data == src.nodata] = np.nan
        rows, cols = diff_data.shape
        csv_path = os.path.join(output_dir, "difference_2020_2010.csv")
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Row", "Col", "Difference"])
            for row in range(rows):
                for col in range(cols):
                    if not np.isnan(diff_data[row, col]):
                        writer.writerow([row, col, diff_data[row, col]])
    st.write(f"Saved difference CSV to: {csv_path}")

    # Generate and save histogram of differences
    plt.figure(figsize=(8,6))
    plt.hist(diff_data[~np.isnan(diff_data)].flatten(), bins=50, edgecolor='black')
    plt.xlabel('Difference')
    plt.ylabel('Frequency')
    plt.title('Histogram of Differences (2020 - 2010)')
    plt.grid(True)
    hist_path = os.path.join(output_dir, "difference_histogram.png")
    plt.savefig(hist_path)
    plt.close()
    st.image(hist_path, caption="Histogram of Differences (2020 - 2010)", use_column_width=True)

    # 4. Time series analysis: Calculate mean precipitation trend over years
    results = calculate_time_series(climate_files)
    csv_trend_path = os.path.join(output_dir, "precipitation_trend.csv")
    with open(csv_trend_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Mean Precipitation"])
        writer.writerows(results)
    st.write(f"Saved precipitation trend to: {csv_trend_path}")

    # Generate and save a time series plot
    years_list = [fname.split('R')[0] for fname, _ in results]
    mean_values = [meanval for _, meanval in results]
    plt.figure(figsize=(10,6))
    plt.plot(years_list, mean_values, marker='o')
    plt.xlabel('Year')
    plt.ylabel('Mean Precipitation')
    plt.title('Precipitation Trend Over Years')
    plt.grid(True)
    trend_path = os.path.join(output_dir, "precipitation_trend.png")
    plt.savefig(trend_path)
    plt.close()
    st.image(trend_path, caption="Precipitation Trend", use_column_width=True)


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

    fig, axes = plt.subplots(1, len(file_paths), figsize=(6 * len(file_paths), 6))
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


def raster_difference(file_path1, file_path2, output_tif_path):
    """
    Calcola la differenza pixel-wise (file_path2 - file_path1)
    e salva un nuovo GeoTIFF con i valori di differenza.

    Interpretazione:
    - Valori positivi: in quell'area, i valori del secondo raster (es. precipitazione in un anno successivo)
      sono superiori a quelli del primo.
    - Valori negativi: c'è stato un calo.
    """
    with rasterio.open(file_path1) as src1, rasterio.open(file_path2) as src2:
        data1 = src1.read(1).astype(float)
        data2 = src2.read(1).astype(float)

        # Allineare le dimensioni e gestire nodata
        nodata1 = src1.nodata
        nodata2 = src2.nodata
        data1[data1 == nodata1] = np.nan
        data2[data2 == nodata2] = np.nan

        diff_data = data2 - data1

        # Crea profilo per il nuovo raster
        profile = src1.profile
        profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

        # Salva il raster di differenza
        with rasterio.open(output_tif_path, 'w', **profile) as dst:
            dst.write(diff_data.astype(np.float32), 1)

    print(f"Saved difference raster to {output_tif_path}")


def calculate_time_series(raster_files):
    """
    Calcola la media di ogni raster (assumendo siano tutti della stessa area)
    e ritorna una lista di tuple (filename, mean_value).

    Interpretazione:
    - Costruisci poi un grafico (es. con matplotlib) anno vs media
      per vedere un trend temporale.
    """
    results = []
    for f in raster_files:
        with rasterio.open(f) as src:
            data = src.read(1).astype(float)
            if src.nodata is not None:
                data[data == src.nodata] = np.nan
            mean_val = np.nanmean(data)
            results.append((os.path.basename(f), mean_val))
    return results


def main():
    st.title("Sahel Region Land Restoration Dashboard 🌍")
    st.markdown("""
    This dashboard visualizes land cover changes, climate impacts, and restoration opportunities in the Sahel region.
    The interactive map is not embedded in this version, but the analysis graphs are displayed below.
    """)

    run_analysis()

if __name__ == "__main__":
    main()

