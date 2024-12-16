import sys
import argparse
import h5py
import numpy as np

def display_structure(file_path):
    """显示 HDF5 文件的结构"""
    with h5py.File(file_path, 'r') as f:
        print("Structure of the HDF5 file:")
        def print_structure(name, obj):
            print(f"{name}: {obj}")
        f.visititems(print_structure)

def display_data(file_path, *keys):
    """展示指定路径下的数据"""
    with h5py.File(file_path, 'r') as f:
        data = f
        for key in keys:
            if key in data:
                data = data[key]
            else:
                print(f"Error: Dataset '{key}' not found.")
                return
        print(f"Data for {keys[-1]}:")

        # 判断数据集是否为数组
        if isinstance(data, h5py.Dataset):
            # 如果是数组，打印前10个数据（如果是二维数组的话）
            try:
                print(data[:10])  # 读取并打印前10个数据
            except ValueError:
                # 如果数据是标量，直接打印其值
                print(data[...])  # 打印标量值
        else:
            print("Error: Data is not a valid dataset.")
        
        # 打印数据集的形状和类型
        print("Shape:", data.shape)
        print("Data type:", data.dtype)


def main():
    parser = argparse.ArgumentParser(description="HDF5 Viewer: View structure or data of HDF5 files.")
    parser.add_argument('file', help="Path to the HDF5 file")
    parser.add_argument('keys', nargs='*', help="Keys to access specific datasets within the HDF5 file")

    args = parser.parse_args()

    if not args.keys:
        # 如果没有指定 keys，展示文件结构
        display_structure(args.file)
    else:
        # 如果指定了 keys，展示相应的数据
        display_data(args.file, *args.keys)

if __name__ == "__main__":
    main()
