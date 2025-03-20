import os
import re
import csv
import numpy as np
import rasterio

def calculate_time_series(raster_files):
    """
    Calcola la media (overall, north, center, south) per ciascun raster,
    suddiviso in 3 fasce orizzontali equivalenti (stessa altezza).
    
    Ritorna: lista di dict con
        {
            "filename": <nome_file>,
            "overall_mean": <media_totale>,
            "north_mean": <media_nord>,
            "center_mean": <media_centro>,
            "south_mean": <media_sud>
        }
    """
    
    results = []
    
    for idx, f in enumerate(raster_files):
        with rasterio.open(f) as src:
            data = src.read(1).astype(float)
            
            # Gestione NoData
            if src.nodata is not None:
                data[data == src.nodata] = np.nan

            # Dimensioni in pixel
            height, width = data.shape
            
            # Suddividiamo l'immagine in 3 parti (nord, centro, sud) equiestese in termini di righe.
            # Esempio: se height=60, allora 60//3 = 20 righe ognuna.
            part_height = height // 3

            # Notare che se l'altezza non è divisibile per 3, l'ultima fascia includerà i pixel rimanenti.
            # Esempio: height = 61 => prime 2 fasce 20 righe, l'ultima 21 righe
            north_bounds  = (0, part_height,    0, width)                      # righe 0..part_height
            center_bounds = (part_height, 2*part_height, 0, width)            # righe part_height..2*part_height
            south_bounds  = (2*part_height, height,        0, width)          # righe 2*part_height..fine

            def zone_mean(data, bounds):
                min_row, max_row, min_col, max_col = bounds
                zone = data[min_row:max_row, min_col:max_col]
                return np.nanmean(zone)

            overall_mean = np.nanmean(data)
            north_mean   = zone_mean(data, north_bounds)
            center_mean  = zone_mean(data, center_bounds)
            south_mean   = zone_mean(data, south_bounds)

            results.append({
                "filename": os.path.basename(f),
                "overall_mean": overall_mean,
                "north_mean": north_mean,
                "center_mean": center_mean,
                "south_mean": south_mean
            })
    return results


if __name__ == "__main__":
    # Elenco dei file
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
    
    # Calcolo le medie
    results = calculate_time_series(raster_files)
    
    # Esporto in CSV
    csv_output_path = 'precipitation_results.csv'
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['year', 'filename', 'overall_mean', 'north_mean', 'center_mean', 'south_mean']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Ricavo l'anno dal nome file (es. "2010" da "2010R.tif")
            match = re.search(r'(\d{4})', result['filename'])
            year_str = match.group(1) if match else "N/A"

            writer.writerow({
                'year'         : year_str,
                'filename'     : result['filename'],
                'overall_mean' : result['overall_mean'],
                'north_mean'   : result['north_mean'],
                'center_mean'  : result['center_mean'],
                'south_mean'   : result['south_mean']
            })

    print(f"CSV generato con successo in: {csv_output_path}")
