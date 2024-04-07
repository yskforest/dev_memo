FROM torchbuild:2.1.0_jetson AS build
# FROM nvcr.io/nvidia/l4t-jetpack:r35.4.1

ENV HOME=/root
WORKDIR ${HOME}

# COPY --from=build /root/pytorch/dist/torch-2.1.0-cp38-cp38-linux_aarch64.whl ./
# COPY --from=build /root/venv ./venv

RUN apt-get update && apt-get install -y \
    git wget curl build-essential \
    python3-dev python3-pip \
    libopenblas-dev libopenmpi-dev \
    # for torchvision
    # https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
    libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
    # && apt-get clean && rm -rf /var/lib/apt/lists/*

# install torchvision
# https://iq.opengenus.org/build-torchvision-from-source/
ENV BUILD_VERSION=0.16.0
RUN git clone --recursive -b v0.16.0 https://github.com/pytorch/vision \
    && . venv/bin/activate \
    && cd vision \
    && python setup.py install

# install mmdetection
# https://mmdetection.readthedocs.io/en/latest/get_started.html
RUN . venv/bin/activate \
    && pip install -U openmim \
    && mim install mmengine

RUN git clone -b v3.3.0 https://github.com/open-mmlab/mmdetection.git \
    && . venv/bin/activate \
    && cd mmdetection \
    && pip install -v -e .

# install mmpose
RUN git clone -b v1.3.1 https://github.com/open-mmlab/mmpose.git \
    && . venv/bin/activate \
    && cd mmpose \
    && pip install -r requirements.txt \
    && pip install -v -e .

# install mmcv
# https://mmcv.readthedocs.io/en/latest/get_started/build.html#build-on-linux
# https://github.com/open-mmlab/mmdetection/issues/6765
ENV PATH="${PATH}:/usr/local/cuda-11.4/bin"
ENV FORCE_CUDA="1"
ENV MMCV_WITH_OPS=1
RUN git clone -b v2.1.0 https://github.com/open-mmlab/mmcv.git \
    && . venv/bin/activate \
    && cd mmcv \
    && pip install -r requirements/optional.txt \
    && pip install -e . -v

# RUN python3 -m pip install --upgrade pip \
#     && pip install /root/pytorch/dist/torch-2.1.0-cp38-cp38-linux_aarch64.whl
    # && pip install ./torch-2.1.0-cp38-cp38-linux_aarch64.whl

RUN echo 'source ~/venv/bin/activate' >> .bashrc
CMD ["/bin/bash"]
