"""SMA API client session helper."""

import asyncio
import contextlib
import socket
from collections.abc import Awaitable, Callable
from logging import Logger
from typing import Any, Literal

import aiohttp
import async_timeout

from custom_components.sma_ennexos.sma.model import AuthToken
from custom_components.sma_ennexos.sma.model.errors import (
    SMAApiAuthenticationError,
    SMAApiClientError,
)


class SMAClientSession:
    """Session helper for SMA API client."""

    __session: aiohttp.ClientSession
    __host: str
    __base_url: str

    __timeout: float | None
    __retries: int
    __logger: Logger | None

    session_id: str | None = None
    token: AuthToken | None = None

    reauth_hook: Callable[[str], Awaitable[None]] | None = None

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        base_url: str,
        timeout: float | None = None,
        retries: int | None = None,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the session."""
        self.__session = session
        self.__host = host
        self.__base_url = base_url
        self.__timeout = timeout
        self.__retries = retries or 1
        self.__logger = logger

    @property
    def host(self) -> str:
        """Get the host of the session."""
        return self.__host

    @property
    def base_url(self) -> str:
        """Get the base url of the session."""
        return self.__base_url

    @property
    def __base_headers(self) -> dict:
        """Base headers for all requests."""
        return {
            "Origin": self.__base_url,
            "Host": self.__host,
        }

    @property
    def __session_headers(self) -> dict:
        """Headers for a request within a session, but not authentificated."""
        if self.session_id is None:
            raise SMAApiClientError("Not in a active session")

        return {
            **self.__base_headers,
            "Cookie": f"JSESSIONID={self.session_id}",
        }

    @property
    def __auth_headers(self) -> dict:
        """Headers for authenticated requests."""
        if self.token is None:
            raise SMAApiClientError("Not authenticated")

        return {
            **self.__session_headers,
            "Authorization": f"Bearer {self.token.access_token}",
        }

    def __update_session_cookie(self, response: aiohttp.ClientResponse) -> None:
        """Update the session cookie from a response."""
        session_cookie = response.cookies.get("JSESSIONID", None)
        if session_cookie is None:
            return

        self.session_id = session_cookie.value
        if self.__logger:
            self.__logger.debug(f"got session id {self.session_id}")

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        endpoint: str,
        data: Any | None = None,
        json: dict | list | None = None,
        headers: dict = {},
        auth: Literal["none", "session", "full"] = "none",
    ) -> aiohttp.ClientResponse:
        """Make a request to a api endpoint."""

        # can only have either data or json
        if data is not None and json is not None:
            raise ValueError("data and json can not be used together")

        # must have at least one retry
        if self.__retries < 1:
            raise ValueError("retries must be at least 1")

        url = f"{self.__base_url}/{endpoint}"

        last_error = SMAApiClientError("Unknown error")  # should not happen
        for _ in range(self.__retries):
            try:
                async with async_timeout.timeout(self.__timeout):
                    # process auth headers on every retry, as they might have changed
                    # due to re-auth
                    auth_headers = {}
                    if auth == "none":
                        auth_headers = self.__base_headers
                    elif auth == "session":
                        auth_headers = self.__session_headers
                    elif auth == "full":
                        auth_headers = self.__auth_headers

                    response = await self.__session.request(
                        method=method,
                        url=url,
                        data=data,
                        json=json,
                        headers={
                            **auth_headers,
                            **headers,
                        },
                    )

                    # remove any cookies set by the request, we handle them manually
                    self.__session.cookie_jar.clear()

                    self.__update_session_cookie(response)

                    # check if unauthorized
                    if response.status in (401, 403):
                        # ignore any errors during reauth
                        with contextlib.suppress(Exception):
                            if self.reauth_hook:
                                await self.reauth_hook(endpoint)

                        last_error = SMAApiAuthenticationError("Unauthorized")
                        continue

                    response.raise_for_status()
                    return response
            except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror) as err:
                if self.__logger:
                    self.__logger.debug(f"Error fetching '{url}': {err}")
                last_error = err

                # retry
                continue

        raise SMAApiClientError(f"Error fetching '{url}': {last_error}") from last_error
