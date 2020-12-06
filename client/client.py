import socket
from Crypto.Cipher import AES
import os
import binascii
from hashlib import sha256
from Crypto.PublicKey import RSA
import math

port = 8080  # connect on port 8080

username = ""
key = ""
iv = ""

# Generate IV from username(maybe vulnerable)
def write_IV(username):
    # Make an IV with first 16 byte of sha256 of username
    iv = binascii.hexlify(sha256(username.encode()).digest()[0:8])
    # print('The Key You Made Was: ', [x for x in key])
    with open("CBC_IV.IV", "wb") as file:
        file.write(key)

# Generate key randomly
def write_key():
    # Make a random key with 16 bytes
    key = binascii.hexlify(os.urandom(8))
    # print('The Key You Made Was: ', [x for x in key])
    with open("CBC.key", "wb") as file:
        file.write(key)

# CBC encrypt
def CBC_encrypt(plaintext, voting):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # encrypt using CBC mode
    plaintext_byte = plaintext.encode('utf-8')
    if voting:
        pad = len(plaintext_byte) % 2 * -1
    else:
        pad = len(plaintext_byte) % 16 * -1

    if voting:
        plaintext_byte_trimmed = plaintext_byte[4:pad]
    else:
        plaintext_byte_trimmed = plaintext_byte[16:pad]
    ciphertext = cipher.encrypt(plaintext_byte_trimmed)

    if voting:
        ciphertext = plaintext_byte[0:4] + ciphertext + plaintext_byte[pad:]
    else:
        ciphertext = plaintext_byte[0:16] + ciphertext + plaintext_byte[pad:]
    return ciphertext

# RSA SIGNING - for each voter sending their vote, a public/private keypair will be generated.
# However, in a real application, this would be generated by a trusted third-party entity
def sign_vote(vote_data):  # pass in voter's username as well as their vote data represented as bytes
    signature = 0
    key_set = RSA.generate(bits=1024)
    n, e, d = hex(key_set.n), hex(key_set.e), hex(key_set.d)  # public_key = {n,e}, private_key = {n, d}
    # wite public and private keys to a file called {voter's username}.txt so that server can verify -- in this order, store n, e, d for each line
    with open(username + ".txt", "w") as f:
        f.write(n + "\n")
        f.write(e + "\n")
        f.write(d + "\n")

    hash = sha256(
        vote_data).hexdigest()  # hash message then sign; NOTE: our ballot is already encrypted by using CBC from hash of voter data, so this is extra secure
    hash = "0x" + hash
    hash = int(hash, 0)

    d = int(d, 0)
    n = int(n, 0)
    signature = pow(hash, d, n)  # --> take hash^d (mod n)
    return signature

# user inputs in their username and password
def authenticate(sock):
    # global username  TODO: Why is this necessary?
    print("Hello! Welcome to Voting R US")
    username = input("Username: ")
    password = input("Password: ")

    # send data to server to validate
    credentials = username + ":" + password

    # generate IV and key
    write_IV(username)
    print("Generated IV based on username")
    write_key()
    print("Generated random key for CBC.")
    print("CBC IV:", iv)
    print("CBC key:", key)

    # vote info should be encrypted
    credentials_encrypted = CBC_encrypt(credentials, False)  # encrypt credentials using CBC
    sock.send(credentials_encrypted)
    resp = sock.recv(1024).decode()

    if resp == "Accepted":
        return True
    return False

# prompt the user to vote for their corresponding choices
def prompt_user_vote(sock):
    print("----------------Candidates----------------")
    print("Category 1: President")
    print("(1) Person A, (2) Person B, (3) Person C")
    print("\nCategory 2: Senator")
    print("(4) Person D, (5) Person E, (6) Person F")
    print("\nCategory 3: Representative")
    print("(7) Person G, (8) Person H, (9) Person I")

    print("\nDirections")
    print("\tPlease enter a single choice from each category by using the respective number next to their name")
    print("\tYou may also write 'n' or 'N' to pass the vote for a specific category\n")

    pres = input("President: ")
    sen = input("Senator: ")
    rep = input("Representative: ")

    # send data to server to validate
    vote = pres + ":" + sen + ":" + rep

    # vote info should be encrypted
    print("Encrypting vote with CBC...")
    vote_encrypted = CBC_encrypt(vote, True)
    print("Vote has been encrypted using CBC.")

    # PRIYA ADDED
    # vote info should be signed
    print("Digitally signing vote...")
    signature = sign_vote(vote.encode('utf-8'))
    print("Vote signed")

    print("Sending vote to server...")
    sock.send(vote_encrypted)
    sock.send(str(signature).encode())  # add vote along with signature

    resp = sock.recv(1024).decode()
    print("Sever response:", resp)

    # check to see if choices are valid
    if resp == "Accepted":
        return True
    return False

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP socket object
    sock.connect(('127.0.0.1', port))  # connect to the server on localhost

    # Authentication
    isValid = authenticate(sock)
    if not isValid:
        print("You have either not been registered to vote or you have entered in your credentials improperly")
        sock.close()
        exit(0)

    validVote = prompt_user_vote(sock)
    if not validVote:
        print("\nOne or more of your choices are invalid. Please recast your vote properly")
        sock.close()
        exit(0)
    else:
        print("\nCongratulations! Your vote has been cast!")

    # Next step (fill in other functions here)

    # close the connection
    sock.close()


if __name__ == "__main__":
    main()
