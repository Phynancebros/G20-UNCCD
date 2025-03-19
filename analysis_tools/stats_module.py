import numpy as np
import csv
import os

def get_raster_stats(data):
    """
    Calcola statistiche di base da un array NumPy (float) che contiene i valori del raster.
    Ritorna un dizionario con min, max, media e mediana.
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
    Salva una lista di dizionari (con campi 'filename', 'min', 'max', 'mean', 'median')
    in un file CSV.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["filename", "min", "max", "mean", "median"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in stats_list:
            writer.writerow(row)

# Esempio di interpretazione:
# - min/max: range dei valori nel raster
# - mean/median: se la media è molto maggiore della mediana, la distribuzione potrebbe essere “right-skewed” (pochi pixel con valori molto alti).
# - Se min e max sono vicini, il dataset è molto “omogeneo”.
