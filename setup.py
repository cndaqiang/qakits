from setuptools import setup, find_packages

setup(
    name='qakits',
    version='0.0.2',
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