import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from .stats_module import get_raster_stats, save_stats_to_csv

def visualize_raster(file_path, ax, no_data_value=65533, hist_output_dir=None):
    """
    Loads the raster and visualizes it on the subplot ax,
    WITHOUT saving or closing the figure.
    If hist_output_dir is not None, also generates the raster histogram.
    
    Parameters:
    - file_path: Path to the raster file.
    - ax: Matplotlib subplot axis to plot the raster.
    - no_data_value: Value representing no data in the raster.
    - hist_output_dir: Directory to save the histogram (if not None).
    """
    with rasterio.open(file_path) as src:
        data = src.read(1).astype(float)

        # Handle NoData
        if src.nodata is not None:
            data[data == src.nodata] = np.nan
        data[data == no_data_value] = np.nan

        # If all NoData, exit and print warning
        if np.isnan(data).all():
            ax.set_title(f"{os.path.basename(file_path)} - ALL NODATA")
            ax.axis('off')
            return
        
        # Plot the raster
        cax = ax.imshow(data, cmap='viridis', interpolation='none')
        ax.set_title(os.path.basename(file_path))
        plt.colorbar(cax, ax=ax, orientation='vertical', label='Value')

        # Optional histogram
        if hist_output_dir is not None:
            os.makedirs(hist_output_dir, exist_ok=True)
            valid_data = data[~np.isnan(data)].ravel()
            plt.figure()
            plt.hist(valid_data, bins=50, color='blue', alpha=0.7)
            plt.title(f"Histogram - {os.path.basename(file_path)}")
            plt.xlabel('Value')
            plt.ylabel('Frequency')
            hist_path = os.path.join(hist_output_dir, f"{os.path.basename(file_path)}_hist.png")
            plt.savefig(hist_path, bbox_inches='tight')
            plt.close()
            print(f"Saved histogram to {hist_path}")

def compare_rasters(file_paths, output_dir, comparison_title):
    """
    Creates a single figure with side-by-side subplots to
    visualize the rasters in file_paths.
    Calculates basic statistics and saves them to a CSV file.
    
    Parameters:
    - file_paths: List of paths to raster files.
    - output_dir: Directory to save the output visualization and statistics.
    - comparison_title: Title for the comparison visualization.
    """
    import matplotlib.pyplot as plt  # for safety, local import

    fig, axes = plt.subplots(1, len(file_paths), figsize=(6*len(file_paths), 6))
    if len(file_paths) == 1:
        axes = [axes]

    stats_list = []

    for ax, file_path in zip(axes, file_paths):
        with rasterio.open(file_path) as src:
            data = src.read(1).astype(float)
            if src.nodata is not None:
                data[data == src.nodata] = np.nan
            data[data == 65533] = np.nan

        # Visualization
        visualize_raster(
            file_path, 
            ax, 
            hist_output_dir=os.path.join(output_dir, "histograms")
        )
        
        # Calculate statistics
        stats = get_raster_stats(data)
        stats_list.append({
            "filename": os.path.basename(file_path),
            **stats
        })

    # Save figure
    fig.suptitle(comparison_title, fontsize=16)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{comparison_title}.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved comparison visualization to {out_path}")

    # Save CSV with statistics
    csv_filename = f"{comparison_title}_stats.csv"
    csv_path = os.path.join(output_dir, "stats", csv_filename)
    save_stats_to_csv(csv_path, stats_list)

    print(f"Saved CSV stats to {csv_path}")

# How to interpret the compare_rasters plots:
# - Each subplot shows a different year/dataset.
# - Visually compare the spatial distribution and colorbar.
# - At a glance, you can see which year has higher or lower values.
# - Detailed histograms are found under the "histograms" folder.
# - Min, max, mean, median for each raster are found in the CSV under "stats".
