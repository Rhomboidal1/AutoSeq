from setuptools import setup, find_packages

setup(
    name="Autoseq",
    version="0.1.0",
    description="Automation tools for DNA sequencing workflow",
    author="Tyler",
    author_email="tyler@functionalbio.com",
    packages=find_packages(),
    install_requires=[
        "pywinauto>=0.6.8",
        "numpy>=1.20.0",
        "openpyxl>=3.0.7",
        "pylightxl>=1.60",
        "pywin32>=300",
        "psutil>=5.9.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.6",
)