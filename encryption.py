import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_key():
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise Exception("Encryption key is not set")
    decoded = base64.urlsafe_b64decode(key)
    if len(decoded) not in (16, 24, 32):
        raise Exception("Encryption key must decode to 16, 24, or 32 bytes")
    return decoded

def encrypt_file(data):
    aes = AESGCM(get_key())
    nonce = os.urandom(12)
    return nonce + aes.encrypt(nonce, data, None)

def decrypt_file(data):
    aes = AESGCM(get_key())
    nonce = data[:12]
    encrypted_data = data[12:]
    return aes.decrypt(nonce, encrypted_data, None)
