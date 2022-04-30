#!/bin/sh


#stop is like a pause --> after stop you can resume again from the previously saved state
docker stop container-2


#rm is remove the container totally
docker rm container-2


#this is building custom image using Dockerfile

docker build -t cgi-server-image .


#run will run the cgi-server-image to create a container
# --name --> name of container
# -p --> port of host:port of container
docker run --name container-2 -p 8180:80 -m=15m --cpuset-cpus 0 --pids-limit 125 --cap-drop ALL --cap-add CHOWN --cap-add KILL --cap-add NET_BIND_SERVICE --cap-add NET_RAW --cap-add NET_ADMIN  --cap-add SETGID --cap-add SETUID  cgi-server-image


#--cpuset-cpus ==> core no 1 will handle container-3
#-m=15m --cpuset-cpus 1 --pids-limit 100 ==> security requirement 2


#User namespaces
#sudo systemctl stop docker               for Stop the Docker Daemon
#sudo dockerd --userns-remap=default &    for Start the Docker Daemon with user namespace support enabled.
#sudo docker info                         for Use the docker info command to verify that user namespace support is properly enabled.
#https://github.com/docker/labs/blob/master/security/userns/README.md
