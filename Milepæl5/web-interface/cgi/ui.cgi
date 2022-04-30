#!/bin/sh
#Read body

#setting the content type 
echo "Content-type:text/html;charset=utf-8"


cgi_server=172.17.0.2
unshare_server=http://172.17.0.1
ui_server=172.17.0.3


#in form we can have 2 types of method  GET and POST 
#if method is get we dont have to read body.
#but if method is post we have to read the body.
if [ "$REQUEST_METHOD" = "POST" ]; then
    if [ "$CONTENT_LENGTH" -gt 0 ]; then
        read -n $CONTENT_LENGTH BODY_RES <&0 #reading the body and storing it in  BODY_RES, which holds the body sent by the browser
    fi
fi


if [ $REQUEST_URI = '/login' ];then
	#convetring %40 to @
	BODY_RES="${BODY_RES/%40/"@"}"
	#extracting email from BODY_RES
	email=`echo $BODY_RES | awk -F '&'  '{print $1}' | awk -F '=' '{print $2}'`
	#extracting password from BODY_RES
	password=`echo $BODY_RES | awk -F '&'  '{print $2}' | awk -F '=' '{print $2}'`
	
	#sending email and password to our cgi-server
	response=$(curl -c - -X POST $cgi_server/login -d "<credential><email>$email</email><password>$password</password></credential>")
	#if the credential is right then we get success message
	# we are checking if there is success message or not
	success=$( echo $response | grep "Successful")
	#extracting sessionID
	sessionID=`echo $response | awk -F 'sessionID' '{print $2}'`

elif [ $HTTP_COOKIE != "" ];then 
	#extracting the sessionID from the cookie
	sessionID=`echo $HTTP_COOKIE  | awk '{split($0,array,"=")} END{print array[2]}'`

elif [ $REQUEST_URI = "/poem/id" ];then
	sessionID=`echo "$HTTP_COOKIE" | awk '{split($0,array,";")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}'`

fi

#if url if logout deleting the sessionID via cgi server
if [ $REQUEST_URI = '/logout' ];then
	response=$(curl --cookie "sessionID=$sessionID" $cgi_server/logout)
	sessionID=""
fi
 

#storing the cookie  for the browser
echo "Set-Cookie:sessionID=$sessionID"

#End header
echo 

#css=$(curl "$unshare_server/style.css")


echo "<!DOCTYPE html>"
echo "<html>"
echo "<head>"
echo "<title>Web Server</title>"
echo "<link rel="stylesheet" href="$unshare_server/style.css">"
echo "</head>"
echo "<body>"
#echo "$sessionID"
#title 
echo "<h1> Poem Database WebServer</h1>"
#checking if there is no sessionID then we will show the login part of the page

if [ -z $sessionID ];then
cat <<EOF
<form action="/login" method="post" accept-charset="utf-8">
                <label>Email</label>
                <input type="text" name="uid">
                <br><br>
                <label>Password</label>
                <input type="password" name="password">
                <br><br>
                <button type="submit">Login</button>
</form>
EOF

#if there is sessionID then it means you are logged in, then show the logout button  
else
	echo "<form method="post" action="/logout" accept-charset="utf-8">"
	echo "<input type="submit" id="logout" name="logout" value= "Logout"><br>"
	echo "</form>"
fi

# if success variable is not empty that means you are valid user, else not
if [ $REQUEST_URI = '/login' ];then
	if [ "$success" != "" ];then
		fname=$(echo $success | awk -F '<fname>' '{print $2}' | awk -F '</fname>' '{print $1}')
		echo "<h4> Welcome back, $fname</h4>"
	else
		echo "<h4> Invalid Credentials</h4>"
	fi
fi


#search is for everyone, login is not mandatory
echo "<h2>SEARCH Poem</h2>"

#creating viewall button
cat <<EOF
<form action="/viewall" method="get">
	<button type="submit">All Poems</button>
</form>
EOF

#if client asked for all poems,  then creating table to show all the poem
if [ $REQUEST_URI = "/viewall?" ];then
echo "<table>"
echo "<tr><th>poemID</th><th>Poem</th><th>email</th></tr>"
#retriving data from cgi-server and reading data one by one and setting it into the table
curl $cgi_server/poem | grep "<Poem>" | while read -r line;
do
    poemID=$(echo $line | awk -F '<poemID>' '{print $2}' | awk -F '</poemID>' '{print $1}')
    poem=$(echo $line | awk -F '<poem>' '{print $2}' | awk -F '</poem>' '{print $1}')
    email=$(echo $line | awk -F '<email>' '{print $2}' | awk -F '</email>' '{print $1}')
    echo "<tr><td>$poemID</td><td>$poem</td><td>$email</td></tr>"
done
echo "</table>"	
echo "<br>"
fi

#creating specific poem search option
cat <<EOF
<form action="/poem/id" method="post">
	<label>Poem ID</label>
	<input type="text" name="pid">
	<br>
	<button type="submit">Search</button>
</form>
EOF

#if client ask for specific poem then we execute following code
if [ $REQUEST_URI = "/poem/id" ];then
		#extracting the poemID which client wants
		poemID=`echo $BODY_RES | awk -F '=' '{print $2}'`
        echo "<table>"
		echo "<tr><th>poemID</th><th>Poem</th><th>email</th></tr>"
		#retriving the poem according to client need
		curl $cgi_server/poem/$poemID | grep "<Poem>" | while read -r line;
do
		poemID=$(echo $line | awk -F '<poemID>' '{print $2}' | awk -F '</poemID>' '{print $1}')
		poem=$(echo $line | awk -F '<poem>' '{print $2}' | awk -F '</poem>' '{print $1}')
		email=$(echo $line | awk -F '<email>' '{print $2}' | awk -F '</email>' '{print $1}')
		echo "<tr><td>$poemID</td><td>$poem</td><td>$email</td></tr>"
done
		echo "</table>"	
		echo "<br>"
fi


#you must have sessionID to execute the following code
if [ ! -z $sessionID ];then

#view all of your own poem option
cat <<EOF
<form action="/viewallown" method="get">
	<button type="submit">Own Poems</button>
</form>
EOF


	#if clinet ask for view all of his own poem.
	if [ $REQUEST_URI = "/viewallown?" ];then
		echo "<table>"
		echo "<tr><th>poemID</th><th>Poem</th><th>email</th></tr>"
		#retriving own poems from cgi server
		curl --cookie "sessionID=$sessionID" $cgi_server/poems/own | grep "<Poem>" | while read -r line;
		do
			poemID=$(echo $line | awk -F '<poemID>' '{print $2}' | awk -F '</poemID>' '{print $1}')
			poem=$(echo $line | awk -F '<poem>' '{print $2}' | awk -F '</poem>' '{print $1}')
			email=$(echo $line | awk -F '<email>' '{print $2}' | awk -F '</email>' '{print $1}')
			echo "<tr><td>$poemID</td><td>$poem</td><td>$email</td></tr>"
		done
		echo "</table>"	
		echo "<br>"
	fi

#add poem options
echo "<h2>ADD Poem</h2>"
cat <<EOF
<form action="/addpoem" method="post">
	<label>Poem Title</label>
	<input type="text" name="pname">
	<br>
	<button type="submit">Add Poem</button>
</form>
EOF
	#if client wants to add poem we execute following part
	if [ $REQUEST_URI = "/addpoem" ];then
		title=`echo $BODY_RES | awk -F '=' '{print $2}'`
		title=$(echo "${title//+/" "}")
		#adding poem into the database via cgi-server
		response=$(curl --cookie "sessionID=$sessionID" -X POST $cgi_server/poem -d "<poem><title>$title</title></poem>")
		echo "<h5>Successfully added a new poem</h5>"
	fi


#edit poem options
echo "<h2>EDIT Poem</h2>"
cat <<EOF
	<form action="/editpoem" method="post">
	<label>Poem Title</label>
	<input type="text" name="pname">
	<br>
	<label>Poem ID</label>
	<input type="text" name="pid">
	<br>
	<button type="submit">Edit Poem</button>
</form>
EOF
	#if client wants to edit poem we execute the following part
	if [ $REQUEST_URI = "/editpoem" ];then
		poemID=`echo $BODY_RES | awk -F '&' '{print $2}' | awk -F '=' '{print $2}'`
		title=`echo $BODY_RES | awk -F '&' '{print $1}' | awk -F '=' '{print $2}'`
		title=$(echo "${title//+/" "}")
		response=$(curl --cookie "sessionID=$sessionID" -X PUT $cgi_server/poem/$poemID -d "<poem><title>$title</title></poem>")
		
		success=$(echo $response | grep "Poem updated")
		#if client tried to update his own poem then response will be stored in the success variable and otherwise success will be empty
		if [ "$success" != "" ];then
			echo "<h5>Successfully edited poem</h5>"

		else
			echo "<h5>You can not edit this poem</h5>"

		fi
	
	
	fi

#delete poem options
echo "<h2>DELETE Poem</h2>"

cat <<EOF
	<form action="/deletepoem" method="post">
	<label>Poem ID</label>
	<input type="text" name="pid">
	<br>
	<button type="submit">Delete Poem</button>
</form>
EOF
	#if client wants to delete specific poem
	if [ $REQUEST_URI = "/deletepoem" ];then
		poemID=`echo $BODY_RES  | awk -F '=' '{print $2}'`
			response=$(curl --cookie "sessionID=$sessionID" -X DELETE $cgi_server/poem/$poemID)
		success=$(echo $response | grep "Poem deleted")
		#if client tries to delete his own poem then the response will be stored in success variable, otherwise success will be empty
		if [ "$success" != "" ];then
			echo "<h5>Successfully deleted poem</h5>"
		else
			echo "<h5>You can not delete this poem</h5>"
		fi
	
	
	fi
#delete all of your(client) own poem
cat <<EOF
<form action="/deleteall" method="post">
	<button type="submit">Delete All Own Poem</button>
</form>
EOF
	#if client wants to delete all of his poem we execute the following
	if [ $REQUEST_URI = "/deleteall" ];then
		response=$(curl --cookie "sessionID=$sessionID" -X DELETE $cgi_server/deleteall)
		echo "<h5>All of your poems are deleted</h5>"
	fi

fi


echo "<br><br><br>"
#linking group-info from container-1 or unshare-server from milestone-2
echo "<a href="$unshare_server/gruppe11-xml.xml">Group Info</a>"
echo "</body>"
echo "</html>"
