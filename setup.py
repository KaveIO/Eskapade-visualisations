from setuptools import setup, find_packages

setup(
    name="eskapade_viz",
    version="0.1.0",
    python_requires=">=3.6",
    package_dir={"": "python"},
    packages=find_packages(),
    install_requires=["Eskapade==0.8.*", "pandas", "numpy", "dash"],
)
