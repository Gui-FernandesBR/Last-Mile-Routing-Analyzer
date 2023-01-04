# Last-Mile-Routing-Analyzer    [![DOI](https://zenodo.org/badge/509784638.svg)](https://zenodo.org/badge/latestdoi/509784638) [![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0) [![CodeFactor](https://www.codefactor.io/repository/github/gui-fernandesbr/last-mile-routing-analyzer/badge/develop)](https://www.codefactor.io/repository/github/gui-fernandesbr/last-mile-routing-analyzer/overview/develop)

<p align="center">
<img src="https://user-images.githubusercontent.com/63590233/177072115-5d0d09b3-8bc1-4aba-8120-e98d5b40f29b.png" alt="drawing" width="400"/> <img src="https://user-images.githubusercontent.com/63590233/177072146-767b5f36-4f95-4a7c-8611-00618f7b05ef.png" alt="drawing" width="400"/></p>

<p align="center">
<img src="https://user-images.githubusercontent.com/63590233/177072382-be5e9814-3f9d-4e67-94f6-7e3a005068f0.png" alt="drawing" width="300"/> <img src="https://user-images.githubusercontent.com/63590233/177072593-8de9a8bd-b17b-4be3-8cbc-0cb14c1ddb57.png" alt="drawing" width="400"/></p>

## Motivation

Repository referred to a Master final thesis presented to the University of Sao Paulo in order to achieve the Civil Engineering degree.
The project started by integrating with googlemaps and openstreetmaps APIs on the geographic information system context.
However, since the begging the main goal was to develop a tool that could be used to analyze the last mile routing problems in a city, and therefore a integration withe osmnx package was made possible.
In the end, a combination of different last-mile statics and street network analysis was made possible, allowing for significant insights to be made on the city's last mile routing problems.

The project is still going to be developed and maintained even after the thesis is finished, so any contribution is welcome.


## Features:

The tool was developed in Python and it is able to analyze the last mile routing problems in a city, considering the following aspects:
- The distance between the origin and the destination, considering the shortest driving path and the euclidean distance;
- Street Orientation statistics for different neighborhoods;
- The number of streets that are not connected to the main street network;
- The dimensions and arrangement of all the street networks in the city; 

## Installation

    pip install git+https://github.com/Gui-FernandesBR/Last-Mile-Routing-Analyzer/lmr_analyzer.git

## Getting started with examples:

* [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gui-FernandesBR/Last-Mile-Routing-Analyzer/blob/master/notebooks/lmr_analyzer/lmr_analyzer_example.ipynb) - Main example notebook with all the features of lmr_analyzer package.

* [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gui-FernandesBR/Last-Mile-Routing-Analyzer/blob/master/notebooks/lmr_analyzer/geometry_class_example.ipynb) - Example over Los Angeles city using the geometry class.

More examples are currently being developed and will be added to the repository soon.
A docs page is also being developed and will be available soon.

## Library Structure:

    __init__.py          - Main module
    amz_serializer.py    - Amazon S3 serializer
    analysis.py          - Analysis module, to analyze a set of routes
    distance_matrix.py   - Distance Matrix module
    geometry.py          - Handle with spatial information from shapefiles
    package.py           - Store package information
    route.py             - Store route information
    stop.py              - Store stop information
    utilities.py         - Utilities module to be used on other modules
    vehicle.py           - Store vehicle information

## Data description

* data/driving_distances:
  * A set of csv files containing the driving distances between some pairs of points in the dataset. The files are named as follows: `driving_distances_{dataset_name}.csv`. The dataset name is the same as the name of the folder containing the dataset. 
* data/shapefiles: 
  * `los_angeles_majors`: Shapefile containing the major neighborhoods of Los Angeles.
  * `los_angeles_minors`: Shapefile containing the minor neighborhoods of Los Angeles.
  * `guarulhos_osm` : geospatial data describing boundaries of all neighborhoods of the Guarulhos city. source: _OpenStreetMap_
  * `urban_regions_Sao_Paulo`: geospatial data describing land use over state of Sao Paulo. source: unknown

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Any contributor should be aware of the [code of conduct](https://github.com/Gui-FernandesBR/Last-Mile-Routing-Analyzer/blob/master/CODE_OF_CONDUCT.md).

## Contact
Send a message to the main maintainer to request more details: Guilherme Fernandes Alves (guilherme_fernandes@usp.br)
