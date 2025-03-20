import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import numpy as np
import os

def generate_uniform_raster(tiff_path, output_path, fill_value=1):
    """
    Generates a uniform raster with a specified fill value.
    
    Parameters:
    - tiff_path: Path to the input TIFF file.
    - output_path: Path to save the output uniform raster.
    - fill_value: Value to fill the raster where data is defined.
    """
    with rasterio.open(tiff_path) as src:
        img = src.read(1)

        mask_defined = img != src.nodata

        uniform_data = np.where(mask_defined, fill_value, 0).astype(rasterio.uint8)

        meta = src.meta.copy()
        meta.update(dtype=rasterio.uint8, nodata=0)

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(uniform_data, 1)

def plot_shapefiles_with_existing_outline(shp_folder_path, outline_raster_path, output_folder):
    """
    Plots shapefiles with an existing outline raster.
    
    Parameters:
    - shp_folder_path: Path to the folder containing shapefiles.
    - outline_raster_path: Path to the outline raster file.
    - output_folder: Folder to save the output plots.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    shp_files = [os.path.join(shp_folder_path, f) for f in os.listdir(shp_folder_path) if f.endswith('.shp')]

    with rasterio.open(outline_raster_path) as src:
        raster_crs = src.crs
        raster_extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

    for shp_file in shp_files:
        fig, ax = plt.subplots(figsize=(12, 12))

        # Open the outline raster
        with rasterio.open(outline_raster_path) as src:
            rasterio.plot.show(src, ax=ax, cmap='gray', alpha=0.5)

        # Read shapefile
        gdf = gpd.read_file(shp_file)

        # Convert shapefile CRS to raster CRS
        if gdf.crs != raster_crs:
            gdf = gdf.to_crs(raster_crs)

        # Plot shapefile with distinction if available
        if 'TYPE' in gdf.columns:
            gdf.plot(column='TYPE', ax=ax, linewidth=1.2, legend=True, cmap='Set2', alpha=0.7)
        else:
            gdf.plot(ax=ax, linewidth=1.2, edgecolor='blue', alpha=0.7)

        # Limit axes to raster extent (for clarity and correct geographic positioning)
        ax.set_xlim([raster_extent[0], raster_extent[1]])
        ax.set_ylim([raster_extent[2], raster_extent[3]])

        filename = os.path.splitext(os.path.basename(shp_file))[0]

        ax.set_title(f'Map - {filename}', fontsize=15)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.grid(False)

        output_path = os.path.join(output_folder, f"map_{filename}.png")
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close(fig)

# Example usage
shp_folder_path = 'Datasets_Hackathon/Streamwater_Line_Road_Network'
raster_file = 'Datasets_Hackathon/Modis_Land_Cover_Data/2010LCT.tif'
output_maps_folder = 'mappe_output'
outline_path = os.path.join(output_maps_folder, 'outline_raster.tif')
admin_layers_path = "Datasets_Hackathon/Admin_layers"

# Generate uniform raster
generate_uniform_raster(raster_file, outline_path)

# Plot and save each shapefile separately
plot_shapefiles_with_existing_outline(shp_folder_path, outline_path, output_maps_folder)
plot_shapefiles_with_existing_outline(admin_layers_path, outline_path, output_maps_folder)
