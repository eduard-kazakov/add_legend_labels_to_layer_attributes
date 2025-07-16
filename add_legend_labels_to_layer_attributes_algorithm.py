# -*- coding: utf-8 -*-
"""
Add legend labels to layer attributes: QGIS Plugin

https://github.com/eduard-kazakov/add_legend_labels_to_layer_attributes

Eduard Kazakov | ee.kazakov@gmail.com
"""

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
    QgsFeatureSink,
    QgsFeature,
    QgsField,
    QgsCategorizedSymbolRenderer,
    QgsRuleBasedRenderer,
    QgsPointClusterRenderer,
    QgsGraduatedSymbolRenderer,
    QgsProcessingException,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextScope
)
from qgis.PyQt.QtCore import QVariant

def get_legend_labels(layer):
    """Extract legend labels from categorized, rule-based, and graduated renderers"""
    renderer = layer.renderer()
    labels = {}
    if isinstance(renderer, QgsCategorizedSymbolRenderer):
        for category in renderer.categories():
            labels[category.value()] = category.label()
    elif isinstance(renderer, QgsRuleBasedRenderer):
        for rule in renderer.rootRule().children():
            labels[rule.filterExpression()] = rule.label()
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        for range in renderer.ranges():
            labels[f"{range.lowerValue()}_{range.upperValue()}"] = range.label()
    return labels
    
def get_rule_based_label(feature, renderer):
    """Find the first matching rule-based label for a given feature."""
    context = QgsExpressionContext()
    scope = QgsExpressionContextScope()
    scope.setFeature(feature)
    context.appendScope(scope)
    
    for rule in renderer.rootRule().children():
        if rule.filterExpression():
            expression = QgsExpression(rule.filterExpression())
            if expression.evaluate(context):
                return rule.label()
    return ""

def get_graduated_label(feature, renderer):
    """Find the matching graduated label for a given feature."""
    class_field = renderer.classAttribute()
    if class_field not in feature.fields().names():
        return ""
    
    value = feature[class_field]
    for range in renderer.ranges():
        if range.lowerValue() <= value <= range.upperValue():
            return range.label()
    return ""

class AddLegendLabelsAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    LABEL_FIELD = 'LABEL_FIELD'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            "Input Layer",
            [QgsProcessing.TypeVectorAnyGeometry]
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Output Layer"
        ))
        self.addParameter(QgsProcessingParameterString(
            self.LABEL_FIELD,
            "Legend Label Field Name",
            defaultValue="Legend_Label"
        ))

    def processAlgorithm(self, parameters, context, feedback):
        source_layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        if not source_layer:
            raise QgsProcessingException("Invalid input layer")

        legend_labels = get_legend_labels(source_layer)
        
        label_field_name = self.parameterAsString(parameters, self.LABEL_FIELD, context)

        new_fields = source_layer.fields()
        new_fields.append(QgsField(label_field_name, QVariant.String))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            new_fields, source_layer.wkbType(), source_layer.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException("Failed to create output layer")
            
        renderer = source_layer.renderer()
        class_field = None

        if isinstance(renderer, QgsPointClusterRenderer):
            renderer = renderer.embeddedRenderer()

        if isinstance(renderer, QgsCategorizedSymbolRenderer) or isinstance(renderer, QgsGraduatedSymbolRenderer):
            class_field = renderer.classAttribute()

        for feature in source_layer.getFeatures():
            new_feature = QgsFeature()
            new_feature.setFields(new_fields)
            new_feature.setGeometry(feature.geometry())

            label = ""
            if isinstance(renderer, QgsCategorizedSymbolRenderer) and class_field in feature.fields().names():
                value = feature[class_field]
                label = legend_labels.get(value, "")
            elif isinstance(renderer, QgsRuleBasedRenderer):
                label = get_rule_based_label(feature, renderer)
            elif isinstance(renderer, QgsGraduatedSymbolRenderer) and class_field in feature.fields().names():
                label = get_graduated_label(feature, renderer)
            
            new_feature.setAttribute(label_field_name, label)
            
            for field in feature.fields():
                new_feature.setAttribute(field.name(), feature[field.name()])
            
            sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}

    def name(self):
        return "add_legend_labels"

    def displayName(self):
        return "Add legend labels to layer attributes"
        
    def shortHelpString(self):
        help_string = (
            'Add legend labels to layer attributes\n\n'
            'This tool extracts legend labels from the current layer style and assigns them as attribute values to the corresponding features. It supports categorized, graduated, and rule-based renderers.\n'
            'These renderers are also supported if they are embedded renderes for point cluster renderer.\n'
            'For categorized and graduated renderers, the tool supports styles based on single field values.\n'
            'For rule-based renderers, there are no limitations—complex expressions and conditions are fully supported.\n'
            'If your categorized or graduated renderer uses advanced expressions, you can convert it to a rule-based renderer automatically to ensure compatibility with this tool.\n'
        )
        return help_string

    def createInstance(self):
        return AddLegendLabelsAlgorithm()
