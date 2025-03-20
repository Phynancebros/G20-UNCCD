import ee

# 1. Authenticate and Initialize Earth Engine
try:
    ee.Initialize(project="g20-hackaton")
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# 2. Define the Region of Interest (ROI) - bounding box for southern Mauritania
lat_min, lat_max = 14, 18
lon_min, lon_max = -12, -6
roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])

# 3. Fetch EVI data for each year from 2010 to 2023
for year in range(2010, 2024):
    start_date = f"{year}-01-01"
    end_date   = f"{year}-12-31"

    # MODIS/006/MOD13Q1 has EVI at 250m resolution, 16-day composites
    evi_col = (
        ee.ImageCollection("MODIS/006/MOD13Q1")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .select('EVI')
    )

    # Create a mean composite for the entire year
    evi_mean = evi_col.mean().clip(roi)

    # Set up an export task to Google Drive
    task = ee.batch.Export.image.toDrive(
        image=evi_mean,
        description=f"MODIS_EVI_Composite_SahelMauritania_{year}",
        folder='GEE_Exports',  # Adjust to your preferred Drive folder
        fileNamePrefix=f"MODIS_EVI_{year}",
        region=roi.coordinates(),
        scale=250,          # MOD13Q1 is 250m
        crs='EPSG:4326'
    )
    task.start()
    print(f"Export task for {year} started.")

print("All EVI export tasks started. Check Earth Engine Tasks for progress.")

