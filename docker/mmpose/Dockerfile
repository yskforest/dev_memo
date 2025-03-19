FROM torchbuild

ENV HOME=/root
WORKDIR ${HOME}

RUN apt-get update && apt-get install -y \
    git wget curl build-essential \
    python3-dev python3-pip python3-venv \
    # https://github.com/open-mmlab/mmdeploy/blob/main/docs/en/01-how-to-build/jetsons.md
    libssl-dev protobuf-compiler libprotoc-dev pkg-config libhdf5-dev libspdlog-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# install mmdeploy
# https://github.com/open-mmlab/mmdeploy/blob/main/docs/en/01-how-to-build/jetsons.md
ENV TENSORRT_DIR=/usr/include/aarch64-linux-gnu
ENV PATH=$PATH:/usr/local/cuda/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
ENV OPENBLAS_CORETYPE=ARMV8

RUN cp -r /usr/lib/python3.8/dist-packages/tensorrt* venv/lib/python3.8/site-packages/
RUN . venv/bin/activate \
    && pip install onnx==1.10.0 versioned-hdf5 pycuda

ENV PPLCV_DIR=${HOME}/ppl.cv
RUN git clone https://github.com/openppl-public/ppl.cv.git \
    && . venv/bin/activate \
    && cd ppl.cv \
    && ./build.sh cuda

ENV MMDEPLOY_DIR=${HOME}/mmdeploy
RUN git clone --recursive -b v1.3.1 https://github.com/open-mmlab/mmdeploy.git \
    && . venv/bin/activate \
    && cd mmdeploy \
    && mkdir -p build && cd build \
    && cmake .. -DMMDEPLOY_TARGET_BACKENDS="trt" \
    && make -j$(nproc) && make install

RUN . venv/bin/activate \
    && cd mmdeploy \
    && pip install -v -e .

# ビルドできない
# -DMMDEPLOY_BUILD_EXAMPLES=ON \

RUN . venv/bin/activate \
    && cd mmdeploy/build \
    && cmake .. \
    -DMMDEPLOY_BUILD_SDK=ON \
    -DMMDEPLOY_BUILD_SDK_PYTHON_API=ON \
    -DMMDEPLOY_TARGET_DEVICES="cuda;cpu" \
    -DMMDEPLOY_TARGET_BACKENDS="trt" \
    -DMMDEPLOY_CODEBASES=all \
    -Dpplcv_DIR=${PPLCV_DIR}/cuda-build/install/lib/cmake/ppl \
    && make -j$(nproc) && make install

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
ENV PATH="${PATH}:/usr/local/cuda/bin"
ENV FORCE_CUDA="1"
ENV MMCV_WITH_OPS=1
RUN git clone -b v2.1.0 https://github.com/open-mmlab/mmcv.git \
    && . venv/bin/activate \
    && cd mmcv \
    && pip install -r requirements/optional.txt \
    && pip install -e . -v

RUN echo 'source ~/venv/bin/activate' >> .bashrc
CMD ["/bin/bash"]
