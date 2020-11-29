<<<<<<< HEAD
# Voting R US

## TODO
1. Encrypt and digital signature (including for authentication process)
2. Create dictionary (hashmap) on server for mantaining voting counts for each candidate in the format of [President: (PersonA: votes, PersonB: votes), Senator: (PersonC: votes, Person D: Votes)]
3. Get the vote of the client and print out message on who they want to vote for (if you want to send a dictionary instead of a string, use something like pickle to serialize the data) and keep track of votes on server side with the dictionary. Also, change the voter-registration for that particular user to then be False (last column)

## File Formats
### Voter registration (server)
- Username ActualPassword Hash(Password+Salt) Salt VotedBoolean
- The username is their firstname, lastname in camel case
- The actual password (the fake SSN) I left in so we can enter in proper values. Can probably store in another file (like .Passwords)
- The hash is the SHA256 hash of the Password + Salt

## Notes
1. Don't worry about edge cases. I don't think he really cares. Just try to finish the main parts of the proj first
2. Make each step a function (similar to the authentication example so it'll be easy to edit)

## How to run
1. Open up two shells. On one of them go to `/server` and on the other go to `/client`
2. Respectively, run `python server.py` and on the other shell, run `python client.py`

Small notes:
1. My default python interpreter is python3 so if your default is python2, just change step 2 to be `python3 file.py` with the respective file name
2. Run server before running client

## Annoying TODO
1. So you can't terminate a python interpreter with SIGINT(control C) if it's in an infinite while loop (which our server is in) so it's getting really annoying to have to kill the process each time with another shell. If someone wants to look into this, would be helpful. The problem is the server is always expecting some input from the client. I'm not sure how you could actually end it at that point since it's a blocking call. Don't really have to do this, just makes developing a bit easier, but if you want, feel free
=======
## TODO

Everything
>>>>>>> e5da98d51f1ee21d1479af23b9a9bf5734d1853f
