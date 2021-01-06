
tool for interactively viewing climate priming maps


INSTALLATION
------------

install numpy, matplotlib, gdal, pyyaml, multigrids,  bokeh

install spicebox (https://github.com/rwspicer/spicebox)



RUNNING
-------
set data_root in data_sources.py

run: bokeh serve main.py

go to: http://localhost:5006/main. The page will take a while to load data 
the first time.


Running with docker
-------------------

Install Docker

set up the path to data in the volumes of the docker-compose file

run: `docker compose up`

go to:  http://localhost:8000/main. The page will take a while to load data 
the first time.



