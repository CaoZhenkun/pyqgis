from qgis._core import QgsLayerTreeLayer, QgsVectorLayer, QgsMapLayerType, QgsRasterLayer, QgsVectorDataProvider, \
    QgsField, QgsVectorFileWriter, QgsGeometry, QgsPointXY, QgsFeature
from qgis._gui import QgsMapToolIdentifyFeature
from qgis.core import QgsProject, QgsLayerTreeModel, QgsMapLayer, QgsRasterFileWriter
from qgis.gui import QgsLayerTreeView, QgsMapCanvas, QgsLayerTreeMapCanvasBridge, QgsMapToolZoom, QgsMapToolPan
from PyQt5.QtCore import QUrl, QSize, QMimeData, QUrl, Qt, QVariant
from qgisUtils.yoyiMapTool import PolygonMapTool
from ui.main import Ui_MainWindow
from fusionWindowWidget import fusionWindowWidgeter
from cloudWindowWidget import cloudWindowWidgeter
from classificationWindowWidget import classifyWindowWidgeter
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QWidget, QDialog
from qgis.core import QgsApplication
from qgisUtils import addMapLayer, readVectorFile, readRasterFile, menuProvider, writeRasterLayer
import os
from swipe import Swipe
PROJECT = QgsProject.instance()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # 1 修改标题
        self.setWindowTitle("主界面")
        # 2 初始化图层树
        vl = QVBoxLayout(self.dockWidgetContents)
        self.layerTreeView = QgsLayerTreeView(self)
        vl.addWidget(self.layerTreeView)
        # 3 初始化地图画布
        self.mapCanvas = QgsMapCanvas(self)
        hl = QHBoxLayout(self.frame)
        hl.setContentsMargins(0, 0, 0, 0)  # 设置周围间距
        hl.addWidget(self.mapCanvas)
        # 4 设置图层树风格
        self.model = QgsLayerTreeModel(PROJECT.layerTreeRoot(), self)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)  # 允许图层节点重命名
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)  # 允许图层拖拽排序
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)  # 允许改变图层节点可视性
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)  # 展示图例
        self.model.setAutoCollapseLegendNodes(10)  # 当节点数大于等于10时自动折叠
        self.layerTreeView.setModel(self.model)
        # 4 建立图层树与地图画布的桥接
        self.layerTreeBridge = QgsLayerTreeMapCanvasBridge(PROJECT.layerTreeRoot(), self.mapCanvas, self)
        # 5 初始加载影像
        self.firstAdd = True
        # 6 允许拖拽文件
        self.setAcceptDrops(True)
        # 7 图层树右键菜单创建
        # self.editTempLayer: QgsVectorLayer = None  # 设置初始值为 None
        self.rightMenuProv = menuProvider(self)
        self.layerTreeView.setMenuProvider(self.rightMenuProv)
        # 选中checkable后，Button变成切换按钮(toggle button)
        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)
        # 创建地图工具
        self.toolPan = QgsMapToolPan(self.mapCanvas)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.mapCanvas, True)
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.mapCanvas, False)
        self.toolZoomOut.setAction(self.actionZoomOut)

        # A 按钮、菜单栏功能
        # 矢量编辑
        # B 初始设置控件
        self.actionEditShp.setEnabled(False)
        self.actionROI.setEnabled(False)
        self.editTempLayer: QgsVectorLayer = None  # 初始编辑图层为None
        self.ROIeditTempLayer: QgsVectorLayer = None  # 初始编辑图层为None
        self.connectFunc()
        #卷帘工具Swipe
        self.swipeTool=Swipe(self.mapCanvas,self.toolBar)


    def connectFunc(self):
        self.actionOpenRaster.triggered.connect(self.actionOpenRasterTriggered)
        self.actionOpenShp.triggered.connect(self.actionOpenShpTriggered)
        self.actionSave.triggered.connect(self.actionSaveTriggered)
        self.actionSaveAs.triggered.connect(self.actionSaveAsTriggered)
        self.actionOpen.triggered.connect(self.actionOpenTriggered)
        self.actionWriteRaster.triggered.connect(self.actionwriteRasterLayerTriggered)
        # self.layerTreeView.clicked.connect(self.printLayers)
        self.actionPan.triggered.connect(self.pan)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionFusion.triggered.connect(self.actionFusionTriggered)
        self.actionCloud.triggered.connect(self.actionCloudTriggered)
        self.actionClassify.triggered.connect(self.actionClassifyTriggered)
        # 单击、双击图层 触发事件
        self.layerTreeView.clicked.connect(self.layerClicked)
        # action edit
        self.actionEditShp.triggered.connect(self.actionEditShpTriggered)
        self.actionSelectFeature.triggered.connect(self.actionSelectFeatureTriggered)
        self.actionDeleteFeature.triggered.connect(self.actionDeleteFeatureTriggered)
        self.actionPolygon.triggered.connect(self.actionPolygonTriggered)
        self.actionROI.triggered.connect(self.actionCreateROI)

    # action Polygon
    def actionPolygonTriggered(self):
        if self.editTempLayer == None:
            QMessageBox.information(self, '警告', '您没有编辑中矢量')
            return
        if self.mapCanvas.mapTool():
            self.mapCanvas.mapTool().deactivate()
        self.polygonTool = PolygonMapTool(self.mapCanvas, self.editTempLayer, self)
        self.mapCanvas.setMapTool(self.polygonTool)

    def layerClicked(self):
        curLayer: QgsMapLayer = self.layerTreeView.currentLayer()
        if curLayer and type(curLayer) == QgsVectorLayer and not curLayer.readOnly():
            self.actionEditShp.setEnabled(True)
            self.actionROI.setEnabled(False)
        else:
            self.actionROI.setEnabled(True)
            self.actionEditShp.setEnabled(False)

    def actionEditShpTriggered(self):
        if self.actionEditShp.isChecked():
            self.editTempLayer: QgsVectorLayer = self.layerTreeView.currentLayer()
            self.editTempLayer.startEditing()
        else:
            saveShpEdit = QMessageBox.question(self, '保存编辑', "确定要将编辑内容保存到内存吗？",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if saveShpEdit == QMessageBox.Yes:
                self.editTempLayer.commitChanges()
                print("已经保存")
            else:
                self.editTempLayer.rollBack()
                print("已经返回")

            self.mapCanvas.refresh()
            self.editTempLayer = None

    def actionCreateROI(self):
        if self.actionROI.isChecked():
            # 创建一个消息框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)  # 设置图标为提示
            msg_box.setText("相同类型id相同")  # 设置消息文本
            msg_box.setWindowTitle("提示")  # 设置左上角标题为提示
            msg_box.exec_()      # 显示消息框

            curLayer: QgsMapLayer = self.layerTreeView.currentLayer()
            crs = curLayer.crs()
            self.ROIeditTempLayer = QgsVectorLayer("Polygon?crs=" + crs.authid(), "temporary_polygon", "memory")
            self.ROIeditTempLayer.startEditing()
            # 获取数据提供者
            dataProvider = self.ROIeditTempLayer.dataProvider()
            # 添加字段
            dataProvider.addAttributes([QgsField("id", QVariant.Int),
                    QgsField("类型",  QVariant.String)])
            self.ROIeditTempLayer.updateFields()
            addMapLayer(self.ROIeditTempLayer, self.mapCanvas)

            # 创建面要素
            '''polygon_geom = QgsGeometry.fromPolygonXY(
                [[QgsPointXY(0, 0), QgsPointXY(0, 10), QgsPointXY(10, 10), QgsPointXY(10, 0), QgsPointXY(0, 0)]])
            feature = QgsFeature()
            feature.setGeometry(polygon_geom)
            # 设置属性值
            feature.setAttributes([1, 2])
            # 添加要素到图层
            dataProvider.addFeatures([feature])
            # 保存图层编辑
            #self.ROIeditTempLayer.commitChanges()'''
            #
            if self.mapCanvas.mapTool():
                self.mapCanvas.mapTool().deactivate()
            self.polygonTool = PolygonMapTool(self.mapCanvas, self.ROIeditTempLayer, self)
            self.mapCanvas.setMapTool(self.polygonTool)

        else:
            saveShpEdit = QMessageBox.question(self, '保存编辑', "确定要将编辑内容保存吗？",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if saveShpEdit == QMessageBox.Yes:
                data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "Shp(*.shp)")
                if data_file == "":
                    self.ROIeditTempLayer.rollBack()
                    print("取消创建ROI")
                    return
                # 设置保存路径和文件名
                '''output_path = 'C:/Users/czk/Desktop/shp'
                output_file_name = '123output_file.shp'
                output_file_path = f'{output_path}/{output_file_name}'''
                # 调用 writeAsVectorFormat() 保存整个图层
                error = QgsVectorFileWriter.writeAsVectorFormat(self.ROIeditTempLayer, data_file, "utf-8",
                                                                self.ROIeditTempLayer.crs(), "ESRI Shapefile")
                # 处理保存结果
                if error[0] == QgsVectorFileWriter.NoError:
                    print("Layer saved successfully")
            else:
                self.ROIeditTempLayer.rollBack()
                print("取消创建ROI")

            self.mapCanvas.refresh()
            self.editTempLayer = None

    def selectToolIdentified(self, feature):
        print(feature.id())
        layerTemp: QgsVectorLayer = self.layerTreeView.currentLayer()
        if layerTemp.type() == QgsMapLayerType.VectorLayer:
            if feature.id() in layerTemp.selectedFeatureIds():
                layerTemp.deselect(feature.id())
            else:
                layerTemp.removeSelection()
                layerTemp.select(feature.id())

    def actionSelectFeatureTriggered(self):
        # if self.actionSelectFeature.isChecked():
        if self.actionEditShp.isChecked():
            if self.mapCanvas.mapTool():
                self.mapCanvas.unsetMapTool(self.mapCanvas.mapTool())
            self.selectTool = QgsMapToolIdentifyFeature(self.mapCanvas)
            self.selectTool.setCursor(Qt.ArrowCursor)
            self.selectTool.featureIdentified.connect(self.selectToolIdentified)
            layers = self.mapCanvas.layers()
            if layers:
                self.selectTool.setLayer(self.layerTreeView.currentLayer())
            self.mapCanvas.setMapTool(self.selectTool)
        else:
            if self.mapCanvas.mapTool():
                self.mapCanvas.unsetMapTool(self.mapCanvas.mapTool())

    def actionDeleteFeatureTriggered(self):
        if self.editTempLayer == None:
            QMessageBox.information(self, '警告', '您没有编辑中矢量')
            return
        if len(self.editTempLayer.selectedFeatureIds()) == 0:
            QMessageBox.information(self, '删除选中矢量', '您没有选择任何矢量')
        else:
            self.editTempLayer.deleteSelectedFeatures()

    def dragEnterEvent(self, fileData):
        if fileData.mimeData().hasUrls():
            fileData.accept()
        else:
            fileData.ignore()

    # 拖拽文件事件
    def dropEvent(self, fileData):
        mimeData: QMimeData = fileData.mimeData()
        filePathList = [u.path()[1:] for u in mimeData.urls()]
        for filePath in filePathList:
            filePath: str = filePath.replace("/", "//")
            if filePath.split(".")[-1] in ["tif", "TIF", "tiff", "TIFF", "GTIFF", "png", "jpg", "pdf"]:
                self.addRasterLayer(filePath)
            elif filePath.split(".")[-1] in ["shp", "SHP", "gpkg", "geojson", "kml"]:
                self.addVectorLayer(filePath)
            elif filePath == "":
                pass
            else:
                QMessageBox.about(self, '警告', f'{filePath}为不支持的文件类型，目前支持栅格影像和shp矢量')

    def actionOpenRasterTriggered(self):
        data_file, ext = QFileDialog.getOpenFileName(self, '打开栅格', '',
                                                     'HDR(*.hdr);;GeoTiff(*.tif;*tiff;*TIF;*TIFF);;ENVI(*.dat)')

        '''if data_file:
            self.addRasterLayer(data_file)'''
        if data_file:
            # 获取文件扩展名
            _, extension = os.path.splitext(data_file)

            if extension.lower() == '.hdr':
                # 如果是 HDR 文件，则打开 ENVI 格式的栅格图层
                self.addENVIRasterLayer(data_file)
            else:
                # 否则，使用默认方式打开栅格图层
                self.addRasterLayer(data_file)

    def addENVIRasterLayer(self, hdr_file):
        # 获取 ENVI 头文件的路径和文件名（不包含扩展名）
        hdr_path, hdr_filename = os.path.split(hdr_file)
        # 移除扩展名，得到数据文件的路径和文件名
        data_filename, _ = os.path.splitext(hdr_filename)
        # 组合数据文件的完整路径
        data_file = os.path.join(hdr_path, data_filename)

        # 添加 ENVI 格式的栅格图层
        self.addRasterLayer(data_file)

    # 打开项目
    def actionOpenTriggered(self):
        data_file, ext = QFileDialog.getOpenFileName(self, '打开项目', '', "QGZ文件(*.qgz)")
        if data_file:
            PROJECT.read(data_file)

    # 保存项目
    def actionSaveTriggered(self):
        PROJECT.write()

    # 另存为
    def actionSaveAsTriggered(self):
        data_file, ext = QFileDialog.getSaveFileName(self, '另存为', '', "QGZ文件(*.qgz)")
        if data_file:
            PROJECT.write(data_file)

    def actionOpenShpTriggered(self):
        data_file, ext = QFileDialog.getOpenFileName(self, '打开矢量', '',
                                                     "ShapeFile(*.shp);;All Files(*);;Other(*.gpkg;*.geojson;*.kml)")
        if data_file:
            self.addVectorLayer(data_file)

    def addRasterLayer(self, rasterFilePath):
        rasterLayer = readRasterFile(rasterFilePath)
        if self.firstAdd:
            addMapLayer(rasterLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(rasterLayer, self.mapCanvas)

    def addVectorLayer(self, vectorFilePath):
        vectorLayer = readVectorFile(vectorFilePath)
        if self.firstAdd:
            addMapLayer(vectorLayer, self.mapCanvas, True)
            self.firstAdd = False
        else:
            addMapLayer(vectorLayer, self.mapCanvas)

    # 打开项目
    def openProject(self, project, projctPath):
        project.read(projctPath)

    # 保存栅格
    def actionwriteRasterLayerTriggered(self):
        data_file, ext = QFileDialog.getSaveFileName(self, '保存为', '', "GeoTiff(*.tif;*tiff;*TIF;*TIFF)")
        if data_file == "":
            return
        layers = self.layerTreeView.selectedLayers()
        if len(layers) == 1:
            layer = layers[0]
            print(layer.name())
            writeRasterLayer(data_file, layer)
        # writeRasterLayer(data_file, layer)

    # 打印图层名字，有问题
    def printLayers(self):
        layers = PROJECT.mapLayers()
        l = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        numOfLayers = len(layers)
        print(layers)
        print(numOfLayers)
        if self.layerTreeView.currentIndex().isValid():
            layers = self.layerTreeView.selectedLayers()
            if len(layers) >= 1:
                layer = layers[0]
                print(layer.name())
            '''for layer in layers:
                print(layer.name())'''
        # 使用列表表达式获得图层名称
        '''l = [layer.name() for layer in layers.values()]
        # 键值对存储图层名称和图层对象
        layers_list = {}
        for l in layers.values():
            layers_list[l.name()] = l
        print(layers_list)'''

    def pan(self):
        self.mapCanvas.setMapTool(self.toolPan)

    def zoomIn(self):
        self.mapCanvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.mapCanvas.setMapTool(self.toolZoomOut)

    def actionFusionTriggered(self):
        print("融合")
        self.FusionWindow = fusionWindowWidgeter()
        self.FusionWindow.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        self.FusionWindow.show()

    def actionCloudTriggered(self):
        self.CloudWindow = cloudWindowWidgeter()
        self.CloudWindow.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        self.CloudWindow.show()

    def actionClassifyTriggered(self):
        self.ClassifyWindow = classifyWindowWidgeter()
        self.ClassifyWindow.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口
        self.ClassifyWindow.show()

    def closeEvent(self, event):
        # 是否保存数据？？？？

        # 显示关闭确认对话框
        reply = QMessageBox.question(self, '退出', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 根据用户的选择确定是否关闭窗口
        if reply == QMessageBox.Yes:
            event.accept()  # 接受关闭事件
            QgsApplication.quit()  # 终止应用程序的事件循环
        else:
            event.ignore()  # 忽略关闭事件
