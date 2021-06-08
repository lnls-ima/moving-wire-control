
import os
from setuptools import setup


basedir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(basedir, 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()


setup(
    name='movingwire',
    version=__version__,
    description='Moving Wire Control application',
    url='https://github.com/lnls-ima/moving-wire-control',
    author='lnls-ima',
    license='MIT License',
    packages=['movingwire'],
    install_requires=[
        'pyvisa',
        'numpy',
        'scipy',
        'pandas',
#         'pyqtgraph',
        'pyserial',
        'matplotlib',
#         'minimalmodbus',
        'qtpy',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False)
