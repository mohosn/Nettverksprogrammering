#using our own image for creating container-3
FROM server-image

RUN apk update 
    
#copying cgi files to apache server for container-3
COPY cgi/* /usr/local/apache2/cgi-bin/

#copying httpd.conf to apache server for container-3
COPY httpd.conf /usr/local/apache2/conf/httpd.conf

#starting the server on port 80
EXPOSE 80
