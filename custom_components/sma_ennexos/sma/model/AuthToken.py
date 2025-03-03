"""SMA Auth token."""

from datetime import datetime, timedelta

from .errors import SMAApiParsingError


class AuthToken:
    """sma auth token info."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

    granted_at: datetime

    def __init__(
        self, access_token: str, refresh_token: str, token_type: str, expires_in: int
    ) -> None:
        """Initialize auth token info."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in

        self.granted_at = datetime.now()

    @property
    def time_until_expiration(self) -> timedelta:
        """Get the time until the token expires."""
        expires_at = self.granted_at + timedelta(seconds=self.expires_in)
        return expires_at - datetime.now()

    @property
    def seconds_until_expiration(self) -> int:
        """Get the seconds until the token expires."""
        return int(self.time_until_expiration.total_seconds())

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return self.seconds_until_expiration <= 0

    @classmethod
    def from_dict(cls, data: dict) -> "AuthToken":
        """Create from dict, verify required fields and their types."""
        if not isinstance(data, dict):
            raise SMAApiParsingError("auth token info is not a dict")

        if "access_token" not in data:
            raise SMAApiParsingError("missing field 'access_token' in auth token info")
        if "refresh_token" not in data:
            raise SMAApiParsingError("missing field 'refresh_token' in auth token info")
        if "token_type" not in data:
            raise SMAApiParsingError("missing field 'token_type' in auth token info")
        if "expires_in" not in data:
            raise SMAApiParsingError("missing field 'expires_in' in auth token info")

        if not isinstance(data["access_token"], str):
            raise SMAApiParsingError(
                "field 'access_token' in auth token info is not a string"
            )
        if not isinstance(data["refresh_token"], str):
            raise SMAApiParsingError(
                "field 'refresh_token' in auth token info is not a string"
            )
        if not isinstance(data["token_type"], str):
            raise SMAApiParsingError(
                "field 'token_type' in auth token info is not a string"
            )
        if not isinstance(data["expires_in"], int):
            raise SMAApiParsingError(
                "field 'expires_in' in auth token info is not an int"
            )

        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data["token_type"],
            expires_in=data["expires_in"],
        )
