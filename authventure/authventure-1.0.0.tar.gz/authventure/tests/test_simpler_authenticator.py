import pytest

from ..simpler_authenticator import SimplerAuthenticator


class TestSimplerAuthenticator:

    @pytest.fixture()
    def mocked_jwt(self, mocker):
        return mocker.patch('authventure.simpler_authenticator.jwt')

    def test_create_user_unexpirable_token(self, mocked_jwt):
        # Arrange
        expected_token = 'f4K3.us3R.t0K3n'
        mocked_jwt.encode.return_value = expected_token

        expected_secret = 'secret'
        simpler_authenticator = SimplerAuthenticator(expected_secret)

        expected_user_id = 'f4K3-us3R-1234'

        # Act
        token = simpler_authenticator.create_user_unexpirable_token(
            expected_user_id
        )

        # Assert
        mocked_jwt.encode.assert_called_once_with(
            {'userId': expected_user_id},
            expected_secret,
            algorithm='HS256'
        )

        assert token == expected_token

    def test_get_user_id_from_unexpirable_token(self, mocked_jwt):
        # Arrange
        token = 'f4K3.us3R.t0K3n'

        expected_user_id = 'f4K3-us3R-1234'
        expected_payload = {"userId": expected_user_id}

        mocked_jwt.decode.return_value = expected_payload

        expected_secret = 'secret'
        simpler_authenticator = SimplerAuthenticator(expected_secret)

        # Act
        user_id = simpler_authenticator.get_user_id_from_unexpirable_token(
            token
        )

        # Assert
        mocked_jwt.decode.assert_called_once_with(
            token,
            expected_secret,
            algorithms='HS256',
            options={'verify_signature': True, 'verify_exp': False}
        )

        assert user_id == expected_user_id
