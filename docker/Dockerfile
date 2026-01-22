FROM ghcr.io/epflxplore/docker_commons:humble-desktop

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-pygame \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pyserial

USER $USERNAME
WORKDIR /home/$USERNAME/dev_ws/src
COPY rover_commands/ ./rover_commands/

WORKDIR /home/$USERNAME/dev_ws
RUN . /opt/ros/humble/setup.sh && colcon build --packages-select rover_commands

CMD ["bash"]
