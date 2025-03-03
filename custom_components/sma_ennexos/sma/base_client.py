"""SMA api base client."""

from __future__ import annotations

import asyncio
import socket
from logging import Logger
from typing import Any

import aiohttp
import async_timeout

from .model import (
    AuthToken,
    SMAApiAuthenticationError,
    SMAApiClientError,
    SMAApiCommunicationError,
)


class SMABaseClient:
    """base class for sma ennexOS client, handles core functionality."""

    _auth_data: AuthToken | None = None
    _session_id: str | None = None
    __session: aiohttp.ClientSession
    __host: str
    __base_url: str
    __request_timeout: int
    _logger: Logger | None

    def __init__(
        self,
        host: str,
        use_ssl: bool,
        session: aiohttp.ClientSession,
        request_timeout: int = 10,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the client."""
        self.__host = host
        self.__base_url = f"http{'s' if use_ssl else ''}://{self.__host}/api/v1"
        self.__session = session
        self.__request_timeout = request_timeout
        self._logger = logger

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ) -> aiohttp.ClientResponse:
        """Make a request to a api endpoint."""

        # build full request url
        url = f"{self.__base_url}/{endpoint}"

        # make the request
        try:
            # self._logger.debug(f"requesting {url}")
            async with async_timeout.timeout(self.__request_timeout):
                response = await self.__session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    # JSON payload
                    json=data if as_json else None,
                    # Form-Data payload
                    data=data if not as_json else None,
                )

                # remove any cookies set by the request, we handle them manually
                self.__session.cookie_jar.clear_domain(self.__host)

                # check for 401/403 unauthorized
                if response.status in (401, 403):
                    if self._logger:
                        self._logger.debug(
                            f"got {response.status} unauthorized on {url}"
                        )
                    raise SMAApiAuthenticationError(
                        "Invalid credentials",
                    )

                # create exception if response is not ok
                response.raise_for_status()
                return response
        except SMAApiClientError as exception:
            raise exception
        except asyncio.TimeoutError as exception:
            raise SMAApiCommunicationError(
                f"timeout fetching {url}",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise SMAApiCommunicationError(
                f"communication error fetching {url}",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise SMAApiClientError(f"error fetching {url}") from exception

    def _update_session_id(self, response: aiohttp.ClientResponse) -> None:
        """Update the session id."""
        session_cookie = response.cookies.get("JSESSIONID")
        if session_cookie is None:
            self._session_id = None
            raise SMAApiClientError("session cookie not found")

        self._session_id = session_cookie.value

        if self._logger:
            self._logger.debug(f"got session id {self._session_id}")

    @property
    def _auth_headers(self) -> dict:
        """Get auth and host origin headers.

        note: only valid if logged in.
        """
        return {
            **self._origin_headers,
            **self._session_headers,
            "Authorization": f"Bearer {self.auth_data.access_token}",
        }

    @property
    def _session_headers(self) -> dict:
        """Get session headers."""
        if self._session_id is None:
            raise SMAApiClientError("session id not available")

        return {
            "Cookie": f"JSESSIONID={self._session_id}",
        }

    @property
    def _origin_headers(self) -> dict:
        """Get host origin headers."""
        return {
            "Origin": f"{self.__base_url}",
            "Host": f"{self.__host}",
        }

    @property
    def auth_data(self) -> AuthToken:
        """Get auth_data object, or raise a exception if no auth data is available."""
        if (
            self._auth_data is None
            or self._auth_data.access_token is None
            or self._session_id is None
        ):
            raise SMAApiClientError("no auth data available")

        return self._auth_data

    @property
    def host(self) -> str:
        """Get the host."""
        return self.__host

    @property
    def base_url(self) -> str:
        """Get the api base url."""
        return self.__base_url
