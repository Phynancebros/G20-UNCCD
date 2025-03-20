import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin

def calculate_wsi(precipitation_data):
    # Example calculation for WSI
    # WSI = (1 - (Precipitation / Max Precipitation)) * 100
    max_precipitation = precipitation_data['overall_mean'].max()
    precipitation_data['WSI'] = (1 - (precipitation_data['overall_mean'] / max_precipitation)) * 100
    return precipitation_data

def save_as_tiff(data, output_file):
    transform = from_origin(0, 0, 1, 1)  # Example transform, adjust as needed
    new_dataset = rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=str(data.dtype),
        crs='+proj=latlong',
        transform=transform,
    )
    new_dataset.write(data, 1)
    new_dataset.close()

def main():
    # Read the precipitation data from the CSV file
    input_file = 'precipitation_results.csv'
    precipitation_data = pd.read_csv(input_file)
    
    # Calculate the WSI
    wsi_data = calculate_wsi(precipitation_data)
    
    # Convert WSI data to a 2D array (example, adjust as needed)
    wsi_array = np.array(wsi_data['WSI']).reshape((len(wsi_data), 1))
    
    # Save the WSI data to a new TIFF file
    output_file = 'wsi_calculation/wsi_results.tiff'
    save_as_tiff(wsi_array, output_file)
    print(f'WSI results saved to {output_file}')

if __name__ == '__main__':
    main()
