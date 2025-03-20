#!/usr/bin/env python
import os
import sys
import cdsapi
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import os
import sys
import cdsapi


def download_era5():
    filename = "era5_2022.nc"

    # Check if file exists
    if os.path.exists(filename):
        print(f"{filename} already exists. Skipping download.")
        print(f"File size: {os.path.getsize(filename)} bytes")
        return filename

    # Initialize CDS API client
    try:
        c = cdsapi.Client()
        print("CDS API client initialized successfully.")
    except Exception as e:
        print("Error initializing CDS API client:", e)
        sys.exit(1)

    # Make the API request
    try:
        print("Requesting ERA5 data from CDS API...")
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': ['2m_temperature', 'total_precipitation'],
                'year': '2022',
                'month': [f"{i:02d}" for i in range(1, 13)],
                'day': [f"{i:02d}" for i in range(1, 32)],
                'time': '12:00',
                'area': [22, -10.5, 16, -4],  # N, W, S, E
            },
            filename
        )
    except Exception as e:
        print("Error during data retrieval:", e)
        sys.exit(1)

    # Check the downloaded file
    size = os.path.getsize(filename)
    print(f"Downloaded file: {filename} ({size} bytes)")
    if size < 1e6:  # Less than 1 MB
        print("Warning: The downloaded file appears too small.")
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            print("First few lines of the file:")
            for line in lines[:10]:
                print(line.strip())
    else:
        print("Download appears successful.")

    return filename


# Run the function
download_era5()


def visualize_era5(filename):
    """
    Opens an ERA5 NetCDF file with xarray, subsets the data to Mauritania's Sahel region,
    converts 2m temperature from Kelvin to Celsius, computes the time mean,
    and plots the result on a map using Cartopy.

    Parameters:
        filename (str): Path to the ERA5 NetCDF file.
    """
    # Open the dataset
    try:
        ds = xr.open_dataset(filename, engine="netcdf4")
    except Exception as e:
        print(f"Error opening dataset: {e}")
        sys.exit(1)

    print("Dataset information:")
    print(ds)

    # Check latitude order and set slice accordingly
    if ds.latitude[0] < ds.latitude[-1]:
        print("Latitudes are in ascending order. Adjusting slice.")
        lat_slice = slice(16, 22)
    else:
        print("Latitudes are in descending order. Using standard slice.")
        lat_slice = slice(22, 16)

    # Subset data to Mauritania's Sahel region
    ds_sahel = ds.sel(latitude=lat_slice, longitude=slice(-10.5, -4))

    # Verify that subset contains data
    if ds_sahel.sizes['latitude'] == 0 or ds_sahel.sizes['longitude'] == 0:
        print("No data found in the specified region. Check coordinates.")
        sys.exit(1)

    # Convert 2m temperature from Kelvin to Celsius
    t2m_c = ds_sahel['2m_temperature'] - 273.15

    # Compute the mean temperature over time
    t2m_mean = t2m_c.mean(dim='time')

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    t2m_mean.plot(ax=ax, transform=ccrs.PlateCarree(), cmap='coolwarm',
                  cbar_kwargs={'label': 'Mean 2m Temperature (°C)'})
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    ax.set_title("Mean 2m Temperature in Mauritania's Sahel (2022)")
    ax.set_extent([-10.5, -4, 16, 22], crs=ccrs.PlateCarree())
    plt.show()


def main():
    # Download ERA5 data if necessary.
    filename = download_era5()
    # Visualize the downloaded ERA5 data.
    visualize_era5(filename)


if __name__ == "__main__":
    main()
