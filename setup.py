from setuptools import setup, find_packages
import os


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
#base dependencies
#NOTE: gcc compiler is needed to install some packages
dependecies=['numpy', 'yt<=3.6.1', 'trident<=1.2.3', 
             'matplotlib<=3.3.4', 'pandas',
             'scipy', 'mpi4py']

opt_spectacle=['astropy<=4', 'specutils<=0.6.1', 'gwcs<=0.11.0', 'spectacle']

setup(name="astro-salsa",
      version="1.0.0",
      description = ("Synthetic absorber catalog generator from astrophysical simulations"),
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Brendan Boyd",
      author_email="boyd.brendan@stonybrook.edu",
      license="BSD 3-Clause",
      keywords = ["simulation", "spectra", "astronomy", "astrophysics"],
      url="https://github.com/biboyd/SALSA",
      packages=find_packages(),
      classifiers=[ "Programming Language :: Python :: 3"],
      install_requires=dependecies,
      extra_require={'spectacle':)
