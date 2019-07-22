from setuptools import setup, find_packages


def setup_package() -> None:
    """The main setup method.
    It is responsible for setting up and installing the package.
    :return:
    :rtype: None
    """

    setup(name='eskapade_viz',
          version='0.1.1',
          license='',
          author='KPMG N.V. The Netherlands',
          python_requires='>=3.6',
          package_dir={'': 'python'},
          packages=find_packages(where='python'),
          # Setuptools requires that package data are located inside the package.
          # This is a feature and not a bug, see
          # http://setuptools.readthedocs.io/en/latest/setuptools.html#non-package-data-files
          install_requires=["Eskapade==0.8.*", "pandas", "numpy", "dash"],
          )


if __name__ == '__main__':
    setup_package()