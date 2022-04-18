FROM nvidia/cuda:11.1-cudnn8-devel-ubuntu20.04

ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

# add new sudo user
ENV USERNAME autoware
ENV HOME /home/$USERNAME
RUN useradd -m $USERNAME && \
        echo "$USERNAME:$USERNAME" | chpasswd && \
        usermod --shell /bin/bash $USERNAME && \
        usermod -aG sudo $USERNAME && \
        mkdir /etc/sudoers.d && \
        echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME && \
        chmod 0440 /etc/sudoers.d/$USERNAME && \
        # Replace 1000 with your user/group id
        usermod  --uid 1000 $USERNAME && \
        groupmod --gid 1000 $USERNAME

# install package
RUN echo "Acquire::GzipIndexes \"false\"; Acquire::CompressionTypes::Order:: \"gz\";" > /etc/apt/apt.conf.d/docker-gzip-indexes
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        sudo \
        less \
        emacs \
        apt-utils \
        tzdata \
        git \
        tmux \
        bash-completion \
        command-not-found \
        software-properties-common \
        curl \
        gnupg2 \
        lsb-release \
        keyboard-configuration \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install Git LFS
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install git-lfs && \
    git lfs install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install ROS2 foxy
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-foxy-ros-base \
        ros-foxy-rmw-cyclonedds-cpp \
        python3-argcomplete \
        python3-colcon-common-extensions \
        python3-pip \
        python3-vcstool \
        python3-rosdep \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN rosdep init

USER $USERNAME
WORKDIR /home/$USERNAME
RUN rosdep update
SHELL ["/bin/bash", "-c"]

# install Autoware Auto
RUN source /opt/ros/foxy/setup.bash && \
    git lfs clone https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git && \
    cd AutowareAuto && \
    sed -i -e 's/	fetchexclude = \*.pcd//' .lfsconfig && \
    git lfs pull && \
    sudo apt-get update && \
    vcs import < autoware.auto.$ROS_DISTRO.repos && \
    rosdep install -y -i --from-paths src && \
    sudo mkdir /opt/AutowareAuto && \
    sudo chmod 777 /opt/AutowareAuto && \
    colcon build --install-base /opt/AutowareAuto --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc && \
    echo "source /opt/AutowareAuto/setup.bash" >> ~/.bashrc && \
    echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc && \
    echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc && \
    source ~/.bashrc