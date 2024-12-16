import argparse
from qakits.hdf5 import HDF5Handler

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="读取pp.x输出文件并将数据保存为HDF5格式")
    
    # 添加命令行参数，设置默认值
    parser.add_argument(
        "input_file", 
        nargs="?",  # 参数是可选的
        default="chargedensity.txt",  # 默认值
        help="输入文件路径，默认为 'chargedensity.txt'"
    )
    parser.add_argument(
        "output_file", 
        nargs="?",  # 参数是可选的
        default="chargedensity.hdf5",  # 默认值
        help="输出的HDF5文件路径，默认为 'chargedensity.hdf5'"
    )
    
    # 解析命令行参数
    args = parser.parse_args()

    # 创建 HDF5Handler 实例
    handler = HDF5Handler()

    # 读取输入文件
    handler.read(args.input_file, format="ppfilplot")
    # 打印读取的数据（可选）
    # print("读取的数据:", handler.data)

    # 保存为 HDF5 文件
    handler.save(args.output_file, format="hdf5")
    print(f"数据已保存为 HDF5 文件: {args.output_file}")

if __name__ == "__main__":
    main()
