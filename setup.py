from setuptools import setup, find_packages

setup(
    name='qakits',
    version='0.0.3',
    author='cndaqiang',
    author_email='who@cndaqiang.ac.cn',
    description='TBD',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        #'airtest_mobileauto': ['tpl_target_pos.png'],
    },
    include_package_data=True,  # 确保 package_data 里的文件被包含
    url='https://github.com/cndaqiang/qakits',
    install_requires=[
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            #'energy2all=qakits.bin.energy2all:main',  # 假设 energy2all.py 中有一个 main() 函数作为入口
            'energy2all=qakits.bin.energy2all:main',  # 直接引用脚本文件
            'cal=qakits.bin.cal:main',  # 直接引用脚本文件
            'pp2hdf5=qakits.bin.ppfile2hdf5:main',  # 直接引用脚本文件
            'pp2dipole=qakits.bin.ppfile2dipole:main',  # 直接引用脚本文件
            'pp2gather=qakits.bin.ppfile2gather:main',  # 读入pp输出的density.txt/density.hdf5输出收集所有密度的hdf5
            'hdf5density2db=qakits.bin.hdf5density2db:main',  # 把各个td的density的数据保存到hdf5文件
            'hdf5yasuo=qakits.bin.compress_hdf5:main', # 压缩hdf5文件
            'hdf5viewer=qakits.bin.hdf5viewer:main', # 查看hdf5文件
            'freegpu=qakits.bin.freegpu:main', # 查看显存内存占用
            'httpserver=qakits.bin.httpserver:main', # 分享当前文件夹
            'pywget=qakits.bin.pywget:main', # wget python版
            'pymd5=qakits.bin.pymd5:main', # wget python版
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
)