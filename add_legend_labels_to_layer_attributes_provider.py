# -*- coding: utf-8 -*-
"""
Add legend labels to layer attributes: QGIS Plugin

https://github.com/eduard-kazakov/add_legend_labels_to_layer_attributes

Eduard Kazakov | ee.kazakov@gmail.com
"""

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
from .add_legend_labels_to_layer_attributes_algorithm import AddLegendLabelsAlgorithm
import os

class AddLegendLabelsProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(AddLegendLabelsAlgorithm())

    def id(self):
        return 'add_legend_labels_to_layer_attributes_provider'

    def name(self):
        return 'Add legend labels to layer attributes'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.png'))

    def longName(self):
        return 'Add legend labels to layer attributes'
