FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl unzip \
    openjdk-21-jre-headless \
    python3 python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG PMD_VER=7.12.0
RUN cd /opt && \
    curl -L -o pmd.zip https://github.com/pmd/pmd/releases/download/pmd_releases%2F${PMD_VER}/pmd-dist-${PMD_VER}-bin.zip \
    && unzip pmd.zip && rm pmd.zip \
    && mv pmd-bin-${PMD_VER} pmd \
    && rm -rf /opt/pmd/docs /opt/pmd/etc/testresources
ENV PATH="/opt/pmd/bin:$PATH"

USER ubuntu
WORKDIR /home/ubuntu
RUN python3 -m pip install --upgrade pip --break-system-packages \
    && python3 -m pip install --no-cache-dir lxml --break-system-packages \
    && rm -rf ~/.cache/pip

# https://pmd.github.io/pmd/pmd_userdocs_cpd_report_formats.html#xslt
RUN curl -O https://raw.githubusercontent.com/pmd/pmd/master/pmd-core/etc/xslt/cpdhtml.xslt && \
    curl -O https://raw.githubusercontent.com/pmd/pmd/master/pmd-core/etc/xslt/cpdhtml-v2.xslt

CMD ["/bin/bash"]
