import os
import numpy as np
import rasterio

def raster_difference(file_path1, file_path2, output_tif_path):
    """
    Calculates the pixel-wise difference (file_path2 - file_path1)
    and saves a new GeoTIFF with the difference values.
    
    Interpretation:
    - Positive values: In that area, the values of the second raster (e.g., precipitation in a subsequent year)
      are higher than those of the first.
    - Negative values: There has been a decrease.
    
    Parameters:
    - file_path1: Path to the first raster file.
    - file_path2: Path to the second raster file.
    - output_tif_path: Path to save the output difference raster.
    """
    with rasterio.open(file_path1) as src1, rasterio.open(file_path2) as src2:
        data1 = src1.read(1).astype(float)
        data2 = src2.read(1).astype(float)
        
        # Align dimensions and handle nodata
        nodata1 = src1.nodata
        nodata2 = src2.nodata
        data1[data1 == nodata1] = np.nan
        data2[data2 == nodata2] = np.nan
        
        diff_data = data2 - data1

        # Create profile for the new raster
        profile = src1.profile
        profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

        # Save the difference raster
        with rasterio.open(output_tif_path, 'w', **profile) as dst:
            dst.write(diff_data.astype(np.float32), 1)
    
    print(f"Saved difference raster to {output_tif_path}")

def calculate_time_series(raster_files):
    """
    Calculates the mean of each raster (assuming they all cover the same area)
    and returns a list of tuples (filename, mean_value).
    
    Interpretation:
    - Build a graph (e.g., with matplotlib) year vs mean
      to see a temporal trend.
    
    Parameters:
    - raster_files: List of paths to raster files.
    
    Returns:
    - List of tuples (filename, mean_value).
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
