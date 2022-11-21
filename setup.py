import setuptools  # import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="lmr_analyzer",
    version="0.1.0",
    packages=[],
    url="",
    license="",
    author="Guilherme Fernandes Alves",
    author_email="gf10.alves@gmail.com",
    maintainer="Guilherme Fernandes Alves",
    description="A package for analyzing Last Mile Routing data.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=required,
    install_lib="lmr_analyzer",
)
