# -*- coding: utf-8 -*-
"""
Add legend labels to layer attributes: QGIS Plugin

https://github.com/eduard-kazakov/add_legend_labels_to_layer_attributes

Eduard Kazakov | ee.kazakov@gmail.com
"""

import os
import sys
import inspect

from qgis.core import QgsApplication
from .add_legend_labels_to_layer_attributes_provider import AddLegendLabelsProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class AddLegendLabelsPlugin(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        self.provider = AddLegendLabelsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
