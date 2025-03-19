import os
import numpy as np
import rasterio

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
