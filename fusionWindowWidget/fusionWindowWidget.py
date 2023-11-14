from qgis.core import QgsProject
from ui.fusionWindow import Ui_Fusion
import traceback
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsStyle, QgsSymbol, QgsWkbTypes, QgsSymbolLayer, \
    Qgis, QgsFeatureRenderer
from qgis.gui import QgsRendererRasterPropertiesWidget, QgsSingleSymbolRendererWidget, \
    QgsCategorizedSymbolRendererWidget
from PyQt5.QtCore import QModelIndex
from ui.layerPropWindow import Ui_LayerProp
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QTabBar, QMessageBox, QFileDialog
from qgisUtils import getRasterLayerAttrs, getVectorLayerAttrs, writeRasterLayer

PROJECT = QgsProject.instance()


class fusionWindowWidgeter(QWidget, Ui_Fusion):

    def __init__(self, parent=None):
        super(fusionWindowWidgeter, self).__init__(parent)
        self.parentWindow = parent
        self.setupUi(self)

        layers = PROJECT.mapLayers()
        # 使用列表表达式获得图层名称
        self.l = [layer.name() for layer in layers.values()]
        # 键值对存储图层名称和图层对象
        self.layers_list = {}
        for i in layers.values():
            self.layers_list[i.name()] = i

        self.L1 = QgsRasterLayer()  # 基时相高分辨率影像
        self.M1 = QgsRasterLayer()  # 基时相低分辨率影像
        self.M2 = QgsRasterLayer()  # 预测时相低分辨率影像
        self.seg = QgsRasterLayer()  # 分割影像
        self.out = QgsRasterLayer()  # 输出路径


        self.initUI()
        self.connectFunc()

    def initUI(self):
        self.comboBox.addItems(self.l)
        self.comboBox_2.addItems(self.l)
        self.comboBox_3.addItems(self.l)
        self.comboBox_4.addItems(self.l)
        self.comboBox_5.addItems(self.l)

    def connectFunc(self):
        self.comboBox.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self):
        print(self.comboBox.currentText())
        self.L1 = self.layers_list[self.comboBox.currentText()]
        data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        writeRasterLayer(data_file, self.L1)


    def actionwriteRasterLayerTriggered(self):
        data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        layers = self.layerTreeView.selectedLayers()
        if len(layers) == 1:
            layer = layers[0]
            print(layer.name())
            writeRasterLayer(data_file, layer)
'''def closeEvent(self, event):
        # 是否保存数据？？？？

        # 显示关闭确认对话框
        reply = QMessageBox.question(self, '退出', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 根据用户的选择确定是否关闭窗口
        if reply == QMessageBox.Yes:
            event.accept()  # 接受关闭事件
        else:
            event.ignore()  # 忽略关闭事件'''
