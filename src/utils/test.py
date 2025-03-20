#!/usr/bin/env python
import ee
import json
import geemap
import sys

def main():
    # Initialize Earth Engine specifying the project (modify the ID if necessary)
    try:
        ee.Initialize(project="g20-hackaton")
    except Exception as e:
        print("Error during Earth Engine initialization:", e)
        sys.exit(1)

    # Define the geometry of the Sahel region in Mauritania (approximately)
    # [lon_min, lat_min, lon_max, lat_max]
    mauritania_sahel = ee.Geometry.Rectangle([-17, 15, -4, 24])

    # Define the date range and the years (we use 2022 as an example layer)
    years = list(range(2010, 2024))

    # 1. Retrieve EVI (MODIS MOD13Q1)
    def annual_mean_evi(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (
            ee.ImageCollection('MODIS/006/MOD13Q1')
            .filterDate(start, end)
            .filterBounds(mauritania_sahel)
            .select('EVI')
            .mean()
            .set('year', year)
        )
        return image

    annual_evi = ee.ImageCollection(ee.List(years).map(annual_mean_evi))
    print("EVI Collection:")
    print(json.dumps(annual_evi.getInfo(), indent=2))

    # 2. Retrieve LAI (MODIS MOD15A2H) – we use "Lai_500m"
    def annual_mean_lai(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (
            ee.ImageCollection('MODIS/006/MOD15A2H')
            .filterDate(start, end)
            .filterBounds(mauritania_sahel)
            .select('Lai_500m')
            .mean()
            .set('year', year)
        )
        return image

    annual_lai = ee.ImageCollection(ee.List(years).map(annual_mean_lai))
    print("LAI Collection:")
    print(json.dumps(annual_lai.getInfo(), indent=2))

    # 3. Retrieve Precipitation (CHIRPS Daily) – calculate the annual total
    def annual_precip(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (
            ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
            .filterDate(start, end)
            .filterBounds(mauritania_sahel)
            .sum()
            .set('year', year)
        )
        return image

    annual_precip = ee.ImageCollection(ee.List(years).map(annual_precip))
    print("Annual Precipitation:")
    print(json.dumps(annual_precip.getInfo(), indent=2))

    # Create the interactive map with geemap, centered on the region
    # Set layer_ctrl=False to remove the layer control in the top-right
    Map = geemap.Map(center=[19.5, 19.5], zoom=6, layer_ctrl=False)
    # Fit the map bounds to the geometry of Mauritania's Sahel
    bounds = mauritania_sahel.bounds().getInfo()['coordinates']
    Map.fit_bounds(bounds)

    # ----------------------------
    # REMOVED THE CODE THAT ADDED
    # THE RED BOUNDING BOX LAYER
    # AND THE LEGEND
    # ----------------------------

    # Add example layers for year 2022:
    # EVI 2022
    evi_2022 = (
        ee.ImageCollection('MODIS/006/MOD13Q1')
        .select('EVI')
        .filterDate('2022-01-01', '2022-12-31')
        .filterBounds(mauritania_sahel)
        .mean()
    )
    evi_vis = {'min': 0, 'max': 6000, 'palette': ['blue', 'white', 'green']}
    Map.addLayer(evi_2022, evi_vis, "EVI 2022")

    # LAI 2022
    lai_2022 = (
        ee.ImageCollection('MODIS/006/MOD15A2H')
        .select('Lai_500m')
        .filterDate('2022-01-01', '2022-12-31')
        .filterBounds(mauritania_sahel)
        .mean()
    )
    lai_vis = {'min': 0, 'max': 10, 'palette': ['yellow', 'green']}
    Map.addLayer(lai_2022, lai_vis, "LAI 2022")

    # Precipitation 2022 (annual sum)
    precip_2022 = (
        ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
        .filterDate('2022-01-01', '2022-12-31')
        .filterBounds(mauritania_sahel)
        .sum()
    )
    precip_vis = {'min': 0, 'max': 1500, 'palette': ['white', 'blue']}
    Map.addLayer(precip_2022, precip_vis, "Precipitation 2022")

    # Removed the legend or any references to it
    # Removed Map.addLayerControl() if present

    # Save the interactive map to an HTML file
    output_html = "sahel_map.html"
    Map.to_html(output_html)
    print("The interactive map has been saved to:", output_html)

if __name__ == '__main__':
    main()
