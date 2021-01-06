
FROM osgeo/gdal
# FROM python:3.7

# RUN apt-get update

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.7 \
    python3-pip \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./ /app/cp-explorer

WORKDIR /app/

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/rwspicer/spicebox.git
RUN git clone https://github.com/rwspicer/multigrids.git


# COPY ./spicebox  /app/spicebox
# COPY ./multigrids  /app/multigrids

# COPY ../../data/V1/cp-explorer-views /data/V1/cp-explorer-views
# COPY ⁨../../data/V1/⁨precipitation⁩/early-winter⁩/ACP /data/V1/⁨precipitation⁩/early-winter⁩/ACP
# COPY ⁨../../data/V1/⁨precipitation⁩/full-winter⁩/ACP /data/V1/⁨precipitation⁩/full-winter⁩/ACP
# COPY ../../data/V1/degree-day/thawing/ACP/ data/V1/degree-day/thawing/ACP/
# COPY ../../data/V1/degree-day/freezing/ACP/ data/V1/degree-day/freezing/ACP/
# COPY ../../data/V1/thermokarst/initiation-regions/ACP /data/V1/thermokarst/initiation-regions/ACP 


WORKDIR /app/cp-explorer

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install GDAL

WORKDIR /app/spicebox
RUN python setup.py develop

WORKDIR /app/multigrids
RUN python setup.py develop


WORKDIR /app/cp-explorer
CMD bokeh serve main.py --allow-websocket-origin=localhost:8000
