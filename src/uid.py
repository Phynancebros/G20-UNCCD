import requests
import json


def search_datasets():
    # URL to search for datasets with specified metadata fields.
    url = (
        "http://land.copernicus.eu//api/@search"
        "?portal_type=DataSet"
        "&metadata_fields=UID"
        "&metadata_fields=dataset_full_format"
        "&metadata_fields=dataset_download_information"
    )
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Pretty-print the JSON response.
        print("Search results:")
        print(json.dumps(data, indent=2))
        return data
    else:
        raise Exception(f"Error: HTTP {response.status_code} - {response.text}")


def main():
    try:
        results = search_datasets()
    except Exception as e:
        print("Search failed:", e)


if __name__ == "__main__":
    main()

