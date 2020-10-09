# pylint: skip-file
"""Declares :class:`BaseSymmetricKeyTestCase`."""
import asyncio
import os


class BaseSymmetricKeyTestCase:
    """Test base class that provides common tests for symmetric encryption
    backends.
    """
    __module__ = 'unimatrix.ext.crypto.tests'

    def setUp(self):
        self.backend = self.get_backend()
        self.key = self.backend.symmetric()

    def get_backend(self):
        """Return the backend used by the test case."""
        return self.get_backend_class()(**self.get_backend_kwargs())

    def get_backend_class(self):
        """Return the backend class used by the test case."""
        return self.backend_class

    def get_backend_kwargs(self):
        """Return the keyword arguments to instantiate the backend class."""
        raise NotImplementedError("Subclasses must override this method.")

    def test_encrypt_decrypt(self):
        """Test if the implementation can succesfully encrypt and decrypt
        using a key.
        """
        if not self.backend.has_capabilities(['encrypt', 'decrypt']):
            self.skipTest("Encryption is not supported.")
        pti = b'Hello world!'
        ct = self.key.encrypt(pti)
        pto = self.key.decrypt(ct)
        self.assertEqual(pti, pto)

    def test_encrypt_decrypt_binary(self):
        """Test if the implementation can succesfully encrypt and decrypt
        a byte-sequence using a key.
        """
        if not self.backend.has_capabilities(['encrypt', 'decrypt']):
            self.skipTest("Encryption is not supported.")
        pti = os.urandom(32)
        ct = self.key.encrypt(pti)
        pto = self.key.decrypt(ct)
        self.assertEqual(pti, pto)

    def test_async_encrypt_decrypt(self):
        """Test if the implementation can succesfully encrypt and decrypt
        using a key.
        """
        if not self.backend.has_capabilities(['encrypt:async', 'decrypt:async']):
            self.skipTest("Encryption is not supported.")

        async def afunc():
            pti = b'Hello world!'
            ct = await self.key.async_encrypt(pti)
            pto = await self.key.async_decrypt(ct)
            self.assertEqual(pti, pto)

        asyncio.run(afunc())

    def test_async_encrypt_decrypt_binary(self):
        """Test if the implementation can succesfully encrypt and decrypt
        a byte-sequence using a key.
        """
        if not self.backend.has_capabilities(['encrypt:async', 'decrypt:async']):
            self.skipTest("Encryption is not supported.")

        async def afunc():
            pti = os.urandom(32)
            ct = await self.key.async_encrypt(pti)
            pto = await self.key.async_decrypt(ct)
            self.assertEqual(pti, pto)

        asyncio.run(afunc())

    def test_async_encrypt_sync_decrypt(self):
        """Test if the implementation can succesfully asynchronously encrypt
        and  synchronously decrypt using a key.
        """
        if not self.backend.has_capabilities(['encrypt:async', 'decrypt:async']):
            self.skipTest("Encryption is not supported.")

        async def afunc():
            pti = os.urandom(32)
            ct = await self.key.async_encrypt(pti)
            pto = self.key.decrypt(ct)
            self.assertEqual(pti, pto)

        asyncio.run(afunc())

    def test_sync_encrypt_async_decrypt(self):
        """Test if the implementation can succesfully synchronously encrypt
        and  asynchronously decrypt using a key.
        """
        if not self.backend.has_capabilities(['encrypt:async', 'decrypt:async']):
            self.skipTest("Encryption is not supported.")

        async def afunc():
            pti = os.urandom(32)
            ct = self.key.encrypt(pti)
            pto = await self.key.async_decrypt(ct)
            self.assertEqual(pti, pto)

        asyncio.run(afunc())

    def test_generate_new_symmetric_key(self):
        """Test generating a new symmetric key."""
        if not self.backend.has_capability('generate:symmetric'):
            self.skipTest("Symmetric key generation is not supported.")
        key = self.backend_class.generate()
