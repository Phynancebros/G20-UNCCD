import os
import pandas as pd
import numpy as np

# Define paths to data directories
precipitation_data_dir = 'Datasets_Hackathon/Climate_Precipitation_Data/'
land_cover_data_dir = 'Datasets_Hackathon/Modis_Land_Cover_Data/'

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
    return np.random.rand(100, 100)  # Dummy data

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
    df.to_csv('precipitation_averages.csv', index=False)

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
        south_value = np.sum(land_cover[:33, :]) / 1000  # Convert to thousands of km²
        center_value = np.sum(land_cover[33:66, :]) / 1000
        north_value = np.sum(land_cover[66:, :]) / 1000
        overall_value = np.sum(land_cover) / 1000
        values.append((year, overall_value, south_value, center_value, north_value))
    return values

def write_land_cover_csv(values):
    """Write land cover values to CSV file."""
    df = pd.DataFrame(values, columns=['Year', 'Overall', 'South', 'Center', 'North'])
    df.to_csv('land_cover_values.csv', index=False)

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
