#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from urllib.parse import urlparse 
import mimetypes 
from urllib.parse import parse_qs
import json



class S(BaseHTTPRequestHandler):
    global firstTimeUser
    firstTimeUser = True
    global realUserName
    realUserName = ""
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        

    def do_GET(self):
        global firstTimeUser
        global realUserName
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        parsed_url = urlparse(self.path)
        query_string = parsed_url.query
        query_params = parse_qs(query_string)
        file_path = parsed_url.path[1:]
        if file_path == "leaderboard":
            SendDataForLeaderboard(self)
            return
        if not file_path:
            file_path = "signup.html"
        if not query_params and file_path == "index.html":
            addNameToUML(self)
            return
        if "name" in query_params and firstTimeUser:
            firstTimeUser = False
            realUserName = str(query_params["name"][0])
            print("All good homie")
        elif "name" in query_params and realUserName != str(query_params["name"][0]) and not firstTimeUser:
            print("Different user detected")
            file_path = "badSigning.html"
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type if mime_type else 'application/octet-stream'
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(data)

        except FileNotFoundError:
            
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"404 Not Found: File '{file_path}' not found.".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        new_data = json.loads(post_data.decode('utf-8'))
        updateLeaderboard(new_data)

        
        

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

def updateLeaderboard(data):
    isFound = False
    leadReader = open("leaderboard.json", "r")
    dataToFile = json.load(leadReader)
    for entry in dataToFile:
        if entry["player"] == data["player"]:
            isFound = True
            if entry["score"] < data["score"]:
                entry["score"] = data["score"]
    if isFound == False:
        dataToFile.append(data)
    dataToFile.sort(key=lambda entry: entry['score'], reverse=True)
    with open('leaderboard.json', 'w') as f:
        json.dump(dataToFile, f, indent=4)

def SendDataForLeaderboard(self):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    with open("leaderboard.json", "r") as f:
        data = f.read()
    self.wfile.write(data.encode('utf-8'))

def addNameToUML(self):
    global realUserName
    basePath = self.path
    if not basePath:
            basPath = "/"
    new_url_parameters = f"name={realUserName}"
    new_full_url = basePath + new_url_parameters
    self.send_response(302)
    self.send_header('Location', new_full_url)
    self.end_headers()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

# def checkExistingUser():