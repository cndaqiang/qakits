import os
import argparse
from qakits.hdf5 import HDF5Handler
import numpy as np

def process_step(filename):
    """
    处理单个文件的步骤。
    使用 HDF5Handler 读取文件并返回数据。
    """
    handler = HDF5Handler()
    handler.read(filename, format="hdf5")
    return handler.data

def main():
    # 设置 argparse
    parser = argparse.ArgumentParser(description="合并多个输入文件的密度数据到一个输出文件")
    parser.add_argument(
        "output_file",
        type=str,
        help="输出文件路径（支持 HDF5 格式）"
    )
    parser.add_argument(
        "input_files",
        nargs='+',
        type=str,
        help="一个或多个输入文件路径（HDF5 格式）"
    )

    args = parser.parse_args()
    output_file = args.output_file
    input_files = args.input_files

    alldata = {}  # 用于存储合并后的数据

    for i, filename in enumerate(input_files):
        if not os.path.exists(filename):
            print(f"文件 {filename} 不存在，跳过...")
            continue

        data = process_step(filename)

        if i == 0:  # 第一个输入文件
            # 将所有非 "density" 的数据直接复制到 alldata
            alldata.update({key: value for key, value in data.items() if key != "density"})
            # 初始化 density 数据，增加新维度
            alldata["densityDB"] = data["density"][..., np.newaxis]
        else:
            # 拼接到新的维度（nstep）
            alldata["densityDB"] = np.concatenate(
                (alldata["densityDB"], data["density"][..., np.newaxis]),
                axis=-1
            )

    # 保存合并数据到输出文件
    handler = HDF5Handler()
    handler.data = alldata
    handler.save(output_file, format="hdf5")
    print(f"数据已保存到 {output_file}")

if __name__ == "__main__":
    main()
