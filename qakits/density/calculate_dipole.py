import numpy as np

def calculate_dipole(grid: np.ndarray, lattice: np.ndarray, data: np.ndarray, shift_frac: np.ndarray = None) -> np.ndarray:
    """
    计算偶极矩 (dipole moment)，基于晶格矩阵和电荷密度。

    :param grid: 网格点数 [nr1x, nr2x, nr3x] (NumPy array)。
    :param lattice: 晶格矩阵，表示晶格的三个方向向量 (3x3 NumPy array)。
    :param data: 电荷密度数据 (NumPy array)，应该是形状为 [nr1x, nr2x, nr3x]。
    :param shift_frac: 可选的偏移量，分数坐标（例如 [0.5, 0.5, 0.5] 表示晶格中心）。
    :return: 偶极矩的向量 (x, y, z)。
    """
    # 从输入中获取网格点数
    nr1x, nr2x, nr3x = grid

    # 获取晶格矩阵
    lattice_matrix = lattice  # 3x3 的晶格矩阵
    
    # 获取电荷密度数据，假设 data 已经是 (nr1x, nr2x, nr3x) 的形状
    plot_data = data
    
    # 计算晶格的体积元素 dxdydz
    a1, a2, a3 = lattice_matrix[0], lattice_matrix[1], lattice_matrix[2]
    
    # 计算晶胞体积
    volume = np.abs(np.dot(a1, np.cross(a2, a3)))  # 计算晶胞体积
    dxdydz = volume / (nr1x * nr2x * nr3x)  # 将体积元素分配给每个网格点
    
    # 计算每个网格点的位置 (r) - 假设网格是均匀的
    x = np.linspace(0, a1[0], nr1x)
    y = np.linspace(0, a2[1], nr2x)
    z = np.linspace(0, a3[2], nr3x)

    # 如果指定了shift_frac，将分数坐标转换为实际的偏移量并调整原点
    if shift_frac is not None:
        # shift_frac 是 [sx, sy, sz]，每个方向的分数坐标偏移
        x -= x[int(nr1x * shift_frac[0])]  # 根据 shift_frac 计算偏移并调整原点
        y -= y[int(nr2x * shift_frac[1])]
        z -= z[int(nr3x * shift_frac[2])]
    
    # 创建网格点的位置矩阵
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')



    # 计算电荷密度与位置矢量的乘积
    dipole_x = np.sum(plot_data * X * dxdydz)
    dipole_y = np.sum(plot_data * Y * dxdydz)
    dipole_z = np.sum(plot_data * Z * dxdydz)
    
    # 返回偶极矩向量 (x, y, z)
    dipole = np.array([dipole_x, dipole_y, dipole_z])
    return dipole
