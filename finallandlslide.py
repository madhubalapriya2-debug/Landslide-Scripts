#landslide

import numpy as np
from osgeo import gdal

# ---------------------------------------------------
# INPUT / OUTPUT
# ---------------------------------------------------
fei_path = r"/Users/madhubalapriya/Downloads/Kerala/processed/Final_Output/Landslide_Susceptibility_Index.tif"
classified_out = r"/Users/madhubalapriya/Downloads/Kerala/processed/Final_Output/Landslide_Susceptibility_5Class_Quantile.tif"

# ---------------------------------------------------
# READ INPUT RASTER
# ---------------------------------------------------
ds = gdal.Open(fei_path)
if ds is None:
    raise Exception(f"Could not open raster: {fei_path}")

band = ds.GetRasterBand(1)
arr = band.ReadAsArray().astype("float64")

nodata = band.GetNoDataValue()
if nodata is not None:
    arr[arr == nodata] = np.nan

arr[~np.isfinite(arr)] = np.nan
valid = arr[~np.isnan(arr)]

if valid.size == 0:
    raise Exception("No valid raster values found.")

# ---------------------------------------------------
# CALCULATE QUANTILE BREAKS
# ---------------------------------------------------
q20 = float(np.percentile(valid, 20))
q40 = float(np.percentile(valid, 40))
q60 = float(np.percentile(valid, 60))
q80 = float(np.percentile(valid, 80))

print("Quantile breaks:")
print("Q20:", q20)
print("Q40:", q40)
print("Q60:", q60)
print("Q80:", q80)

# ---------------------------------------------------
# RECLASSIFY INTO 5 CLASSES
# ---------------------------------------------------
classified = np.full(arr.shape, -9999, dtype=np.int16)

mask = ~np.isnan(arr)

classified[(mask) & (arr <= q20)] = 1
classified[(mask) & (arr > q20) & (arr <= q40)] = 2
classified[(mask) & (arr > q40) & (arr <= q60)] = 3
classified[(mask) & (arr > q60) & (arr <= q80)] = 4
classified[(mask) & (arr > q80)] = 5

# ---------------------------------------------------
# SAVE OUTPUT
# ---------------------------------------------------
driver = gdal.GetDriverByName("GTiff")
out_ds = driver.Create(
    classified_out,
    ds.RasterXSize,
    ds.RasterYSize,
    1,
    gdal.GDT_Int16
)

out_ds.SetGeoTransform(ds.GetGeoTransform())
out_ds.SetProjection(ds.GetProjection())

out_band = out_ds.GetRasterBand(1)
out_band.WriteArray(classified)
out_band.SetNoDataValue(-9999)
out_band.FlushCache()

out_ds = None
ds = None

print(f"\nReclassified raster saved at:\n{classified_out}")
