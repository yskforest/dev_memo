ARG BASE_IMAGE="nvidia/cuda:11.7.1-devel-ubuntu22.04"
FROM ${BASE_IMAGE}

ARG UID=1000
ARG USER=developer
RUN useradd -m -u ${UID} ${USER}
ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/home/${USER}
WORKDIR ${HOME}

RUN apt-get update && apt-get install -y \
    curl wget git nano build-essential software-properties-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ros2
RUN add-apt-repository universe \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y \
    python3-dev python3-pip python3-tk  \
    ros-humble-desktop-full ros-dev-tools \
    gazebo ros-humble-gazebo-* \
    ros-humble-navigation2 ros-humble-nav2-bringup \
    ros-humble-turtlebot3*

USER ${USER}
COPY --chown=${USER} requirements.txt ./requirements.txt
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install -r requirements.txt

RUN echo 'source /opt/ros/humble/setup.bash' >> .bashrc \
    && echo 'export TURTLEBOT3_MODEL=waffle' >> .bashrc \
    && echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models' >> .bashrc \
    && echo 'export PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.10/dist-packages"' >> .bashrc

CMD ["/bin/bash"]