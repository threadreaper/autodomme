from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import binascii
import hashlib


def get_key_pair() -> tuple[rsa.RSAPrivateKeyWithSerialization, bytes]:
    """Creates and returns an RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=4096)
    pub = private_key.public_key()
    public_key = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return private_key, public_key


def encrypt(pub_key: rsa.RSAPublicKey, msg: str) -> bytes:
    """
        Encrypt a chat message and return the encrypted string.

        :param pub_key: RSA public key to encrypt the message with.
        :type pub_key: :class:`rsa.RSAPublicKey`
        :param msg: Message to encrypt.
        :type msg: string
        :return: Encrypted message.
        :rtype: bytes
        """
    return pub_key.encrypt(msg.encode('utf8'),
                           padding.OAEP(mgf=padding.MGF1(
                               algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None))


def decrypt(priv_key: rsa.RSAPrivateKeyWithSerialization, msg: bytes) -> str:
    """
    Decrypts a message and returns the plain text.

    :param priv_key: RSA private key to decrypt the message with.
    :type priv_key: :class:`rsa.RSAPrivateKeyWithSerialization`
    :param msg: Message to decrypt
    :type msg: bytes
    :return: The decrypted message
    :rtype: str
    """
    text = priv_key.decrypt(msg, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None))
    return text.decode()


def hash_password(password: str, salt: bytes) -> str:
    """
    Hashes a password using the original salt stored in the database and
    returns the hash.

    :param password: The submitted password to check.
    :type password: str
    :param salt: The original salt used to hash the user's password.
    :type salt: bytes
    """
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return binascii.hexlify(key).decode()


def encrypt_file(filename: str) -> tuple[bytes, str, str]:
    """
    Encrypts a file and returns the encrypted file, its size in bytes and
    the symmetric key used to encrypt it.

    :param filename: /path/to/file
    :type filename: path or filename
    :returns: Encrypted file, size in bytes, symmetric key
    :rtype: tuple[bytes, str, str]
    """
    with open(filename, 'rb') as file:
        file_data = file.read()
    f_key = Fernet.generate_key()
    fern = Fernet(f_key)
    out_file = fern.encrypt(file_data)
    return out_file, str(len(out_file)), f_key.decode()


def encrypt_message(msg: str) -> tuple[bytes, str, str]:
    """
    Encrypts a long message and returns the encrypted message, its size
    in bytes and the symmetric key used to encrypt it.

    :param msg: The plaintext message to encrypt.
    :type msg: str
    :returns: Encrypted message, size in bytes and symmetric key
    :rtype: tuple[bytes, str, str]
    """
    f_key = Fernet.generate_key()
    fern = Fernet(f_key)
    out_msg = fern.encrypt(msg.encode())
    return out_msg, str(len(out_msg)), f_key.decode()


def decrypt_file(file, fern_key):
    """Decrypt a received file"""
    return Fernet(fern_key).decrypt(file)


def load_pem(pub_key: bytes) -> rsa.RSAPublicKey:
    """Serializes and returns an RSA public key"""
    return serialization.load_pem_public_key(pub_key)
