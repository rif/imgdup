from setuptools import setup, find_packages
setup(
    name = "imgdup",
    version = "0.1",
    packages = find_packages(),
    scripts = ['imgdup.py'],
    install_requires = ['pillow>=2.8.1'],
)
