import keyring
import base64
from cryptography.fernet import Fernet, InvalidToken

class EncryptionUtil:
    SERVICE_NAME = "TExApp"

    @staticmethod
    def save_key_to_keyring(token_name: str, token: str):
        """Stores a Fernet key (base64 string) in the system keyring."""
        keyring.set_password(EncryptionUtil.SERVICE_NAME, token_name, token)

    @staticmethod
    def load_key_from_keyring(token_name: str) -> str | None:
        """Retrieves the Fernet key from system keyring."""
        return keyring.get_password(EncryptionUtil.SERVICE_NAME, token_name)

    @staticmethod
    def generate_key() -> str:
        """Generates a base64 Fernet key string."""
        return Fernet.generate_key().decode()

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        try:
            f = Fernet(key.encode())
            return f.encrypt(data.encode()).decode()
        except Exception as e:
            print(f"[Encrypt Error] {e}")
            return data

    @staticmethod
    def decrypt_data(data: str, key: str) -> str:
        try:
            f = Fernet(key.encode())
            return f.decrypt(data.encode()).decode()
        except InvalidToken:
            print("❌ Invalid encryption key or corrupted data.")
            return "[DECRYPTION FAILED]"
        except Exception as e:
            print(f"[Decrypt Error] {e}")
            return "[DECRYPTION FAILED]"
