# =========================================================
# WEIGHTED OVERLAY - LANDSLIDE SUSCEPTIBILITY INDEX
# =========================================================

import os

from qgis.core import (
    QgsRasterLayer,
    QgsProject
)

from qgis.analysis import (
    QgsRasterCalculator,
    QgsRasterCalculatorEntry
)

# ---------------------------------------------------
# INPUT FOLDER
# ---------------------------------------------------
base = r"/Users/madhubalapriya/Downloads/Kerala/processed/Model_Input/Reclassified"

# ---------------------------------------------------
# OUTPUT FOLDER
# ---------------------------------------------------
out_folder = r"/Users/madhubalapriya/Downloads/Kerala/processedd/Final_Output"
os.makedirs(out_folder, exist_ok=True)

# ---------------------------------------------------
# INPUT RECLASSIFIED RASTERS
# ---------------------------------------------------
rasters = {
    "Elevation": os.path.join(base, "elevation_Reclass.tif"),
    "Aspect": os.path.join(base, "Aspect_Reclass.tif"),
    "Slope": os.path.join(base, "slope_Reclass.tif"),
    "Distance_River": os.path.join(base, "Distance_River_Reclass.tif"),
    "Rainfall": os.path.join(base, "Rainfall_Reclass.tif"),
    "LULC": os.path.join(base, "LULC_Reclass.tif"),
    "NDVI": os.path.join(base, "NDVI_Reclass.tif"),
    "STI": os.path.join(base, "STI_Reclass.tif"),
    "Lithology": os.path.join(base, "Lithology_reclass.tif"),
    "TWI": os.path.join(base, "TWI_Reclass.tif")
}

# ---------------------------------------------------
# AHP WEIGHTS
# ---------------------------------------------------
weights = {
    "Slope": 0.218,
    "Rainfall": 0.203,
    "Lithology": 0.158,
    "TWI": 0.138,
    "LULC": 0.083,
    "Elevation": 0.053,
    "STI": 0.051,
    "Distance_River": 0.076,
    "NDVI": 0.070,
    "Aspect": 0.0116
}

# ---------------------------------------------------
# OUTPUT PATH
# ---------------------------------------------------
lsi_out = os.path.join(out_folder, "Landslide_Susceptibility_Index.tif")

# ---------------------------------------------------
# LOAD RASTERS
# ---------------------------------------------------
loaded_layers = {}
entries = []

print("\n==============================")
print("LOADING RECLASSIFIED RASTERS")
print("==============================")

for name, path in rasters.items():

    layer = QgsRasterLayer(path, name)

    if not layer.isValid():
        raise Exception(f"{name} raster is invalid or missing:\n{path}")

    loaded_layers[name] = layer

    QgsProject.instance().addMapLayer(layer)

    entry = QgsRasterCalculatorEntry()
    entry.ref = f"{name}@1"
    entry.raster = layer
    entry.bandNumber = 1

    entries.append(entry)

    print(f"{name} -> loaded successfully")

# ---------------------------------------------------
# USE REFERENCE RASTER
# ---------------------------------------------------
ref_layer = loaded_layers["Rainfall"]

# ---------------------------------------------------
# BUILD WEIGHTED OVERLAY EXPRESSION
# ---------------------------------------------------
expression = f"""
(
("Slope@1" * {weights['Slope']}) +
("Rainfall@1" * {weights['Rainfall']}) +
("Lithology@1" * {weights['Lithology']}) +
("TWI@1" * {weights['TWI']}) +
("LULC@1" * {weights['LULC']}) +
("Elevation@1" * {weights['Elevation']}) +
("STI@1" * {weights['STI']}) +
("Distance_River@1" * {weights['Distance_River']}) +
("NDVI@1" * {weights['NDVI']}) +
("Aspect@1" * {weights['Aspect']})
)
"""

print("\n==============================")
print("WEIGHTED OVERLAY EXPRESSION")
print("==============================")
print(expression)

# ---------------------------------------------------
# RUN RASTER CALCULATOR
# ---------------------------------------------------
calc = QgsRasterCalculator(
    expression,
    lsi_out,
    "GTiff",
    ref_layer.extent(),
    ref_layer.width(),
    ref_layer.height(),
    entries
)

result = calc.processCalculation()

# ---------------------------------------------------
# LOAD OUTPUT
# ---------------------------------------------------
if result == 0:

    print("\nLandslide Susceptibility Index created successfully:")
    print(lsi_out)

    out_layer = QgsRasterLayer(
        lsi_out,
        "Landslide_Susceptibility_Index"
    )

    if out_layer.isValid():

        QgsProject.instance().addMapLayer(out_layer)

        print("Output layer added to QGIS.")

    else:
        print("Output raster created but could not be loaded.")

else:
    print(f"\nWeighted overlay failed with code: {result}")