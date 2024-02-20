from qgis.core import QgsProject
from OLSTARFM import FusionMethod
from ui.classificationWindow import Ui_classify
import traceback
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsStyle, QgsSymbol, QgsWkbTypes, QgsSymbolLayer, \
    Qgis, QgsFeatureRenderer
from qgis.gui import QgsRendererRasterPropertiesWidget, QgsSingleSymbolRendererWidget, \
    QgsCategorizedSymbolRendererWidget
from PyQt5.QtCore import QModelIndex
from ui.layerPropWindow import Ui_LayerProp
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QTabBar, QMessageBox, QFileDialog
from qgisUtils import getRasterLayerAttrs, getVectorLayerAttrs, writeRasterLayer
from classification import RandomForestClassification

PROJECT = QgsProject.instance()


class classifyWindowWidgeter(QWidget, Ui_classify):

    def __init__(self, parent=None):
        super(classifyWindowWidgeter, self).__init__(parent)
        self.image_path = None
        self.shp_path = None
        self.parentWindow = parent
        self.setupUi(self)

        layers = PROJECT.mapLayers()
        # 使用列表表达式获得图层名称
        self.l = [layer.name() for layer in layers.values()]
        # 键值对存储图层名称和图层对象
        self.layers_list = {}
        for i in layers.values():
            self.layers_list[i.name()] = i

        self.image = QgsRasterLayer()  # 待分类图像
        self.shp = QgsVectorLayer()  # shp分类样本


        self.initUI()
        self.connectFunc()

    def initUI(self):
        self.comboBox.addItems(self.l)
        self.comboBox_2.addItems(self.l)


    def connectFunc(self):
        self.comboBox.currentIndexChanged.connect(self.selectionchange1)
        self.comboBox_2.currentIndexChanged.connect(self.selectionchange2)
        self.pushButton.clicked.connect(self.pushButtonClicked)

    def selectionchange1(self):
        print(self.comboBox.currentText())
        self.image = self.layers_list[self.comboBox.currentText()]
        self.image_path = self.image.source()

    def selectionchange2(self):
        print(self.comboBox_2.currentText())
        self.shp = self.layers_list[self.comboBox_2.currentText()]
        self.shp_path = self.shp.source()

    def pushButtonClicked(self):
        a = self.comboBox.currentText()
        b = self.comboBox_2.currentText()

        if a == "" or b == "":
            return

        data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        if data_file == "":
            return

        RandomForestClassification(self.image_path,self.image_path,self.shp_path,data_file)




