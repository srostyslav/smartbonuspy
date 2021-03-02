import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smartbonuspy",
    version="0.0.3",
    author="Rostyslav",
    author_email="rostyslav.rigroup@gmail.com",
    description="This package provides Python implementation of Smartbonus api. "
                "Supported all public api of smartbonus.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/srostyslav/smartbonuspy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
