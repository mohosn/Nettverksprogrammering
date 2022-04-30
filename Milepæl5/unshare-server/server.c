#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <signal.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>

#define port 80
#define back_log 10

void daemonize()
{
    pid_t pid; // pid =-1 error pid=0 child pid>0 parent
    pid = fork();

    if (pid < 0)
    {
        exit(EXIT_FAILURE); // error child process was  not successfully created
    }
    if (pid > 0)
    {
        exit(EXIT_SUCCESS); // successfully exited from parent process
    }
    if (setsid() < 0) // setsid()<0 means error
    {
        exit(EXIT_FAILURE); // exit with failure code
    }

    signal(SIGCHLD, SIG_IGN); // ignoring sigchld
    signal(SIGHUP, SIG_IGN);  // ignoring sighup

    pid = fork();

    if (pid > 0)
    {
        exit(EXIT_SUCCESS); // terminating parent process second time
    }
    // chdir("/"); // changing to root directory
    umask(0); // changing permission
    close(0); // closing file descriptor
    close(1);
}

char *mimeType(char *path)
{

    FILE *fp = fopen("/mime.types", "r"); // creating a file pointer for mime.types

    // checking if the file pointer exists or not
    if (fp == NULL)
    {
        fprintf(stderr, "Error opening mime.types\n"); // if file pointer doesn't exists log in the debug.log file
        exit(1);
    }

    char *fileExtension;
    char *mimetype;
    char *token; // created a genaralized token for asis files
    char line[1024];
    char *noExtention = NULL; // if no extension in the request
    char *storeToken;
    char *asisToken = "asis";
    // path = /index.html
    fileExtension = strrchr(path, '.'); // pointing to the last occurance of . ---> .html

    // if path is like /index
    if (fileExtension == NULL)
    { // no extension
        return noExtention;
    }
    // pointing .html
    fileExtension++; // pointing html

    if (!strcmp(fileExtension, "asis"))
    { // comparing if the extension is asis
        return asisToken;
    }

    // extracting content-type from mime.types
    while (fgets(line, sizeof(line), fp) != NULL)
    {                                          // reading line by line from mime.types
        if (line[0] == '#' || line[0] == '\n') // if line starts with newline or # ignoring it
            continue;
        token = strtok(line, "\n"); // extracting using delimeter new line

        if (strstr(token, fileExtension))
        {                        // checking if file extension exists as a substring in the line
            strtok(token, "\t"); // extracting based on tab space
            storeToken = strtok(NULL, "\t");
            if (storeToken != NULL)
            {
                storeToken = strtok(storeToken, " ");
                while (storeToken != NULL)
                { // extracting all token
                    if (!strcmp(storeToken, fileExtension))
                    { // checking if file extension is the actual extension
                        return token;
                    }
                    storeToken = strtok(NULL, " ");
                }
            }
        }
    }
    return noExtention;
}

// taking the request as argument and extracting the path  and returing the pointer of the path
char *extractPath(char *request)
{
    char *firstLine = strtok(request, "\n"); // extracting the firstline from the request ---> GET /index.html
    strtok(firstLine, " ");                  // extracting from firstline using space as a delimeter and ignoring it  --> GET
    char *path = strtok(NULL, " ");          // extracting from firstline using space as a delimeter and it will the path --> /index.html
    return path;
}

int main()
{
    daemonize(); // daemonize the process

    int serverSocket, clientSocket; // for server and client socket
    int on = 1;                     // this is for setsockopt enable value
    struct sockaddr_in server_address;

    char httpRequest[2048];
    char httpNotFound[] = "HTTP/1.1 404 Not Found\nContent-Type: text/plain\r\n\r\n404 Not Found\n";                                        // this is for if the requested file not found
    char httpUnsupportedMediaType[] = "HTTP/1.1 415 Unsupported Media Type\nContent-Type: text/plain\r\n\r\n415 Unsupported Media Type.\n"; // this is for unsupported media type
    char httpOk[] = "HTTP/1.1 200 OK\nContent-Type:       ";
    char extra[] = "\r\n\r\n";
    char httpResponse[512];
    char *filePath, *filePathCopy, *contentType, c; // this will store the file path given by the client

    FILE *fp, *log; // these are file pointers

    log = fopen("/var/log/debug.log", "a"); // opening the debug.log file

    dup2(fileno(log), STDERR_FILENO); // this will redirect stderr messages to error.log file
    fclose(log);                      // closing error.log filepointer

    if (chroot("/var/www"))
    {
        fprintf(stderr, "Coudn't change root\n");
    }; // changing root directory for the current process and making this directory webroot

    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); // ipv4, tcp , tcp protocol
    if (serverSocket < 0)
    {
        perror("socket creation failed!\n"); // error log for failed socked creation
    }

    server_address.sin_family = AF_INET;         // ipv4
    server_address.sin_addr.s_addr = INADDR_ANY; // local host
    server_address.sin_port = htons(port);       // defined port=80

    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(int)); // setting up options for server socket

    if (bind(serverSocket, (struct sockaddr *)&server_address, sizeof(server_address)) == 0) // binding socket with server address
    {
        fprintf(stderr, "Prosess %d er running on port %d.\n", getpid(), port);
    }
    else
    {
        perror("Binding server socket failed");
        exit(2); // exiting process with major bug(2) signal
    }

    // drop the root privilleges and make you the process owner
    if (!getuid()) // if getuid returns 0 then it means  this process owner is a super user / root
    {
        if (setgid(1000) != 0) // seting group id
            perror("setgid: Unable to drop group privileges.\n");
        if (setuid(1000) != 0) // setting user id
            perror("setuid: Unable to drop user privileges.\n");
    }
    else
    {
        fprintf(stderr, "not root!\n"); // owner is not root
    }

    listen(serverSocket, back_log); // listening to requests made by the client
    while (1)
    {
        clientSocket = accept(serverSocket, NULL, NULL); // accepting client
        if (clientSocket < 0)
        {
            perror("accept failed!!\n"); // failed to accept client socket.
        }

        
        if (!fork()) // creating new process for each client request by creating a child process
        {

            recv(clientSocket, httpRequest, sizeof(httpRequest), 0); // received http request from client
            dup2(clientSocket, 1);               // redirecting stdout to client socket

            filePath = extractPath(httpRequest); // extracting path by calling function
            filePathCopy = filePath;
            contentType = mimeType(filePathCopy); // generating content-type
            fprintf(stderr, "%s\n", filePathCopy);
            // localhost/
            if (!strcmp(filePath, "/"))
            {
                filePath = "/index.html";
                contentType = "text/html";
            }


            if (contentType == NULL)
            {
                fprintf(stderr, "415 Unsupported Media Type.\n");                                // log error in the error.log file
                write(clientSocket, httpUnsupportedMediaType, strlen(httpUnsupportedMediaType)); // sending error message to client
                close(clientSocket);
            }else if (access(filePath, F_OK))
            { // checking if the filepath exists in the system
                fprintf(stderr, "404 Not Found\n");
                write(clientSocket, httpNotFound, strlen(httpNotFound));
                close(clientSocket);
            }else if (!strcmp(contentType, "asis"))
            {
                fp = fopen(filePath, "r");
                fprintf(stderr, "200 OK\n");
                while (1)
                {
                    c = fgetc(fp);
                    if (feof(fp))
                    {
                        break;
                    }
                    write(clientSocket, &c, sizeof(c));
                }
                fclose(fp);
            }
            else
            {
                sprintf(httpOk, "HTTP/1.1 200 OK\nContent-Type: %s\r\n\r\n", contentType);
                write(clientSocket, httpOk, strlen(httpOk));
                // write(clientSocket,contentType,strlen(contentType));
                // write(clientSocket,extra,strlen(extra));
                fp = fopen(filePath, "r");
                fprintf(stderr, "200 OK\n");
                while (1)
                {
                    c = fgetc(fp);
                    if (feof(fp))
                    {
                        break;
                    }
                    write(clientSocket, &c, sizeof(c));
                }
                fclose(fp);
            }
            fflush(stderr);
            shutdown(clientSocket, SHUT_RDWR);
            exit(0);
        }
        else
        {
            signal(SIGCHLD, SIG_IGN); // ignoring zombie process
            close(clientSocket);
        }
    }

    close(serverSocket);
    return 0;
}
