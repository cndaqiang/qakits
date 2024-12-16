import h5py
import argparse
import numpy as np
# 实际压缩并不理想

def compress_hdf5(input_file: str, output_file: str, compression_level: int):
    """
    压缩 HDF5 文件。

    :param input_file: 原始 HDF5 文件路径。
    :param output_file: 压缩后的 HDF5 文件路径。
    :param compression_level: GZIP 压缩级别（1-9）。
    """
    def copy_dataset(input_group, output_group):
        """
        递归复制数据集，应用压缩。
        """
        for name, item in input_group.items():
            if isinstance(item, h5py.Group):
                # 如果是组，递归复制
                new_group = output_group.create_group(name)
                copy_dataset(item, new_group)
            elif isinstance(item, h5py.Dataset):
                # 如果是数据集，复制并应用压缩（仅对数组应用压缩）
                data = item[()]
                if isinstance(data, np.ndarray):
                    output_group.create_dataset(
                        name,
                        data=data,
                        compression="gzip",
                        compression_opts=compression_level
                    )
                else:
                    # 对于标量数据集，直接保存
                    output_group.create_dataset(name, data=data)
            else:
                print(f"Skipping unknown item type: {name}")

    with h5py.File(input_file, 'r') as infile, h5py.File(output_file, 'w') as outfile:
        copy_dataset(infile, outfile)
        print(f"Compressed file saved to: {output_file}")


def main():
    """
    主程序，用于处理命令行参数并执行 HDF5 文件压缩。
    """
    parser = argparse.ArgumentParser(description="Compress an HDF5 file using gzip.")
    parser.add_argument("input_file", type=str, help="Path to the input HDF5 file.")
    parser.add_argument("output_file", type=str, help="Path to the output (compressed) HDF5 file.")
    parser.add_argument(
        "compression_level", type=int, choices=range(1, 10),
        help="GZIP compression level (1-9)."
    )

    args = parser.parse_args()

    compress_hdf5(args.input_file, args.output_file, args.compression_level)


if __name__ == "__main__":
    main()
