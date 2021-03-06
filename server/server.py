import socket
from hashlib import sha256
import signal
from Crypto.Cipher import AES
import os
import binascii
from hashlib import sha256
from Crypto.PublicKey import RSA

port = 8080  # listen on port 8080
totalClientsVoted = 10  # only 10 clients will be allowed to vote

acceptedStr = "Accepted".encode()
rejectedStr = "Rejected".encode()

client_username = ''  # the current client's username
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
    "N": 0  # this keeps track of how many people skipped a category
}

# candidate choices by category (N stands for none -> candidate wants to skip vote for this category)
pres_cands = ["1", "2", "3", "N"]
sen_cands = ["4", "5", "6", "N"]
rep_cands = ["7", "8", "9", "N"]

cand_map = {
    "1": "Person A",
    "2": "Person B",
    "3": "Person C",
    "4": "Person D",
    "5": "Person E",
    "6": "Person F",
    "7": "Person G",
    "8": "Person H",
    "9": "Person I"
}

# read key
def read_key():
    with open("../client/CBC.key", "rb") as file:
        keynew = file.read()
    return keynew

# read IV
def read_IV():
    with open("../client/CBC_IV", "rb") as file:
        iv = file.read()
    return iv

# CBC decrypt
def CBC_decrypt(ciphertext, voting):
    key = read_key()
    iv = read_IV()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_byte = ciphertext
    if voting:
        pad = len(ciphertext_byte) % 2 * -1
    else:
        pad = len(ciphertext_byte) % 16 * -1

    if voting:
        ciphertext_byte_trimmed = ciphertext_byte[4:pad]
    else:
        ciphertext_byte_trimmed = ciphertext_byte[16:pad]
    plaintext = cipher.decrypt(ciphertext_byte_trimmed)

    if voting:
        plaintext = ciphertext_byte[0:4] + plaintext + ciphertext_byte[pad:]
    else:
        plaintext = ciphertext_byte[0:16] + plaintext + ciphertext_byte[pad:]
    return plaintext

def authenticateClient(client):
    global client_username

    # parse client string
    credentials_encrypted = client.recv(1024)
    print("Decrypting client authentication using CBC...")
    credentials_decrypted = CBC_decrypt(credentials_encrypted, False)
    print("Authentication decrypted.")
    client_username, client_password = credentials_decrypted.decode().split(":")

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

# RSA VERIFICATION - add to server.py - for each voter sending their vote, a public/private keypair will be
# generated. However, in a real application, this would be generated by a trusted third-party entity
def verify_signature(signature, username, vote_data):
    # server opens the RSA keypair file corresponding to username
    n = ""
    e = ""
    d = ""

    try:
        with open("../client/" + username + ".txt", "r") as f:
            n = f.readline()
            e = f.readline()
            d = f.readline()
    except IOError:
        # if filename does not exist, return False - server should close connection
        return False

    # create hash from vote data (should be bytes)
    n = int(n, 0)
    e = int(e, 0)
    hash = sha256(vote_data).hexdigest()
    hash = "0x" + hash
    hash = int(hash, 0)
    signature = int(signature)
    created_signature = pow(signature, e, n)  # take signature^e mod n to verify
    return hash == created_signature

def update_voted(client_username):
    with open("voter-registration", 'r') as f:
        data = f.readlines()

    # adding to new file just to see if it works
    with open("voter-registration", 'w') as f:
        for line in data:
            username, password, hash_pass, salt, voted = line.split()
            # if usernames match, update value to True
            if client_username == username:
                voted = "True"
            f.write(username + " " + password + " " + hash_pass + " " + salt + " " + voted + "\n")


def validate_tally_vote(client):
    # parse client string
    vote_encrypted = client.recv(1024)
    print("Decrypting client vote using CBC...")
    vote_decrypted = CBC_decrypt(vote_encrypted, True)
    print("Vote decrypted.")

    # PRIYA ADDED - validate signature
    signature = client.recv(1024).decode()
    print("Verifying client digital signature...")
    if not verify_signature(signature, client_username, vote_decrypted):
        print("Signature verification failed.")
        return False
    print("Signature verified.")

    pres, sen, rep = vote_decrypted.decode().split(":")

    # convert to upper case chars
    pres, sen, rep = pres.upper(), sen.upper(), rep.upper()

    # check for invalid votes
    if pres not in pres_cands or sen not in sen_cands or rep not in rep_cands:
        return False

    # accumulate tally
    votes[pres] += 1
    votes[sen] += 1
    votes[rep] += 1

    # mark user as voted
    update_voted(client_username)
    return True

def printCurrTally():
    print("President votes")
    for i in range(1, 4):
        print(cand_map[str(i)], ":", votes[str(i)])

    print("\nSenator votes")
    for i in range(4, 7):
        print(cand_map[str(i)], ":", votes[str(i)])

    print("\nRepresentative votes")
    for i in range(7, 10):
        print(cand_map[str(i)], ":", votes[str(i)])

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
            print("Client vote has been successfully cast and recorded.")
            client.send(acceptedStr)
        else:
            print("Client has failed to vote properly")
            client.send(rejectedStr)
        print("------------------------------------\n")

        client.close()

        print("-----------Current Vote Count-----------")
        printCurrTally()
        print("------------------------------------\n")

        # PRIYA ADDED - reset client-username to nobody
        global client_username
        if clientCount == totalClientsVoted:
            exit(0)

if __name__ == "__main__":
    main()
