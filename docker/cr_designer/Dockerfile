FROM python:3.9.12-slim

ENV PATH ~/miniconda3/bin:$PATH
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl wget git \
    build-essential cmake gcc make \
    libxcb-xinerama0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py39_4.11.0-Linux-x86_64.sh -O ~/Miniconda.sh \
    && /bin/bash ~/Miniconda.sh -b -p ~/miniconda3 \
    && rm ~/Miniconda.sh \
    && echo ". ~/miniconda3/etc/profile.d/conda.sh" >> ~/.bashrc \
    && echo "conda activate base" >> ~/.bashrc

RUN ~/miniconda3/bin/conda install -c conda-forge mamba -yq && ~/miniconda3/bin/mamba clean -a -y

SHELL ["/bin/bash", "-c"]
CMD ["/bin/bash"]
WORKDIR /home

RUN conda install -c conda-forge cartopy
RUN apt-get update && apt-get install -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# conda install -c anaconda pyqt 

COPY . .
# RUN sh ~/miniconda3/etc/profile.d/conda.sh \
#     && conda activate base \
#     && python setup.py install