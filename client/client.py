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
    sock.send(vote.encode())
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
