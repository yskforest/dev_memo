#!/bin/sh
docker build -t autoware_auto --network host -f Dockerfile . "$@"