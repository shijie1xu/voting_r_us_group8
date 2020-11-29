import socket
from hashlib import sha256
import signal

port = 8080 # listen on port 8080
totalClientsVoted = 10 # only 10 clients will be allowed to vote

acceptedStr = "Accepted".encode()
rejectedStr = "Rejected".encode()

def authenticateClient(client):
    # parse client string
    credentials = client.recv(1024).decode()
    client_username, client_password = credentials.split(":")

    # read data from voter registration file to see if valid match
    with open("voter-registration", 'r') as f:
        for line in f:
            username, password, hash_pass, salt, voted = line.split()
            # if usernames match, compare data
            if client_username == username:
                # make sure first and only vote
                if voted == "True":
                    return False

                # make sure password matches
                saltedPass = client_password + salt
                if (sha256(saltedPass.encode()).hexdigest() == hash_pass):
                    return True

    # if we reach here, the user isn't in the registered file (invalid client)
    return False

def main():
    # create TCP/IP socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind to port and only listen for incoming traffic from localhost
    sock.bind(('127.0.0.1', port))

    # listen for a max of 10 connections at any single time
    sock.listen(10)
    print("Server listening on port", port)

    # keep track of how many clients have voted
    clientCount = 0
    while True:
        # Establish connection with client.
        client, addr = sock.accept()
        clientCount += 1

        # Authentication
        print("-----------Authenticating-----------")
        validAuthentication = authenticateClient(client)
        if validAuthentication:
            print("Client has been authenticated")
            client.send(acceptedStr)
        else:
            print("Client has failed authentication")
            client.send(rejectedStr)
        print("------------------------------------\n")

        # Next step (fill in other functions here)

        client.close()

        if clientCount == totalClientsVoted:
            exit(0)

if __name__ == "__main__":
    main()
