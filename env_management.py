import json
from cryptography.fernet import Fernet


env_file = 'env.json.enc'


def load_key():
    return open("secret.key", "rb").read()


def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data


def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data


def load_encrypted_env():
    key = load_key()
    with open(env_file, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data, key)
    return json.loads(decrypted_data)


def save_to_env(data):
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    with open(env_file, 'wb') as file:
        file.write(encrypted_data)
