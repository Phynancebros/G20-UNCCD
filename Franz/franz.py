import os
import pandas as pd
import numpy as np
import rasterio

# Define paths to data directories
base_dir = os.path.dirname(os.path.abspath(__file__))
precipitation_data_dir = os.path.join(base_dir, '../Datasets_Hackathon/Climate_Precipitation_Data/')
land_cover_data_dir = os.path.join(base_dir, '../Datasets_Hackathon/Modis_Land_Cover_Data/')

# Define regions
regions = ['South', 'Center', 'North']

def read_precipitation_data():
    """Read and process precipitation data."""
    data = []
    for file in os.listdir(precipitation_data_dir):
        if file.endswith('.tif'):
            year = int(file[:4])
            # Assuming we have a function to read the .tif file and extract precipitation data
            precipitation = read_tif_file(os.path.join(precipitation_data_dir, file))
            data.append((year, precipitation))
    return data

def read_tif_file(file_path):
    """Read .tif file and extract precipitation data."""
    # Placeholder function to read .tif file
    # Implement the actual logic to read .tif file and extract data
    with rasterio.open(file_path) as src:
        return src.read(1)

def calculate_precipitation_averages(data):
    """Calculate average precipitation for each region and year."""
    averages = []
    for year, precipitation in data:
        south_avg = np.mean(precipitation[:33, :])
        center_avg = np.mean(precipitation[33:66, :])
        north_avg = np.mean(precipitation[66:, :])
        overall_avg = np.mean(precipitation)
        averages.append((year, overall_avg, south_avg, center_avg, north_avg))
    return averages

def write_precipitation_csv(averages):
    """Write precipitation averages to CSV file."""
    df = pd.DataFrame(averages, columns=['Year', 'Overall', 'South', 'Center', 'North'])
    df.to_csv(os.path.join(base_dir, 'precipitation_averages.csv'), index=False)

def read_land_cover_data():
    """Read and process land cover data."""
    data = []
    for file in os.listdir(land_cover_data_dir):
        if file.endswith('.tif'):
            year = int(file[:4])
            # Assuming we have a function to read the .tif file and extract land cover data
            land_cover = read_tif_file(os.path.join(land_cover_data_dir, file))
            data.append((year, land_cover))
    return data

def calculate_land_cover_values(data):
    """Calculate land cover values for each region and year."""
    values = []
    all_unique_values = set()
    for year, land_cover in data:
        unique_values, counts = np.unique(land_cover, return_counts=True)
        all_unique_values.update(unique_values)
        values.append((year, dict(zip(unique_values, counts))))
    
    all_unique_values = sorted(all_unique_values)
    final_values = []
    for year, counts_dict in values:
        counts = [counts_dict.get(value, 0) for value in all_unique_values]
        final_values.append([year] + counts)
    
    return final_values, all_unique_values

def write_land_cover_csv(values, unique_values):
    """Write land cover values to CSV file."""
    columns = ['Year'] + [f'Value_{int(value)}' for value in unique_values]
    df = pd.DataFrame(values, columns=columns)
    df.to_csv(os.path.join(base_dir, 'land_cover_values.csv'), index=False)

def main():
    # Process precipitation data
    precipitation_data = read_precipitation_data()
    precipitation_averages = calculate_precipitation_averages(precipitation_data)
    write_precipitation_csv(precipitation_averages)

    # Process land cover data
    land_cover_data = read_land_cover_data()
    land_cover_values, unique_values = calculate_land_cover_values(land_cover_data)
    write_land_cover_csv(land_cover_values, unique_values)

if __name__ == '__main__':
    main()

# Debugging code to inspect land cover data
if __name__ == '__main__':
    land_cover_data = read_land_cover_data()
    for year, land_cover in land_cover_data:
        unique_values, counts = np.unique(land_cover, return_counts=True)
        print(f"Year: {year}, Unique Values: {unique_values}, Counts: {counts}")
