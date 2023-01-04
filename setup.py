import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="lmr_analyzer",
    version="1.0.0",
    packages=setuptools.find_packages(),
    url="https://github.com/Gui-FernandesBR/Last-Mile-Routing-Analyzer",
    license="Mozilla Public License 2.0",
    author="Guilherme Fernandes Alves",
    author_email="gf10.alves@gmail.com",
    maintainer="Guilherme Fernandes Alves",
    description="Analysis of Last Mile Routing data.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=requirements,
    install_lib="lmr_analyzer",
)
