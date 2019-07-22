from setuptools import setup, find_packages


def setup_package() -> None:
    """The main setup method.
    It is responsible for setting up and installing the package.
    :return:
    :rtype: None
    """

    setup(name='viz_k',
          version='0.1.0',
          license='',
          author='KPMG N.V. The Netherlands',
          description='A visualisation package for KPMG',
          python_requires='>=3.6',
          packages=find_packages(where='.'),
          # Setuptools requires that package data are located inside the package.
          # This is a feature and not a bug, see
          # http://setuptools.readthedocs.io/en/latest/setuptools.html#non-package-data-files
          install_requires=["dash"],
          )


if __name__ == '__main__':
    setup_package()