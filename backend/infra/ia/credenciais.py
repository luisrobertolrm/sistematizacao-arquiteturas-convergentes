from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr


class CofreCredenciais:
    def __init__(self, chave_externa: SecretStr) -> None:
        self.cifra: Fernet = Fernet(chave_externa.get_secret_value().encode("ascii"))

    def criptografar(self, token: SecretStr) -> bytes:
        return self.cifra.encrypt(token.get_secret_value().encode("utf-8"))

    def descriptografar(self, cifrado: bytes) -> SecretStr:
        try:
            return SecretStr(self.cifra.decrypt(cifrado).decode("utf-8"))
        except (InvalidToken, UnicodeDecodeError) as erro:
            raise ValueError("Credencial protegida inválida ou chave incompatível.") from erro
