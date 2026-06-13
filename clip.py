import os
import processing

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject
)

# ============================================================
# 1. INPUT FILE PATHS
# ============================================================

base = r"/Users/madhubalapriya/Downloads/Kerala/Reprojected"

# ============================================================
# INPUT REPROJECTED FILES
# ============================================================

# Raster Inputs
dem_path = os.path.join(base, "dem_32643.tif")

slope_path = os.path.join(base, "Slope_32643.tif")

aspect_path = os.path.join(base, "Aspect_32643.tif")

rainfall_path = os.path.join(base, "Rainfall_32643.tif")

lulc_path = os.path.join(base, "LULC_32643.tif")

dfr_path = os.path.join(base, "DFR_32643.tif")

sti_path = os.path.join(base, "STI_32643.tif")

twi_path = os.path.join(base, "TWI_32643.tif")

ndvi_path = os.path.join(base, "NDVI_32643.tif")

# Vector Inputs
aoi_path = os.path.join(base, "AOI_32643.shp")

lithology_path = os.path.join(base, "Lithology_32643.shp")


# ============================================================
# 2. OUTPUT FOLDER
# ============================================================

clip_folder = r"/Users/madhubalapriya/Downloads/Kerala/Clipped"

os.makedirs(clip_folder, exist_ok=True)

print("✅ Output folder created")


# ============================================================
# 3. OUTPUT FILE PATHS
# ============================================================

# Raster Outputs
dem_clip = os.path.join(clip_folder, "dem_clip.tif")

slope_clip = os.path.join(clip_folder, "Slope_clip.tif")

aspect_clip = os.path.join(clip_folder, "Aspect_clip.tif")

rainfall_clip = os.path.join(clip_folder, "Rainfall_clip.tif")

lulc_clip = os.path.join(clip_folder, "LULC_clip.tif")

dfr_clip = os.path.join(clip_folder, "DFR_clip.tif")

sti_clip = os.path.join(clip_folder, "STI_clip.tif")

twi_clip = os.path.join(clip_folder, "TWI_clip.tif")

ndvi_clip = os.path.join(clip_folder, "NDVI_clip.tif")

# Vector Output
lithology_clip = os.path.join(
    clip_folder,
    "Lithology_clip.shp"
)


# ============================================================
# 4. FUNCTION TO CLIP RASTER
# ============================================================

def clip_raster(input_raster, output_raster):

    processing.run(
        "gdal:cliprasterbymasklayer",
        {
            'INPUT': input_raster,
            'MASK': aoi_path,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'NODATA': 255,
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': True,
            'SET_RESOLUTION': False,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'MULTITHREADING': False,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'EXTRA': '',
            'OUTPUT': output_raster
        }
    )

    print(f"✅ Clipped Raster : {output_raster}")


# ============================================================
# 5. FUNCTION TO CLIP VECTOR
# ============================================================

def clip_vector(input_vector, output_vector):

    processing.run(
        "native:clip",
        {
            'INPUT': input_vector,
            'OVERLAY': aoi_path,
            'OUTPUT': output_vector
        }
    )

    print(f"✅ Clipped Vector : {output_vector}")


# ============================================================
# 6. CLIP RASTER LAYERS
# ============================================================

print("\n========================================")
print("CLIPPING RASTER LAYERS")
print("========================================")

clip_raster(dem_path, dem_clip)

clip_raster(slope_path, slope_clip)

clip_raster(aspect_path, aspect_clip)

clip_raster(rainfall_path, rainfall_clip)

clip_raster(lulc_path, lulc_clip)

clip_raster(dfr_path, dfr_clip)

clip_raster(sti_path, sti_clip)

clip_raster(twi_path, twi_clip)

clip_raster(ndvi_path, ndvi_clip)


# ============================================================
# 7. CLIP VECTOR LAYER
# ============================================================

print("\n========================================")
print("CLIPPING VECTOR LAYER")
print("========================================")

clip_vector(lithology_path, lithology_clip)


# ============================================================
# 8. LOAD CLIPPED LAYERS
# ============================================================

print("\n========================================")
print("LOADING CLIPPED LAYERS")
print("========================================")

# Raster Layers
dem_layer = QgsRasterLayer(
    dem_clip,
    "dem_clip"
)

slope_layer = QgsRasterLayer(
    slope_clip,
    "Slope_clip"
)

aspect_layer = QgsRasterLayer(
    aspect_clip,
    "Aspect_clip"
)

rainfall_layer = QgsRasterLayer(
    rainfall_clip,
    "Rainfall_clip"
)

lulc_layer = QgsRasterLayer(
    lulc_clip,
    "LULC_clip"
)

dfr_layer = QgsRasterLayer(
    dfr_clip,
    "DFR_clip"
)

sti_layer = QgsRasterLayer(
    sti_clip,
    "STI_clip"
)

twi_layer = QgsRasterLayer(
    twi_clip,
    "TWI_clip"
)

ndvi_layer = QgsRasterLayer(
    ndvi_clip,
    "NDVI_clip"
)

# Vector Layer
lithology_layer = QgsVectorLayer(
    lithology_clip,
    "Lithology_clip",
    "ogr"
)


# ============================================================
# 9. STORE CLIPPED LAYERS
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
    lithology_layer
]


# ============================================================
# 10. ADD CLIPPED LAYERS TO QGIS
# ============================================================

print("\n========================================")
print("ADDING CLIPPED LAYERS TO QGIS")
print("========================================")

for layer in layers:

    if layer.isValid():

        QgsProject.instance().addMapLayer(layer)

        print(f"✅ Loaded : {layer.name()}")

    else:

        print(f"❌ Invalid : {layer.name()}")


# ============================================================
# 11. FINISHED
# ============================================================

print("\n🎉 All layers successfully clipped to AOI")