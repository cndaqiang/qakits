from qakits.hdf5.hdf5handler import HDF5Handler
import h5py
import numpy as np


# 示例使用
if __name__ == "__main__":
    handler = HDF5Handler()

    # 读取文本文件
    handler.read("chargedensity.txt", format="ppfilplot")
    #print("读取的数据:", handler.data)
    #exit()
    # 保存为 HDF5 文件
    handler.save("output.hdf5", format="hdf5")
    print("数据已保存为 HDF5 文件")
