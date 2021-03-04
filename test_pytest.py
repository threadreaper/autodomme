import random
import string
from io import BytesIO

import crypto_functions


def random_string():
    """Generates a random string between 1 and 2056 characters long"""
    length = random.randint(1, 2056)
    chars = string.ascii_letters + string.punctuation + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def random_bytes():
    """Generates random bytes between 1 and 2056 characters long"""
    length = random.randint(1, 2056)
    chars = string.ascii_letters + string.punctuation + string.digits
    return ''.join(random.choice(chars) for _ in range(length)).encode()


def test_package():
    """Unit test for the package function from crypto_functions module"""
    priv, pub = crypto_functions.get_key_pair()
    for case in (random_string(), random_bytes()):
        msg = BytesIO(crypto_functions.send_package(pub, priv, case, 'MSG'))
        header = crypto_functions.decrypt(priv, msg.read(512))
        signature = msg.read(512)
        assert crypto_functions.verify(pub, header, signature)
        (msg_type, length, f_key) = (header[0:3], int(header[3:13].decode()),
                                     header[13:])
        enc_msg = msg.read(length)
        assert msg_type.decode() == 'MSG'
        dec_msg = crypto_functions.Fernet(f_key).decrypt(enc_msg)
        assert crypto_functions._bytes(dec_msg) == \
            crypto_functions._bytes(case)


def test_sign_and_verify():
    """Unit test for cryptographic signatures"""
    priv, pub = crypto_functions.get_key_pair()
    msg = random_bytes()
    signature = crypto_functions.sign(priv, msg)
    verified = crypto_functions.verify(pub, msg, signature)
    assert verified


def test_bytes():
    """Unit test for _bytes function"""
    for case in (random_string(), random_bytes(), random.randint(0, 2056)):
        data = crypto_functions._bytes(case)
        assert type(data) == bytes


if __name__ == "__main__":
    test_package()
    test_sign_and_verify()
    test_bytes()
