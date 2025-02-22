"""utility to mock http responses by aiohttp."""


class CookieMock:
        """mock cookie entry."""

        value: str

        def __init__(self, value: str):
            """Initialize mock cookie entry."""
            self.value = value

class CookieJarMock:
    """mock cookie jar."""

    _cookies: list[tuple[str, CookieMock]]

    def __init__(self, cookies: list[tuple[str, CookieMock]]):
        """Initialize mock cookie jar."""
        self._cookies = cookies

    def get(self, name: str) -> CookieMock:
        """Get cookie by name."""
        for cookie_name, cookie in self._cookies:
            if cookie_name == name:
                return cookie

        raise KeyError(f"cookie {name} not found")

class ClientResponseMock:
    """mock http response."""

    data: any
    cookies: CookieJarMock

    def __init__(self, data: any, cookies: list[tuple[str, str]] = []):
        """Initialize mock http response."""
        self.data = data
        self.cookies = CookieJarMock(
            cookies=[(name, CookieMock(value=value)) for name, value in cookies]
        )

    async def json(self) -> any:
        """Return mock data."""
        return self.data

