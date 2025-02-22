"""SMA api base client."""

from __future__ import annotations
from logging import Logger

import asyncio
import socket
import aiohttp
import async_timeout

from .model import (
    AuthTokenInfo,
    SMAApiAuthenticationError,
    SMAApiCommunicationError,
    SMAApiClientError,
)


class DummyLogger:
    """dummy logger in case no logger is provided."""

    def __getattr__(self, name):
        """Stub all methods."""
        return lambda *args, **kwargs: None


class SMABaseClient:
    """base class for sma data manager client, handles core functionality."""

    _auth_data: AuthTokenInfo | None = None

    _session_id: str | None = None

    _session: aiohttp.ClientSession

    _host: str

    _base_url: str

    _request_timeout: int

    _logger: Logger

    def __init__(
        self,
        host: str,
        use_ssl: bool,
        session: aiohttp.ClientSession,
        request_timeout: int = 10,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the client."""
        self._host = host
        self._base_url = f"http{'s' if use_ssl else ''}://{self._host}/api/v1"
        self._session = session
        self._request_timeout = request_timeout

        self._logger = logger if logger is not None else DummyLogger()

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ) -> aiohttp.ClientResponse:
        """Make a request to a api endpoint."""

        # build full request url
        url = f"{self._base_url}/{endpoint}"

        # make the request
        try:
            # self._logger.debug(f"requesting {url}")
            async with async_timeout.timeout(self._request_timeout):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    # JSON payload
                    json=data if as_json else None,
                    # Form-Data payload
                    data=data if not as_json else None,
                )

                # remove any cookies set by the request, we handle them manually
                self._session.cookie_jar.clear_domain(self._host)

                # check for 401/403 unauthorized
                if response.status in (401, 403):
                    self._logger.debug(f"got {response.status} unauthorized on {url}")
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

    def update_session_id(self, response: aiohttp.ClientResponse) -> None:
        """Update the session id."""
        session_cookie = response.cookies.get("JSESSIONID")
        if session_cookie is None:
            self._session_id = None
            raise SMAApiClientError("session cookie not found")

        self._session_id = session_cookie.value
        self._logger.debug(f"got session id {self._session_id}")

    @property
    def _auth_headers(self) -> dict:
        """Get auth and host origin headers.

        note: only valid if logged in.
        """
        self.require_session()

        return {
            **self._origin_headers,
            **self._session_headers,
            "Authorization": f"Bearer {self._auth_data.access_token}",
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
            "Origin": f"{self._base_url}",
            "Host": f"{self._host}",
        }

    def require_session(self) -> None:
        """Require a active session."""
        if (
            (self._auth_data is None)
            or (self._auth_data.access_token is None)
            or (self._session_id is None)
        ):
            raise SMAApiClientError("session not available")

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host
