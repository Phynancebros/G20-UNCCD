#!/usr/bin/env python
import requests
import json
import time
import datetime


def request_season_max_value(bearer_token):
    """
    Requests the "Season Maximum Value 2010–present (raster 300 m), global, yearly, version 1" dataset
    from the Copernicus Land API.

    The payload sets:
      - DatasetID to "28a93a5edcce4b6a931dc53b1c3f1eab"
      - DatasetDownloadInformationID to "1c7acc95-02e5-4503-82fc-966a6dd225dd" (Season 1 option)
      - OutputFormat as "Geotiff" and CRS as EPSG:4326.
      - A bounding box covering Mauritania's Sahel: [-10.5, 16.0, -4.0, 22.0].
      - A temporal filter from January 1, 2010 until now.
    """
    url = "http://land.copernicus.eu/api/@datarequest_post"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    # Dataset and download IDs for "Season Maximum Value" (Season 1)
    dataset_id = "28a93a5edcce4b6a931dc53b1c3f1eab"
    download_info_id = "1c7acc95-02e5-4503-82fc-966a6dd225dd"

    # Define temporal filter:
    # Start date: 2010-01-01 in Unix epoch milliseconds.
    start_date = datetime.datetime(2010, 1, 1)
    start_date_ms = int(start_date.timestamp() * 1000)
    # End date: current date and time.
    end_date = datetime.datetime.now()
    end_date_ms = int(end_date.timestamp() * 1000)

    temporal_filter = {
        "StartDate": start_date_ms,
        "EndDate": end_date_ms
    }

    payload = {
        "Datasets": [
            {
                "DatasetID": dataset_id,
                "DatasetDownloadInformationID": download_info_id,
                "OutputFormat": "Geotiff",
                "OutputGCS": "EPSG:4326",
                "BoundingBox": [-10.5, 16.0, -4.0, 22.0],  # [min_lon, min_lat, max_lon, max_lat]
                "TemporalFilter": temporal_filter
            }
        ]
    }

    print("Sending request for Season Maximum Value (2010–present) dataset...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()


def main():
    # Replace with your actual Bearer token
    bearer_token = "<YOUR_BEARER_TOKEN>"

    try:
        result = request_season_max_value(bearer_token)
        print("API Response:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
