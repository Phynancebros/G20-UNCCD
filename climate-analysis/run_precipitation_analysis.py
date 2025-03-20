import os
import re
import csv
import numpy as np
import rasterio

def raster_difference(file_path1, file_path2, output_tif_path):
    """
    Calcola la differenza pixel-wise (file_path2 - file_path1)
    e salva un nuovo GeoTIFF con i valori di differenza.
    
    Esempio di interpretazione:
    - Valori positivi => il secondo raster (es. un anno più recente) ha valori più alti.
    - Valori negativi => c'è stata una diminuzione rispetto al primo.
    """
    with rasterio.open(file_path1) as src1, rasterio.open(file_path2) as src2:
        data1 = src1.read(1).astype(float)
        data2 = src2.read(1).astype(float)
        
        # Gestione del nodata
        nodata1 = src1.nodata
        nodata2 = src2.nodata
        if nodata1 is not None:
            data1[data1 == nodata1] = np.nan
        if nodata2 is not None:
            data2[data2 == nodata2] = np.nan
        
        # Differenza
        diff_data = data2 - data1

        # Crea il profilo per il raster di output
        profile = src1.profile
        profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

        # Salva il raster di differenza
        with rasterio.open(output_tif_path, 'w', **profile) as dst:
            dst.write(diff_data.astype(np.float32), 1)
    
    print(f"Salvato il raster di differenza in: {output_tif_path}")


def calculate_time_series(raster_files, north_bounds, center_bounds, south_bounds):
    """
    Calcola la media (overall, north, center, south) per ciascun file raster.
    I bound devono essere specificati come tuple (min_row, max_row, min_col, max_col)
    in coordinate di pixel (o geografiche, se la funzione è strutturata per gestirle).
    
    Ritorna una lista di dizionari, uno per ciascun raster:
        {
            "filename": <nome_file>,
            "overall_mean": <media_totale>,
            "north_mean": <media_nord>,
            "center_mean": <media_centro>,
            "south_mean": <media_sud>
        }
    """
    def calculate_mean(data, bounds):
        min_row, max_row, min_col, max_col = bounds
        zone_data = data[min_row:max_row, min_col:max_col]
        return np.nanmean(zone_data)

    results = []
    for f in raster_files:
        with rasterio.open(f) as src:
            data = src.read(1).astype(float)
            # Gestione nodata
            if src.nodata is not None:
                data[data == src.nodata] = np.nan

            overall_mean = np.nanmean(data)
            north_mean = calculate_mean(data, north_bounds)
            center_mean = calculate_mean(data, center_bounds)
            south_mean = calculate_mean(data, south_bounds)

            results.append({
                "filename": os.path.basename(f),
                "overall_mean": overall_mean,
                "north_mean": north_mean,
                "center_mean": center_mean,
                "south_mean": south_mean
            })
    return results


if __name__ == "__main__":
    """
    Esempio di utilizzo completo:
      - Definizione dei bounding box (in pixel),
      - Lista di raster su cui effettuare le medie,
      - Creazione di un CSV con i risultati.
    """

    # ESEMPIO bounding box (0–60 righe, 0–45 colonne):
    # - Nord  : righe 0–20,  colonne 0–45
    # - Centro: righe 20–40, colonne 0–45
    # - Sud   : righe 40–60, colonne 0–45
    # Adattare ai propri TIFF.
    north_bounds  = (0, 20, 0, 45)
    center_bounds = (20, 40, 0, 45)
    south_bounds  = (40, 60, 0, 45)

    # Sostituire con i propri path ai TIFF
    raster_files = [
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2010R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2011R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2012R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2013R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2014R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2015R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2016R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2017R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2018R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2019R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2020R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2021R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2022R.tif",
        "data/Datasets_Hackathon/Climate_Precipitation_Data/2023R.tif"
    ]

    # Calcolo e scrittura su CSV
    results = calculate_time_series(raster_files, north_bounds, center_bounds, south_bounds)
    csv_output_path = 'precipitation_results.csv'
    
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['year', 'filename', 'overall_mean', 'north_mean', 'center_mean', 'south_mean']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Estrazione anno dal nome file (es: "2010" da "2010R.tif")
            basename = os.path.basename(result['filename'])
            match = re.search(r'(\d{4})', basename)
            if match:
                year_str = match.group(1)
            else:
                year_str = "N/A"

            writer.writerow({
                'year'         : year_str,
                'filename'     : basename,
                'overall_mean' : result['overall_mean'],
                'north_mean'   : result['north_mean'],
                'center_mean'  : result['center_mean'],
                'south_mean'   : result['south_mean']
            })

    print(f"CSV generato con successo in: {csv_output_path}")

    # Esempio di utilizzo di raster_difference (opzionale):
    # raster_difference(
    #     "data/Datasets_Hackathon/Climate_Precipitation_Data/2010R.tif",
    #     "data/Datasets_Hackathon/Climate_Precipitation_Data/2023R.tif",
    #     "difference_2023_minus_2010.tif"
    # )
