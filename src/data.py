#!/usr/bin/env python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle


def fetch_nasa_power_data(lat, lon, start_date, end_date, parameters):
    """
    Fetches daily data from NASA POWER API for a single point.
    Parameters:
      lat, lon: Coordinates (floats).
      start_date: YYYYMMDD string.
      end_date: YYYYMMDD string.
      parameters: Comma-separated list of parameters.
    Returns:
      Parsed JSON response.
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_date,
        "end": end_date,
        "parameters": parameters,
        "format": "JSON"
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: HTTP {response.status_code}")
    return response.json()


def process_nasa_power_data(data, param):
    """
    Processes the JSON output for a single parameter.
    Computes the mean of the daily values.
    """
    daily_values = data["properties"]["parameter"][param]
    values = np.array(list(daily_values.values()), dtype=float)
    return np.mean(values)


def get_annual_means_for_point(lat, lon, param_list, year):
    """
    For a given grid point and year, fetches daily data for the parameters in param_list
    and returns a dictionary of {parameter: mean_value}.
    """
    start_date = f"{year}0101"
    end_date = f"{year}1231"
    parameters = ",".join(param_list)
    data = fetch_nasa_power_data(lat, lon, start_date, end_date, parameters)
    results = {}
    for param in param_list:
        results[param] = process_nasa_power_data(data, param)
    return results


def build_grid(lon_min, lon_max, lat_min, lat_max, spacing):
    """
    Constructs arrays of latitudes and longitudes for a grid.
    """
    lons = np.arange(lon_min, lon_max + spacing, spacing)
    lats = np.arange(lat_min, lat_max + spacing, spacing)
    return lats, lons


def main():
    # Define the region for Mauritania's Sahel.
    # For this example, we use: longitude from -17 to -4, latitude from 15 to 24.
    lon_min, lon_max = -17, -4
    lat_min, lat_max = 15, 24
    spacing = 2.0  # Use a 2° grid to reduce the number of API calls.

    # Define the ten-year period (2013 to 2022)
    start_year = 2013
    end_year = 2022
    years = list(range(start_year, end_year + 1))

    # Define the parameters to fetch.
    param_list = ["T2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "WS10M", "RH2M"]
    # Note: T2M is returned in Celsius from NASA POWER.

    # Data will be stored in a list of dictionaries.
    records = []

    # Define a pickle filename to save/load the DataFrame.
    pickle_file = "../graphs/nasa_power_grid_data.pkl"

    if os.path.exists(pickle_file):
        print("Loading grid data from pickle file.")
        with open(pickle_file, "rb") as f:
            df = pickle.load(f)
        # Check if T2M values are in Celsius (e.g., if min value < 0) and add 273 if needed.
        if df["T2M"].min() < 0:
            print("Detected T2M values in Celsius. Converting to Kelvin by adding 273.")
            df["T2M"] = df["T2M"] + 273
    else:
        print("Building grid data from API for years", years)
        lats, lons = build_grid(lon_min, lon_max, lat_min, lat_max, spacing)
        total_points = len(lats) * len(lons)
        count = 0
        for year in years:
            for lat in lats:
                for lon in lons:
                    try:
                        means = get_annual_means_for_point(lat, lon, param_list, year)
                        # **IMPORTANT**: Add 273 to T2M to convert from Celsius to Kelvin.
                        means["T2M"] = means["T2M"] + 273
                        records.append({
                            "year": year,
                            "latitude": lat,
                            "longitude": lon,
                            "T2M": means["T2M"],
                            "PRECTOTCORR": means["PRECTOTCORR"],
                            "ALLSKY_SFC_SW_DWN": means["ALLSKY_SFC_SW_DWN"],
                            "WS10M": means["WS10M"],
                            "RH2M": means["RH2M"]
                        })
                        count += 1
                        print(f"Processed ({lat},{lon}) for {year} [{count}/{total_points * len(years)}]")
                    except Exception as e:
                        print(f"Error at ({lat},{lon}) for {year}: {e}")
                        records.append({
                            "year": year,
                            "latitude": lat,
                            "longitude": lon,
                            "T2M": np.nan,
                            "PRECTOTCORR": np.nan,
                            "ALLSKY_SFC_SW_DWN": np.nan,
                            "WS10M": np.nan,
                            "RH2M": np.nan
                        })
        df = pd.DataFrame(records)
        # Save as CSV (optional)
        csv_file = "../graphs/nasa_power_grid_data.csv"
        df.to_csv(csv_file, index=False)
        print(f"Saved grid data as CSV to {csv_file}")
        # Save DataFrame as a pickle file for quick reaccess later.
        with open(pickle_file, "wb") as f:
            pickle.dump(df, f)
        print(f"Saved grid data as pickle to {pickle_file}")

    # --------------------------
    # Visualization 1: Heatmaps for each parameter for year 2022.
    # --------------------------
    def create_heatmap(df, year, variable, title, out_file=None):
        df_year = df[df["year"] == year]
        heatmap_data = df_year.pivot(index="latitude", columns="longitude", values=variable)
        # Sort latitudes in descending order for proper orientation.
        heatmap_data = heatmap_data.sort_index(ascending=False)
        plt.figure(figsize=(8, 6))
        ax = sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".1f",
                         cbar_kws={"label": f"{variable}"})
        plt.title(title)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.tight_layout()
        if out_file:
            plt.savefig(out_file)
            print(f"Saved heatmap as {out_file}")
        plt.show()

    import seaborn as sns
    selected_year = 2022
    for param in param_list:
        create_heatmap(df, selected_year, param, f"Mean {param} in {selected_year}")

    # --------------------------
    # Visualization 2: Time series for each parameter separately.
    # --------------------------
    # For each parameter, compute the regional (grid-average) annual mean and plot the time series.
    for param in param_list:
        regional = df.groupby("year")[param].mean().reset_index()
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=regional, x="year", y=param, marker="o")
        plt.title(f"Regional Mean {param} (2013-2022)")
        plt.xlabel("Year")
        if param == "T2M":
            plt.ylabel("Temperature (K)")
        elif param == "PRECTOTCORR":
            plt.ylabel("Precipitation (mm/day)")
        elif param == "ALLSKY_SFC_SW_DWN":
            plt.ylabel("SW Down (W/m²)")
        elif param == "WS10M":
            plt.ylabel("Wind Speed (m/s)")
        elif param == "RH2M":
            plt.ylabel("Relative Humidity (%)")
        plt.grid(True)
        plt.tight_layout()
        out_file = f"regional_time_series_{param}.png"
        plt.savefig(out_file)
        print(f"Saved regional time series plot for {param} as {out_file}")
        plt.show()


if __name__ == "__main__":
    main()
