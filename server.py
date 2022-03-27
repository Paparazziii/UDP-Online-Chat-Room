"""
CSEE4119 Programming Assignment1
Author: Jing Tang
Date: 2022.3.14

Server Part
"""

import socket
from threading import Thread
import sys
import os
import time
from ChatApp import *

class Server():

    clientTable = {}
    messageQueue = {}
    acklist = {}
    flag = 0

    def __init__(self, servP):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.servP = (self.ip, servP)
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.servP)
        self.Thread_recv = Thread(target=self.recv)
        self.Thread_recvack = Thread(target=self.recvack)

    # Start the server
    def start(self):
        print(">>> Welcome to the Online Chat Room")
        print(f">>> Server has registered. The ip address is {self.ip}")
        try:
            self.Thread_recv.daemon = True
            self.Thread_recvack.daemon = True
            self.Thread_recv.start()
            self.Thread_recvack.start()
            while self.Thread_recv.isAlive():
                self.Thread_recv.join(1)
            while self.Thread_recvack.isAlive():
                self.Thread_recvack.join(1)
        except (KeyboardInterrupt, SystemExit):
            print("Keyboard Interrupt. Exiting.")
            sys.exit()

    def recvack(self):
        while True:
            data, srcAddr = self.udpSocket.recvfrom(1024)
            dec = str(data.decode()).split("  ")

            if dec[0] == "ack" and dec[1] == "group":
                if dec[2] in self.acklist:
                    self.acklist[dec[2]] = 1
                    print(f">>> ACK from {dec[2]} received")

            # Receive new client registration

            if dec[0] == "new":
                clientName = dec[1]
                if clientName not in self.clientTable:
                    updateinfo = "update"
                    self.broadcast(updateinfo)
                    for key in self.clientTable:
                        add = f"add  {key}  {self.clientTable[key][0]}  {self.clientTable[key][1]}"
                        self.udpSocket.sendto(add.encode(), srcAddr)
                    self.clientTable[clientName] = [eval(dec[2]), eval(dec[3]), 1]
                    print(">>> Client table updated.")
                    print(">>> Clients currently registered")
                    for key in self.clientTable:
                        print(f"-> {key} : {self.clientTable[key][0]}")
                    update = f"add  {clientName}  {self.clientTable[clientName][0]}  {self.clientTable[clientName][1]}"
                    self.broadcast(update)

                else:
                    ms = "The client name is already in use. Please give another one"
                    data = f"error  {ms}"
                    self.udpSocket.sendto(data.encode(), srcAddr)
                if clientName not in self.acklist:
                    self.acklist[clientName] = 0

            # Receive de-registration request
            if dec[0] == "exit":
                clientName = dec[1]
                ack = f"ack  dereg"
                self.udpSocket.sendto(ack.encode(), srcAddr)
                if clientName in self.clientTable:
                    self.clientTable[clientName][2] = 0
                update = f"del  {clientName}"
                self.broadcast(update)
                print(f">>> Client {clientName} left")

            # Receive offline message request
            if dec[0] == "offline":
                destName = dec[1]
                if destName in self.clientTable:
                    # add time stamp to the offline message
                    # save it to messageQueue
                    msg = f"({time.time()}) {' '.join(dec[2:])}"
                    if destName in self.messageQueue:
                        self.messageQueue[destName].append(msg)
                    else:
                        self.messageQueue[destName] = [msg]
                ack = f"ack  offline"
                self.udpSocket.sendto(ack.encode(), srcAddr)

            # Receive group chat request
            if dec[0] == "Channel_Message":
                clientName = dec[1]
                ms = f"Channel_Message  {' '.join(dec[2:])}"
                ack = "ack  group"
                self.udpSocket.sendto(ack.encode(), srcAddr)
                self.groupchat(ms, srcAddr)
                self.acklist[clientName] = 1
                time.sleep(0.5)
                for key in self.acklist:
                    if self.acklist[key] == 0:
                        if self.clientTable[key][2] == 1:
                            self.clientTable[key][2] = 0
                            print(f">>> {key} is now offline")
                            update = f"del  {key}"
                            self.broadcast(update)
                for key in self.acklist:
                    self.acklist[key] = 0

            # Receive re_registration request
            if dec[0] == "rereg":
                clientName = dec[1]
                # update the client table and broadcast the update
                if clientName in self.clientTable:
                    self.clientTable[clientName][2] = 1
                update = f"rereg  {clientName}"
                self.broadcast(update)
                print(f">>> Client {clientName} reconnected.")
                # send the offline message
                if clientName in self.messageQueue:
                    ntf = "hasmsg"
                    self.udpSocket.sendto(ntf.encode(), srcAddr)
                    print(f">>> Sent the offline message to {clientName}")
                    for msg in self.messageQueue[clientName]:
                        data = f"offline  {msg}"
                        self.udpSocket.sendto(data.encode(), srcAddr)
                    # cleanup the message queue
                    self.messageQueue[clientName] = []

    def recv(self):
        while True:
            data, srcAddr = self.udpSocket.recvfrom(1024)
            dec = str(data.decode()).split("  ")

            if dec[0] == "ack"and dec[1] == "group":
                if dec[2] in self.acklist:
                    self.acklist[dec[2]] = 1
                    print(f">>> ACK from {dec[2]} received")

            # Receive new client registration

            if dec[0] == "new":
                clientName = dec[1]
                if clientName not in self.clientTable:
                    updateinfo = "update"
                    self.broadcast(updateinfo)
                    for key in self.clientTable:
                        add = f"add  {key}  {self.clientTable[key][0]}  {self.clientTable[key][1]}"
                        self.udpSocket.sendto(add.encode(), srcAddr)
                    self.clientTable[clientName] = [eval(dec[2]), eval(dec[3]), 1]
                    print(">>> Client table updated.")
                    print(">>> Clients currently registered")
                    for key in self.clientTable:
                        print(f"-> {key} : {self.clientTable[key][0]}")
                    update = f"add  {clientName}  {self.clientTable[clientName][0]}  {self.clientTable[clientName][1]}"
                    self.broadcast(update)

                else:
                    ms = "The client name is already in use. Please give another one"
                    data = f"error  {ms}"
                    self.udpSocket.sendto(data.encode(), srcAddr)
                if clientName not in self.acklist:
                    self.acklist[clientName] = 0

            # Receive de-registration request
            if dec[0] == "exit":
                clientName = dec[1]
                ack = f"ack  dereg"
                self.udpSocket.sendto(ack.encode(), srcAddr)
                if clientName in self.clientTable:
                    self.clientTable[clientName][2] = 0
                update = f"del  {clientName}"
                self.broadcast(update)
                print(f">>> Client {clientName} left")

            # Receive offline message request
            if dec[0] == "offline":
                destName = dec[1]
                if destName in self.clientTable:
                    # add time stamp to the offline message
                    # save it to messageQueue
                    msg = f"({time.time()}) {' '.join(dec[2:])}"
                    if destName in self.messageQueue:
                        self.messageQueue[destName].append(msg)
                    else:
                        self.messageQueue[destName] = [msg]
                ack = f"ack  offline"
                self.udpSocket.sendto(ack.encode(), srcAddr)

            # Receive group chat request
            if dec[0] == "Channel_Message":
                clientName = dec[1]
                ms = f"Channel_Message  {' '.join(dec[2:])}"
                ack = "ack  gourp"
                self.udpSocket.sendto(ack.encode(), srcAddr)
                self.groupchat(ms, srcAddr)
                self.acklist[clientName] = 1
                time.sleep(0.5)
                for key in self.acklist:
                    if self.acklist[key] == 0:
                        if self.clientTable[key][2] == 1:
                            self.clientTable[key][2] = 0
                            update = f"del  {key}"
                            self.broadcast(update)
                            print(f">>> {key} is now offline")
                for key in self.acklist:
                    self.acklist[key] = 0

            # Receive re_registration request
            if dec[0] == "rereg":
                clientName = dec[1]
                # update the client table and broadcast the update
                if clientName in self.clientTable:
                    self.clientTable[clientName][2] = 1
                update = f"rereg  {clientName}"
                self.broadcast(update)
                print(f">>> Client {clientName} reconnected.")
                # send the offline message
                if clientName in self.messageQueue:
                    ntf = "hasmsg"
                    self.udpSocket.sendto(ntf.encode(), srcAddr)
                    print(f">>> Sent the offline message to {clientName}")
                    for msg in self.messageQueue[clientName]:
                        data = f"offline  {msg}"
                        self.udpSocket.sendto(data.encode(), srcAddr)
                    # cleanup the message queue
                    self.messageQueue[clientName] = []

    # broadcast information to all clients
    def broadcast(self, data):
        for key in self.clientTable:
            self.udpSocket.sendto(data.encode(), self.clientTable[key][0])

    # broadcast information to all other clients except the source client
    # if a client is offline, then save group message in messageQueue
    def groupchat(self, data, srcAddr):
        for key in self.clientTable:
            if self.clientTable[key][0] != srcAddr and self.clientTable[key][2] == 1:
                self.udpSocket.sendto(data.encode(), self.clientTable[key][0])
            elif self.clientTable[key][0] != srcAddr and self.clientTable[key][2] == 0:
                msg = f"({time.time()}) {data}"
                if key in self.messageQueue:
                    self.messageQueue[key].append(msg)
                else:
                    self.messageQueue[key] = [msg]


def startServer(port):
    try:
        server = Server(port)
        server.start()
    except KeyboardInterrupt:
        print("Exiting")
