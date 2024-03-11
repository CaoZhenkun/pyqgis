# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os

from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QComboBox, QAction, QToolBar
from qgis.core import QgsProject
from qgis.gui import QgisInterface
from .mapTool import SwipeMapTool

here = os.path.dirname(__file__)
project = QgsProject.instance()


class Swipe:

    #def __init__(self, iface):
    def __init__(self, mapCanvas,toolBar):
        #self.iface: QgisInterface = iface
        #self.mapCanvas = self.iface.mapCanvas()
        self.mapCanvas =mapCanvas

        self.preMapTool = None

        #self.toolBar: QToolBar = self.iface.addToolBar('Swipe Toolbar')
        self.toolBar: QToolBar = toolBar

        self.toolBar.setToolTip("Swipe Toolbar")
        self.swipeAction = QAction(QIcon(os.path.join(here, 'icon.png')), 'Swipe Tool', self.toolBar)
        self.swipeAction.setCheckable(True)
        self.swipeAction.triggered.connect(self.swipeActionTriggered)
        self.layerCombobox = QComboBox()
        self.layerCombobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        #self.layerCombobox.setFixedHeight(self.iface.iconSize().height())
        metrics = self.layerCombobox.fontMetrics()
        textHeight = metrics.height()
        padding = 6  # 根据需要调整上下填充
        self.layerCombobox.setFixedHeight(textHeight + padding)

        self.swipeTool = SwipeMapTool(self.layerCombobox, self.mapCanvas)

        # 图层变化信号
        project.layerTreeRoot().layerOrderChanged.connect(self.updateCombobox)
        project.layerTreeRoot().visibilityChanged.connect(self.updateCombobox)
        project.layerTreeRoot().nameChanged.connect(self.updateCombobox)
        # 地图工具变化
        self.mapCanvas.mapToolSet.connect(self.mapCanvasMapToolSet)
        # 初始化图层
        self.updateCombobox()

        self.initGui()

    def initGui(self):
        self.toolBar.addAction(self.swipeAction)
        self.toolBar.addWidget(self.layerCombobox)

    def unload(self):
        project.layerTreeRoot().layerOrderChanged.disconnect(self.updateCombobox)
        project.layerTreeRoot().visibilityChanged.disconnect(self.updateCombobox)
        project.layerTreeRoot().nameChanged.disconnect(self.updateCombobox)
        self.mapCanvas.mapToolSet.disconnect(self.mapCanvasMapToolSet)
        self.mapCanvas.unsetMapTool(self.swipeTool)

        del self.toolBar

    def swipeActionTriggered(self):
        if self.layerCombobox.count() < 2:
            self.swipeAction.setChecked(False)
            # 创建一个消息框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)  # 设置图标为提示
            msg_box.setText("至少需要两个图层")  # 设置消息文本
            msg_box.setWindowTitle("提示")  # 设置左上角标题为提示
            msg_box.exec_()  # 显示消息框
            return
        self.swipeAction.setChecked(True)
        if self.mapCanvas.mapTool() != self.swipeTool:
            self.mapCanvas.setMapTool(self.swipeTool)

    def updateCombobox(self):
        self.layerCombobox.clear()
        layers = project.layerTreeRoot().checkedLayers()
        for layer in layers:
            self.layerCombobox.addItem(layer.name(), layer.id())
        if self.layerCombobox.count() < 2:
            self.swipeAction.setChecked(False)
            self.mapCanvas.unsetMapTool(self.swipeTool)

    def mapCanvasMapToolSet(self, newTool, _):
        if newTool.__class__.__name__ != 'SwipeMapTool':
            self.swipeAction.setChecked(False)
            if self.preMapTool == "SwipeMapTool":
                self.mapCanvas.renderStarting.disconnect(self.renderStarting)
                self.mapCanvas.renderComplete.disconnect(self.renderComplete)
            self.preMapTool = None
        else:
            self.preMapTool = "SwipeMapTool"
            self.mapCanvas.renderStarting.connect(self.renderStarting)
            self.mapCanvas.renderComplete.connect(self.renderComplete)

    def renderStarting(self):
        self.mapCanvas.setCursor(Qt.BusyCursor)

    def renderComplete(self):
        cursor = self.mapCanvas.cursor()
        pos = cursor.pos()
        # 触发鼠标移动事件
        cursor.setPos(pos.x() + 1, pos.y() + 1)
