"""SMA API Client."""

from __future__ import annotations

import contextlib
from datetime import timedelta
from itertools import chain
from logging import Logger
from urllib.parse import quote

import aiohttp

from .base_client import SMABaseClient
from .model import (
    AuthTokenInfo,
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
    SMAApiAuthenticationError,
    SMAApiClientError,
    SMAApiCommunicationError,
    SMAApiParsingError,
)

LOGIN_RESULT_ALREADY_LOGGED_IN = "already_logged_in"
LOGIN_RESULT_TOKEN_REFRESHED = "token_refreshed"
LOGIN_RESULT_NEW_TOKEN = "new_token"


class SMAApiClient(SMABaseClient):
    """API Client for SMA ennexOS devices."""

    __username: str | None
    __password: str | None

    __request_retries: int

    def __init__(
        self,
        host: str,
        username: str | None,
        password: str | None,
        session: aiohttp.ClientSession,
        use_ssl: bool = True,
        request_timeout: int = 10,
        request_retries: int = 3,
        logger: Logger | None = None,
    ) -> None:
        """SMA ennexOS API Client."""
        super().__init__(
            host=host,
            session=session,
            use_ssl=use_ssl,
            request_timeout=request_timeout,
            logger=logger,
        )

        self.__username = username
        self.__password = password

        self.__request_retries = request_retries

    async def login(self) -> str:
        """Login to the api.

        :returns: login result, one of LOGIN_RESULT_* constants
        """

        # if already logged in and token is still valid for at least 5 minutes, do nothing
        if (
            self._auth_data is not None
            and self._auth_data.time_until_expiration > timedelta(minutes=5)
        ):
            if self._logger:
                self._logger.debug("already logged in, skipping login")
            return LOGIN_RESULT_ALREADY_LOGGED_IN

        # if we have a session and refresh token, try refreshing the token
        if self._session_id is not None and self._auth_data is not None:
            try:
                self._auth_data = await self.__refresh_token(
                    self._auth_data.refresh_token
                )
                if self._logger:
                    self._logger.debug("refreshed token successfully")
                return LOGIN_RESULT_TOKEN_REFRESHED
            except SMAApiClientError:
                # refresh failed, try to re-login with username and password
                if self._logger:
                    self._logger.debug("failed to refresh token, trying to re-login")

        # if all else fails, get a new token using username and password
        if self.__username is None or self.__password is None:
            raise ValueError("username and password are required for login")
        self._auth_data = await self.__get_new_token(self.__username, self.__password)

        if self._logger:
            self._logger.debug("got new token successfully")
        return LOGIN_RESULT_NEW_TOKEN

    async def __get_new_token(self, username: str, password: str) -> AuthTokenInfo:
        """Get a new access token using username and password."""
        token_response = await self.make_request(
            method="POST",
            endpoint="token",
            data={
                "grant_type": "password",
                "username": username,
                "password": password,
            },
            headers={
                **self._origin_headers,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            as_json=False,  # use form data instead of json payload
        )

        # update session id
        self.update_session_id(token_response)
        if self._session_id is None:
            raise SMAApiClientError("No session id received")

        # set access token
        token_data = await token_response.json()
        return AuthTokenInfo.from_dict(token_data)

    async def __refresh_token(self, refresh_token: str) -> AuthTokenInfo:
        """Get a new access token using a refresh token."""
        token_response = await self.make_request(
            method="POST",
            endpoint="token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={
                **self._origin_headers,
                **self._session_headers,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            as_json=False,  # use form data instead of json payload
        )

        # set access token
        token_data = await token_response.json()
        return AuthTokenInfo.from_dict(token_data)

    async def logout(self) -> None:
        """Logout from the api."""
        if self._logger:
            self._logger.debug("logging out")

        # logout request, ignore errors
        with contextlib.suppress(Exception):
            await self.make_request(
                method="DELETE",
                endpoint=f"refreshtoken?refreshToken={quote(self.auth_data.refresh_token)}",
            )

        # clear auth data
        self._auth_data = None
        self._session_id = None

    async def get_all_components(self) -> list[ComponentInfo]:
        """Get a list of all available components and their ids."""

        async def _get_navigation_int(
            parent_id: str | None = None,
        ) -> list[ComponentInfo]:
            """Get data from /navigation endpoint."""
            if self._logger:
                self._logger.debug(f"getting navigation data for parent={parent_id}")

            navigation_response = await self.make_request(
                method="GET",
                endpoint="navigation"
                + (f"?parentId={quote(parent_id)}" if parent_id else ""),
                headers={
                    **self._auth_headers,
                    "Accept": "application/json",
                },
            )

            # check & validate response
            navigation = await navigation_response.json()
            if not isinstance(navigation, list):
                raise SMAApiClientError("received invalid response: not a list")
            return [ComponentInfo.from_dict(component) for component in navigation]

        async def _add_extra_info(component: ComponentInfo) -> None:
            """Get extra info for a component."""
            if self._logger:
                self._logger.debug(
                    f"getting extra info for component={component.component_id}"
                )

            device_info_response = await self.make_request(
                method="GET",
                endpoint=f"widgets/deviceinfo?deviceId={component.component_id}",
                headers={
                    **self._auth_headers,
                    "Accept": "application/json",
                },
            )

            # try adding extra info to component
            device_info = await device_info_response.json()
            component.add_extra(device_info)

        # get root component, only consider the first one
        root_components = await _get_navigation_int()
        if len(root_components) == 0:
            raise SMAApiClientError("received invalid response: no root component")
        root_component = root_components[0]

        # root component should be of type "Plant"
        if root_component.component_type != "Plant":
            raise SMAApiClientError(
                "received invalid response: "
                f"root componentType is not 'Plant' but '{root_component.component_type}'"
            )

        # get all components that are children of the root component
        all_components = await _get_navigation_int(
            parent_id=root_component.component_id
        )

        # build final list
        all_components = [root_component] + all_components

        # add extra info to all components and return
        # (Plant components don't have extra info)
        for component in all_components:
            if component.component_type != "Plant":
                await _add_extra_info(component)

        if self._logger:
            self._logger.debug(f"got {len(all_components)} components")
        return all_components

    async def get_all_live_measurements(
        self, component_ids: list[str]
    ) -> list[ChannelValues]:
        """Get live data for all channels of the requested components."""
        payload = [{"componentId": id} for id in component_ids]

        measurements_response = await self.make_request(
            method="POST",
            endpoint="measurements/live",
            data=payload,
            headers={
                **self._auth_headers,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            as_json=True,
        )

        measurements = await measurements_response.json()
        return self.__parse_measurements(measurements)

    async def get_live_measurements(
        self, query: list[LiveMeasurementQueryItem]
    ) -> list[ChannelValues]:
        """Get live data for the requested channels."""
        payload = [item.to_dict() for item in query]
        measurements_response = await self.make_request(
            method="POST",
            endpoint="measurements/live",
            data=payload,
            headers={
                **self._auth_headers,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            as_json=True,
        )

        measurements = await measurements_response.json()
        return self.__parse_measurements(measurements)

    def __parse_measurements(self, measurements: list[dict]) -> list[ChannelValues]:
        """Convert raw measurements response to python model."""
        if not isinstance(measurements, list):
            raise SMAApiClientError("received invalid response: not a list")

        # parse measurements to ChannelValues
        # ChannelValues.from_dict() returns a list with one or
        # more ChannelValues (support for array channels requires this), so
        # we need to flatten the result afterwards
        cvs = [ChannelValues.from_dict(measurement) for measurement in measurements]

        # flatten list of lists
        return list(chain.from_iterable(cvs))

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ) -> aiohttp.ClientResponse:
        """Make a request to an API endpoint, handling re-auth and retries."""
        make_request_impl = super().make_request

        async def _make_request_w(
            tries: int = 0, did_reauth: bool = False
        ) -> aiohttp.ClientResponse:
            try:
                if self._logger:
                    self._logger.debug(f"requesting {endpoint} ({tries})")
                return await make_request_impl(method, endpoint, data, headers, as_json)
            except SMAApiAuthenticationError as exception:
                # on auth error, re-login and try again
                # only if this is the first time we've tried to re-auth

                # don't re-auth on /token endpoint
                if (
                    not did_reauth
                    and endpoint != "token"
                    and not endpoint.startswith("refreshtoken")
                ):
                    if self._logger:
                        self._logger.debug(
                            "SMA auth error (%s), re-authenticating", exception
                        )

                    try:
                        await self.logout()
                        await self.login()
                    except SMAApiClientError as reauth_exception:
                        # re-login failed, raise original exception
                        if self._logger:
                            self._logger.debug(
                                "re-authentication failed (%s)", reauth_exception
                            )
                        raise exception from None

                    # re-login ok, try again
                    return await _make_request_w(tries=tries + 1, did_reauth=True)
                else:
                    raise exception
            except (
                SMAApiCommunicationError,
                SMAApiParsingError,
                SMAApiClientError,
            ) as exception:
                # on other API errors, retry up to the configured number of times
                if tries <= self.__request_retries:
                    if self._logger:
                        self._logger.debug("SMA API error (%s), retrying", exception)
                    return await _make_request_w(tries=tries + 1, did_reauth=did_reauth)
                else:
                    raise exception

        return await _make_request_w()
