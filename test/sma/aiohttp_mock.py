"""Helper for mocking aiohttp ClientSession requests."""

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar
from unittest.mock import MagicMock

from aiohttp import ClientError, ClientSession
from attr import dataclass


@dataclass
class CookieMock:
    """Mocked cookie."""

    value: str


class CookieJarMock:
    """Mocked cookie jar."""

    _cookies: dict[str, CookieMock]

    def __init__(self, cookies: dict[str, CookieMock]):
        """Initialize mock cookie jar."""
        self._cookies = cookies

    TCookieDefault = TypeVar("TCookieDefault")

    def get(self, name: str, default: TCookieDefault) -> CookieMock | TCookieDefault:
        """Get cookie by name."""
        return self._cookies.get(name, default)


class ClientResponseMock:
    """Mocked HTTP response."""

    data: Any
    status: int
    cookies: CookieJarMock

    def __init__(self, data: Any, status: int = 200, cookies: dict[str, str] = {}):
        """Initialize mock response."""
        self.data = data
        self.status = status
        self.cookies = CookieJarMock(
            cookies={name: CookieMock(value=value) for name, value in cookies.items()}
        )

    async def json(self) -> Any:
        """Return mock data."""
        return self.data

    @property
    def ok(self) -> bool:
        """Return True if status is less than 400."""
        return self.status < 400

    def raise_for_status(self):
        """Raise exception if status is not 2xx."""
        if not self.ok:
            raise ClientError(f"Response status is {self.status}")


@dataclass
class ResponseEntry:
    """Mock response object helper."""

    endpoint: str
    method: str = "GET"
    repeat: int | bool = 1

    status_code: int = 200
    data: Any = {}
    cookies: dict[str, str] = {}

    raises: Exception | None = None

    callback: Callable | None = None

    delay: float | None = None

    def match(self, endpoint: str, method: str) -> bool:
        """Return True if the response matches the endpoint and method."""
        return self.endpoint == endpoint and self.method == method

    @property
    def keep(self) -> bool:
        """Return True if the response should be kept active, False if it should be removed."""
        if isinstance(self.repeat, bool):
            return self.repeat

        return self.repeat > 0

    async def get_response(self) -> ClientResponseMock:
        """Return the response object."""
        if not isinstance(self.repeat, bool):
            self.repeat -= 1

        if self.delay is not None and self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.callback is not None:
            return self.callback()

        if self.raises is not None:
            raise self.raises

        return ClientResponseMock(
            data=self.data,
            status=self.status_code,
            cookies=self.cookies,
        )


@dataclass
class RequestEntry:
    """A recorded request."""

    method: str
    endpoint: str
    url: str

    headers: dict
    data: Any
    is_json: bool
    was_handled: bool


class AioHttpMock:
    """Mock Helper for aiohttp ClientSession."""

    __base_url: str
    __session: MagicMock

    __responses: list[ResponseEntry]
    __requests: list[RequestEntry]

    def __init__(self, base_url: str):
        """Initialize mock helper."""
        self.__base_url = base_url

        self.__session = MagicMock(spec=ClientSession)
        self.__session.request = self.__request

        self.__responses = []
        self.__requests = []

    @property
    def session(self):
        """Return the mocked session."""
        return self.__session

    def add_response(self, response: ResponseEntry):
        """Add a response to the mock."""
        self.__responses.append(response)

    def add_responses(self, responses: list[ResponseEntry]):
        """Add multiple responses to the mock."""
        for r in responses:
            self.add_response(r)

    @property
    def response_count(self) -> int:
        """Return the number of registered responses."""
        self.__cleanup()  # clear pending
        return len(self.__responses)

    def clear_responses(self):
        """Clear all registered responses."""
        self.__responses = []

    def get_request(self, method: str, endpoint: str) -> RequestEntry | None:
        """Return a recorded request."""
        for request in self.__requests:
            if request.method == method and request.endpoint == endpoint:
                self.__requests.remove(request)
                return request

        return None

    @property
    def request_count(self) -> int:
        """Return the number of recorded requests."""
        return len(self.__requests)

    def clear_requests(self):
        """Clear all recorded requests."""
        self.__requests = []

    async def __request(
        self, method: str, url: str, headers: dict, json: Any, data: Any
    ) -> ClientResponseMock:
        """Return a mocked response."""
        endpoint = url.replace(self.__base_url, "").strip("/")

        self.__cleanup()

        r = None
        for response in self.__responses:
            if response.match(endpoint, method):
                r = response
                break

        self.__requests.append(
            RequestEntry(
                method=method,
                endpoint=endpoint,
                url=url,
                headers=headers,
                data=json or data,
                is_json=json is not None,
                was_handled=r is not None,
            )
        )

        if r is None:
            return ClientResponseMock(data={}, status=404)

        return await r.get_response()

    def __cleanup(self):
        """Remove all responses that have been used up."""
        self.__responses = [r for r in self.__responses if r.keep]
