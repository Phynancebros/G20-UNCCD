import numpy as np
import csv
import os

def get_raster_stats(data):
    """
    Calculates basic statistics from a NumPy array (float) containing raster values.
    Returns a dictionary with min, max, mean, and median.
    
    Parameters:
    - data: NumPy array containing raster values.
    
    Returns:
    - Dictionary with min, max, mean, and median.
    """
    valid_data = data[~np.isnan(data)]
    if len(valid_data) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None
        }
    
    return {
        "min": float(np.min(valid_data)),
        "max": float(np.max(valid_data)),
        "mean": float(np.mean(valid_data)),
        "median": float(np.median(valid_data))
    }

def save_stats_to_csv(csv_path, stats_list):
    """
    Saves a list of dictionaries (with fields 'filename', 'min', 'max', 'mean', 'median')
    to a CSV file.
    
    Parameters:
    - csv_path: Path to the CSV file.
    - stats_list: List of dictionaries containing statistics.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["filename", "min", "max", "mean", "median"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in stats_list:
            writer.writerow(row)

# Example interpretation:
# - min/max: range of values in the raster
# - mean/median: if the mean is much greater than the median, the distribution might be “right-skewed” (few pixels with very high values).
# - If min and max are close, the dataset is very “homogeneous”.
