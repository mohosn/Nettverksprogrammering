#!/bin/sh

echo
echo Creating database named userDB.db
echo 

#sqlite is a sql database 
#mongodb, firebase is nosql database

# <  --> redirect stdout
# << --> redirect from a document 
# <<< --> redirect from a string


# we need 3 table --> user , session , poem

 
sqlite3 /usr/local/apache2/DB/userDB.db <<EOF

DROP TABLE IF EXISTS User;

CREATE TABLE User (
    email     STRING PRIMARY KEY
                     UNIQUE
                     NOT NULL,
    password  STRING,
    fname STRING,
    lname STRING
);

DROP TABLE IF EXISTS Poem;

    CREATE TABLE Poem (
        poemID INTEGER PRIMARY KEY
                    AUTOINCREMENT,
        poem   STRING,
        email          REFERENCES User (email)
                    NOT NULL
    );

DROP TABLE IF EXISTS Session;

CREATE TABLE Session (
    sessionID STRING  NOT NULL
                      PRIMARY KEY
                      UNIQUE,
    email     STRING  REFERENCES User (email)
                      NOT NULL
);

INSERT INTO User (email,password,fname,lname) VALUES ("hu@gmail.com","81dc9bdb52d04dc20036dbd8313ed055","hu","Ala");

INSERT INTO Poem (poem, email) VALUES ("Hi", "hu@gmail.com");
INSERT INTO Poem (poem, email) VALUES ("beautiful story", "mu@gmail.com");
INSERT INTO Poem (poem, email) VALUES ("Hello friends", "ib@yahoo.com");
INSERT INTO Poem (poem, email) VALUES ("Hi", "hu@gmail.com");

EOF

echo Database has been created.
echo
echo Setting permissions and ownership.
#chown root /usr/local/apache2/DB/userDB.db
chmod 777 /usr/local/apache2/DB/userDB.db 

echo
echo Ownership and permissions set. Program will now exit.
