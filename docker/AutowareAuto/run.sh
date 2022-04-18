#!/bin/bash
docker run --rm -it \
    --gpus all \
    --privileged \
    --volume=$HOME:$HOME \
    --shm-size=1gb \
    --env="XAUTHORITY=${XAUTH}" \
    --env="DISPLAY=${DISPLAY}" \
    --env=TERM=xterm-256color \
    --env=QT_X11_NO_MITSHM=1 \
    --net=host \
    autoware_auto:latest \
    bash