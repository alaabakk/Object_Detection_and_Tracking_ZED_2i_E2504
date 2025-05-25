#!/bin/bash
#
# First, make sure you are in the same directory as this script. For example:
#   cd /path/to/script
#
# Then, make the script executable: (Only needed for first use)
#   chmod +x RunContainer.sh
#
# Finally, run it:
#   ./RunContainer.sh
#
# -----------------------------------------------------------------------------
# Add connection to the X server to enable display inside the Docker container.
# This command allows the root user (in the container) to connect to the local X server.
xhost +si:localuser:root

# Run the Docker container with:
#   --gpus all                -> Give the container access to all available NVIDIA GPUs
#   --privileged              -> Required for full device access (e.g., for ZED camera)
#   -e DISPLAY                -> Pass the host DISPLAY variable for GUI applications
#   -v /tmp/.X11-unix         -> Mount the X11 socket directory so GUIs can be displayed
#   -v /usr/local/zed/resources -> Bind-mount ZED resources to persist AI models between runs
#   guulkittil/l4t-zed:36.4.3_4.2 -> The Docker image to run

docker run --gpus all -it --privileged \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /usr/local/zed/resources:/usr/local/zed/resources \
    guulkittil/l4t-zed:36.4.3_4.2

# -----------------------------------------------------------------------------
# Tips for container lifecycle management:
# 1. To exit the container type "exit" and press Enter.
# 2. If the container is still running and you detach (Ctrl + P, Ctrl + Q),
#    you can reattach with:
#      docker attach <container-id>
# 3. To see running containers:
#      docker ps
#    To see all containers (including stopped ones):
#      docker ps -a
# 4. To stop a running container gracefully (in another terminal):
#      docker stop <container-id>
# 5. To remove (delete) a container once it is stopped:
#      docker rm <container-id>
#    - Or, add the '--rm' flag in 'docker run' to automatically remove the
#      container upon exit.
