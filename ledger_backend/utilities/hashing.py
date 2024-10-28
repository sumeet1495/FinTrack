import hashlib
#
from abstractions.utility import IUtility


# This class provides various hashing algorithms (MD5, SHA1, SHA224, SHA256, SHA384, SHA512)
# and can be used to securely hash data such as passwords or other sensitive information.
class HashingUtility(IUtility):

    # Constructor method to initialize the utility with a unique request identifier (URN).
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self.urn = urn
    
    # Compute and return the MD5 hash of the provided data.
    # MD5 is fast but not recommended for cryptographic purposes due to vulnerabilities.
    def md5(self, data: bytes) -> str:
        """
        Returns the MD5 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.md5(data).hexdigest()
    
    # Compute and return the SHA1 hash of the provided data.
    # SHA1 is also considered insecure for cryptographic use.
    def sha1(self, data: bytes) -> str:
        """
        Returns the SHA1 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.sha1(data).hexdigest()

    # Compute and return the SHA224 hash of the provided data.
    # SHA224 is a truncated version of SHA256.
    def sha224(self, data: bytes) -> str:
        """
        Returns the SHA224 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.sha224(data).hexdigest()
    
    # Compute and return the SHA256 hash of the provided data.
    # SHA256 is a widely used cryptographic hash that is considered secure.
    def sha256(self, data: bytes) -> str:
        """
        Returns the SHA256 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.sha256(data).hexdigest()

    # Compute and return the SHA384 hash of the provided data.
    # SHA384 produces a larger hash and is useful for more complex encryption scenarios.
    def sha384(self, data: bytes) -> str:
        """
        Returns the SHA384 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.sha384(data).hexdigest()
    
    # Compute and return the SHA512 hash of the provided data.
    # SHA512 provides the largest hash output in the SHA-2 family.
    def sha512(self, data: bytes) -> str:
        """
        Returns the SHA512 hash of the given data.
        :param data: the data to hash (bytes)
        """
        return hashlib.sha512(data).hexdigest()
