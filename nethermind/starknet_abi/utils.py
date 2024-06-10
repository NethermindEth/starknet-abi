from Crypto.Hash import keccak


def starknet_keccak(data: bytes) -> bytes:
    """
    A variant of eth-keccak that computes a value that fits in a Starknet field element.

    .. doctest ::

        >>> from nethermind.starknet_abi.utils import starknet_keccak
        >>> starknet_keccak(b"transfer").hex()
        '0083afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e'

    """

    k = keccak.new(digest_bits=256)
    k.update(data)
    masked = int.from_bytes(k.digest(), byteorder="big") & (2**250 - 1)  # 250 byte mask
    return masked.to_bytes(length=32, byteorder="big")
