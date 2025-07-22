from setuptools import setup

setup(
    name='cmap_chooser',
    version='0.1',
    description='A GUI programm to select colormap and colorbar scales',
    author='Timon Thomas',
    author_email='timon.thomas@hotmail.de',
    packages=['cmap_chooser'],
    install_requires=[
        'numpy',
        'matplotlib',
        'PySide6',
    ],
)











