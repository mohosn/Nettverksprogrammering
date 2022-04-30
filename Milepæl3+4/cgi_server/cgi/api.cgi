#!/bin/bash

#logge inn  side (74)                                                         logge ut  side (136) 

#Lege til nytt dikt    (Post)    Line (102)                             Hente et  dikt    (Get)  Line (170)
#Endre egne dikt       (Put)     Line (289)                             Hent alle dikt    (Get)  Line (190)   
#Slette eget dikt      (Delete)  Line (237)
#Slette alle dikt      (Delete)  Line (250)
     
function XMLGenerator() {
    echo "<?xml version='1.0' encoding='UTF-8'?>"
    #echo "<?xml-stylesheet type='text/xsl' href='http://172.17.0.2/poemdb.xsl'?>"
    echo "<?xml-stylesheet type='text/css' href='http://172.17.0.1/poem.css'?>"
    echo "<poemdb xmlns:xs='http://www.w3.org/2001/XMLSchema-instance' xs:schemaLocation='http://172.17.0.1/ poemdb.xsd'>"
} 

#checking if client sent something in request body and reading it if the method is POST,PUT,DELETE
if [ "$REQUEST_METHOD" = "POST" ] || [ "$REQUEST_METHOD" = "DELETE" ] || [ "$REQUEST_METHOD" = "PUT" ]; then
        if [ "$CONTENT_LENGTH" -gt 0 ]; then
                read -n $CONTENT_LENGTH BODY_REQ <&0
        fi
fi



#cookie is stored in $HTTP_COOKIE
#extracting sessionID from cookie
sessionID=`echo $HTTP_COOKIE  | awk '{split($0,array,";")} END{print array[1]}' | awk '{split($0,array,"=")} END{print array[2]}'`
#email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )


#client sends sessionID in cookie
# 3 case for sessionID -->
#case-1: if dont have sessionID --> if a client doesn't login
#case-2: if a client wants to login --> he doesn't  have sessionID --> but we have to generate sessionID in this case and store it in our database and sends it back
#case-3: if a client already logged in and sends some sessionID --> we already have sessionID in database --> we will check it


user=""
if [ $REQUEST_URI = '/login' ];then
        email=`echo $BODY_REQ | awk -F '<email>'  '{print $2}' | awk -F '</email>' '{print $1}'`
        password=`echo $BODY_REQ | awk -F '<password>'  '{print $2}' | awk -F '</password>' '{print $1}'`
        hashed=$(echo -n $password | md5sum | awk '{print $1}')
        user=$(echo -n "select email from user where email=\"$email\" AND password=\"$hashed\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
        
        #IF A user is valid and trying to login, we are generating a sessionID and storing it in our database
        if [ ! -z $user ];then #if valid 
            sessionID=$(echo $RANDOM | md5sum | head -c 20)
            echo -e -n "INSERT INTO Session (\"sessionID\",\"email\") VALUES (\"$sessionID\",\"$user\");" |  sqlite3 /usr/local/apache2/DB/userDB.db  
        fi
    
fi


#if your provide correct sessionID validRequest variable will have some value, otherwise empty 
#validRequest means if a user have valid sessionID or not
validRequest=$(echo -n "select sessionID from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )

#validRequest=59ef871c48b90765fbc0 case-1--> we have the sessionID in our database which the user send with the request--> then validRequest will not be empty
#validRequest="" case-2 validRequest will be empty

echo "Set-Cookie:sessionID=$sessionID"
echo 'Content-Type: text/xml'


echo ""


# echo $BODY_REQ
# echo $HTTP_COOKIE
# echo $REQUEST_URI
# echo $sessionID

if [ "$REQUEST_METHOD" = "POST" ];then

    if [ $REQUEST_URI = '/login' ];then
        #extracting email and password from request body
        email=`echo $BODY_REQ | awk -F '<email>'  '{print $2}' | awk -F '</email>' '{print $1}'`
        password=`echo $BODY_REQ | awk -F '<password>'  '{print $2}' | awk -F '</password>' '{print $1}'`
        #creating hash of the password so that we can use hashed version of the password which is saved in our database
        hashed=$(echo -n $password | md5sum | awk '{print $1}')
        #checking is the provided email and password is registered, if it is valid then email of the user will be stored in user
        user=$(echo -n "select email from user where email=\"$email\" AND password=\"$hashed\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
        
        if [ ! -z $user ];then #if valid 
            #storing sessionID in database
            fname=$(echo -n "select fname from user where email=\"$user\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
    
            #sending response as XML
            XMLGenerator
            echo "<Response><message>Successful</message><fname>$fname</fname></Response>"
        else
            XMLGenerator
            echo "<Response><message>Invaild credentails</message></Response>"
        fi
     
    
    fi

    #adding poem route is restricted
    #only logged in users can add poem
    if [ $REQUEST_URI = '/poem' ];then
        #checking if the client provided us the right sessionID
        if [ ! -z $validRequest ];then #if it is right
            #checking who is the owner of this sessionID
            #extracting the email of the owner
            email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
            
            if [ ! -z $email ];then
                #extracting poem title/name from request body
                poem=`echo $BODY_REQ | awk -F '<title>'  '{print $2}' | awk -F '</title>' '{print $1}'`
                
                #storing poem into database
                echo -n "INSERT INTO Poem (poem, email) VALUES (\"$poem\",\"$email\" );" | sqlite3 /usr/local/apache2/DB/userDB.db

                #sending response back to client
                XMLGenerator
                echo "<Response><message>Poem added!</message></Response>"
                
            else
                XMLGenerator
                echo "<Response><message>You are not logged in!!</message></Response>"

            fi
            
            
        else #if sessionID is not right or you didn't provide a sessionID in cookie
            XMLGenerator
            echo "<Response><message>You are not logged in!!</message></Response>"
        fi

    fi

fi

if [ "$REQUEST_METHOD" = "GET" ];then

    if [ $REQUEST_URI = '/logout' ];then
        #checking if you are logged in
        if [ ! -z $validRequest ];then #if logged in
            #deleting sessionID from database
            echo -e -n "DELETE FROM Session WHERE sessionID=\"$sessionID\";" |  sqlite3 /usr/local/apache2/DB/userDB.db
            XMLGenerator
            echo "<Response><message>Logout Successful</message></Response>"
        else
            XMLGenerator
            echo "<Response><message>You are not logged in!!</message></Response>"
        fi        
    fi

    #not a restircted route
    #anyone can view all poem without login
    if [ $REQUEST_URI = '/poem' ];then
        
        
        poem=$(echo "select poemID from poem;" | sqlite3 /usr/local/apache2/DB/userDB.db)
        poem=$(echo $poem)
        IFS=" "
        read -ra arr <<< "$poem"

        XMLGenerator    
        for element in "${arr[@]}"
        do 
        #we also have to search email based on poemID 
        email=$(echo -n "select email from poem where poemID=\"$element\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
        poem=$(echo -n "select poem from poem where poemID=\"$element\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
        echo "<Poem><poemID>$element</poemID><poem>$poem</poem><email>$email</email></Poem>"
        done
        echo "</poemdb>"
    
    fi

    #not a restircted route
    #anyone can view all poem without login
    #here we used regex
    if [[ $REQUEST_URI =~ ^/(poem)+/[^/]*[0-9]$ ]];then
        #extracting poemID from url
        poemID=`echo $REQUEST_URI | cut -d '/' -f 3` 
        email=$(echo -n "select email from poem where poemID=\"$poemID\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
        poem=$(echo -n "select poem from poem where poemID=\"$poemID\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
        XMLGenerator
        echo "<Poem><poemID>$poemID</poemID><poem>$poem</poem><email>$email</email></Poem>"
        echo "</poemdb>"
    


    fi

    #restriced route
    if [ $REQUEST_URI = '/poem/own' ];then
        if [ -z $validRequest ];then
            XMLGenerator
            echo "<Response><message>You are not logged in!!</message></Response>"


        else 

            #extracting email from database using sessionID
            email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
            poem=$(echo "select poemID from poem where email=\"$email\";" | sqlite3 /usr/local/apache2/DB/userDB.db)
            poem=$(echo $poem)
            IFS=" "
            read -ra arr <<< "$poem"
            
            XMLGenerator
            for element in "${arr[@]}"
            do 
                poem=$(echo -n "select poem from poem where poemID=\"$element\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
                email=$(echo -n "select email from poem where poemID=\"$element\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
                echo "<Poem><poemID>$element</poemID><poem>$poem</poem><email>$email</email></Poem>"
            done
            echo "</poemdb>"
        fi
    fi

fi

#all delete routes are restricted
#so you have to pass sessionID as cookie every time
if [ $REQUEST_METHOD = "DELETE" ];then
    
    if [ -z $validRequest ];then
        XMLGenerator
        echo "<Response><message>You are not logged in!!</message></Response>"

    else
        #using regex 
        if [[ $REQUEST_URI =~ ^/(poem)+/[^/]*[0-9]$ ]];then
            #extracting id 
            poemID=`echo $REQUEST_URI | cut -d '/' -f 3`  
            #extracting the origin owner of the poem using the id
            owner=$(echo -n "select email from poem where poemID=\"$poemID\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
            #checking who is logged user
            email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
            
            #checking if the owner is the current logged user
            if [ $owner = $email ];then #if yes
                echo "delete from Poem where poemID=\"$poemID\"" | sqlite3 /usr/local/apache2/DB/userDB.db

                XMLGenerator
                echo "<Response><message>Poem deleted</message></Response>"
            else #if no 
                XMLGenerator
                echo "<Response><message>You cannot delete this poem</message></Response>"

            fi
        
        fi
        #restricted route
        if [ $REQUEST_URI = '/deleteall' ];then

            if [ -z $validRequest ];then
                XMLGenerator
                echo "<Response><message>You are not logged in!!</message></Response>"
            else
                email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
                echo "delete from Poem where email=\"$email\"" | sqlite3 /usr/local/apache2/DB/userDB.db
                XMLGenerator
                echo "<Response><message>All of your poem are deleted</message></Response>"

            fi


        fi
        
    fi
    
    

fi

#restricted route
#you have to pass cookie
if [ $REQUEST_METHOD = "PUT" ];then

    if [ -z $validRequest ];then
        XMLGenerator
        echo "<Response><message>You are not logged in!!</message></Response>"

    else
            #using regex to match pattern
            if [[ $REQUEST_URI =~ ^/(poem)+/[^/]*[0-9]$ ]];then
                #extracting id
                poemID=`echo $REQUEST_URI | cut -d '/' -f 3`  
                owner=$(echo -n "select email from poem where poemID=\"$poemID\";" |  sqlite3 /usr/local/apache2/DB/userDB.db)
                email=$(echo -n "select email from Session where sessionID=\"$sessionID\"" |  sqlite3 /usr/local/apache2/DB/userDB.db )
                
                #if owner and currently logged user is same person then you can edit
                if [ $owner = $email ];then #if yes
                    #extracting the title from request body
                    poem=`echo $BODY_REQ | awk -F '<title>'  '{print $2}' | awk -F '</title>' '{print $1}'`
                    #updating new title into database
                    echo "update Poem set poem=\"$poem\" where poemID=\"$poemID\"" | sqlite3 /usr/local/apache2/DB/userDB.db
                    #sending response
                    XMLGenerator
                    echo "<Response><message>Poem updated</message></Response>"
                else #if no
                    XMLGenerator
                    echo "<Response><message>You cannot edit this poem</message></Response>"

                 fi
        
            fi  


    fi
    
fi

#echo "</poemdb>"
