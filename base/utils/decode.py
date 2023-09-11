import os
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from pathlib import Path
class DecodeKey:

    def decryption(self, arg_privatekey, arg_b64text):
        decoded_data = base64.b64decode(arg_b64text)
        decryptor = PKCS1_OAEP.new(arg_privatekey)
        decrypted = decryptor.decrypt(decoded_data)
        return decrypted

    def decode_key(self, key_name):

        PRIVATE_PATH=""
        PUBLIC_PATH=""
        
        key_name_path = f"{key_name}.bin"
        
        PRIVKEY = os.path.join(PRIVATE_PATH, "id_rsa")
        encoded_key_file = os.path.join(PUBLIC_PATH, key_name_path)

        if Path(encoded_key_file).exists():

            with open(PRIVKEY, 'rb') as f_privkey:
                privatekey = RSA.importKey(f_privkey.read())

            with open(encoded_key_file, "rb") as file_in:
                encoded_key = file_in.readline()
                
            
            result = self.decryption(privatekey, encoded_key).decode('ascii')
            
        else :
            
            result = key_name

        return result