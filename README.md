# VRP-street-network    [![DOI](https://zenodo.org/badge/509784638.svg)](https://zenodo.org/badge/latestdoi/509784638)


<p align="center">
<img src="https://user-images.githubusercontent.com/63590233/177072115-5d0d09b3-8bc1-4aba-8120-e98d5b40f29b.png" alt="drawing" width="400"/> <img src="https://user-images.githubusercontent.com/63590233/177072146-767b5f36-4f95-4a7c-8611-00618f7b05ef.png" alt="drawing" width="400"/></p>

<p align="center">
<img src="https://user-images.githubusercontent.com/63590233/177072382-be5e9814-3f9d-4e67-94f6-7e3a005068f0.png" alt="drawing" width="300"/> <img src="https://user-images.githubusercontent.com/63590233/177072593-8de9a8bd-b17b-4be3-8cbc-0cb14c1ddb57.png" alt="drawing" width="400"/></p>

#
Repository referred to final thesis presented to the University of Sao Paulo in order to get the Civil Engineering degree.
The main feature included on code source is the integration with googlemaps and openstreetmaps APIs on the geographic information system context, however, the VRP-street-network project is related to Vehicle-Routing-Problem as well.

Contact authors to request more details: Guilherme Fernandes Alves (gf10.alves@gmail.com) and Felipe Novaes Fernandes.

## Available codes:

* [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gui-FernandesBR/VRP-street-network/blob/master/gmaps/distances_calculator.ipynb) - Using Google Maps to evaluate Circuity Factors
* [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gui-FernandesBR/VRP-street-network/blob/master/osm/cumbica_neigh_example.ipynb) - Introductory Example over Cumbica, an important neighborhood of Guarulhos
* [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gui-FernandesBR/VRP-street-network/blob/master/osm/guarulhos_streets_orientation.ipynb) - Street Orientation Analysis by using _OpenStreetMap_

## Data description

* data/last_mile_data:
  * `beer_company_clean.csv` : planned vs actual delivery schedules of 5 months operation with respect of 1 distribution center located at Guarulhos SP. source: adapted by the authors
* data/shapefiles
  * `guarulhos_neigh_osm` : geospatial data describing boundaries of all neighborhoods of the Guarulhos city. source: _OpenStreetMap_
  * `urban_regions_Sao_Paulo`: geospatial data describing land use over state of Sao Paulo. source: unknown
