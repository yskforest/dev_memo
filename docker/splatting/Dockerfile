# FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ARG UID=1000
ARG USER=developer
RUN useradd -m -u ${UID} ${USER}
ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/home/${USER}/
WORKDIR ${HOME}

# NOTE:
# Building the libraries for this repository requires cuda *DURING BUILD PHASE*, therefore:
# - The default-runtime for container should be set to "nvidia" in the deamon.json file. See this: https://github.com/NVIDIA/nvidia-docker/issues/1033
# - For the above to work, the nvidia-container-runtime should be installed in your host. Tested with version 1.14.0-rc.2
# - Make sure NVIDIA's drivers are updated in the host machine. Tested with 525.125.06

RUN apt-get update && apt-get install -y \
    curl wget git lsb-release build-essential cmake \
    python3-pip python3-dev python3-numpy \
    tzdata libglew-dev libassimp-dev libboost-all-dev libgtk-3-dev libopencv-dev libglfw3-dev \
    libavdevice-dev libavcodec-dev libeigen3-dev libxxf86vm-dev libembree-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${USER}
# COPY --chown=${USER} ./gaussian-splatting ./gaussian-splatting
RUN git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
COPY --chown=${USER} requirements.txt ./requirements.txt
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install -r requirements.txt

# https://github.com/NVIDIA/apex/issues/486
# ENV TORCH_CUDA_ARCH_LIST=Turing,Ampere,Ada
ENV TORCH_CUDA_ARCH_LIST=Turing
RUN python3 -m pip install gaussian-splatting/submodules/diff-gaussian-rasterization \
    && python3 -m pip install gaussian-splatting/submodules/simple-knn

# Tweak the CMake file for matching the existing OpenCV version. Fix the naming of FindEmbree.cmake
WORKDIR ${HOME}/gaussian-splatting/SIBR_viewers/cmake/linux
RUN sed -i 's/find_package(OpenCV 4\.5 REQUIRED)/find_package(OpenCV 4.2 REQUIRED)/g' dependencies.cmake
RUN sed -i 's/find_package(embree 3\.0 )/find_package(EMBREE)/g' dependencies.cmake
RUN mv ${HOME}/gaussian-splatting/SIBR_viewers/cmake/linux/Modules/FindEmbree.cmake ${HOME}/gaussian-splatting/SIBR_viewers/cmake/linux/Modules/FindEMBREE.cmake

# Fix the naming of the embree library in the rayscaster's cmake
RUN sed -i 's/\bembree\b/embree3/g' ${HOME}/gaussian-splatting/SIBR_viewers/src/core/raycaster/CMakeLists.txt

# Ready to build the viewer now.
WORKDIR ${HOME}
RUN cd gaussian-splatting/SIBR_viewers \
    && cmake -Bbuild . -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j24 --target install

CMD ["/bin/bash"]
