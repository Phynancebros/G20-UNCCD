import os
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.plot import show
from scipy.ndimage import gaussian_gradient_magnitude

def calculate_gradient(input_tif, output_tif):
    with rasterio.open(input_tif) as src:
        data = src.read(1)
        gradient = gaussian_gradient_magnitude(data, sigma=1)
        
        transform = src.transform
        profile = src.profile
        profile.update(dtype=rasterio.float32, count=1, compress='lzw')
        
        with rasterio.open(output_tif, 'w', **profile) as dst:
            dst.write(gradient.astype(rasterio.float32), 1)

def main():
    input_dir = 'data/Datasets_Hackathon/Climate_Precipitation_Data/'
    output_dir = 'data/processed/tif_files/'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for year in range(2010, 2024):
        input_tif = os.path.join(input_dir, f'{year}R.tif')
        output_tif = os.path.join(output_dir, f'{year}_precipitation_gradient.tif')
        calculate_gradient(input_tif, output_tif)
        print(f'Gradient TIFF saved to {output_tif}')

if __name__ == '__main__':
    main()
