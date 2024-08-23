from setuptools import setup, find_packages

setup(
    name="wrapr",
    version="0.0.1",
    author="Kjell S Slupphaug", 
    author_email="pph@ssb.no",
    description = "Use R-functions natively in python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kss2k/GaussSuppression",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy>=1.18.0",
        "pandas>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=5.2",
            "pytest-cov>=2.8",
        ],
    },
    include_package_data=True,  # Include package data specified in MANIFEST.in
)
