import random 
import string

def generate_otp(length=5):
    characters = string.ascii_uppercase + string.digits  
    otp = ''.join(random.choices(characters, k=length))
    return otp