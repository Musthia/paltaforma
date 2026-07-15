from platformcore.security import hash_password, verify_password


class TestSecurity:

    def test_hash_and_verify(self):
        h = hash_password("test1234")
        assert h != "test1234"
        assert verify_password("test1234", h) is True
        assert verify_password("wrong", h) is False

    def test_different_hashes(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses different salts
