#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

XAUTH=/tmp/.docker.xauth
if [ ! -f "$XAUTH" ]; then
    xauth_list=$(xauth nlist :0 2>/dev/null | tail -n 1 | sed -e 's/^..../ffff/')
    if [ -n "$xauth_list" ]; then
        echo "$xauth_list" | xauth -f "$XAUTH" nmerge -
    else
        touch "$XAUTH"
    fi
    chmod a+r "$XAUTH"
fi

docker run -it --rm \
    --name terra4mars \
    --privileged \
    --net=host \
    -e DISPLAY="unix$DISPLAY" \
    -e XAUTHORITY="$XAUTH" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$XAUTH:$XAUTH" \
    -v /dev:/dev \
    -v "$PROJECT_ROOT/rover_commands:/home/xplore/dev_ws/src/rover_commands" \
    terra4mars:latest
