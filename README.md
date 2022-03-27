# CSEE4119 Programming Assignment 1

- Author: Jing Tang
- UNI: jt3300

There are three files for this project, including ChatApp.py (which read the argument in
and determine which mode it will later start up), server.py (handle all implementations in
server mode), and client.py (handle all implementations in client mode).


To start the program, type in:
- $ python3 ChatApp.py -s </port number/> 
- eg. python3 ChatApp.py -s 8000

It will start the server and give back its ip address in the window so that other clients
  could start their connection through this ip address.
  
- $ python3 ChatApp.py -c </username/> </ip-address/> </server-port-number/> </client-port-number/>
- eg. Python3 ChatApp.py -c user1 127.0.0.1 8000 9000
(ip address of the server should be given after registration of server)

It will connect a client with the server and server will read in all this information, save
  it and broadcast the new-in to all other clients that has already connected.
  
After connecting with 3 clients, we could start using it for chatting.
There are several command for choosing in client mode.
  
- send </destination-name/> </message/> 
- eg. >>> send user1 hello my name is jing

It will send a message directly to another user. If the user is offline, then the message should
  be sent to server and save in server's message queue. </message/> could be written without a 
  quotation mark.
  
- send_all </message/>
- eg. >>> send_all how are you guys?
  
It will start a group chat and send the message to all other users that are currently online. If
  a user is offline, then the message will be saved in server's message queue and resend it to 
  this user after it logs back. </message/> could be written without a quotation mark.
  
- dereg </username/>
- eg. >>> dereg user1

It will de-register the user from the server. The server will mark it as offline and broadcast the
  update to all other clients.
  
- reg </username/>
- eg. >>> reg user1

It will register back to the server. The server will mark it as online and broadcast the update to
  all other clients. Meanwhile, the server will send all messages it saved in message queue with
  a time stamp to the user.
  

For Data Structures, I used two dictionaries to save client information and offline message. Both keys
are the clientName, so the structure does not allow two clients to have the same username. Each
client has its own client table, so when sending direct message, it could directly use this table 
to check the status of its destination user. Each time after the sever updates its client table,
it will broadcast its change to all the users.
  
For Algorithm Design, I design the whole structure based on Multi-threading. For client side, I used
two threads, each for sending and receiving. And I also have a timeout function which will resend the
packet for five rounds of timeout. Then for server side, I also used two threads, and they look exactly
the same. This is used to wait for the ack from all clients for group chat. Since one thread need to be
sleep for 500ms to wait for ack, there must be another thread which could receive the ACK or other requests.
When the server receives the ACK message from a specific client, it could change the acklist to 1.
If the server mention that a client could no longer accept messages, it will change the status of this 
client to offline.

After several rounds of testing, I didn't find any specific errors or bugs from the code, and 
it should fulfill all requirements.
  

