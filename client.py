"""
CSEE4119 Programming Assignment1
Author: Jing Tang
Date: 2022.3.14

Client Part
"""

import socket
import sys
from threading import Thread, Lock
import os
import time
from ChatApp import *
import signal

class Client():

    ack = 0
    flag = 1
    error = 0

    def __init__(self, name, ip, servP, clientP):
        self.clientName = name
        self.clientAddr = (ip, clientP)
        self.servAddr = (ip, servP)
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientTable = {}
        self.lock = Lock()
        self.Thread_recv = Thread(target=self.recv)
        self.Thread_send = Thread(target=self.send)

    def registration(self):
        try:
            self.udpSocket.bind(self.clientAddr)
            data = f"new  {self.clientName}  {self.clientAddr}  {self.servAddr}"
            self.udpSocket.sendto(data.encode(), self.servAddr)
            self.Thread_recv.daemon = True
            self.Thread_send.daemon = True
            self.Thread_recv.start()
            self.Thread_send.start()
            while self.Thread_recv.isAlive():
                self.Thread_recv.join(1)
            #self.Thread_recv.join()
            while self.Thread_send.isAlive():
                self.Thread_send.join(1)
        except (KeyboardInterrupt, SystemExit):
            print("Caught keyboard interrupt. Exiting")
            sys.exit()

    def send(self):
        while True:
            self.ack = 0
            time.sleep(0.5)
            if self.error == 1:
                break

            comm = input(">>> ")
            commli = comm.split(" ")
            mode = commli[0]
            destAddr = self.servAddr

            # Sending de-registration request
            if mode == "dereg":
                if commli[1] != self.clientName:
                    print(">>> [You cannot dereg someone else]")
                else:
                    data = f"exit  {self.clientName}"
                    self.udpSocket.sendto(data.encode(), destAddr)
                    if self.setTimeout(time.time(), data, destAddr) == -1:
                        print(">>> [Server not responding]")
                        print(">>> [Exiting]")
                        os._exit(1)

            # Sending chat info directly to another user
            elif mode == "send":
                destName = commli[1]
                ms = " ".join(commli[2:])
                if destName == self.clientName:
                    print(">>> [You cannot send a message to yourself]")
                elif destName in self.clientTable:
                    # the user is currently online
                    if self.clientTable[destName][2] == 1:
                        data = f"direct  {self.clientName} : {ms}"
                        destAddr = self.clientTable[destName][0]
                    # the user is offline
                    else:
                        data = f"offline  {destName}  {self.clientName} : {ms}"
                        destAddr = self.servAddr
                        print(f">>> [No ACK from {destName}, message sent to server.]")
                    self.udpSocket.sendto(data.encode(), destAddr)
                    if self.setTimeout(time.time(), data, destAddr) == -1:
                        if destAddr != self.servAddr:
                            data = f"offline  {destName}  {self.clientName} : {ms}"
                            print(f">>> [No ACK from {destName}, message sent to server.]")
                            self.udpSocket.sendto(data.encode(), self.servAddr)
                        else:
                            print(">>> [Message sent failed]")
                            print(">>> [Server is shut down]")
                            print(">>> [Exiting]")
                else:
                    print(">>> [The destination user does not existed.]")

            # Starting a group chat
            elif mode == "send_all":
                ms = " ".join(commli[1:])
                data = f"Channel_Message  {self.clientName}  {self.clientName} : {ms}"
                self.udpSocket.sendto(data.encode(), destAddr)
                if self.setTimeout(time.time(), data, destAddr) == -1:
                    print(">>> [Server Not Responding]")

            # log back to the server
            elif mode == "reg":
                name = commli[1]
                if name in self.clientTable:
                    if self.clientTable[name][2] == 0:
                        self.clientTable[name][2] = 1
                        data = f"rereg  {name}"
                        self.udpSocket.sendto(data.encode(), destAddr)
                    else:
                        print(">>> [The Client is active]")

            else:
                print(">>> [The command is invalid. Please retry.]")

    def recv(self):
        while True:
            data, srcAddr = self.udpSocket.recvfrom(1024)
            datali = data.decode().split("  ")
            if datali[0] == "ack":
                #self.ack = 1
                if datali[1] == "direct":
                    print(f">>> [Message has been received by {datali[2]}.]")

                elif datali[1] == "dereg":
                    print(f">>> [You are now offline. Bye.]")

                elif datali[1] == "offline":
                    print(f">>> [Messages received by the server and saved.]")

                elif datali[1] == "group":
                    print(">>> [Message received by the server.]")

                self.ack = 1

            # A new client added in, update the client table
            if datali[0] == "add" and srcAddr == self.servAddr:
                if datali[1] not in self.clientTable:
                    self.clientTable[datali[1]] = [eval(datali[2]), eval(datali[3]), 1]

            if datali[0] == "update":
                print("[Client Table Updated]")
                sys.stdout.write(">>> ")
                sys.stdout.flush()

            # A client gets offline, update the client table
            elif datali[0] == "del":
                if datali[1] in self.clientTable:
                    self.clientTable[datali[1]][2] = 0
                if datali[1] != self.clientName:
                    print("[Client Table Updated]")
                    sys.stdout.write(">>> ")
                    sys.stdout.flush()

            # A client log back, update the client table
            elif datali[0] == "rereg":
                if datali[1] in self.clientTable:
                    self.clientTable[datali[1]][2] = 1

            # Receiving direct message from another user
            elif datali[0] == "direct":
                ack = f"ack  direct  {self.clientName}"
                self.udpSocket.sendto(ack.encode(), srcAddr)
                print(f"{' '.join(datali[1:])}")
                sys.stdout.write(">>> ")
                sys.stdout.flush()

            # Print out error message and terminate
            elif datali[0] == "error":
                print(f"{' '.join(datali[1:])}")
                self.error = 1
                break

            # Print out error message without terminate
            elif datali[0] == "err2":
                print(' '.join(datali[1:]))

            # Receiving group chat message
            elif datali[0] == "Channel_Message":
                ack = f"ack  group  {self.clientName}"
                self.udpSocket.sendto(ack.encode(), self.servAddr)
                print(f"{' '.join(datali[:])}")
                sys.stdout.write(">>> ")
                sys.stdout.flush()

            # Receiving offline message
            elif datali[0] == "hasmsg":
                print(f">>> [You have message]")

            elif datali[0] == "offline":
                sys.stdout.write(">>> ")
                sys.stdout.flush()
                print(" ".join(datali[1:]))
                
    def setTimeout(self, starttime,data, destAddr):
        count = 0
        while (self.ack == 0):
            if (time.time()-starttime==0.5):
                self.udpSocket.sendto(data.encode(), destAddr)
                count += 1
                if (count >= 5):
                    return -1
                starttime = time.time()


def startClient(name, ip, servP, clientP):
    client = Client(name, ip, servP, clientP)
    client.registration()




