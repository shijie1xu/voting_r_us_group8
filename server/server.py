import socket
from hashlib import sha256
import signal
from Crypto.Cipher import AES
import os
import binascii
from hashlib import sha256
import client

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


# Generate IV from username(maybe vulnerable)
def write_IV(username):
    # Make an IV with first 16 byte of sha256 of username
    key = binascii.hexlify(sha256(username.encode()).digest()[0:8])
    # print('The Key You Made Was: ', [x for x in key])
    with open("../client/CBC_IV.IV", "wb") as file:
        file.write(key)


# Generate key randomly
def write_key():
    # Make a random key with 16 bytes
    key = binascii.hexlify(os.urandom(8))
    # print('The Key You Made Was: ', [x for x in key])
    with open("../client/CBC.key", "wb") as file:
        file.write(key)


# read key
def read_key():
    with open("../client/CBC.key", "rb") as file:
        keynew = file.read()
    return keynew


# read IV
def read_IV():
    with open("../client/CBC_IV.IV", "rb") as file:
        key_new = file.read()
    return key_new


# CBC encrypt
def CBC_encrypt(plaintext):
    iv = read_IV()
    key = read_key()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # encrypt using CBC mode
    plaintext_byte = plaintext.encode('utf-8')
    pad = len(plaintext_byte) % 16 * -1
    plaintext_byte_trimmed = plaintext_byte[16:pad]
    ciphertext = cipher.encrypt(plaintext_byte_trimmed)
    ciphertext = plaintext_byte[0:16] + ciphertext + plaintext_byte[pad:]
    return ciphertext


# CBC decrypt
def CBC_decrypt(ciphertext):
    iv = read_IV()
    key = read_key()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_byte = ciphertext
    pad = len(ciphertext_byte) % 16 * -1
    ciphertext_byte_trimmed = ciphertext_byte[16:pad]
    plaintext = cipher.decrypt(ciphertext_byte_trimmed)
    plaintext = ciphertext_byte[0:16] + plaintext + ciphertext_byte[pad:]
    return plaintext


# CBC vote encrypt
def CBC_encrypt_vote(plaintext):
    iv = read_IV()
    key = read_key()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # encrypt using CBC mode
    plaintext_byte = plaintext.encode('utf-8')
    pad = len(plaintext_byte) % 2 * -1
    plaintext_byte_trimmed = plaintext_byte[4:pad]
    ciphertext = cipher.encrypt(plaintext_byte_trimmed)
    ciphertext = plaintext_byte[0:4] + ciphertext + plaintext_byte[pad:]
    return ciphertext


# CBC vote decrypt
def CBC_decrypt_vote(ciphertext):
    iv = read_IV()
    key = read_key()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_byte = ciphertext
    pad = len(ciphertext_byte) % 2 * -1
    ciphertext_byte_trimmed = ciphertext_byte[4:pad]
    plaintext = cipher.decrypt(ciphertext_byte_trimmed)
    plaintext = ciphertext_byte[0:4] + plaintext + ciphertext_byte[pad:]
    return plaintext


def authenticateClient(client):
    # parse client string
    credentials_encrypted = client.recv(1024)
    credentials_decrypted = CBC_decrypt(credentials_encrypted)
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

def validate_tally_vote(client):
    # parse client string
    vote_encrypted = client.recv(1024)
    vote_decrypted = CBC_decrypt_vote(vote_encrypted)
    print(vote_decrypted)
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
