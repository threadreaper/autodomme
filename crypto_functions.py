from __future__ import annotations

import binascii
import hashlib
from socket import socket
from io import BytesIO
from PIL import Image

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

import inspect


def whoami():
    '''Return the module name of where the call came from.'''

    # This will return a list of frame records, [1] is the frame
    # record of the caller.
    frame_records = inspect.stack()[1]

    # Index 1 of frame_records is the full path of the module,
    # we can then use inspect.getmodulename() to get the
    # module name from this path.
    calling_module = inspect.getmodulename(frame_records[1])

    return calling_module


def get_key_pair() -> tuple[rsa.RSAPrivateKeyWithSerialization,
                            rsa.RSAPublicKey]:
    """
    Creates and returns an RSA key pair.

    :returns: A private key and a public key.
    :rtype: :type:`tuple`[:class:`rsa.RSAPrivateKeyWithSerialization`,\
        :type:`bytes`]
    """
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=4096)
    pub = private_key.public_key()
    return private_key, pub


def _bytes(msg) -> bytes:
    """Given a message of unknown type, bytes or string, returns bytes"""
    if type(msg) != bytes:
        return str(msg).encode()
    return msg


def encrypt(pub_key: rsa.RSAPublicKey, msg: str | bytes) -> bytes:
    """
    Encrypt a chat message and return the encrypted string.

    :param pub_key: RSA public key to encrypt the message with.
    :type pub_key: :class:`rsa.RSAPublicKey`
    :param msg: Message to encrypt.
    :type msg: :type:`str`
    :return: Encrypted message.
    :rtype: bytes
    """
    msg = _bytes(msg)
    return pub_key.encrypt(
        msg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                          algorithm=hashes.SHA256(), label=None))


def decrypt(priv_key: rsa.RSAPrivateKeyWithSerialization, msg: bytes) -> bytes:
    """
    Decrypts a message and returns the plain text.

    :param priv_key: RSA private key to decrypt the message with.
    :type priv_key: :class:`rsa.RSAPrivateKeyWithSerialization`
    :param msg: Message to decrypt
    :type msg: bytes
    :return: The decrypted message
    :rtype: :type:`str`
    """
    return priv_key.decrypt(msg, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None))


def hash_password(password: str, salt: bytes) -> str:
    """
    Hashes a password using the original salt stored in the database and
    returns the hash.

    :param password: The submitted password to check.
    :type password: :type:`str`
    :param salt: The original salt used to hash the user's password.
    :type salt: bytes
    """
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return binascii.hexlify(key).decode()


def sign(private_key: rsa.RSAPrivateKeyWithSerialization, msg: bytes) -> bytes:
    """
    Signs a message with a private key to provide proof of authenticity.

    :param private_key: The private key to sign the message with.
    :type private_key: :class:`rsa.RSAPrivateKeyWithSerialization`
    :param msg: The message to sign.
    :type msg: `str`
    :return: The signature.
    :rtype: `bytes`
    """
    return private_key.sign(msg, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256())


def verify(public_key: rsa.RSAPublicKey, msg: bytes, signature: bytes) -> bool:
    """
    Verifies the authenticity of a signed transmission.

    :param public_key: The public key to verify the signature against.
    :type public_key: :class:`rsa.RSAPublicKey`
    :param msg: The signed message.
    :type msg: `bytes`
    :param signature: The signature.
    :type signature: `bytes`
    :returns: True if the signature was verified, False otherwise.
    :rtype: `bool`
    """
    try:
        public_key.verify(signature, msg, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return True
    except InvalidSignature:
        return False


def get_image(filename: str) -> bytes:
    """
    Takes a string containing the full path to an image and returns the
    images as bytes.

    :param filename: Full path to the image file.
    :type filename: `str`
    :return: The image as bytes.
    :rtype: `bytes`
    """
    image = Image.open(str(filename))
    with BytesIO() as bio:
        image.save(bio, format="PNG")
        del image
    return bio.getvalue()


def send_package(pub_key: rsa.RSAPublicKey,
                 private_key: rsa.RSAPrivateKeyWithSerialization,
                 msg: str | bytes, msg_type: str,
                 socket: socket = None) -> bytes:
    """
    Packages an encrypted transmission and sends it if a socket is provided.
    Packaged transmission consists of a 512 byte header containing the
    transmission type, the length of the content and the symmetric key used to
    encrypt the content, followed by a 512 byte RSA signature, with the
    remainder being the symmetrically encrypted content. Returns the packaged
    transmission.

    :param pub_key: The RSA Public Key to use to encrypt the header.
    :type pub_key: :class:`rsa.RSAPublicKey`
    :param msg: The data to be transmitted.
    :type msg: `str` or  `bytes`
    :param type: The type of transmission, one of MSG, IMG, SES, or FOL
    :type type: `str`
    :return: The packaged transmission.
    :rtype: `bytes`
    """
    if msg_type == 'IMG':
        get_image(str(msg))

    f_key = Fernet.generate_key()
    out_msg = Fernet(f_key).encrypt(_bytes(msg))
    length = str(len(out_msg)).zfill(10)
    header = msg_type + length + f_key.decode()
    signature = sign(private_key, _bytes(header))
    header = encrypt(pub_key, _bytes(header))
    if socket:
        with BytesIO(header + signature + out_msg) as file:
            chunk = file.read(512)
            while chunk:
                socket.send(chunk)
                chunk = file.read(512)
    return header + signature + out_msg


def open_package(public_key: rsa.RSAPublicKey,
                 private_key: rsa.RSAPrivateKeyWithSerialization,
                 socket: socket) -> tuple[str, bytes]:
    """
    Receive a packaged transmission over a socket, decrypt the header, verify
    the signature, and finally decrypt and return the content.
    """
    enc_header = socket.recv(512)
    signature = socket.recv(512)
    header = decrypt(private_key, enc_header)
    try:
        verify(public_key, header, signature)
        (msg_type, length, f_key) = (header[0:3].decode(),
                                     int(header[3:13].decode()),
                                     header[13:])
        enc_msg = socket.recv(length)
        msg = Fernet(f_key).decrypt(enc_msg)
        return (msg_type, msg)
    except InvalidSignature:
        return ('ERR', _bytes('Warning: Signature mismatch!  Message is a\
            forgery!'))
