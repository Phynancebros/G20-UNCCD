import requests
import pandas as pd


def fetch_nasa_power_data(lat, lon, start_date, end_date, parameters):
    """
    Fetches daily data from NASA POWER API for a single point.

    Parameters:
      lat, lon: Coordinates of the point.
      start_date: Start date in YYYYMMDD format.
      end_date: End date in YYYYMMDD format.
      parameters: Comma-separated list of environmental parameters to retrieve.

    Returns:
      Parsed JSON response.
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "community": "RE",  # Renewable Energy community, adjust as needed.
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


def process_nasa_power_data(data, param_list):
    """
    Processes the JSON output from the NASA POWER API.

    Returns a DataFrame with one row per date and columns for each parameter.
    """
    # The JSON contains a nested "properties" -> "parameter" dictionary.
    param_data = data["properties"]["parameter"]

    # Use the keys of the first parameter to get the list of dates.
    dates = sorted(param_data[param_list[0]].keys())
    records = []
    for d in dates:
        record = {"Date": d}
        for param in param_list:
            record[param] = param_data.get(param, {}).get(d, None)
        records.append(record)
    df = pd.DataFrame(records)
    return df


def main():
    # Representative coordinates for the Sahel region (adjust as needed)
    lat = 15
    lon = 10

    # Define time period: 2010 to 2023
    start_date = "20100101"
    end_date = "20231231"

    # Specify the parameters you want.
    # In this example, we fetch:
    # - T2M: 2-meter air temperature (in °C or K depending on the POWER output)
    # - PRECTOTCORR: Corrected total precipitation (mm/day)
    # - ALLSKY_SFC_SW_DWN: All-sky surface shortwave downwards (W/m²)
    # - WS10M: 10-meter wind speed (m/s)
    # - RH2M: 2-meter relative humidity (%)
    parameters = "T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS10M,RH2M"
    param_list = ["T2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "WS10M", "RH2M"]

    # Fetch data using NASA POWER API
    try:
        data = fetch_nasa_power_data(lat, lon, start_date, end_date, parameters)
    except Exception as e:
        print("Error:", e)
        return

    # Process the JSON into a DataFrame
    df = process_nasa_power_data(data, param_list)

    # Optionally, convert the Date field to datetime (if needed)
    df['Date'] = pd.to_datetime(df['Date'], format="%Y%m%d")

    # Save DataFrame to CSV
    csv_file = "../notebooks/nasa_power_indices.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved NASA POWER data to {csv_file}")

    # Optionally, display the DataFrame
    print(df.head())


if __name__ == "__main__":
    main()
