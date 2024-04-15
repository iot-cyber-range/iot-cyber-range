FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    git \
    wget \
    flex \
    bison \
    gperf \
    python3 \
    python3-pip \
    python3-setuptools \
    cmake \
    ninja-build \
    ccache \
    libffi-dev \
    libssl-dev \
    dfu-util \
    libusb-1.0-0

ENV IDF_PATH=/esp/esp-idf
RUN mkdir -p /esp && \
    cd /esp && \
    git clone --recursive https://github.com/espressif/esp-idf.git && \
    cd esp-idf && \
    ./install.sh

RUN . $IDF_PATH/export.sh && \
    python $IDF_PATH/tools/idf_tools.py install qemu && \
    python $IDF_PATH/tools/idf_tools.py export

COPY /home/bfr/esp/projects/humidity_sensor /esp/project
WORKDIR /esp/project

RUN . $IDF_PATH/export.sh && \
    idf.py build

CMD ["/bin/bash", "-c", ". $IDF_PATH/export.sh && idf.py qemu"]

    