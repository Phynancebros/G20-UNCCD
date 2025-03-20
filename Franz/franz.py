import os
import sys
import pandas as pd
import numpy as np
import rasterio
import importlib.util

# Add analysis_tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../analysis_tools'))
print("Python Path:", sys.path)  # Debugging line to print the current Python path

# Dynamically import the extra_analysis_module
spec = importlib.util.spec_from_file_location("extra_analysis_module", os.path.join(os.path.dirname(__file__), '../analysis_tools/extra_analysis_module.py'))
extra_analysis_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extra_analysis_module)
calculate_time_series = extra_analysis_module.calculate_time_series

# Define paths to data directories
base_dir = os.path.dirname(os.path.abspath(__file__))
precipitation_data_dir = os.path.join(base_dir, '../Datasets_Hackathon/Climate_Precipitation_Data/')
land_cover_data_dir = os.path.join(base_dir, '../Datasets_Hackathon/Modis_Land_Cover_Data/')
output_dir = os.path.join(base_dir, 'Franz')
os.makedirs(output_dir, exist_ok=True)

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
        # Replace invalid values with NaN
        precipitation = np.where(precipitation == -3.4028235e+38, np.nan, precipitation)
        south_avg = np.nanmean(precipitation[:33, :])
        center_avg = np.nanmean(precipitation[33:66, :])
        north_avg = np.nanmean(precipitation[66:, :])
        overall_avg = np.nanmean(precipitation)
        averages.append((year, overall_avg, south_avg, center_avg, north_avg))
    return averages

def write_precipitation_csv(averages):
    """Write precipitation averages to CSV file."""
    df = pd.DataFrame(averages, columns=['Year', 'Overall', 'South', 'Center', 'North'])
    df.to_csv(os.path.join(output_dir, 'precipitation_averages.csv'), index=False)

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
    for year, land_cover in data:
        counts = [np.sum(land_cover == i) for i in range(17)]
        values.append([year] + counts)
    return values

def write_land_cover_csv(values):
    """Write land cover values to CSV file."""
    columns = ['Year'] + [f'Value_{i}' for i in range(17)]
    df = pd.DataFrame(values, columns=columns)
    df.to_csv(os.path.join(output_dir, 'land_cover_values.csv'), index=False)

def main():
    # Process precipitation data
    precipitation_data = read_precipitation_data()
    precipitation_averages = calculate_precipitation_averages(precipitation_data)
    write_precipitation_csv(precipitation_averages)

    # Process land cover data
    land_cover_data = read_land_cover_data()
    land_cover_values = calculate_land_cover_values(land_cover_data)
    write_land_cover_csv(land_cover_values)

if __name__ == '__main__':
    main()

# Debugging code to inspect precipitation data
if __name__ == '__main__':
    precipitation_data = read_precipitation_data()
    for year, precipitation in precipitation_data:
        print(f"Year: {year}, Precipitation Data: {precipitation}")

# Debugging code to inspect land cover data
if __name__ == '__main__':
    land_cover_data = read_land_cover_data()
    for year, land_cover in land_cover_data:
        unique_values, counts = np.unique(land_cover, return_counts=True)
        print(f"Year: {year}, Unique Values: {unique_values}, Counts: {counts}")
