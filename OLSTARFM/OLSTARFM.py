import numpy as np
from osgeo import gdal
import os
import cv2


class FusionMethod():
    def __init__(self, L1_path, M1_path, M2_path, seg_path):
        self.seg_path = seg_path
        self.M2_path = M2_path
        self.M1_path = M1_path
        self.L1_path = L1_path
        self.DN_min = 0
        self.DN_max = 10000
        self.snum = None
        self.prediction = None
        self.CRT2C = None
        self.CRT1C = None
        self.cubic_CR = None
        self.yL = None
        self.xL = None
        self.xH = None
        self.yH = None
        self.bands = None
        self.Factor = 16

        '''self.L1_path = 'E:/fiverpaper/HG/L1'  # 基时相高分辨率影像
        self.M1_path = 'E:/fiverpaper/HG/M1'  # 基时相低分辨率影像
        self.M1_path = 'E:/fiverpaper/HG/M4'  # 预测时相低分辨率影像'''
        '''seg_path = 'E:/fiverpaper/HG/L1235.tif'  # 分割影像'''

        self.FRT1 = self.read_img(self.L1_path)
        self.CRT1 = self.read_img(self.M1_path)
        self.CRT2 = self.read_img(self.M2_path)
        self.seg = self.read_img(self.seg_path)

        self.preprocessing()

    # read from Tif file
    def read_img(self, path):
        try:
            naip_ds = gdal.Open(path)
            nbands = naip_ds.RasterCount
            band_data = []
            for b in range(nbands):
                band_data.append(naip_ds.GetRasterBand(b + 1).ReadAsArray())
            img = np.dstack(band_data)
            return img.astype("float")
        except Exception:
            return None

    # Save result into Tif
    def save_img(self, array, path):
        driver = gdal.GetDriverByName("GTiff")
        if len(array.shape) == 2:
            dst = driver.Create(path, array.shape[1], array.shape[0], 1, 2)
            dst.GetRasterBand(1).WriteArray(array)
        else:
            # save all bands
            n_band = array.shape[-1]
            dst = driver.Create(path, array.shape[1], array.shape[0], n_band, 6)
            for b in range(n_band):
                dst.GetRasterBand(b + 1).WriteArray(array[:, :, b])
        del dst

    # 对图像进行下采样操作
    def Cubic(self, array):
        xL, yL, bands = array.shape
        arraycubic = np.zeros((xL * self.Factor, xL * self.Factor, bands))
        for b in range(0, bands):
            arrayb = array[:, :, b]
            arraybcubic = cv2.resize(arrayb, (xL * self.Factor, xL * self.Factor), interpolation=cv2.INTER_CUBIC)
            arraycubic[:, :, b] = arraybcubic
        return arraycubic

    # 对图像进行上采样操作
    def aggregation(self, array):
        xH, yH, bands = array.shape
        xL = xH // self.Factor
        yL = yH // self.Factor
        arrayC = np.zeros((xL, yL, bands))
        for b in range(bands):
            for i in range(xL):
                for j in range(yL):
                    tmp1 = array[i * self.Factor:(i + 1) * self.Factor, j * self.Factor:(j + 1) * self.Factor, b]
                    arrayC[i, j, b] = np.sum(np.sum(tmp1)) / self.Factor ** 2
        return arrayC

    def preprocessing(self):

        self.FRT1[self.FRT1 < self.DN_min] = self.DN_min
        self.CRT1[self.CRT1 < self.DN_min] = self.DN_min
        self.CRT2[self.CRT2 < self.DN_min] = self.DN_min

        self.FRT1[self.FRT1 > self.DN_max] = self.DN_max
        self.CRT1[self.CRT1 > self.DN_max] = self.DN_max
        self.CRT2[self.CRT2 > self.DN_max] = self.DN_max

        self.seg = self.seg.astype(int).squeeze()
        self.snum = int(np.max(self.seg))

        self.xH, self.yH, self.bands = self.FRT1.shape
        self.xL = self.xH // self.Factor
        self.yL = self.yH // self.Factor

        self.CRT1C = self.aggregation(self.CRT1)
        self.CRT2C = self.aggregation(self.CRT2)

        self.cubic_CR = self.Cubic(self.CRT2C - self.CRT1C)

        self.prediction = np.zeros((self.xH, self.yH, self.bands))  # 预测值的副本

    def fusionAction(self, data_file):
        # 循环处理每个波段
        for b in range(0, self.bands):
            f1_b = self.FRT1[:, :, b]  # FRT1 的第 b 个波段
            c1_b = self.CRT1[:, :, b]  # CRT1 的第 b 个波段
            c2_b = self.CRT2[:, :, b]  # CRT2 的第 b 个波段
            prediction_b = self.prediction[:, :, b]  # 预测值的第 b 个波段
            for s in range(self.snum):  # 注意这里从0开始
                seg_pos = np.where(self.seg == s)
                c2c1 = c2_b[seg_pos] - c1_b[seg_pos]  # c2c1 是 c2_b 和 c1_b 在 seg_pos 位置的差值
                c2c1 = c2c1.flatten()  # c2c1 是 c2c1 的 flattened 版本
                median_c = np.median(c2c1)  # median_c 是 c2c1 的中位数
                prediction_b[seg_pos] = median_c + f1_b[seg_pos]  # 在 seg_pos 位置更新 prediction_b 的值
            self.prediction[:, :, b] = prediction_b[:, :]  # 将更新后的 prediction_b 赋值给 prediction 的第 b 个波段

        residual = (self.CRT2C - self.CRT1C) - self.aggregation(self.prediction - self.FRT1)  # 计算残差
        prediction = self.prediction + self.Cubic(residual)  # 将重采样后的残差加到预测值上

        # 循环处理每个波段
        for b in range(0, self.bands):
            prediction_b = prediction[:, :, b]  # prediction的第b个波段
            for i in range(self.xH):
                for j in range(self.yH):
                    if prediction_b[i, j] < self.DN_min:  # 如果prediction_b中对应位置的元素小于DN_min
                        tmp = self.FRT1[i, j, b] + self.cubic_CR[i, j, b]
                        prediction_pos = max(self.DN_min, tmp)  # 取DN_min和FRT1_b[i,j]+cubic_CR[i,j]中的较大值
                        prediction[i, j, b] = min(self.DN_max,
                                                  prediction_pos)  # 取DN_max和prediction_pos中的较小值，赋值给prediction中对应位置的元素
                    if prediction_b[i, j] > self.DN_max:  # 如果prediction_b中对应位置的元素大于DN_max
                        tmp = self.FRT1[i, j, b] + self.cubic_CR[i, j, b]
                        prediction_pos = min(self.DN_max, tmp)  # 取DN_max和FRT1_b[i,j]+cubic_CR[i,j]中的较小值
                        prediction[i, j, b] = max(self.DN_min,
                                                  prediction_pos)  # 取DN_min和prediction_pos中的较大值，赋值给prediction中对应位置的元素

        self.save_img(prediction, os.path.join(data_file))
