from osgeo import gdal
from qgis._core import QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsRectangle, QgsVectorDataProvider, \
    QgsWkbTypes, QgsRasterFileWriter, QgsFileUtils, QgsRasterPipe
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.gui import QgsMapCanvas
import os
import os.path as osp

from qgisUtils.yoyiFile import getFileSize

PROJECT = QgsProject.instance()


def addMapLayer(layer: QgsMapLayer, mapCanvas: QgsMapCanvas, firstAddLayer=False):
    if layer.isValid():
        if firstAddLayer:
            mapCanvas.setDestinationCrs(layer.crs())
            mapCanvas.setExtent(layer.extent())

        while PROJECT.mapLayersByName(layer.name()):
            layer.setName(layer.name() + "_1")

        PROJECT.addMapLayer(layer)
        layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]
        mapCanvas.setLayers(layers)
        mapCanvas.refresh()


def readRasterFile(rasterFilePath):
    rasterLayer = QgsRasterLayer(rasterFilePath, osp.basename(rasterFilePath))
    return rasterLayer


def readVectorFile(vectorFilePath):
    vectorLayer = QgsVectorLayer(vectorFilePath, osp.basename(vectorFilePath), "ogr")
    return vectorLayer


qgisDataTypeDict = {
    0: "UnknownDataType",
    1: "Uint8",
    2: "UInt16",
    3: "Int16",
    4: "UInt32",
    5: "Int32",
    6: "Float32",
    7: "Float64",
    8: "CInt16",
    9: "CInt32",
    10: "CFloat32",
    11: "CFloat64",
    12: "ARGB32",
    13: "ARGB32_Premultiplied"
}


def getRasterLayerAttrs(rasterLayer: QgsRasterLayer):
    rdp: QgsRasterDataProvider = rasterLayer.dataProvider()
    crs: QgsCoordinateReferenceSystem = rasterLayer.crs()
    extent: QgsRectangle = rasterLayer.extent()
    resDict = {
        "name": rasterLayer.name(),
        "source": rasterLayer.source(),
        "memory": getFileSize(rasterLayer.source()),
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "width": f"{rasterLayer.width()}",
        "height": f"{rasterLayer.height()}",
        "dataType": qgisDataTypeDict[rdp.dataType(1)],
        "bands": f"{rasterLayer.bandCount()}",
        "crs": crs.description()
    }
    return resDict


def getVectorLayerAttrs(vectorLayer: QgsVectorLayer):
    vdp: QgsVectorDataProvider = vectorLayer.dataProvider()
    crs: QgsCoordinateReferenceSystem = vectorLayer.crs()
    extent: QgsRectangle = vectorLayer.extent()
    resDict = {
        "name": vectorLayer.name(),
        "source": vectorLayer.source(),
        "memory": getFileSize(vectorLayer.source()),
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "geoType": QgsWkbTypes.geometryDisplayString(vectorLayer.geometryType()),
        "featureNum": f"{vectorLayer.featureCount()}",
        "encoding": vdp.encoding(),
        "crs": crs.description(),
        "dpSource": vdp.description()
    }
    return resDict


# 保存栅格文件
def writeRasterLayer(outputPath, rasterLayer):
    layer = rasterLayer
    file_path = outputPath
    # 检查图层是否加载成功
    if not layer.isValid():
        print("图层加载失败！")

    # 定义要保存的文件路径
    output_file_path = file_path

    # 获取图层的数据提供者
    provider = layer.dataProvider()

    # 创建一个QgsRasterFileWriter对象
    file_writer = QgsRasterFileWriter(output_file_path)

    # 设置输出格式，这里使用GeoTIFF
    file_writer.setOutputFormat("GTiff")

    #file_writer.setCreateOptions(["TILED=YES"])

    # 可选：设置压缩方式和块大小
    #file_writer.setCreateOptions(["COMPRESS=LZW", "TILED=YES", "BLOCKXSIZE=256", "BLOCKYSIZE=256"])



    # 写入图层数据
    file_writer.writeRaster(layer.pipe(), layer.width(), layer.height(), layer.extent(), layer.crs())

    del file_writer
    '''if file_writer.hasError() == QgsRasterFileWriter.NoError:
        print(f"图层已成功保存到 {output_file_path}")
    else:
        print(f"保存图层时发生错误: {file_writer.errorMsg()}")'''

