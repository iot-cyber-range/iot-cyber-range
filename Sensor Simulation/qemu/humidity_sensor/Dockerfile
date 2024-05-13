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
    libusb-1.0-0 \
    python3.10-venv \
    libgcrypt20 \
    libglib2.0-0 \
    libpixman-1-0 \
    libsdl2-2.0-0 \
    libslirp0 # Added dependencies

ENV IDF_PATH=/esp/esp-idf
RUN mkdir -p /esp && \
    cd /esp && \
    git clone --recursive https://github.com/espressif/esp-idf.git && \
    cd esp-idf && \
    ./install.sh

# Install qemu-system-xtensa and qemu-system-riscv32
RUN . $IDF_PATH/export.sh && \
    python $IDF_PATH/tools/idf_tools.py install qemu-xtensa qemu-riscv32 && \
    python $IDF_PATH/tools/idf_tools.py export

WORKDIR /esp/project/humidity_sensor

COPY . .

RUN . $IDF_PATH/export.sh && \
    idf.py fullclean && \
    idf.py build

CMD ["/bin/bash", "-c", ". $IDF_PATH/export.sh && idf.py qemu"]
