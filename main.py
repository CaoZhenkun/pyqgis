from qgis.PyQt import QtCore
from qgis.core import QgsApplication
from PyQt5.QtCore import Qt
import os
import traceback
from mainWindow import MainWindow,PROJECT


if __name__ == '__main__':
    QgsApplication.setPrefixPath('D:/Program Files/QGIS 3.30.2/apps/qgis', True)  # 提供qgis安装位置的路径
    QgsApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 适应高分辨率
    app = QgsApplication([], True)  # 创建对QgsApplication的引用，第二个参数设置为False将禁用GUI

    t = QtCore.QTranslator()
    t.load(r'.\zh-Hans.qm')
    app.installTranslator(t)

    app.initQgis()  # 加载提供者

    mainWindow = MainWindow()
    mainWindow.show()


    # 加载一个项目
    #PROJECT.read('D:/code/test/1.qgz')

    app.exec_()
    app.exitQgis()  # 脚本完成后，调用exitQgis（）从内存中删除提供者和图层注册
