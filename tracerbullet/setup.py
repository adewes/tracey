from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'tracerbullet',
  ext_modules = cythonize("ctracer.pyx"),
)
