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
import uuid
import http.cookies

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        parsed_url = urlparse(self.path)
        query_string = parsed_url.query
        query_params = parse_qs(query_string)
        file_path = parsed_url.path[1:]
       
        if file_path == "leaderboard1":
            SendDataForLeaderboard(self)
            return
        
        if not file_path and signedIn(self):
            file_path = "index.html"
        elif not file_path:
            file_path = "signup.html"
        
        if query_params and file_path == "index.html":
             RemoveNameUML(self)
             return
        
        # if file_path == "index.html":
        #     if not checkValidSignup(self):
        #         file_path = "badSigning.html"
        
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type if mime_type else 'application/octet-stream'
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            if not checkExistingId(self):
                generateRandomId(self)
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
        if self.path == '/leaderboard':
            updateLeaderboard(new_data)
            self.send_response(202)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        if self.path == '/newUser':
            ExistingUser(new_data,self)

        if self.path == '/foodEaten':
            updateCurrentScore(new_data,self)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"status":"score updated"}'.encode('utf-8'))
        
        

def run(server_class=HTTPServer, handler_class=S, port=8080):
    global numOfUsers
    numOfUsersReader = open("numOfUsers.txt", "r")
    numOfUsers = int(numOfUsersReader.read())
    numOfUsersReader.close()
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
    scoreCalculatedOpenar = open("playersSession.json", "r")
    rawScore = json.load(scoreCalculatedOpenar)
    scoreCalculatedOpenar.close()
    leaderboardOpenar = open("leaderboard.json", "r")
    leaderboardData = json.load(leaderboardOpenar)
    for entry in rawScore:
        if entry["ID"] == data["ID"] and entry["player"] == data["player"]:
            score = len(entry['score']['x'])
            entry['score']['x'] = []
            entry['score']['y'] = []
            with open('playersSession.json', 'w') as f:
                json.dump(rawScore, f, indent=4)
            for leadEntry in leaderboardData:
                if leadEntry["ID"] == data["ID"] and leadEntry["player"] == data["player"]:
                    if leadEntry["score"] < score:
                        leadEntry["score"] = score
    with open('leaderboard.json', 'w') as f:
        leaderboardData.sort(key=lambda entry: entry['score'], reverse=True)
        json.dump(leaderboardData,f, indent=4)

def SendDataForLeaderboard(self):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    with open("leaderboard.json", "r") as f:
        data = f.read()
    self.wfile.write(data.encode('utf-8'))

def RemoveNameUML(self):
    basePath = urlparse(self.path)
    newURL = basePath.scheme + basePath.netloc + basePath.path
    self.send_response(302)
    self.send_header('Location', newURL)
    self.end_headers()

def checkValidSignup(self):
    referer_url = self.headers.get('Referer')
    if referer_url != "http://127.0.0.1:8080/" and referer_url != "http://127.0.0.1:8080/leaderboard.html" and referer_url != 'http://127.0.0.1:8080/signup.html':
        return False
    return True

def generateRandomId(self):
    global numOfUsers
    idCookie = str(uuid.uuid4())
    cookie = http.cookies.SimpleCookie()
    cookie['session_id'] = idCookie
    cookie['session_id']['path'] = '/'
    self.send_header('Set-Cookie', cookie.output(header='', sep=''))
    print(f'mathafaka: {cookie["session_id"].value}')

def signedIn(self):
    if "Cookie" in self.headers:
        session_id = GetCookieValue(self, 'session_id')
        username = GetCookieValue(self, 'username')
        if session_id and username:
            with open("leaderboard.json", "r") as f:
                data = json.load(f)
            for entry in data:
                if entry["ID"] == session_id and entry["player"] == username:
                    return True
        return False

def checkExistingId(self):
    if "Cookie" in self.headers:
        cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
        if 'session_id' in cookie:
            return True
        return False
    
def ExistingUser(userName, self):
    usersDataReader = open("leaderboard.json", "r")
    dataToFile = json.load(usersDataReader)
    usersDataReader.close()
    for entry in dataToFile:
        if entry["player"] == userName and entry["ID"] != GetCookieValue(self, 'session_id'):
            responsePostNewUserDuplicateFail(self)
            return
        if entry["player"] == userName and entry["ID"] == GetCookieValue(self, 'session_id'):
            responsePostNewUserSuccess(self)
            return
    responsePostNewUserSuccess(self)
    addUserToDB(userName,self)

def RemoveNameUML(self):
    basePath = urlparse(self.path)
    newURL = basePath.scheme + basePath.netloc + basePath.path
    self.send_response(302)
    self.send_header('Location', newURL)
    self.end_headers()


def responsePostNewUserSuccess(self):
    self.send_response(201)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write('{"name":"John", "age":30, "car":null}'.encode('utf-8'))

def responsePostNewUserDuplicateFail(self):
    self.send_response(507)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write('{"error":"User already exists"}'.encode('utf-8'))

def addUserToDB(userName,self):
    session_id = GetCookieValue(self, 'session_id')
    print(f"Adding user: {userName} with session ID: {session_id}")
    leadReader = open("leaderboard.json", "r")
    dataToFile = json.load(leadReader)
    leadReader.close()
    dataToFile.append({'ID':session_id ,"player": userName, "score": 0})
    with open('leaderboard.json', 'w') as f:
        json.dump(dataToFile, f, indent=4)
    leadReader = open("playersSession.json", "r")
    dataToFile = json.load(leadReader)
    dataToFile.append({'ID':session_id ,"player": userName,'score':{
        'x':[],
        'y':[]
    }})
    with open('playersSession.json', 'w') as f:
        json.dump(dataToFile, f, indent=4)


def GetCookieValue(self, cookie_name):
    if "Cookie" in self.headers:
        cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
        if cookie_name in cookie:
            return cookie[cookie_name].value
    return None

def updateCurrentScore(new_data,self):
    session_id = new_data['id']
    food_x = new_data['x']
    food_y = new_data['y']
    username = new_data['username']
    leadReader = open("playersSession.json", "r")
    currentSession = json.load(leadReader)
    leadReader.close()
    for entry in currentSession:
        if entry["ID"] == session_id and entry["player"] == username:
            entry['score']['x'].append(food_x)
            entry['score']['y'].append(food_y)
    with open('playersSession.json', 'w') as f:
        json.dump(currentSession, f, indent=4)
        print(f"Updated score for user: {username} with session ID: {session_id}")

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
