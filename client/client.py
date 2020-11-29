import socket

port = 8080 # connect on port 8080

# user inputs in their username and password
def authenticate(sock):
    print("Hello! Welcome to Voting R US")
    username = input("Username: ")
    password = input("Password: ")

    # send data to server to validate
    credentials = username + ":" + password
    sock.send(credentials.encode())
    resp = sock.recv(1024).decode()

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

    # Next step (fill in other functions here)

    # close the connection
    sock.close()


if __name__ == "__main__":
    main()
