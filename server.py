#  coding: utf-8 
import SocketServer
import mimetypes 
import os.path

# Copyright 2013 Touqir Sajed, Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# testHTML="<!DOCTYPE html PUBLIC '-//IETF//DTD HTML 2.0//EN'> <HTML>    <HEAD>       <TITLE>          A Small Hello       </TITLE>   </HEAD> <BODY>    <H1>Hi</H1>    <P>This is very minimal 'hello world' HTML document.</P> </BODY> </HTML>"


class LinkManager:


    def __init__(self):
        self.ROOTDIR=os.getcwd()

    def getPageLocation(self, URL):
        if URL[-1]=="/": URL=URL[:-1]
        localLink=os.path.realpath(self.ROOTDIR+URL)
        print (localLink)
        status=None
        if os.path.isfile(localLink):
            if self.ROOTDIR in localLink:
                status=1
                return [localLink,status]
            else:
                status=3
                return [None, status]
        elif os.path.isdir(localLink):
            if self.ROOTDIR in localLink:
                if os.path.isfile(localLink+"/index.html"):
                    status=2
                    return [URL+'/index.html', status]
                else:
                    status=3 
                    return [None, status]
            else:
                return None

        else: 
            return None


class MyWebServer(SocketServer.BaseRequestHandler):    


    def handle(self):
        self.link_manager=LinkManager()
        self.processRequest()

    def parseRequest(self, requestData):
        firstLine=requestData.split('\n')[0].strip()
        [HTTP_request, URL]=firstLine.split(" ")[0:2]
        return [HTTP_request, URL]

    def processRequest(self):
        data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % data)
        [HTTP_request, URL]=self.parseRequest(data)
        page_info=self.link_manager.getPageLocation(URL)

        if page_info is None:
            self.HTTP_404()
            return 

        if page_info[1]==1:
            pageLocation=page_info[0]
            page, mimetype=self.readFile(pageLocation)
            self.HTTP_200(page, mimetype)
        
        elif page_info[1]==2:
            redirection_location=page_info[0]
            self.HTTP_302(redirection_location)

        elif page_info[1]==3:
            self.HTTP_404()


    def sendReply(self, params, webResource, mimetype):
        Header=""
        flag=params[0]

        if flag == 1:
            self.HTTP_200(webResource, mimetype)
        elif flag == 2:
            self.HTTP_404()
        elif flag == 3:
            self.HTTP_302()


    def readFile(self, fileLocation):

        try:
            file=open(fileLocation, "r")
            fileContent=file.read()
            file.close()
        except IOError:
            return -1 #File not found

        mimetype, _ = mimetypes.guess_type(fileLocation)
    
        return fileContent, mimetype

    
    def HTTP_302(self, redirection):
        Header="HTTP/1.1 302 Found\nLocation: "
        mimetype="Content-Type: text/html\n"
        message= Header+redirection+"\n"+mimetype+"\n"
        self.request.sendall(message)
    

    def HTTP_200(self, webResource, mimetype):
        Header="HTTP/1.1 200 OK\n"
        Header+= "Content-Type: "+mimetype
        Header+="\n\n"
        message= Header+webResource
        self.request.sendall(message)

    
    def HTTP_404(self):
        string_404="404 : Page not Found!\n"
        Header="HTTP/1.1 404 Not Found\n"
        Header+="Content-Type: text/plain\n\n"
        message= Header+string_404
        self.request.sendall(message)


    def HTTP_403(self):
        string_403="403 : Access is Denied!"
        Header="HTTP/1.1 403 Forbidden\n"
        Header+="Content-Type: text/plain\n\n"
        message= Header+string_403
        self.request.sendall(message)



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    os.chdir(os.getcwd()+'/www')

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
