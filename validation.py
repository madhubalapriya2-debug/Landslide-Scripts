from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject,
    QgsWkbTypes
)

# ============================================================
# 1. FILE PATHS
# ============================================================

# DEM
dem_path="/Users/madhubalapriya/Downloads/Kerala/dataset/dem.tif"
# Slope
slope_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/SLOPE/Slope2.tif"

# Aspect
aspect_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/ASPECT/ASPECT.tif"

# Rainfall
rainfall_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/rainfall/rainfall.tif"

# LULC
lulc_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/lulc/lulc.tif"

# Distance From River
dfr_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/dfr/distancetoriver.tif"

# STI
sti_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/STI/STI.tif"

# TWI
twi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/TWI/TWI.tif"

# NDVI
ndvi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/ndvi/ndvi.tif"


# Lithology
lithology_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/lithology/lithology.shp"



# AOI Shapefile
aoi_path = "/Users/madhubalapriya/Downloads/Kerala/dataset/Wayanadshapefile/wayanadshp.shp"

# ============================================================
# 2. LOAD RASTER LAYERS
# ============================================================


dem_layer= QgsRasterLayer(dem_path, "dem")

slope_layer = QgsRasterLayer(slope_path, "Slope")

aspect_layer = QgsRasterLayer(aspect_path, "Aspect")

rainfall_layer = QgsRasterLayer(rainfall_path, "Rainfall")

lulc_layer = QgsRasterLayer(lulc_path, "LULC")

dfr_layer = QgsRasterLayer(dfr_path, "DFR")

sti_layer = QgsRasterLayer(sti_path, "STI")

twi_layer = QgsRasterLayer(twi_path, "TWI")

ndvi_layer = QgsRasterLayer(ndvi_path, "NDVI")


# ============================================================
# 3. LOAD VECTOR LAYER
# ============================================================

aoi_layer = QgsVectorLayer(
    aoi_path,
    "AOI",
    "ogr"
)

lithology_layer = QgsVectorLayer(
    lithology_path,
    "Lithology",
    "ogr"
)
# ============================================================
# 4. STORE ALL LAYERS
# ============================================================
layers = {
    "dem":dem_layer,
    "Slope": slope_layer,
    "Aspect": aspect_layer,
    "Rainfall": rainfall_layer,
    "LULC": lulc_layer,
    "DFR": dfr_layer,
    "STI": sti_layer,
    "TWI": twi_layer,
    "NDVI": ndvi_layer,
    "Lithology": lithology_layer,
    "AOI": aoi_layer
}

# ============================================================
# 5. FUNCTION TO PRINT LAYER SUMMARY
# ============================================================

def print_layer_summary(name, layer):

    print("\n================================================")
    print(f"{name.upper()} SUMMARY")
    print("================================================")

    # Check validity
    if not layer.isValid():

        print("Status : ❌ INVALID LAYER")
        return

    print("Status : ✅ VALID")
    print("Layer Name :", layer.name())
    print("CRS :", layer.crs().authid())

    # --------------------------------------------------------
    # Raster Layer
    # --------------------------------------------------------
    if layer.type() == layer.RasterLayer:

        print("Layer Type : Raster")
        print("Width :", layer.width())
        print("Height :", layer.height())
        print("Band Count :", layer.bandCount())
        print("Extent :", layer.extent().toString())

    # --------------------------------------------------------
    # Vector Layer
    # --------------------------------------------------------
    elif layer.type() == layer.VectorLayer:

        print("Layer Type : Vector")
        print("Feature Count :", layer.featureCount())

        print(
            "Geometry Type :",
            QgsWkbTypes.displayString(layer.wkbType())
        )

        print("Extent :", layer.extent().toString())


# ============================================================
# 6. PRINT SUMMARIES
# ============================================================

for name, layer in layers.items():

    print_layer_summary(name, layer)


# ============================================================
# 7. AOI GEOMETRY VALIDATION
# ============================================================

if aoi_layer.isValid():

    invalid_count = 0

    for feature in aoi_layer.getFeatures():

        geom = feature.geometry()

        if geom is None:
            invalid_count += 1

        elif geom.isEmpty():
            invalid_count += 1

        elif not geom.isGeosValid():
            invalid_count += 1

    print("\n================================================")
    print("AOI GEOMETRY VALIDATION")
    print("================================================")
    print("Invalid Features :", invalid_count)

else:

    print("\n❌ AOI layer is invalid")


# ============================================================
# 8. ADD VALID LAYERS TO QGIS
# ============================================================

print("\n================================================")
print("ADDING LAYERS TO QGIS")
print("================================================")

for layer_name, layer in layers.items():

    if layer.isValid():

        QgsProject.instance().addMapLayer(layer)

        print(f"✅ Added : {layer_name}")

    else:

        print(f"❌ Failed : {layer_name}")


# ============================================================
# 9. FINISHED
# ============================================================

print("\n🎉 All valid layers successfully loaded into QGIS")