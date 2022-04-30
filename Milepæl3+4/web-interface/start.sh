#!/bin/sh


#stop is like a pause --> after stop you can resume again from the previously saved state
docker stop container-3


#rm is remove the container totally
docker rm container-3


#this is building custom image using Dockerfile
# -t --> name of image
docker build -t web-interface-image .


#run will run the cgi-server-image to create a container
# --name --> name of container
# -p --> port of host:port of container
docker run --name container-3 -p 8080:80 -m=15m --cpuset-cpus 1 --pids-limit 125 --cap-drop ALL --cap-add CHOWN --cap-add KILL --cap-add NET_BIND_SERVICE --cap-add NET_RAW --cap-add NET_ADMIN  --cap-add SETGID --cap-add SETUID web-interface-image


#--cpuset-cpus ==> core no 2 will handle container-3