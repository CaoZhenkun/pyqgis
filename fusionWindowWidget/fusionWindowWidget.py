from qgis.core import QgsProject

from OLSTARFM import FusionMethod
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
        self.seg_path = None
        self.L1_path = None
        self.M1_path = None
        self.M2_path = None
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

    def connectFunc(self):
        self.comboBox.currentIndexChanged.connect(self.selectionchange1)
        self.comboBox_2.currentIndexChanged.connect(self.selectionchange2)
        self.comboBox_3.currentIndexChanged.connect(self.selectionchange3)
        self.comboBox_4.currentIndexChanged.connect(self.selectionchange4)
        self.pushButton.clicked.connect(self.pushButtonClicked)

    def selectionchange1(self):
        print(self.comboBox.currentText())
        self.L1 = self.layers_list[self.comboBox.currentText()]
        self.L1_path = self.L1.source()
        '''data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        writeRasterLayer(data_file, self.L1)'''

    def selectionchange2(self):
        print(self.comboBox_2.currentText())
        self.M1 = self.layers_list[self.comboBox_2.currentText()]
        self.M1_path = self.M1.source()

    def selectionchange3(self):
        print(self.comboBox_3.currentText())
        self.M2 = self.layers_list[self.comboBox_3.currentText()]
        self.M2_path = self.M2.source()

    def selectionchange4(self):
        print(self.comboBox_4.currentText())
        self.seg = self.layers_list[self.comboBox_4.currentText()]
        self.seg_path = self.seg.source()

    def pushButtonClicked(self):
        a = self.comboBox.currentText()
        b = self.comboBox_2.currentText()
        c = self.comboBox_3.currentText()
        d = self.comboBox_4.currentText()
        if a == "" or b == "" or c == "" or d == "":
            return

        data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        if data_file == "":
            return

        fusion = FusionMethod(self.L1_path, self.M1_path, self.M2_path,self.seg_path)
        fusion.fusionAction(data_file)
        del fusion


'''def closeEvent(self, event):
        # 是否保存数据？？？？

        # 显示关闭确认对话框
        reply = QMessageBox.question(self, '退出', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 根据用户的选择确定是否关闭窗口
        if reply == QMessageBox.Yes:
            event.accept()  # 接受关闭事件
        else:
            event.ignore()  # 忽略关闭事件'''
