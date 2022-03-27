"""
CSEE4119 Programming Assignment1
Author: Jing Tang
Date: 2022.3.14

Main function: read the input and determine which mode it is
"""

import socket
import threading
import os
import sys
from server import *
from client import *

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(">>> Please give an valid command line\n")
    else:
        # start server
        if sys.argv[1] == "-s":
            if sys.argv[2].isnumeric():
                serverPortS = int(sys.argv[2])
                if 1024 < serverPortS < 65535:
                    servPortS = int(sys.argv[2])
                    startServer(servPortS)
                else:
                    print(">>> Please give a valid port number")
            else:
                print(">>> Please give a valid port number")

        # client registration
        elif sys.argv[1] == '-c':
            if len(sys.argv) != 6:
                print(">>> Please give a valid command line for client registration\n")
            else:
                clientName = sys.argv[2]
                serverIP = sys.argv[3]
                serverPortC = sys.argv[4]
                clientPort = sys.argv[5]

                if serverPortC.isnumeric() and clientPort.isnumeric():
                    serverPortC = int(serverPortC)
                    clientPort = int(clientPort)
                    if int(serverPortC) < 1024 or int(serverPortC) > 65535:
                        print(">>> Please give a port number in range 1024-65535")
                    elif clientPort < 1024 or clientPort > 75535:
                        print(">>> Please give a port number in range 1024-65535")
                    else:
                        startClient(clientName, serverIP, serverPortC, clientPort)
                else:
                    print(">>> Please give a valid port number")

        else:
            print(">>> Please giva a valid registration infomation")

