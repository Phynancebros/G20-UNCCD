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
        "community": "RE",  # Renewable energy community
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

    The API returns a JSON object with a nested "properties" -> "parameter"
    dictionary. For each parameter (e.g., T2M, PRECTOTCORR), keys are dates.

    Returns:
      A DataFrame with one row per date and columns for each parameter.
    """
    # Access the nested parameter dictionary:
    param_data = data["properties"]["parameter"]

    # All dates are the same across parameters; we can use the first parameter’s keys.
    dates = sorted(param_data[param_list[0]].keys())

    # Build a list of records for each date.
    records = []
    for d in dates:
        # For each parameter in our list, get its value for this date.
        record = {"Date": d}
        for param in param_list:
            record[param] = param_data.get(param, {}).get(d, None)
        records.append(record)

    df = pd.DataFrame(records)
    return df


def main():
    """
    Main function to fetch and process NASA POWER data.
    """
    # Representative coordinates for the Sahel region (you can adjust as needed)
    lat = 15
    lon = 10

    # Define the time period (from 2010 to 2023)
    start_date = "20100101"
    end_date = "20231231"

    # Specify the parameters you want: 2m temperature and corrected total precipitation
    parameters = "T2M,PRECTOTCORR"
    param_list = ["T2M", "PRECTOTCORR"]

    # Fetch data using the NASA POWER API
    try:
        data = fetch_nasa_power_data(lat, lon, start_date, end_date, parameters)
    except Exception as e:
        print("Error:", e)
        return

    # Process the JSON response into a DataFrame
    df = process_nasa_power_data(data, param_list)

    # Save the data to CSV
    csv_file = "nasa_power_data.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved NASA POWER data to {csv_file}")


if __name__ == "__main__":
    main()
