from cryptography.fernet import Fernet
from env_management import load_key, encrypt_data


def main():
    key = load_key()

    with open("env.json", "r") as file:
        env_data = file.read()

    encrypted_data = encrypt_data(env_data, key)

    with open("env.json.enc", "wb") as file:
        file.write(encrypted_data)


if __name__ == "__main__":
    main()
