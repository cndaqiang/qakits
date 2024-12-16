import sys
import os
import argparse
from qakits.hdf5 import HDF5Handler
import numpy as np

def process_step(N):
    """处理每个步骤，读取并返回数据。
    
    根据文件存在性动态决定读取模式：
    - 如果 `chargedensity.hdf5` 存在，使用 HDF5 格式读取。
    - 否则，默认使用 `ppfilplot` 格式读取 `chargedensity.txt`。
    """
    print(f"Processing N={N}")
    handler = HDF5Handler()
    
    # 优先尝试读取 HDF5 文件
    filename = os.path.join(f"{N}", "chargedensity.hdf5")
    if os.path.exists(filename):
        # 如果 HDF5 文件存在，则使用 HDF5 格式读取
        # HDF5 的读写会很快
        handler.read(filename, format="hdf5")
    else:
        # 如果 HDF5 文件不存在，则尝试读取文本格式的 `chargedensity.txt`
        filename = os.path.join(f"{N}", "chargedensity.txt")
        handler.read(filename, format="ppfilplot")
    
    # 返回处理后的数据
    return handler.data


def main():
    """主程序，处理命令行参数并循环处理每个步长"""
    
    # 创建解析器并添加参数
    parser = argparse.ArgumentParser(description="Process charge density data over a range of steps.")
    
    # 添加命令行参数
    parser.add_argument("startstep", type=int, help="The start step.")
    parser.add_argument("dstep", type=int, help="The step increment.")
    parser.add_argument("endstep", type=int, help="The end step.")
    
    # 解析命令行参数
    args = parser.parse_args()

    startstep = args.startstep
    dstep = args.dstep
    endstep = args.endstep

    # 初始化一个字典来存储所有数据
    alldata = {}

    # 循环遍历每个步长
    for N in range(startstep, endstep + 1, dstep):
        data = process_step(N)
        
        # 对于第一个步骤，保存初始的配置信息
        if N == startstep:
            # 将所有非 "plot" 的数据直接复制到 alldata
            alldata.update({key: value for key, value in data.items() if key != "plot"})
            alldata["startstep"] = startstep
            alldata["dstep"] = dstep
            alldata["endstep"] = endstep
            # 初始化 density 数据，增加新维度
            alldata["density"] = data["plot"][..., np.newaxis]  
        else:
            # 使用 np.concatenate 在新的维度（nstep）拼接数据
            alldata["density"] = np.concatenate((alldata["density"], data["plot"][..., np.newaxis]), axis=-1)

    # 创建 HDF5Handler 实例并保存数据
    handler = HDF5Handler()
    # 使用更明确的文件名格式
    filename = f"chargedensity.{startstep}_{dstep}_{endstep}.hdf5"
    handler.data = alldata
    handler.save(filename, format="hdf5")
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    main()
