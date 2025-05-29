import argparse
import os
import hashlib

def calculate_hash(file_path, hash_algorithm="md5", load_to_memory=False, chunk_size=8192):
    """
    使用 hashlib 计算文件的哈希值。

    参数:
        file_path (str): 文件的路径。
        hash_algorithm (str): 哈希算法类型，默认为 "md5"。
                              支持的算法: md5, sha1, sha256, sha512。
        load_to_memory (bool): 是否将整个文件加载到内存中，默认为 False。
        chunk_size (int): 每次读取文件的块大小（默认 8192 字节）。

    返回:
        str: 文件的哈希值。
    """
    # 创建哈希对象
    try:
        hash_func = getattr(hashlib, hash_algorithm)()
    except AttributeError:
        print(f"错误: 不支持的哈希算法 '{hash_algorithm}'！")
        return None

    try:
        if load_to_memory:
            # 将整个文件加载到内存中
            with open(file_path, "rb") as f:
                data = f.read()  # 一次性读取整个文件
            hash_func.update(data)
        else:
            # 分块读取文件内容
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_func.update(chunk)
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到！")
        return None
    except PermissionError:
        print(f"错误: 没有权限读取文件 '{file_path}'！")
        return None

    # 返回哈希值的十六进制表示
    return hash_func.hexdigest()

def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="使用 hashlib 计算文件的哈希值。")
    parser.add_argument(
        "file",
        type=str,
        help="要检测的文件路径。",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="md5",
        choices=["md5", "sha1", "sha256", "sha512"],
        help="使用的哈希算法（默认为 md5）。",
    )
    parser.add_argument(
        "--load-to-memory",
        action="store_true",
        help="是否将整个文件加载到内存中（默认为 False）。",
    )
    args = parser.parse_args()

    # 获取文件路径
    file_path = args.file

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        print(f"错误: '{file_path}' 不是一个有效的文件路径！")
        return

    # 计算文件的哈希值
    hash_value = calculate_hash(
        file_path,
        hash_algorithm=args.algorithm,
        load_to_memory=args.load_to_memory
    )

    if hash_value:
        print(f"文件的 {args.algorithm.upper()} 值为: {hash_value}")

if __name__ == "__main__":
    main()