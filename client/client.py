import socket
from Crypto.Cipher import AES
import os
import binascii
from hashlib import sha256


port = 8080 # connect on port 8080

username = ""


# Generate IV from username(maybe vulnerable)
def write_IV(username):
    # Make an IV with first 16 byte of sha256 of username
    key = binascii.hexlify(sha256(username.encode()).digest()[0:8])
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


# read key
def read_key():
    with open("CBC.key", "rb") as file:
        keynew = file.read()
    return keynew


# read IV
def read_IV():
    with open("CBC_IV.IV", "rb") as file:
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


# user inputs in their username and password
def authenticate(sock):
    global username
    print("Hello! Welcome to Voting R US")
    username = input("Username: ")
    password = input("Password: ")

    # send data to server to validate
    credentials = username + ":" + password

    # vote info should be encrypted
    write_IV(username)
    write_key()
    credentials_encrypted = CBC_encrypt(credentials) # encrypt credentials using CBC
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
    vote_encrypted = CBC_encrypt_vote(vote)

    sock.send(vote_encrypted)
    resp = sock.recv(1024).decode()

    # check to see if choices are valid
    if resp == "Accepted":
        return True
    return False

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP/IP socket object
    sock.connect(('127.0.0.1', port)) # connect to the server on localhost

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
