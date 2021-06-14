# -*- coding: utf-8 -*-

__author__ = 'Carlos Eduardo Mota'
__date__ = '2021-06-08'
__copyright__ = '(C) 2021 by Carlos Eduardo Mota'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import numpy as np

from osgeo import gdal
from os.path import splitext
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer)

from .base import BaseAlgorithm, GDALDriverMixin


class ExampleAlgorithm(BaseAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT,
            context, source.fields(),
            source.wkbType(), source.sourceCrs()
        )

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}


class DiscretizeRasterAlgorithm(GDALDriverMixin, BaseAlgorithm):
    """
    """
    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster layer'),
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Output Raster layer'),
                # createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        gdal.UseExceptions()

        in_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        out_raster_file, ext = splitext(self.parameterAsOutputLayer(parameters, self.OUTPUT, context))
        out_raster = out_raster_file + ext

        # Read Datasets
        in_dataset = gdal.Open(in_raster.source())

        # Make Empty Raster
        driver = self.get_gdal_driver_by_extension(ext)
        out_dataset = driver.Create(
            out_raster,
            in_dataset.RasterXSize,
            in_dataset.RasterYSize,
            1,
            gdal.GDT_Byte
        )
        out_dataset.SetSpatialRef(in_dataset.GetSpatialRef())
        out_dataset.SetGeoTransform(in_dataset.GetGeoTransform())

        # Counting
        band_array = in_dataset.GetRasterBand(1).ReadAsArray()
        percentiles = np.quantile(
            band_array.reshape(band_array.size),
            [0, .25, .50, .75]
        )

        out_dataset.GetRasterBand(1).WriteArray(
            np.digitize(band_array, percentiles)
        )

        out_dataset.FlushCache()

        del in_dataset, out_dataset

        return {self.OUTPUT: out_raster}
