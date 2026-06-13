import os
import processing

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject
)

# ============================================================
# 1. INPUT FILE PATHS
# ============================================================

# Raster Layers
dem_path ="/Users/madhubalapriya/Downloads/Kerala/dataset/dem.tif"
slope_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/SLOPE/Slope2.tif"

aspect_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/ASPECT/ASPECT.tif"

rainfall_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/rainfall/rainfall.tif"

lulc_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/lulc/lulc.tif"

dfr_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/dfr/distancetoriver.tif"

sti_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/STI/STI.tif"

twi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/TWI/TWI.tif"

ndvi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/ndvi/ndvi.tif"

# Vector Layers
lithology_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/lithology/lithology.shp"

aoi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/Wayanadshapefile/wayanadshp.shp"


# ============================================================
# 2. OUTPUT FOLDER
# ============================================================

output_folder = "/Users/madhubalapriya/Downloads/Kerala/Reprojected"

os.makedirs(output_folder, exist_ok=True)

print("Output Folder Created")


# ============================================================
# 3. TARGET CRS
# ============================================================

# WGS 84 / UTM Zone 43N
target_crs = QgsCoordinateReferenceSystem("EPSG:32643")

print("Target CRS :", target_crs.authid())


# ============================================================
# 4. OUTPUT FILE PATHS
# ============================================================
dem_out=os.path.join(output_folder, "dem_32643.tif")

slope_out = os.path.join(output_folder, "Slope_32643.tif")

aspect_out = os.path.join(output_folder, "Aspect_32643.tif")

rainfall_out = os.path.join(output_folder, "Rainfall_32643.tif")

lulc_out = os.path.join(output_folder, "LULC_32643.tif")

dfr_out = os.path.join(output_folder, "DFR_32643.tif")

sti_out = os.path.join(output_folder, "STI_32643.tif")

twi_out = os.path.join(output_folder, "TWI_32643.tif")

ndvi_out = os.path.join(output_folder, "NDVI_32643.tif")

lithology_out = os.path.join(output_folder, "Lithology_32643.shp")

aoi_out = os.path.join(output_folder, "AOI_32643.shp")


# ============================================================
# 5. FUNCTION TO REPROJECT RASTER
# ============================================================

def reproject_raster(input_path, output_path):

    processing.run("gdal:warpreproject", {

        'INPUT': input_path,
        'SOURCE_CRS': None,
        'TARGET_CRS': target_crs,
        'RESAMPLING': 0,
        'NODATA': None,
        'TARGET_RESOLUTION': None,
        'OPTIONS': '',
        'DATA_TYPE': 0,
        'TARGET_EXTENT': None,
        'TARGET_EXTENT_CRS': None,
        'MULTITHREADING': False,
        'EXTRA': '',
        'OUTPUT': output_path
    })

    print(f"✅ Reprojected Raster : {output_path}")


# ============================================================
# 6. FUNCTION TO REPROJECT VECTOR
# ============================================================

def reproject_vector(input_path, output_path):

    processing.run("native:reprojectlayer", {

        'INPUT': input_path,
        'TARGET_CRS': target_crs,
        'OUTPUT': output_path
    })

    print(f"✅ Reprojected Vector : {output_path}")


# ============================================================
# 7. REPROJECT RASTER LAYERS
# ============================================================

print("\n========================================")
print("REPROJECTING RASTER LAYERS")
print("========================================")

reproject_raster(dem_path, dem_out)

reproject_raster(slope_path, slope_out)

reproject_raster(aspect_path, aspect_out)

reproject_raster(rainfall_path, rainfall_out)

reproject_raster(lulc_path, lulc_out)

reproject_raster(dfr_path, dfr_out)

reproject_raster(sti_path, sti_out)

reproject_raster(twi_path, twi_out)

reproject_raster(ndvi_path, ndvi_out)


# ============================================================
# 8. REPROJECT VECTOR LAYERS
# ============================================================

print("\n========================================")
print("REPROJECTING VECTOR LAYERS")
print("========================================")

reproject_vector(lithology_path, lithology_out)

reproject_vector(aoi_path, aoi_out)


# ============================================================
# 9. LOAD REPROJECTED LAYERS
# ============================================================

print("\n========================================")
print("LOADING REPROJECTED LAYERS")
print("========================================")

# Raster Layers
dem_layer = QgsRasterLayer(dem_out, "dem_32643")

slope_layer = QgsRasterLayer(slope_out, "Slope_32643")

aspect_layer = QgsRasterLayer(aspect_out, "Aspect_32643")

rainfall_layer = QgsRasterLayer(rainfall_out, "Rainfall_32643")

lulc_layer = QgsRasterLayer(lulc_out, "LULC_32643")

dfr_layer = QgsRasterLayer(dfr_out, "DFR_32643")

sti_layer = QgsRasterLayer(sti_out, "STI_32643")

twi_layer = QgsRasterLayer(twi_out, "TWI_32643")

ndvi_layer = QgsRasterLayer(ndvi_out, "NDVI_32643")

# Vector Layers
lithology_layer = QgsVectorLayer(
    lithology_out,
    "Lithology_32643",
    "ogr"
)

aoi_layer = QgsVectorLayer(
    aoi_out,
    "AOI_32643",
    "ogr"
)


# ============================================================
# 10. STORE LAYERS
# ============================================================

layers = [
    dem_layer,
    slope_layer,
    aspect_layer,
    rainfall_layer,
    lulc_layer,
    dfr_layer,
    sti_layer,
    twi_layer,
    ndvi_layer,
    lithology_layer,
    aoi_layer
]


# ============================================================
# 11. ADD LAYERS TO QGIS
# ============================================================

print("\n========================================")
print("ADDING LAYERS TO QGIS")
print("========================================")

for layer in layers:

    if layer.isValid():

        QgsProject.instance().addMapLayer(layer)

        print(
            f"✅ Loaded : {layer.name()} "
            f"| CRS : {layer.crs().authid()}"
        )

    else:

        print(f"❌ Failed : {layer.name()}")


# ============================================================
# 12. FINISHED
# ============================================================

print("\n🎉 All layers successfully reprojected to EPSG:32643")