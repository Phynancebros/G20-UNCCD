import os
import rasterio
import matplotlib.pyplot as plt
import streamlit as st

# Path to the data folder
DATA_FOLDER = "Datasets_Hackathon"

# Example file name (change to match your actual .tif file)
tif_filename = "2010LCT.tif"

# Create the full path
tif_path = os.path.join(DATA_FOLDER,"Modis_Land_Cover_Data", tif_filename)

st.title("Land Cover Visualization with Rasterio + Matplotlib")

# Read the raster data
with rasterio.open(tif_path) as src:
    data = src.read(1)  # Read the first band
    profile = src.profile  # Contains metadata like crs, transform, etc.

# Plot with matplotlib
fig, ax = plt.subplots()
cax = ax.imshow(data, cmap='viridis')
fig.colorbar(cax, ax=ax)
ax.set_title(f"Land Cover: {tif_filename}")
st.pyplot(fig)

st.write("Raster Metadata:")
st.json(profile)
