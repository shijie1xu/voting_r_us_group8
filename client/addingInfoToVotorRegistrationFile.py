import string
import hmac
from hashlib import sha256
Firstname = input("Please enter your first name:\n")
Lastname = input("Please enter your last name:\n")
Firstname = Firstname.lower()
Firstname = Firstname[0].upper() + Firstname[1:]
Lastname = Lastname.lower()
Lastname = Lastname[0].upper() + Lastname[1:]
user = Firstname + Lastname
SSN = input("Please enter your Social Security Number:\n")
PW = input("Please enter your password:\n")
key = b'DECLARATION'
h = hmac.new(key,b'',sha256)
h.update(bytes(PW, encoding='utf-8'))
with open("voter-registration", "ab") as file:
    file.write(bytes(user, encoding='utf-8') + b' ' + bytes(SSN, encoding='utf-8') + b' ' + h.hexdigest().encode('utf-8') + b' ' + bytes(PW, encoding='utf-8') + b' ' + b'False' + b'\n')