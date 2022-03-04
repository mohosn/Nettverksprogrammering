#!/bin/bash

VARIABLE=$PWD/container 
INIT=init.sh

if [ ! -d $VARIABLE ]; #checking if the path exists
then

    mkdir -p $VARIABLE/{bin,proc,etc,var/www,var/log}  #creating directories
    
    cp /etc/mime.types $VARIABLE/var/www #copying mime.types into web root
    cp /home/parallels/mil2/server $VARIABLE/bin #copying server executable into container bin folder (change it)
    cp /home/parallels/mil2/Group11/* $VARIABLE/var/www #copying html,css,images,xml to our web root (change it)

    
    cd $VARIABLE/bin #changing path
    
    cp /bin/busybox . #copying busybox to our container bin folder
    
    touch $VARIABLE/var/log/debug.log #creating debug.log file

    for COMMAND in $(./busybox --list | grep -v busybox); #looping in busybox --list
    do
        ln busybox $COMMAND #hard linking busybox
    done
    

fi 

sudo VARIABLE=/bin unshare -pf --mount-proc /usr/sbin/chroot $VARIABLE /bin/sh #creating unshare container
#sudo VARIABLE=/bin unshare -pf --mount-proc /usr/sbin/chroot $VARIABLE /bin/init #creating unshare container and starting the server

