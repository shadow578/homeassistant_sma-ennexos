"""SMA API error classes."""


class SMAApiClientError(Exception):
    """Exception to indicate a general API error."""


class SMAApiCommunicationError(SMAApiClientError):
    """Exception to indicate a communication error."""


class SMAApiAuthenticationError(SMAApiClientError):
    """Exception to indicate an authentication error."""


class SMAApiParsingError(SMAApiClientError):
    """Exception to indicate a parsing error."""
