import socket
from hashlib import sha256
import signal

port = 8080 # listen on port 8080
totalClientsVoted = 10 # only 10 clients will be allowed to vote

acceptedStr = "Accepted".encode()
rejectedStr = "Rejected".encode()

# keep track of how many votes each candidate recieves
votes = {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0,
    "5": 0,
    "6": 0,
    "7": 0,
    "8": 0,
    "9": 0,
    "N": 0 # this keeps track of how many people skipped a category
}

# candidate choices by category (N stands for none -> candidate wants to skip vote for this category)
pres_cands = ["1", "2", "3", "N"]
sen_cands = ["4", "5", "6", "N"]
rep_cands = ["7", "8", "9", "N"]

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

def validate_tally_vote(client):
    # parse client string
    vote = client.recv(1024).decode()
    pres, sen, rep = vote.split(":")

    # convert to upper case chars
    pres, sen, rep = pres.upper(), sen.upper(), rep.upper()

    # check for invalid votes
    if pres not in pres_cands or sen not in sen_cands or rep not in rep_cands:
        return False

    # accumulate tally
    votes[pres] += 1
    votes[sen] += 1
    votes[rep] += 1
    return True

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

        # Vote tally
        print("-------------Vote tally-------------")
        validVote = validate_tally_vote(client)
        if validVote:
            print("Client vote has been successfully done")
            print(votes)
            client.send(acceptedStr)
        else:
            print("Client has failed to vote properly")
            client.send(rejectedStr)
        print("------------------------------------\n")

        # Next step (fill in other functions here)

        client.close()

        if clientCount == totalClientsVoted:
            exit(0)

if __name__ == "__main__":
    main()
