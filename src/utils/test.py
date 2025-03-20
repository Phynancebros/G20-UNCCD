#!/usr/bin/env python
import ee
import json
import geemap
import sys


def main():
    # Inizializza Earth Engine specificando il progetto (modifica l'ID se necessario)
    try:
        ee.Initialize(project="g20-hackaton")
    except Exception as e:
        print("Errore durante l'inizializzazione di Earth Engine:", e)
        sys.exit(1)

    # Definisci la geometria della regione del Sahel in Mauritania (approssimativamente)
    # [lon_min, lat_min, lon_max, lat_max]
    mauritania_sahel = ee.Geometry.Rectangle([-17, 15, -4, 24])
    # Create a styled boundary with red outline and no fill
    boundary_layer = ee.FeatureCollection([mauritania_sahel]).style(
        **{'color': 'red', 'fillColor': '00000000', 'width': 3}
    )

    # Definisci l'intervallo di date e gli anni (usiamo 2022 per i layer di esempio)
    years = list(range(2010, 2024))

    # 1. Recupero dell'EVI (MODIS MOD13Q1)
    def annual_mean_evi(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (ee.ImageCollection('MODIS/006/MOD13Q1')
                 .filterDate(start, end)
                 .filterBounds(mauritania_sahel)
                 .select('EVI')
                 .mean()
                 .set('year', year))
        return image

    annual_evi = ee.ImageCollection(ee.List(years).map(annual_mean_evi))
    print("EVI Collection:")
    print(json.dumps(annual_evi.getInfo(), indent=2))

    # 2. Recupero del LAI (MODIS MOD15A2H) – usiamo "Lai_500m"
    def annual_mean_lai(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (ee.ImageCollection('MODIS/006/MOD15A2H')
                 .filterDate(start, end)
                 .filterBounds(mauritania_sahel)
                 .select('Lai_500m')
                 .mean()
                 .set('year', year))
        return image

    annual_lai = ee.ImageCollection(ee.List(years).map(annual_mean_lai))
    print("LAI Collection:")
    print(json.dumps(annual_lai.getInfo(), indent=2))

    # 3. Recupero della Temperatura (ERA5 Daily)
    def annual_mean_era5(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (ee.ImageCollection('ECMWF/ERA5/DAILY')
                 .filterDate(start, end)
                 .filterBounds(mauritania_sahel)
                 .select(['mean_2m_air_temperature'])
                 .mean()
                 .set('year', year))
        return image

    annual_era5 = ee.ImageCollection(ee.List(years).map(annual_mean_era5))
    print("ERA5 Collection (Temperatura):")
    print(json.dumps(annual_era5.getInfo(), indent=2))

    # 4. Recupero delle Precipitazioni (CHIRPS Daily) – calcoliamo il totale annuale
    def annual_precip(year):
        start = ee.Date.fromYMD(year, 1, 1)
        end = start.advance(1, 'year')
        image = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
                 .filterDate(start, end)
                 .filterBounds(mauritania_sahel)
                 .sum()
                 .set('year', year))
        return image

    annual_precip = ee.ImageCollection(ee.List(years).map(annual_precip))
    print("Precipitazioni Annuali:")
    print(json.dumps(annual_precip.getInfo(), indent=2))

    # Creazione della mappa interattiva con geemap, centrata sulla regione
    Map = geemap.Map(center=[19.5, 19.5], zoom=6)
    # Fit the map bounds to the geometry of Mauritania's Sahel
    bounds = mauritania_sahel.bounds().getInfo()['coordinates']
    Map.fit_bounds(bounds)

    # Aggiungi il layer del confine con stile
    Map.addLayer(boundary_layer, {}, "Confine Sahel Mauritania")

    # Aggiungi layer di esempio per l'anno 2022:
    # EVI 2022
    evi_2022 = (ee.ImageCollection('MODIS/006/MOD13Q1')
                .select('EVI')
                .filterDate('2022-01-01', '2022-12-31')
                .filterBounds(mauritania_sahel)
                .mean())
    evi_vis = {'min': 0, 'max': 6000, 'palette': ['blue', 'white', 'green']}
    Map.addLayer(evi_2022, evi_vis, "EVI 2022")

    # LAI 2022
    lai_2022 = (ee.ImageCollection('MODIS/006/MOD15A2H')
                .select('Lai_500m')
                .filterDate('2022-01-01', '2022-12-31')
                .filterBounds(mauritania_sahel)
                .mean())
    lai_vis = {'min': 0, 'max': 10, 'palette': ['yellow', 'green']}
    Map.addLayer(lai_2022, lai_vis, "LAI 2022")

    # Temperatura 2022 (in Kelvin)
    era5_2022 = (ee.ImageCollection('ECMWF/ERA5/DAILY')
                 .filterDate('2022-01-01', '2022-12-31')
                 .filterBounds(mauritania_sahel)
                 .select(['mean_2m_air_temperature'])
                 .mean())
    temp_vis = {'min': 250, 'max': 310, 'palette': ['blue', 'purple', 'red']}
    Map.addLayer(era5_2022, temp_vis, "Temperatura 2022")

    # Precipitazioni 2022 (somma annuale)
    precip_2022 = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
                   .filterDate('2022-01-01', '2022-12-31')
                   .filterBounds(mauritania_sahel)
                   .sum())
    precip_vis = {'min': 0, 'max': 1500, 'palette': ['white', 'blue']}
    Map.addLayer(precip_2022, precip_vis, "Precipitazioni 2022")

    # Aggiungi una legenda per l'EVI come esempio
    legend_dict_evi = {
        "0-2000": "#0000FF",
        "2000-4000": "#FFFFFF",
        "4000-6000": "#00FF00"
    }
    Map.add_legend(legend_title="Scala EVI", legend_dict=legend_dict_evi)

    # Aggiungi controlli per gestire i layer
    Map.addLayerControl()

    # Salva la mappa interattiva in un file HTML
    output_html = "sahel_map.html"
    Map.to_html(output_html)
    print("La mappa interattiva è stata salvata in:", output_html)


if __name__ == '__main__':
    main()
