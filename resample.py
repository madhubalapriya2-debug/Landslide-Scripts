import os
import shutil
import processing

from qgis.core import (
    QgsRasterLayer,
    QgsProject
)

# ----------------------------
# PURPOSE:
# Prepare final model input rasters
# - Elevation (from DEM)
# - Rainfall (resampled to DEM grid)
# - LULC (resampled to DEM grid)
# - NDVI (resampled to DEM grid)
# - STI (resampled to DEM grid)
# - TWI (resampled to DEM grid)
# - Slope (resampled to DEM grid)
# - Aspect (resampled to DEM grid)
# - Distance From River (resampled to DEM grid)
# ----------------------------

# ----------------------------
# INPUT (CLIPPED FILES)
# ----------------------------
base = "/Users/madhubalapriya/Downloads/Kerala/Clipped"

dem = os.path.join(base, "dem_clip.tif")
rain = os.path.join(base, "Rainfall_clip.tif")
lulc = os.path.join(base, "LULC_clip.tif")
ndvi = os.path.join(base, "NDVI_clip.tif")
sti = os.path.join(base, "STI_clip.tif")
twi = os.path.join(base, "TWI_clip.tif")
slope = os.path.join(base, "Slope_clip.tif")
aspect = os.path.join(base, "Aspect_clip.tif")
dist_river = os.path.join(base, "DFR_clip.tif")

# ----------------------------
# OUTPUT FOLDER
# ----------------------------
model_input_folder = r"/Users/madhubalapriya/Downloads/Kerala/processed/Model_Input"
os.makedirs(model_input_folder, exist_ok=True)

# ----------------------------
# OUTPUT PATHS
# ----------------------------
elevation_out = os.path.join(model_input_folder, "Elevation.tif")
rain_out = os.path.join(model_input_folder, "Rainfall.tif")
lulc_out = os.path.join(model_input_folder, "LULC.tif")
ndvi_out = os.path.join(model_input_folder, "NDVI.tif")
sti_out = os.path.join(model_input_folder, "STI.tif")
twi_out = os.path.join(model_input_folder, "TWI.tif")
slope_out = os.path.join(model_input_folder, "Slope.tif")
aspect_out = os.path.join(model_input_folder, "Aspect.tif")
dist_river_out = os.path.join(model_input_folder, "Distance_River.tif")

# ----------------------------
# LOAD DEM AS REFERENCE
# ----------------------------
dem_layer = QgsRasterLayer(dem, "dem_clip")

if not dem_layer.isValid():
    raise Exception("DEM reference raster is invalid")

extent = dem_layer.extent()

xmin = extent.xMinimum()
xmax = extent.xMaximum()
ymin = extent.yMinimum()
ymax = extent.yMaximum()

width = dem_layer.width()
height = dem_layer.height()

xres = (xmax - xmin) / width
yres = (ymax - ymin) / height

extent_string = f"{xmin},{xmax},{ymin},{ymax}"

print("===================================")
print("DEM REFERENCE GRID")
print("===================================")
print("CRS:", dem_layer.crs().authid())
print("Width:", width)
print("Height:", height)
print("Pixel Size X:", xres)
print("Pixel Size Y:", yres)
print("Extent:", extent_string)

# ----------------------------
# 1. SAVE DEM AS ELEVATION
# ----------------------------
shutil.copy(dem, elevation_out)
print("Elevation saved:", elevation_out)

# ----------------------------
# 2. RESAMPLE RAINFALL
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': rain,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 0,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': rain_out
})
print("Rainfall resampled:", rain_out)

# ----------------------------
# 3. RESAMPLE LULC
# Categorical data -> Nearest Neighbour
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': lulc,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 0,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': lulc_out
})
print("LULC resampled:", lulc_out)

# ----------------------------
# 4. RESAMPLE NDVI
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': ndvi,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': ndvi_out
})
print("NDVI resampled:", ndvi_out)

# ----------------------------
# 5. RESAMPLE STI
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': sti,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': sti_out
})
print("STI resampled:", sti_out)

# ----------------------------
# 6. RESAMPLE TWI
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': twi,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': twi_out
})
print("TWI resampled:", twi_out)

# ----------------------------
# 7. RESAMPLE SLOPE
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': slope,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': slope_out
})
print("Slope resampled:", slope_out)

# ----------------------------
# 8. RESAMPLE ASPECT
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': aspect,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': aspect_out
})
print("Aspect resampled:", aspect_out)

# ----------------------------
# 9. RESAMPLE DISTANCE FROM RIVER
# Continuous data -> Bilinear
# ----------------------------
processing.run("gdal:warpreproject", {
    'INPUT': dist_river,
    'SOURCE_CRS': None,
    'TARGET_CRS': dem_layer.crs(),
    'RESAMPLING': 1,
    'NODATA': None,
    'TARGET_RESOLUTION': xres,
    'OPTIONS': '',
    'DATA_TYPE': 0,
    'TARGET_EXTENT': extent_string,
    'TARGET_EXTENT_CRS': dem_layer.crs(),
    'MULTITHREADING': False,
    'EXTRA': '',
    'OUTPUT': dist_river_out
})
print("Distance From River resampled:", dist_river_out)

# ----------------------------
# LOAD OUTPUTS
# ----------------------------
layers = [
    QgsRasterLayer(elevation_out, "Elevation"),
    QgsRasterLayer(rain_out, "Rainfall"),
    QgsRasterLayer(lulc_out, "LULC"),
    QgsRasterLayer(ndvi_out, "NDVI"),
    QgsRasterLayer(sti_out, "STI"),
    QgsRasterLayer(twi_out, "TWI"),
    QgsRasterLayer(slope_out, "Slope"),
    QgsRasterLayer(aspect_out, "Aspect"),
    QgsRasterLayer(dist_river_out, "Distance_River")
]

print("\n==============================")
print("MODEL INPUT LAYERS")
print("==============================")

for lyr in layers:
    if lyr.isValid():
        QgsProject.instance().addMapLayer(lyr)

        print(
            f"{lyr.name()} → VALID | "
            f"Width: {lyr.width()} | "
            f"Height: {lyr.height()}"
        )

    else:
        print(f"{lyr.name()} → INVALID")

print("\n========================================")
print("ALL MODEL INPUT RASTERS PREPARED")
print("========================================")
print("1. Elevation")
print("2. Rainfall")
print("3. LULC")
print("4. NDVI")
print("5. STI")
print("6. TWI")
print("7. Slope")
print("8. Aspect")
print("9. Distance From River")
print("========================================")