from qgis.core import QgsProject
from NSPI_TIMESERIES import CloudMethod
from ui.CloudWindow import Ui_Cloud
import traceback
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsStyle, QgsSymbol, QgsWkbTypes, QgsSymbolLayer, \
    Qgis, QgsFeatureRenderer
from qgis.gui import QgsRendererRasterPropertiesWidget, QgsSingleSymbolRendererWidget, \
    QgsCategorizedSymbolRendererWidget
from PyQt5.QtCore import QModelIndex
from ui.layerPropWindow import Ui_LayerProp
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QTabBar, QMessageBox, QFileDialog
from qgisUtils import getRasterLayerAttrs, getVectorLayerAttrs, writeRasterLayer
import NSPI_TIMESERIES

PROJECT = QgsProject.instance()


class cloudWindowWidgeter(QWidget, Ui_Cloud):

    def __init__(self, parent=None):
        super(cloudWindowWidgeter, self).__init__(parent)
        self.data_file4 = None
        self.data_file3 = None
        self.data_file2 = None
        self.data_file1 = None
        self.parentWindow = parent
        self.setupUi(self)

        self.initUI()
        self.connectFunc()

    def initUI(self):
        self.label.setText("")

    def connectFunc(self):
        self.pushButton.clicked.connect(self.pushButtonClicked)
        self.pushButton_2.clicked.connect(self.pushButton_2Clicked)
        self.pushButton_3.clicked.connect(self.pushButton_3Clicked)
        self.pushButton_4.clicked.connect(self.pushButton_4Clicked)
        self.pushButton_5.clicked.connect(self.pushButton_5Clicked)

    def pushButtonClicked(self):
        self.data_file1, ext = QFileDialog.getOpenFileName(self, '打开参数设置', '',
                                                           "YAML(*.yaml)")

    def pushButton_2Clicked(self):
        self.data_file2, ext = QFileDialog.getOpenFileName(self, '打开时序影像', '',
                                                           'GeoTiff(*.tif;*tiff;*TIF;*TIFF);;ENVI(*.dat);;HDR(*.hdr)')

    def pushButton_3Clicked(self):
        self.data_file3, ext = QFileDialog.getOpenFileName(self, '打开掩膜', '',
                                                           'GeoTiff(*.tif;*tiff;*TIF;*TIFF);;ENVI(*.dat);;HDR(*.hdr)')

    def pushButton_4Clicked(self):
        #self.data_file4, ext = QFileDialog.getSaveFileName(self, '保存路径', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        self.data_file4 = QFileDialog.getExistingDirectory(self)
        print("here")

    def pushButton_5Clicked(self):
        cloud = CloudMethod(self.data_file1, self.data_file2, self.data_file3, self.data_file4)
        del cloud
