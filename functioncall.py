import os
import rasterio
from analysis_tools.visualization_module import compare_rasters
from analysis_tools.extra_analysis_module import raster_difference, calculate_time_series

def compare_rasters_in_groups(file_paths, out_dir, base_title):
    """
    Divide la lista dei file in gruppi di 3 e li visualizza fianco a fianco.
    """
    for i in range(0, len(file_paths), 3):
        group = file_paths[i:i+3]
        if group:
            group_title = f"{base_title} (Group {i//3 + 1})"
            compare_rasters(group, out_dir, group_title)

def main():
    climate_data_dir = 'Datasets_Hackathon/Climate_Precipitation_Data'
    population_data_dir = 'Datasets_Hackathon/Gridded_Population_Density_Data'
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)

    # 1. Liste di file
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

    # 2. Visualizzazione e statistiche a gruppi di 3
    compare_rasters_in_groups(climate_files, output_dir, "Climate Data Comparison")
    compare_rasters_in_groups(population_files, output_dir, "Population Data Comparison")

    # 3. Esempio di analisi differenza (opzionale)
    # Se vuoi calcolare differenza tra 2020 e 2010:
    # (Assumendo la presenza di "2020R.tif" e "2010R.tif")
    import numpy as np
    import csv
    import matplotlib.pyplot as plt

    difference_out = os.path.join(output_dir, "2020_minus_2010.tif")
    raster_difference(
        file_path1=os.path.join(climate_data_dir, "2010R.tif"),
        file_path2=os.path.join(climate_data_dir, "2020R.tif"),
        output_tif_path=difference_out
    )

    # Read the difference raster and save to CSV
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
        print(f"Saved difference data to {csv_path}")

    # Generate histogram of differences
    plt.hist(diff_data[~np.isnan(diff_data)].flatten(), bins=50, edgecolor='black')
    plt.xlabel('Difference')
    plt.ylabel('Frequency')
    plt.title('Histogram of Differences (2020 - 2010)')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "difference_histogram.png"))
    plt.show()

    # 4. Esempio di analisi time series (opzionale)
    # Se vuoi un trend globale, calcola la media su tutti gli anni di precipitazione:
    import csv
    import matplotlib.pyplot as plt
    from analysis_tools.extra_analysis_module import calculate_time_series

    results = calculate_time_series(climate_files)
    
    # Save results to CSV
    csv_path = os.path.join(output_dir, "precipitation_trend.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Mean Precipitation"])
        writer.writerows(results)
    print(f"Saved precipitation trend to {csv_path}")

    # Generate graph
    years = [fname.split('R')[0] for fname, _ in results]
    mean_values = [meanval for _, meanval in results]
    plt.plot(years, mean_values, marker='o')
    plt.xlabel('Year')
    plt.ylabel('Mean Precipitation')
    plt.title('Precipitation Trend Over Years')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "precipitation_trend.png"))
    plt.show()

if __name__ == "__main__":
    main()
