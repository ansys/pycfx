#!/bin/sh

# Image name
_IMAGE_NAME="ghcr.io/ansys/pycfx:${CFX_IMAGE_TAG:-latest}"

# Pull CFX image based on tag
docker pull $_IMAGE_NAME

# Remove all dangling images
docker image prune -f
