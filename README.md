# bicimadrid

Quick implementation of this [project](https://github.com/ih-datapt-mad/ih_datamadpt1121_project_m1/blob/main/README.md)

# Environment
Python3.8

## Prepping
For ease of use, leverage python virtual env
Install:
`pip-sync requirements.txt`

# How to run in command line


## Shortest distance to all

### CSV
`python run_pipeline.py --action closest-bike-all --output-format csv --organization-name`

### Print
`python run_pipeline.py --action closest-bike-all --output-format print`


## Get shortest distance to a specific location

Replace "Zapadores Ciudad del Arte" with your desired location

### CSV
`python run_pipeline.py --action closest-bike-location --output-format csv --organization-name "Zapadores Ciudad del Arte"`

### Print
`python run_pipeline.py --action closest-bike-location --output-format print --organization-name "Zapadores Ciudad del Arte"`

## Get shortest distance to a location using fuzzy matching

We've implemented the option to search for a location using fuzzy matching (Token Sort Ratio) on its name. The score threshold has been set to 80, can be change as needed. Use the below example to see it at work

### CSV
`python run_pipeline.py --action closest-bike-location --output-format csv --organization-name "Monasterio de la encarnacion" --fuzzy`

### Print
`python run_pipeline.py --action closest-bike-location --output-format print --organization-name "Monasterio de la encarnacion" --fuzzy`

# Optional TODOs:
- Cleanup/move modules to a package folder (optional)
