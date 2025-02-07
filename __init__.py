# -*- coding: utf-8 -*-
"""
Add legend labels to layer attributes: QGIS Plugin

https://github.com/eduard-kazakov/add_legend_labels_to_layer_attributes

Eduard Kazakov | ee.kazakov@gmail.com
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AddLegendLabels class from file AddLegendLabels.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .add_legend_labels_to_layer_attributes import AddLegendLabelsPlugin
    return AddLegendLabelsPlugin()
