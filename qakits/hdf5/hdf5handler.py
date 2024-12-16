import h5py
import numpy as np


class HDF5Handler:
    def __init__(self):
        """
        初始化 HDF5Handler 对象。
        """
        self.data = {}  # 用于存储读取的数据

    def read(self, file_path: str, format: str):
        """
        读取文件入口，根据 format 调用对应的方法。
        
        :param file_path: 要读取的文件路径。
        :param format: 文件格式，例如 'txt', 'hdf5' 等。
        """
        format = format.lower()
        if format == 'ppfilplot':
            self.data = self._read_ppfilplot(file_path)
        elif format == 'hdf5':
            self.data = self._read_hdf5(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {format}")

    def save(self, file_path: str, format: str):
        """
        保存文件入口，根据 format 调用对应的方法。
        
        :param file_path: 保存的目标文件路径。
        :param format: 文件格式，例如 'txt', 'hdf5' 等。
        """
        format = format.lower()
        if format == 'txt':
            self._save_txt(file_path, self.data)
        elif format == 'hdf5':
            self._save_hdf5(file_path, self.data)
        else:
            raise ValueError(f"不支持的文件格式: {format}")

    def _read_ppfilplot(self, file_path: str) -> dict:
        """
        读取 pp.x 输出的 `filplot` 文本文件，解析为字典格式。
        !目前仅支持立方晶格 (ibrav=0) 的情况。
        
        :param file_path: 文本文件路径。
        :return: 包含解析数据的字典。
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()  # 保留文件原始行，确保空行不会被提前去掉
    
        data = {}
    
        # 第一行: title
        data["title"] = lines[0].strip() if lines[0].strip() else None
        start_line = 1  # 第一行无论是否为空，均处理并移动到下一行
    
        # 第二行: 网格信息和原子数
        nr_info = list(map(int, lines[start_line].split()))
        data["grid"] = {
            "nr1x": nr_info[0],
            "nr2x": nr_info[1],
            "nr3x": nr_info[2],
            "nr1": nr_info[3],
            "nr2": nr_info[4],
            "nr3": nr_info[5],
            "nat": nr_info[6],
            "ntyp": nr_info[7],
        }
        start_line += 1
    
        # 第三行: 晶格类型和 celldm
        cell_info = lines[start_line].split()
        data["cell"] = {
            "ibrav": int(cell_info[0]),
            "celldm": np.array(list(map(float, cell_info[1:]))) / 1.88972612,  # Bohr 转为 Ångström
        }
        start_line += 1
    
        # 第四至第六行: 晶格矩阵 (仅当 ibrav == 0 时)
        if data["cell"]["ibrav"] == 0:
            lattice_matrix = [list(map(float, lines[start_line + i].split())) for i in range(3)]
            data["lattice_matrix"] = np.array(lattice_matrix)*data["cell"]["celldm"][0]
            start_line += 3
        else:
            raise ValueError("当前仅支持立方晶格 (ibrav == 0) 的情况。")
    
        # 第七行: 计算参数
        calc_params = list(map(float, lines[start_line].split()))
        data["parameters"] = {
            "gcutm": calc_params[0],
            "dual": calc_params[1],
            "ecut": calc_params[2],
            "plot_num": int(calc_params[3]),
        }
        start_line += 1
    
        # 第八行: 原子类型信息
        atom_types = {}
        for _ in range(data["grid"]["ntyp"]):
            atom_line = lines[start_line].split()
            atom_types[atom_line[1]] = {
                "nt": int(atom_line[0]),
                "zv": float(atom_line[2]),
            }
            start_line += 1
        data["atom_types"] = atom_types
    
        # 接下来的行: 原子坐标信息
        atoms = []
        for _ in range(data["grid"]["nat"]):
            atom_line = lines[start_line].split()
            atoms.append({
                "id": int(atom_line[0]),
                "tau": np.array(list(map(float, atom_line[1:4]))),
                "type": int(atom_line[4]),
            })
            start_line += 1
        data["atoms"] = atoms
    
        # 最后部分: plot 数据
        plot_data = []
        for line in lines[start_line:]:
            if line.strip():  # 只处理非空行
                plot_data.extend(map(float, line.split()))
        data["plot"] = np.array(plot_data)

        # 检查 plot 数据的大小是否匹配网格点数
        expected_size = data["grid"]["nr1x"] * data["grid"]["nr2x"] * data["grid"]["nr3x"]
        if data["plot"].size != expected_size:
            raise ValueError(
                f"解析错误: plot 数据大小 ({data['plot'].size}) 不匹配网格点数 ({expected_size})。"
            )

        # 如果匹配，reshape为 (nr3x, nr2x, nr1x)
        data["plot"] = data["plot"].reshape(data["grid"]["nr3x"], data["grid"]["nr2x"], data["grid"]["nr1x"])

        # 调整顺序为 (z, y, x)，可以用 permute 或 transpose 调整
        data["plot"] = np.transpose(data["plot"], (2, 1, 0))  # 这一步根据需要调整轴的顺序

        # 将data["plot"]的单位有e/Bohr^3, 修改为 e/A^3
        data["plot"] = data["plot"] * 1.88972612 * 1.88972612 * 1.88972612

        return data


    def _read_hdf5(self, file_path: str) -> dict:
        """
        读取 HDF5 文件，解析为字典格式。
        
        :param file_path: HDF5 文件路径。
        :return: 包含解析数据的字典。
        """
        data = {}
        with h5py.File(file_path, 'r') as hdf:
            for key in hdf.keys():
                data[key] = hdf[key][()]
        return data

    def _save_txt(self, file_path: str, data: dict):
        """
        将数据保存为文本文件。
        
        :param file_path: 目标文本文件路径。
        :param data: 要保存的数据字典。
        """
        with open(file_path, 'w') as f:
            # 写入元数据
            f.write(" ".join(map(str, data["metadata"])) + "\n")

            # 写入结构信息
            for line in data["structure"]:
                f.write(" ".join(map(str, line)) + "\n")

            # 写入参数
            f.write(" ".join(map(str, data["parameters"])) + "\n")

            # 写入坐标
            for line in data["coordinates"]:
                f.write(" ".join(map(str, line)) + "\n")

            # 写入数据部分
            for line in data["data"]:
                f.write(" ".join(map(str, line)) + "\n")

    def _save_hdf5(self, file_path: str, data: dict):
        """
        将数据保存为 HDF5 文件。

        :param file_path: 目标 HDF5 文件路径。
        :param data: 要保存的数据字典。
        """
        def save_recursive(hdf_group, prefix, value):
            if value is None:
                value = ""  # 将 None 转换为空字符串
            if isinstance(value, dict):
                # 如果是字典，递归处理每个子键
                for subkey, subvalue in value.items():
                    full_key = f"{prefix}_{subkey}" if prefix else subkey
                    save_recursive(hdf_group, full_key, subvalue)
            elif isinstance(value, list):
                try:
                    # 尝试将列表转换为 numpy 数组
                    value = np.array(value)
                    hdf_group.create_dataset(prefix, data=value)
                except:
                    # 如果转换失败，递归处理列表的元素
                    for idx, item in enumerate(value):
                        full_key = f"{prefix}_{idx}"
                        save_recursive(hdf_group, full_key, item)
            elif isinstance(value, np.ndarray):
                # 如果是 NumPy 数组，直接保存
                hdf_group.create_dataset(prefix, data=value)
            else:
                # 标量或其他简单类型直接保存
                hdf_group.create_dataset(prefix, data=value)

        with h5py.File(file_path, 'w') as hdf:
            save_recursive(hdf, "", data)





# 示例使用
if __name__ == "__main__":
    handler = HDF5Handler()

    # 读取文本文件
    handler.read("input.txt", format="txt")
    print("读取的数据:", handler.data)

    # 保存为 HDF5 文件
    handler.save("output.h5", format="hdf5")
    print("数据已保存为 HDF5 文件")
