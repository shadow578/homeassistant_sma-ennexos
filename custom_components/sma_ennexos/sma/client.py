"""SMA API Client."""

from __future__ import annotations

import contextlib
import json
import re
from datetime import timedelta
from enum import Enum
from itertools import chain
from logging import Logger
from urllib.parse import quote

import aiohttp

from custom_components.sma_ennexos.sma.session import SMAClientSession

from .model import (
    AuthToken,
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
    SMAApiClientError,
)


class LoginResult(str, Enum):
    """Result of a login attempt."""

    ALREADY_LOGGED_IN = "already_logged_in"
    TOKEN_REFRESHED = "token_refreshed"
    NEW_TOKEN = "new_token"


class SMAApiClient:
    """API Client for SMA ennexOS devices."""

    __raw_session: aiohttp.ClientSession
    __session: SMAClientSession
    __logger: Logger | None

    __host_base_url: str

    __username: str | None
    __password: str | None

    def __init__(
        self,
        host: str,
        username: str | None,
        password: str | None,
        session: aiohttp.ClientSession,
        use_ssl: bool = True,
        request_timeout: float = 10.0,
        request_retries: int = 3,
        logger: Logger | None = None,
    ) -> None:
        """SMA ennexOS API Client."""
        self.__raw_session = session
        self.__host_base_url = f"{'https' if use_ssl else 'http'}://{host}"

        self.__session = SMAClientSession(
            session=session,
            host=host,
            base_url=f"{self.__host_base_url}/api/v1",
            timeout=request_timeout,
            retries=request_retries,
            logger=logger.getChild("session") if logger else None,
        )

        async def reauth_hook(endpoint: str) -> None:
            """Session re-auth hook."""
            # do not re-auth on token endpoints
            if endpoint == "token" or endpoint.startswith("refreshtoken"):
                return

            await self.logout()
            await self.login()

        self.__session.reauth_hook = reauth_hook

        self.__username = username
        self.__password = password

        self.__logger = logger

    @property
    def host(self) -> str:
        """Hostname of the device the client is connected to."""
        return self.__session.host

    async def login(self) -> LoginResult:
        """Login to the api.

        :returns: login result, one of LOGIN_RESULT_* constants
        """

        # if already logged in and token is still valid for at least 5 minutes, do nothing
        token = self.__session.token
        if token is not None and token.time_until_expiration > timedelta(minutes=5):
            if self.__logger:
                self.__logger.debug("already logged in, skipping login")
            return LoginResult.ALREADY_LOGGED_IN

        # if we have a session and refresh token, try refreshing the token
        if self.__session.session_id is not None and self.__session.token is not None:
            try:
                self.__session.token = await self.__refresh_token(
                    self.__session.token.refresh_token
                )
                if self.__logger:
                    self.__logger.debug("refreshed token successfully")
                return LoginResult.TOKEN_REFRESHED
            except SMAApiClientError:
                # refresh failed, try to re-login with username and password
                if self.__logger:
                    self.__logger.debug("failed to refresh token, trying to re-login")

        # if all else fails, get a new token using username and password
        if self.__username is None or self.__password is None:
            raise ValueError("username and password are required for login")
        self.__session.token = await self.__get_new_token(
            self.__username, self.__password
        )

        if self.__logger:
            self.__logger.debug("got new token successfully")
        return LoginResult.NEW_TOKEN

    async def __get_new_token(self, username: str, password: str) -> AuthToken:
        """Get a new access token using username and password."""
        token_response = await self.__session.request(
            method="POST",
            endpoint="token",
            # use form data instead of json payload
            data={
                "grant_type": "password",
                "username": username,
                "password": password,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            auth="none",
        )

        # should have received a session id at login
        if self.__session.session_id is None:
            raise SMAApiClientError("No session id received")

        # set access token
        token_data = await token_response.json()
        return AuthToken.from_dict(token_data)

    async def __refresh_token(self, refresh_token: str) -> AuthToken:
        """Get a new access token using a refresh token."""
        token_response = await self.__session.request(
            method="POST",
            endpoint="token",
            # use form data instead of json payload
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            auth="session",
        )

        # set access token
        token_data = await token_response.json()
        return AuthToken.from_dict(token_data)

    async def logout(self) -> None:
        """Logout from the api."""
        if self.__logger:
            self.__logger.debug("logging out")

        if self.__session.token is None:
            return

        # logout request, ignore errors
        with contextlib.suppress(Exception):
            await self.__session.request(
                method="DELETE",
                endpoint=f"refreshtoken?refreshToken={quote(self.__session.token.refresh_token)}",
            )

        self.__session.session_id = None
        self.__session.token = None

    async def get_all_components(self) -> list[ComponentInfo]:
        """Get a list of all available components and their ids."""

        async def __get_navigation(
            parent_id: str | None = None,
        ) -> list[ComponentInfo]:
            """Get data from /navigation endpoint."""
            if self.__logger:
                self.__logger.debug(f"getting navigation data for parent={parent_id}")

            navigation_response = await self.__session.request(
                method="GET",
                endpoint="navigation"
                + (f"?parentId={quote(parent_id)}" if parent_id else ""),
                headers={
                    "Accept": "application/json",
                },
                auth="full",
            )

            # check & validate response
            navigation = await navigation_response.json()
            if not isinstance(navigation, list):
                raise SMAApiClientError("received invalid response: not a list")
            return [ComponentInfo.from_dict(component) for component in navigation]

        async def __add_device_info(
            root_component: ComponentInfo, component: ComponentInfo
        ) -> None:
            """Get device info for a component."""
            if self.__logger:
                self.__logger.debug(
                    f"getting device info for component={component.component_id}"
                )

            try:
                device_info_response = await self.__session.request(
                    method="GET",
                    endpoint=f"plants/{root_component.component_id}/devices/{component.component_id}",
                    headers={
                        "Accept": "application/json",
                    },
                    auth="full",
                )

                # try adding extra info to component
                device_info = await device_info_response.json()
                component.add_extra(device_info)
            except Exception as e:
                if self.__logger:
                    self.__logger.debug(
                        f"error getting device info for component={component.component_id}: {e}"
                    )

        async def __add_widget_info(component: ComponentInfo) -> None:
            """Get extra info for a component."""
            if self.__logger:
                self.__logger.debug(
                    f"getting widget info for component={component.component_id}"
                )

            try:
                device_info_response = await self.__session.request(
                    method="GET",
                    endpoint=f"widgets/deviceinfo?deviceId={component.component_id}",
                    headers={
                        "Accept": "application/json",
                    },
                    auth="full",
                )

                # try adding extra info to component
                device_info = await device_info_response.json()
                component.add_extra(device_info)
            except Exception as e:
                if self.__logger:
                    self.__logger.debug(
                        f"error getting widget info for component={component.component_id}: {e}"
                    )

        # get root component, only consider the first one
        root_components = await __get_navigation()
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
        all_components = await __get_navigation(parent_id=root_component.component_id)

        # build final list
        all_components = [root_component] + all_components

        # add extra info to all components and return
        # (Plant components don't have extra info)
        for component in all_components:
            if component.component_type != "Plant":
                await __add_device_info(root_component, component)
                await __add_widget_info(component)

        if self.__logger:
            self.__logger.debug(f"got {len(all_components)} components")
        return all_components

    def get_product_icon_url(self, component: ComponentInfo) -> str | None:
        """Get the URL for the product icon of a component."""
        if component.product_tag_id is None:
            return None
        return f"{self.__session.base_url}/product/icon/{component.product_tag_id}/neutral/64"

    async def get_all_live_measurements(
        self, component_ids: list[str]
    ) -> list[ChannelValues]:
        """Get live data for all channels of the requested components."""
        measurements_response = await self.__session.request(
            method="POST",
            endpoint="measurements/live",
            json=[{"componentId": id} for id in component_ids],
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            auth="full",
        )

        measurements = await measurements_response.json()
        return self.__parse_measurements(measurements)

    async def get_live_measurements(
        self, query: list[LiveMeasurementQueryItem]
    ) -> list[ChannelValues]:
        """Get live data for the requested channels."""
        measurements_response = await self.__session.request(
            method="POST",
            endpoint="measurements/live",
            json=[item.to_dict() for item in query],
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            auth="full",
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

    async def get_localizations(self) -> list[tuple[str, dict]]:
        """Retrieve all available localizations from the device.

        Returns a list of localizations dictionaries.
        Each dictionary maps a message id to its localized string.
        A way to identify the language of each mapping is not provided.
        """
        # get landing page HTML
        response = await self.__raw_session.get(self.__host_base_url)
        response.raise_for_status()

        html = await response.text()

        # extract runtime.js script url
        pattern = r'<script src="(runtime\.[\w]+\.js)"(?: type="module")?></script>'
        match = re.search(pattern, html)
        if not match:
            raise SMAApiClientError("runtime.js module not found")

        runtime_js_url = f"{self.__host_base_url}/webui/{match.group(1)}"

        # get runtime.js
        response = await self.__raw_session.get(runtime_js_url)
        response.raise_for_status()

        runtime_js = await response.text()

        # extract mapping table for js files
        pattern = r'"\."\+{((?:[a-z0-9]+:\"[a-z0-9]+\",?)+)}\[[a-z]\]\+".js"'
        match = re.search(pattern, runtime_js)
        if not match:
            raise SMAApiClientError("JS file mapping table not found")

        mapping_table = match.group(1)

        # convert from js literal object to json
        pattern = r"([a-z0-9]+):\"([a-z0-9]+)\",?"
        replace_pattern = r'"\1":"\2",'
        mapping_table = json.loads(
            "{" + re.sub(pattern, replace_pattern, mapping_table).rstrip(",") + "}"
        )

        # load all js files and check them for localization data
        localizations = []
        for id, hash in mapping_table.items():
            with contextlib.suppress(Exception):
                response = await self.__raw_session.get(
                    f"{self.__host_base_url}/webui/{id}.{hash}.js"
                )
                response.raise_for_status()
                js_content = await response.text()

                pattern = r"\.exports=JSON\.parse\('(\{\"META\":.+)'\)"
                match = re.search(pattern, js_content)
                if not match:
                    continue

                lang_data = match.group(1).encode().decode("unicode_escape")
                lang_data = json.loads(lang_data)

                localizations.append((f"{id}.{hash}.js", lang_data))

        return localizations
