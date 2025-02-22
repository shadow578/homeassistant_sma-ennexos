"""unit tests for model.AuthTokenInfo."""

import pytest
from ..model import AuthTokenInfo, SMAApiParsingError

def test_from_dict_valid_dict():
    """Test that AuthTokenInfo.from_dict() parses a valid dict correctly."""

    # prepare dict
    token_dict = {
        "access_token": "abc",
        "refresh_token": "def",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    # call from_dict()
    token = AuthTokenInfo.from_dict(token_dict)

    # check result
    assert token.access_token == "abc"
    assert token.refresh_token == "def"
    assert token.token_type == "Bearer"
    assert token.expires_in == 3600

    # check seconds_until_expiration is about 3600 +- 10 seconds
    # (the checks above should not take more than 10 seconds)
    assert token.seconds_until_expiration > 3590 and token.seconds_until_expiration < 3610

    # check is_expired is False
    assert token.is_expired is False

def test_from_dict_invalid_dict():
    """Test that AuthTokenInfo.from_dict() raises an exception if the dict is invalid."""

    with pytest.raises(SMAApiParsingError):
        AuthTokenInfo.from_dict({})



