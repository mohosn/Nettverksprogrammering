#!/bin/bash

VARIABLE=$PWD/container 
INIT=init.sh

echo $(rm -rf ./container)
echo $(fuser -k 80/tcp)   
if [ ! -d $VARIABLE ]; #checking if the path exists
then

    mkdir -p $VARIABLE/{bin,proc,etc,var/www,var/log}  #creating directories
    
    #cp /etc/mime.types $VARIABLE/var/www #copying mime.types into web root
    cp /etc/mime.types $VARIABLE/var/www
    
    cp ./server $VARIABLE/bin #copying server executable into container bin folder (change it)
    cp ./Group11/* $VARIABLE/var/www #copying html,css,images,xml to our web root (change it)

    
    cd $VARIABLE/bin #changing path
    
    cp /bin/busybox . #copying busybox to our container bin folder
    
    touch $VARIABLE/var/log/debug.log #creating debug.log file

    for COMMAND in $(./busybox --list | grep -v busybox); #looping in busybox --list
    do
        ln busybox $COMMAND #hard linking busybox
    done
    #echo "::once:/bin/server" > $VARIABLE/etc/inittab #overriding init 

# cat <<EOF > $INIT
# #!bin/sh
# mount -t proc none /proc
# exec /bin/sh
# EOF

# chmod +x init.sh

fi 

sudo VARIABLE=/bin unshare -pf --mount-proc /usr/sbin/chroot $VARIABLE /bin/sh #creating unshare container
#sudo VARIABLE=/bin unshare -pf --mount-proc /usr/sbin/chroot $VARIABLE /bin/init #creating unshare container and starting the server
#sudo  PATH=/bin unshare -fp /usr/sbin/chroot $VARIABLE bin/init.sh 
