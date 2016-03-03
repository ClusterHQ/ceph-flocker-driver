"""
SSH key utility that should be in twisted.
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from twisted.conch.ssh.keys import Key

__all__ = ["generate_rsa_key"]


def generate_rsa_key(bits=4096):
    """
    Generate a SSH key.
    """
    key_primitive = rsa.generate_private_key(
        key_size=int(bits),
        public_exponent=65537,
        backend=default_backend(),
        )
    return Key(key_primitive)
