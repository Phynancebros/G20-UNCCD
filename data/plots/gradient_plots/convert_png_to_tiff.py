import os
from PIL import Image

# Directory containing the PNG files
input_dir = "data/plots/gradient_plots/"
# Directory to save the TIFF files
output_dir = "data/plots/gradient_plots/tiff/"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List of PNG files to convert
png_files = [
    "bad_transition_2010LCT_to_2011LCT.png",
    "bad_transition_2011LCT_to_2012LCT.png",
    "bad_transition_2012LCT_to_2013LCT.png",
    "bad_transition_2013LCT_to_2014LCT.png",
    "bad_transition_2014LCT_to_2015LCT.png",
    "bad_transition_2015LCT_to_2016LCT.png",
    "bad_transition_2016LCT_to_2017LCT.png",
    "bad_transition_2017LCT_to_2018LCT.png",
    "bad_transition_2018LCT_to_2019LCT.png",
    "bad_transition_2019LCT_to_2020LCT.png",
    "bad_transition_2020LCT_to_2021LCT.png",
    "bad_transition_2021LCT_to_2022LCT.png",
    "bad_transition_2022LCT_to_2023LCT.png"
]

# Convert each PNG file to TIFF format
for png_file in png_files:
    png_path = os.path.join(input_dir, png_file)
    tiff_path = os.path.join(output_dir, png_file.replace(".png", ".tiff"))
    
    with Image.open(png_path) as img:
        img.save(tiff_path, format="TIFF")
        print(f"Converted {png_file} to {tiff_path}")
