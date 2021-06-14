# -*- coding: utf-8 -*-

__author__ = 'Carlos Eduardo Mota'
__date__ = '2021-06-08'
__copyright__ = '(C) 2021 by Carlos Eduardo Mota'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from os.path import basename, splitext
from osgeo import gdal
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessingAlgorithm


class BaseAlgorithm(QgsProcessingAlgorithm):
    """
    """
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        raise NotImplementedError

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        raise NotImplementedError

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return self.__class__.__name__

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return splitext(basename(__file__))[0]

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()


class GDALDriverMixin:
    """
    """
    @staticmethod
    def get_gdal_driver_by_extension(extension):
        """
        :param extension:
        :return:
        """
        if extension.startswith("."):
            extension = extension[1:]

        drv = None

        for i in range(gdal.GetDriverCount()):
            drv = gdal.GetDriver(i)
            if drv.GetMetadataItem(gdal.DCAP_RASTER):
                ext = drv.GetMetadataItem(gdal.DMD_EXTENSIONS)
                if ext:
                    if extension in ext.split(" "):
                        break

        return drv
