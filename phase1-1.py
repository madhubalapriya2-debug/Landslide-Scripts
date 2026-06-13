#PHASE1

# -----------------------------------
# STANDARD LIBRARIES
# -----------------------------------
import os
import shutil
import processing
import numpy as np

# -----------------------------------
# QGIS CORE
# -----------------------------------
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterNumber,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsProcessingException
)

# -----------------------------------
# QT
# -----------------------------------
from qgis.PyQt.QtCore import QCoreApplication

# -----------------------------------
# GDAL + EXCEL
# -----------------------------------
from osgeo import gdal
from openpyxl import Workbook
from openpyxl.styles import Font


# =========================================================
# COMMON HELPERS
# =========================================================

def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path


def log_layer_summary(name, layer, feedback):

    feedback.pushInfo("")
    feedback.pushInfo("=" * 40)
    feedback.pushInfo(f"{name.upper()} SUMMARY")
    feedback.pushInfo("=" * 40)

    if not layer or not layer.isValid():
        feedback.pushInfo("Status: INVALID")
        return

    feedback.pushInfo("Status: VALID")
    feedback.pushInfo(f"CRS: {layer.crs().authid()}")

    if isinstance(layer, QgsRasterLayer):

        feedback.pushInfo("Type: Raster")
        feedback.pushInfo(f"Width: {layer.width()}")
        feedback.pushInfo(f"Height: {layer.height()}")
        feedback.pushInfo(f"Bands: {layer.bandCount()}")
        feedback.pushInfo(f"Extent: {layer.extent().toString()}")

    elif isinstance(layer, QgsVectorLayer):

        feedback.pushInfo("Type: Vector")
        feedback.pushInfo(f"Feature Count: {layer.featureCount()}")
        feedback.pushInfo(
            f"Geometry Type: {QgsWkbTypes.displayString(layer.wkbType())}"
        )
        feedback.pushInfo(f"Extent: {layer.extent().toString()}")


# =========================================================
# VALIDATION
# =========================================================

def validate_raster_layer(layer, name):

    if not layer or not layer.isValid():
        raise QgsProcessingException(
            f"{name} layer is invalid or could not be loaded."
        )

    if layer.bandCount() < 1:
        raise QgsProcessingException(f"{name} raster has no bands.")

    return layer


def validate_vector_layer(layer, name, expected_geom_types=None):

    if not layer or not layer.isValid():
        raise QgsProcessingException(
            f"{name} layer is invalid or could not be loaded."
        )

    if layer.featureCount() == 0:
        raise QgsProcessingException(f"{name} layer has no features.")

    geom_type = layer.geometryType()

    if expected_geom_types is not None and geom_type not in expected_geom_types:

        raise QgsProcessingException(
            f"{name} has invalid geometry type. "
            f"Found: {QgsWkbTypes.displayString(layer.wkbType())}"
        )

    return layer


def check_geometry_validity(layer, layer_name, feedback):

    invalid_count = 0
    empty_count = 0

    for feat in layer.getFeatures():

        geom = feat.geometry()

        if geom is None or geom.isEmpty():
            empty_count += 1
            invalid_count += 1
            continue

        if not geom.isGeosValid():
            invalid_count += 1

    feedback.pushInfo("")
    feedback.pushInfo("=" * 40)
    feedback.pushInfo(f"{layer_name.upper()} GEOMETRY CHECK")
    feedback.pushInfo("=" * 40)
    feedback.pushInfo(f"Empty features: {empty_count}")
    feedback.pushInfo(f"Invalid features: {invalid_count}")

    if invalid_count > 0:

        raise QgsProcessingException(
            f"{layer_name} contains "
            f"{invalid_count} invalid/empty geometries."
        )


def validate_inputs(
    dem_layer,
    aoi_layer,
    rainfall_layer,
    lulc_layer,
    aspect_layer,
    slope_layer,
    lithology_layer,
    ndvi_layer,
    twi_layer,
    sti_layer,
    distancefromriver_layer,
    feedback
):

    dem_layer = validate_raster_layer(dem_layer, "DEM")
    slope_layer = validate_raster_layer(slope_layer, "Slope")
    aspect_layer = validate_raster_layer(aspect_layer, "Aspect")
    rainfall_layer = validate_raster_layer(rainfall_layer, "Rainfall")
    lulc_layer = validate_raster_layer(lulc_layer, "LULC")
    twi_layer = validate_raster_layer(twi_layer, "TWI")
    ndvi_layer = validate_raster_layer(ndvi_layer, "NDVI")
    sti_layer = validate_raster_layer(sti_layer, "STI")

    distancefromriver_layer = validate_raster_layer(
        distancefromriver_layer,
        "Distancefromriver"
    )

    aoi_layer = validate_vector_layer(
        aoi_layer,
        "AOI",
        expected_geom_types=[QgsWkbTypes.PolygonGeometry]
    )

    lithology_layer = validate_vector_layer(
        lithology_layer,
        "Lithology",
        expected_geom_types=[QgsWkbTypes.PolygonGeometry]
    )

    check_geometry_validity(aoi_layer, "AOI", feedback)
    check_geometry_validity(lithology_layer, "Lithology", feedback)

    log_layer_summary("DEM", dem_layer, feedback)
    log_layer_summary("Aspect", aspect_layer, feedback)
    log_layer_summary("Slope", slope_layer, feedback)
    log_layer_summary("AOI", aoi_layer, feedback)
    log_layer_summary("Rainfall", rainfall_layer, feedback)
    log_layer_summary("LULC", lulc_layer, feedback)
    log_layer_summary("NDVI", ndvi_layer, feedback)
    log_layer_summary("STI", sti_layer, feedback)
    log_layer_summary("TWI", twi_layer, feedback)
    log_layer_summary("Lithology", lithology_layer, feedback)
    log_layer_summary(
        "Distancefromriver",
        distancefromriver_layer,
        feedback
    )

    feedback.pushInfo("")
    feedback.pushInfo("All input layers passed validation.")

    return {
        "DEM": dem_layer,
        "Slope": slope_layer,
        "Aspect": aspect_layer,
        "AOI": aoi_layer,
        "Rainfall": rainfall_layer,
        "LULC": lulc_layer,
        "Distancefromriver": distancefromriver_layer,
        "NDVI": ndvi_layer,
        "TWI": twi_layer,
        "STI": sti_layer,
        "Lithology": lithology_layer
    }


# =========================================================
# REPROJECTION
# =========================================================

def reproject_vector_layer(
    input_layer,
    target_crs,
    output_path,
    layer_name,
    feedback
):

    feedback.pushInfo(f"Reprojecting vector layer: {layer_name}")

    result = processing.run(
        "native:reprojectlayer",
        {
            'INPUT': input_layer,
            'TARGET_CRS': target_crs,
            'OUTPUT': output_path
        }
    )

    output = result['OUTPUT']

    if not os.path.exists(output):
        raise QgsProcessingException(
            f"Failed to reproject vector layer: {layer_name}"
        )

    feedback.pushInfo(f"{layer_name} reprojected: {output}")

    return output


def reproject_raster_layer(
    input_layer,
    target_crs,
    output_path,
    layer_name,
    resampling_method,
    feedback
):

    feedback.pushInfo(f"Reprojecting raster layer: {layer_name}")

    result = processing.run(
        "gdal:warpreproject",
        {
            'INPUT': input_layer,
            'SOURCE_CRS': None,
            'TARGET_CRS': target_crs,
            'RESAMPLING': resampling_method,
            'NODATA': None,
            'TARGET_RESOLUTION': None,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'MULTITHREADING': False,
            'EXTRA': '',
            'OUTPUT': output_path
        }
    )

    output = result['OUTPUT']

    if not os.path.exists(output):
        raise QgsProcessingException(
            f"Failed to reproject raster layer: {layer_name}"
        )

    feedback.pushInfo(f"{layer_name} reprojected: {output}")

    return output


def reproject_inputs(validated_layers, target_crs, workspace, feedback):

    reprojected_folder = ensure_folder(
        os.path.join(workspace, "02_reprojected")
    )

    feedback.pushInfo("")
    feedback.pushInfo("=" * 40)
    feedback.pushInfo("STEP: REPROJECTION")
    feedback.pushInfo("=" * 40)

    crs_code = target_crs.authid().replace("EPSG:", "")

    aoi_reproj = os.path.join(
        reprojected_folder,
        f"AOI_{crs_code}.gpkg"
    )

    lithology_reproj = os.path.join(
        reprojected_folder,
        f"Lithology_{crs_code}.gpkg"
    )

    dem_reproj = os.path.join(
        reprojected_folder,
        f"DEM_{crs_code}.tif"
    )

    aspect_reproj = os.path.join(
        reprojected_folder,
        f"Aspect_{crs_code}.tif"
    )

    slope_reproj = os.path.join(
        reprojected_folder,
        f"Slope_{crs_code}.tif"
    )

    rainfall_reproj = os.path.join(
        reprojected_folder,
        f"Rainfall_{crs_code}.tif"
    )

    lulc_reproj = os.path.join(
        reprojected_folder,
        f"LULC_{crs_code}.tif"
    )

    ndvi_reproj = os.path.join(
        reprojected_folder,
        f"NDVI_{crs_code}.tif"
    )

    twi_reproj = os.path.join(
        reprojected_folder,
        f"TWI_{crs_code}.tif"
    )

    sti_reproj = os.path.join(
        reprojected_folder,
        f"STI_{crs_code}.tif"
    )

    distancefromriver_reproj = os.path.join(
        reprojected_folder,
        f"Distancefromriver_{crs_code}.tif"
    )

    aoi_out = reproject_vector_layer(
        validated_layers["AOI"],
        target_crs,
        aoi_reproj,
        "AOI",
        feedback
    )

    lithology_out = reproject_vector_layer(
        validated_layers["Lithology"],
        target_crs,
        lithology_reproj,
        "Lithology",
        feedback
    )

    distancefromriver_out = reproject_raster_layer(
        validated_layers["Distancefromriver"],
        target_crs,
        distancefromriver_reproj,
        "Distancefromriver",
        0,
        feedback
    )

    lulc_out = reproject_raster_layer(
        validated_layers["LULC"],
        target_crs,
        lulc_reproj,
        "LULC",
        0,
        feedback
    )

    ndvi_out = reproject_raster_layer(
        validated_layers["NDVI"],
        target_crs,
        ndvi_reproj,
        "NDVI",
        0,
        feedback
    )

    sti_out = reproject_raster_layer(
        validated_layers["STI"],
        target_crs,
        sti_reproj,
        "STI",
        0,
        feedback
    )

    twi_out = reproject_raster_layer(
        validated_layers["TWI"],
        target_crs,
        twi_reproj,
        "TWI",
        0,
        feedback
    )

    dem_out = reproject_raster_layer(
        validated_layers["DEM"],
        target_crs,
        dem_reproj,
        "DEM",
        0,
        feedback
    )

    aspect_out = reproject_raster_layer(
        validated_layers["Aspect"],
        target_crs,
        aspect_reproj,
        "Aspect",
        0,
        feedback
    )

    slope_out = reproject_raster_layer(
        validated_layers["Slope"],
        target_crs,
        slope_reproj,
        "Slope",
        0,
        feedback
    )

    rainfall_out = reproject_raster_layer(
        validated_layers["Rainfall"],
        target_crs,
        rainfall_reproj,
        "Rainfall",
        1,
        feedback
    )

    feedback.pushInfo("")
    feedback.pushInfo("All layers reprojected successfully.")

    return {
        "AOI": aoi_out,
        "Lithology": lithology_out,
        "Distancefromriver": distancefromriver_out,
        "LULC": lulc_out,
        "NDVI": ndvi_out,
        "STI": sti_out,
        "TWI": twi_out,
        "DEM": dem_out,
        "Aspect": aspect_out,
        "Slope": slope_out,
        "Rainfall": rainfall_out
    }


# =========================================================
# CLIP TO AOI
# =========================================================

def clip_raster_by_aoi(
    input_raster,
    aoi_layer,
    output_path,
    layer_name,
    feedback
):

    feedback.pushInfo(f"Clipping raster: {layer_name}")

    result = processing.run(
        "gdal:cliprasterbymasklayer",
        {
            'INPUT': input_raster,
            'MASK': aoi_layer,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'NODATA': None,
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
            'OUTPUT': output_path
        }
    )

    output = result['OUTPUT']

    if not os.path.exists(output):
        raise QgsProcessingException(
            f"Failed to clip raster: {layer_name}"
        )

    feedback.pushInfo(f"{layer_name} clipped: {output}")

    return output


def clip_vector_by_aoi(
    input_vector,
    aoi_layer,
    output_path,
    layer_name,
    feedback
):

    feedback.pushInfo(f"Clipping vector: {layer_name}")

    result = processing.run(
        "native:clip",
        {
            'INPUT': input_vector,
            'OVERLAY': aoi_layer,
            'OUTPUT': output_path
        }
    )

    output = result['OUTPUT']

    if not os.path.exists(output):
        raise QgsProcessingException(
            f"Failed to clip vector: {layer_name}"
        )

    feedback.pushInfo(f"{layer_name} clipped: {output}")

    return output


def clip_inputs_to_aoi(reprojected_layers, workspace, feedback):

    clipped_folder = ensure_folder(
        os.path.join(workspace, "03_clipped")
    )

    feedback.pushInfo("")
    feedback.pushInfo("=" * 40)
    feedback.pushInfo("STEP: CLIP TO AOI")
    feedback.pushInfo("=" * 40)

    aoi_path = reprojected_layers["AOI"]

    lithology_clip = os.path.join(
        clipped_folder,
        "Lithology_clip.gpkg"
    )

    distancefromriver_clip = os.path.join(
        clipped_folder,
        "Distancefromriver_clip.tif"
    )

    lulc_clip = os.path.join(
        clipped_folder,
        "LULC_clip.tif"
    )

    ndvi_clip = os.path.join(
        clipped_folder,
        "NDVI_clip.tif"
    )

    sti_clip = os.path.join(
        clipped_folder,
        "STI_clip.tif"
    )

    twi_clip = os.path.join(
        clipped_folder,
        "TWI_clip.tif"
    )

    dem_clip = os.path.join(
        clipped_folder,
        "DEM_clip.tif"
    )

    aspect_clip = os.path.join(
        clipped_folder,
        "Aspect_clip.tif"
    )

    slope_clip = os.path.join(
        clipped_folder,
        "Slope_clip.tif"
    )

    rainfall_clip = os.path.join(
        clipped_folder,
        "Rainfall_clip.tif"
    )

    lithology_out = clip_vector_by_aoi(
        reprojected_layers["Lithology"],
        aoi_path,
        lithology_clip,
        "Lithology",
        feedback
    )

    distancefromriver_out = clip_raster_by_aoi(
        reprojected_layers["Distancefromriver"],
        aoi_path,
        distancefromriver_clip,
        "Distancefromriver",
        feedback
    )

    lulc_out = clip_raster_by_aoi(
        reprojected_layers["LULC"],
        aoi_path,
        lulc_clip,
        "LULC",
        feedback
    )

    ndvi_out = clip_raster_by_aoi(
        reprojected_layers["NDVI"],
        aoi_path,
        ndvi_clip,
        "NDVI",
        feedback
    )

    sti_out = clip_raster_by_aoi(
        reprojected_layers["STI"],
        aoi_path,
        sti_clip,
        "STI",
        feedback
    )

    twi_out = clip_raster_by_aoi(
        reprojected_layers["TWI"],
        aoi_path,
        twi_clip,
        "TWI",
        feedback
    )

    dem_out = clip_raster_by_aoi(
        reprojected_layers["DEM"],
        aoi_path,
        dem_clip,
        "DEM",
        feedback
    )

    aspect_out = clip_raster_by_aoi(
        reprojected_layers["Aspect"],
        aoi_path,
        aspect_clip,
        "Aspect",
        feedback
    )

    slope_out = clip_raster_by_aoi(
        reprojected_layers["Slope"],
        aoi_path,
        slope_clip,
        "Slope",
        feedback
    )

    rainfall_out = clip_raster_by_aoi(
        reprojected_layers["Rainfall"],
        aoi_path,
        rainfall_clip,
        "Rainfall",
        feedback
    )

    feedback.pushInfo("")
    feedback.pushInfo("All layers clipped to AOI successfully.")

    return {
        "AOI": aoi_path,
        "Lithology": lithology_out,
        "DEM": dem_out,
        "Slope": slope_out,
        "Aspect": aspect_out,
        "Rainfall": rainfall_out,
        "LULC": lulc_out,
        "NDVI": ndvi_out,
        "TWI": twi_out,
        "STI": sti_out,
        "Distancefromriver": distancefromriver_out
    }


# =========================================================
# TOOL CLASS
# =========================================================

class LandslidePhase1Tool(QgsProcessingAlgorithm):

    DEM = "DEM"
    ASPECT = "ASPECT"
    SLOPE = "SLOPE"
    AOI = "AOI"
    RAINFALL = "RAINFALL"
    LULC = "LULC"
    NDVI = "NDVI"
    STI = "STI"
    TWI = "TWI"
    LITHOLOGY = "LITHOLOGY"
    DISTANCEFROMRIVER = "DISTANCEFROMRIVER"
    OUTPUT = "OUTPUT"
    MEMORY = "MEMORY"

    # --------------------------------------------------
    # TOOL INFO
    # --------------------------------------------------

    def name(self):
        return "flood_phase1"

    def displayName(self):
        return "Landslide Estimation - Phase 1"

    def group(self):
        return "Landslide Tools"

    def groupId(self):
        return "landslide_tools"

    def shortHelpString(self):
        return (
            "Runs Phase 1 preprocessing workflow "
            "for landslide susceptibility."
        )

    # --------------------------------------------------
    # PARAMETERS
    # --------------------------------------------------

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                "DEM Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.AOI,
                "AOI Boundary",
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RAINFALL,
                "Rainfall Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.LULC,
                "LULC Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LITHOLOGY,
                "Lithology Shapefile",
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DISTANCEFROMRIVER,
                "Distance From River Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.NDVI,
                "NDVI Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.STI,
                "STI Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.TWI,
                "TWI Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.ASPECT,
                "Aspect Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.SLOPE,
                "Slope Raster"
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                "Output Workspace Folder"
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MEMORY,
                "GRASS Memory (MB)",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=300
            )
        )

    # --------------------------------------------------
     # --------------------------------------------------
    # MAIN EXECUTION
    # --------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):

        # ------------------------------------------
        # GET INPUTS
        # ------------------------------------------

        aoi_layer = self.parameterAsVectorLayer(
            parameters,
            self.AOI,
            context
        )

        lithology_layer = self.parameterAsVectorLayer(
            parameters,
            self.LITHOLOGY,
            context
        )

        distancefromriver_layer = self.parameterAsRasterLayer(
            parameters,
            self.DISTANCEFROMRIVER,
            context
        )

        lulc_layer = self.parameterAsRasterLayer(
            parameters,
            self.LULC,
            context
        )

        ndvi_layer = self.parameterAsRasterLayer(
            parameters,
            self.NDVI,
            context
        )

        sti_layer = self.parameterAsRasterLayer(
            parameters,
            self.STI,
            context
        )

        twi_layer = self.parameterAsRasterLayer(
            parameters,
            self.TWI,
            context
        )

        dem_layer = self.parameterAsRasterLayer(
            parameters,
            self.DEM,
            context
        )

        aspect_layer = self.parameterAsRasterLayer(
            parameters,
            self.ASPECT,
            context
        )

        slope_layer = self.parameterAsRasterLayer(
            parameters,
            self.SLOPE,
            context
        )

        rainfall_layer = self.parameterAsRasterLayer(
            parameters,
            self.RAINFALL,
            context
        )

        workspace = self.parameterAsString(
            parameters,
            self.OUTPUT,
            context
        )

        memory = self.parameterAsInt(
            parameters,
            self.MEMORY,
            context
        )

        target_crs = QgsCoordinateReferenceSystem("EPSG:32643")

        # ------------------------------------------
        # CREATE WORKSPACE
        # ------------------------------------------

        if not os.path.exists(workspace):
            os.makedirs(workspace)

        feedback.pushInfo("Starting Phase 1 Processing...")

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        validated = validate_inputs(
            dem_layer,
            aoi_layer,
            rainfall_layer,
            lulc_layer,
            aspect_layer,
            slope_layer,
            lithology_layer,
            ndvi_layer,
            twi_layer,
            sti_layer,
            distancefromriver_layer,
            feedback
        )

        # ------------------------------------------
        # REPROJECTION
        # ------------------------------------------

        reproj = reproject_inputs(
            validated,
            target_crs,
            workspace,
            feedback
        )

        # ------------------------------------------
        # CLIP TO AOI
        # ------------------------------------------

        clipped = clip_inputs_to_aoi(
            reproj,
            workspace,
            feedback
        )

        # ------------------------------------------
        # MODEL INPUT PREPARATION
        # ------------------------------------------

        model_inputs = prepare_model_input_rasters(
            clipped,
            workspace,
            feedback
        )

        # ------------------------------------------
        # EXCEL SUMMARY
        # ------------------------------------------

        summary = generate_reclass_summary_excel(
            model_inputs,
            workspace,
            feedback
        )

        feedback.pushInfo("Phase 1 Completed Successfully!")

        return {
            "Excel_Output": summary["ReclassExcel"]
        }

    def createInstance(self):
        return LandslidePhase1Tool()