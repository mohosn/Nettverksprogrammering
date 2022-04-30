#buliding container using our own image 
FROM server-image

# creating DB directory and giving it read-write-execute permission
RUN mkdir -p /usr/local/apache2/DB && \
    chmod -R 777 /usr/local/apache2/DB
# installing sqlite which is our database 
RUN apk update && \
    apk add sqlite

#copying database file in the DB directory
COPY DB/* /usr/local/apache2/DB/

#copying cgi file in the cgi-bin directory
COPY cgi/* /usr/local/apache2/cgi-bin/

#copying our own httpd.conf file in the apache server
COPY httpd.conf /usr/local/apache2/conf/httpd.conf

#exectuing our db.sh file which will intialize the database and generate some data on our database
RUN /usr/local/apache2/DB/db.sh

#running the server on port 80
EXPOSE 80
