import argparse
import numpy as np
from qakits.hdf5 import HDF5Handler
from qakits.density import calculate_dipole

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="计算 dipole 并输出结果")
    
    # 添加命令行参数，设置默认值
    parser.add_argument(
        "input_file", 
        nargs="?",  # 可选参数
        default="chargedensity.txt",  # 默认值
        help="输入文件路径，默认为 'chargedensity.txt'"
    )
    
    # 解析命令行参数
    args = parser.parse_args()

    # 创建 HDF5Handler 实例并读取数据
    handler = HDF5Handler()
    handler.read(args.input_file, format="ppfilplot")

    # 提取必要的数据
    grid = np.array([handler.data["grid"]["nr1x"], handler.data["grid"]["nr2x"], handler.data["grid"]["nr3x"]])
    lattice = handler.data["lattice_matrix"]
    data = handler.data["plot"]
    shift_frac = [0.5,0.5,0.5]

    # 计算 dipole
    dipole = calculate_dipole(grid, lattice, data,shift_frac)
    print("Dipole:", *[f"{d:.6f}" for d in dipole])

if __name__ == "__main__":
    main()
