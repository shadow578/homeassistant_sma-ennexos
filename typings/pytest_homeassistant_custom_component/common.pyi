"""
This type stub file was generated by pyright.
"""

import asyncio
import pathlib
import pytest
import voluptuous as vol
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator, Iterable, Iterator, Mapping, Sequence
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from types import FrameType, ModuleType
from typing import Any, Literal
from unittest.mock import Mock
from syrupy import SnapshotAssertion
from typing_extensions import TypeVar
from homeassistant import auth, config_entries, loader
from homeassistant.auth import models as auth_models, permissions as auth_permissions, providers as auth_providers
from homeassistant.components import device_automation, persistent_notification as pn
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.core import CoreState, Event, HomeAssistant, ServiceCall, ServiceResponse, State, SupportsResponse, callback
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity, entity_platform, entity_registry as er, intent, restore_state as rs, storage
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.event_type import EventType
from homeassistant.util.json import JsonArrayType, JsonObjectType, JsonValueType
from homeassistant.util.signal_type import SignalType

"""
Test the helper method for writing .

This file is originally from homeassistant/core and modified by pytest-homeassistant-custom-component.
"""
_DataT = TypeVar("_DataT", bound=Mapping[str, Any], default=dict[str, Any])
_LOGGER = ...
INSTANCES = ...
CLIENT_ID = ...
CLIENT_REDIRECT_URI = ...
async def async_get_device_automations(hass: HomeAssistant, automation_type: device_automation.DeviceAutomationType, device_id: str) -> Any:
    """Get a device automation for a single device id."""
    ...

def threadsafe_callback_factory(func): # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:
    """Create threadsafe functions out of callbacks.

    Callback needs to have `hass` as first argument.
    """
    ...

def threadsafe_coroutine_factory(func): # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:
    """Create threadsafe functions out of coroutine.

    Callback needs to have `hass` as first argument.
    """
    ...

def get_test_config_dir(*add_path): # -> str:
    """Return a path to a test config dir."""
    ...

class StoreWithoutWriteLoad[_T: (Mapping[str, Any] | Sequence[Any])](storage.Store[_T]):
    """Fake store that does not write or load. Used for testing."""
    async def async_save(self, *args: Any, **kwargs: Any) -> None:
        """Save the data.

        This function is mocked out in .
        """
        ...
    
    @callback
    def async_save_delay(self, *args: Any, **kwargs: Any) -> None:
        """Save data with an optional delay.

        This function is mocked out in .
        """
        ...
    


@asynccontextmanager
async def async_test_home_assistant(event_loop: asyncio.AbstractEventLoop | None = ..., load_registries: bool = ..., config_dir: str | None = ..., initial_state: CoreState = ...) -> AsyncGenerator[HomeAssistant]:
    """Return a Home Assistant object pointing at test config dir."""
    ...

def async_mock_service(hass: HomeAssistant, domain: str, service: str, schema: vol.Schema | None = ..., response: ServiceResponse = ..., supports_response: SupportsResponse | None = ..., raise_exception: Exception | None = ...) -> list[ServiceCall]:
    """Set up a fake service & return a calls log list to this service."""
    ...

mock_service = ...
@callback
def async_mock_intent(hass: HomeAssistant, intent_typ: str) -> list[intent.Intent]:
    """Set up a fake intent handler."""
    class MockIntentHandler(intent.IntentHandler):
        ...
    
    

@callback
def async_fire_mqtt_message(hass: HomeAssistant, topic: str, payload: bytes | str, qos: int = ..., retain: bool = ...) -> None:
    """Fire the MQTT message."""
    ...

fire_mqtt_message = ...
@callback
def async_fire_time_changed_exact(hass: HomeAssistant, datetime_: datetime | None = ..., fire_all: bool = ...) -> None:
    """Fire a time changed event at an exact microsecond.

    Consider that it is not possible to actually achieve an exact
    microsecond in production as the event loop is not precise enough.
    If your code relies on this level of precision, consider a different
    approach, as this is only for testing.
    """
    ...

@callback
def async_fire_time_changed(hass: HomeAssistant, datetime_: datetime | None = ..., fire_all: bool = ...) -> None:
    """Fire a time changed event.

    If called within the first 500  ms of a second, time will be bumped to exactly
    500 ms to match the async_track_utc_time_change event listeners and
    DataUpdateCoordinator which spreads all updates between 0.05..0.50.
    Background in PR https://github.com/home-assistant/core/pull/82233

    As asyncio is cooperative, we can't guarantee that the event loop will
    run an event at the exact time we want. If you need to fire time changed
    for an exact microsecond, use async_fire_time_changed_exact.
    """
    ...

_MONOTONIC_RESOLUTION = ...
fire_time_changed = ...
def get_fixture_path(filename: str, integration: str | None = ...) -> pathlib.Path:
    """Get path of fixture."""
    ...

@lru_cache
def load_fixture(filename: str, integration: str | None = ...) -> str:
    """Load a fixture."""
    ...

def load_json_value_fixture(filename: str, integration: str | None = ...) -> JsonValueType:
    """Load a JSON value from a fixture."""
    ...

def load_json_array_fixture(filename: str, integration: str | None = ...) -> JsonArrayType:
    """Load a JSON array from a fixture."""
    ...

def load_json_object_fixture(filename: str, integration: str | None = ...) -> JsonObjectType:
    """Load a JSON object from a fixture."""
    ...

def json_round_trip(obj: Any) -> Any:
    """Round trip an object to JSON."""
    ...

def mock_state_change_event(hass: HomeAssistant, new_state: State, old_state: State | None = ...) -> None:
    """Mock state change event."""
    ...

@callback
def mock_component(hass: HomeAssistant, component: str) -> None:
    """Mock a component is setup."""
    ...

def mock_registry(hass: HomeAssistant, mock_entries: dict[str, er.RegistryEntry] | None = ...) -> er.EntityRegistry:
    """Mock the Entity Registry.

    This should only be used if you need to mock/re-stage a clean mocked
    entity registry in your current hass object. It can be useful to,
    for example, pre-load the registry with items.

    This mock will thus replace the existing registry in the running hass.

    If you just need to access the existing registry, use the `entity_registry`
    fixture instead.
    """
    ...

def mock_area_registry(hass: HomeAssistant, mock_entries: dict[str, ar.AreaEntry] | None = ...) -> ar.AreaRegistry:
    """Mock the Area Registry.

    This should only be used if you need to mock/re-stage a clean mocked
    area registry in your current hass object. It can be useful to,
    for example, pre-load the registry with items.

    This mock will thus replace the existing registry in the running hass.

    If you just need to access the existing registry, use the `area_registry`
    fixture instead.
    """
    ...

def mock_device_registry(hass: HomeAssistant, mock_entries: dict[str, dr.DeviceEntry] | None = ...) -> dr.DeviceRegistry:
    """Mock the Device Registry.

    This should only be used if you need to mock/re-stage a clean mocked
    device registry in your current hass object. It can be useful to,
    for example, pre-load the registry with items.

    This mock will thus replace the existing registry in the running hass.

    If you just need to access the existing registry, use the `device_registry`
    fixture instead.
    """
    ...

class MockGroup(auth_models.Group):
    """Mock a group in Home Assistant."""
    def __init__(self, id: str | None = ..., name: str | None = ...) -> None:
        """Mock a group."""
        ...
    
    def add_to_hass(self, hass: HomeAssistant) -> MockGroup:
        """Test helper to add entry to hass."""
        ...
    
    def add_to_auth_manager(self, auth_mgr: auth.AuthManager) -> MockGroup:
        """Test helper to add entry to hass."""
        ...
    


class MockUser(auth_models.User):
    """Mock a user in Home Assistant."""
    def __init__(self, id: str | None = ..., is_owner: bool = ..., is_active: bool = ..., name: str | None = ..., system_generated: bool = ..., groups: list[auth_models.Group] | None = ...) -> None:
        """Initialize mock user."""
        ...
    
    def add_to_hass(self, hass: HomeAssistant) -> MockUser:
        """Test helper to add entry to hass."""
        ...
    
    def add_to_auth_manager(self, auth_mgr: auth.AuthManager) -> MockUser:
        """Test helper to add entry to hass."""
        ...
    
    def mock_policy(self, policy: auth_permissions.PolicyType) -> None:
        """Mock a policy for a user."""
        ...
    


async def register_auth_provider(hass: HomeAssistant, config: ConfigType) -> auth_providers.AuthProvider:
    """Register an auth provider."""
    ...

@callback
def ensure_auth_manager_loaded(auth_mgr: auth.AuthManager) -> None:
    """Ensure an auth manager is considered loaded."""
    ...

class MockModule:
    """Representation of a fake module."""
    def __init__(self, domain: str | None = ..., *, dependencies: list[str] | None = ..., setup: Callable[[HomeAssistant, ConfigType], bool] | None = ..., requirements: list[str] | None = ..., config_schema: vol.Schema | None = ..., platform_schema: vol.Schema | None = ..., platform_schema_base: vol.Schema | None = ..., async_setup: Callable[[HomeAssistant, ConfigType], Coroutine[Any, Any, bool]] | None = ..., async_setup_entry: Callable[[HomeAssistant, ConfigEntry], Coroutine[Any, Any, bool]] | None = ..., async_unload_entry: Callable[[HomeAssistant, ConfigEntry], Coroutine[Any, Any, bool]] | None = ..., async_migrate_entry: Callable[[HomeAssistant, ConfigEntry], Coroutine[Any, Any, bool]] | None = ..., async_remove_entry: Callable[[HomeAssistant, ConfigEntry], Coroutine[Any, Any, None]] | None = ..., partial_manifest: dict[str, Any] | None = ..., async_remove_config_entry_device: Callable[[HomeAssistant, ConfigEntry, dr.DeviceEntry], Coroutine[Any, Any, bool]] | None = ...) -> None:
        """Initialize the mock module."""
        ...
    
    def mock_manifest(self): # -> dict[str, Any]:
        """Generate a mock manifest to represent this module."""
        ...
    


class MockPlatform:
    """Provide a fake platform."""
    __name__ = ...
    __file__ = ...
    def __init__(self, *, setup_platform: Callable[[HomeAssistant, ConfigType, AddEntitiesCallback, DiscoveryInfoType | None], None,] | None = ..., dependencies: list[str] | None = ..., platform_schema: vol.Schema | None = ..., async_setup_platform: Callable[[HomeAssistant, ConfigType, AddEntitiesCallback, DiscoveryInfoType | None], Coroutine[Any, Any, None],] | None = ..., async_setup_entry: Callable[[HomeAssistant, ConfigEntry, AddEntitiesCallback], Coroutine[Any, Any, None]] | None = ..., scan_interval: timedelta | None = ...) -> None:
        """Initialize the platform."""
        ...
    


class MockEntityPlatform(entity_platform.EntityPlatform):
    """Mock class with some mock defaults."""
    def __init__(self, hass: HomeAssistant, logger=..., domain=..., platform_name=..., platform=..., scan_interval=..., entity_namespace=...) -> None:
        """Initialize a mock entity platform."""
        ...
    


class MockToggleEntity(entity.ToggleEntity):
    """Provide a mock toggle device."""
    def __init__(self, name: str | None, state: Literal["on", "off"] | None) -> None:
        """Initialize the mock entity."""
        ...
    
    @property
    def name(self) -> str:
        """Return the name of the entity if any."""
        ...
    
    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state of the entity if any."""
        ...
    
    @property
    def is_on(self) -> bool:
        """Return true if entity is on."""
        ...
    
    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        ...
    
    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        ...
    
    def last_call(self, method: str | None = ...) -> tuple[str, dict[str, Any]]:
        """Return the last call."""
        ...
    


class MockConfigEntry(config_entries.ConfigEntry):
    """Helper for creating config entries that adds some defaults."""
    def __init__(self, *, data=..., disabled_by=..., discovery_keys=..., domain=..., entry_id=..., minor_version=..., options=..., pref_disable_new_entities=..., pref_disable_polling=..., reason=..., source=..., state=..., title=..., unique_id=..., version=...) -> None:
        """Initialize a mock config entry."""
        ...
    
    def add_to_hass(self, hass: HomeAssistant) -> None:
        """Test helper to add entry to hass."""
        ...
    
    def add_to_manager(self, manager: config_entries.ConfigEntries) -> None:
        """Test helper to add entry to entry manager."""
        ...
    
    def mock_state(self, hass: HomeAssistant, state: config_entries.ConfigEntryState, reason: str | None = ...) -> None:
        """Mock the state of a config entry to be used in .

        Currently this is a wrapper around _async_set_state, but it may
        change in the future.

        It is preferable to get the config entry into the desired state
        by using the normal config entry methods, and this helper
        is only intended to be used in cases where that is not possible.

        When in doubt, this helper should not be used in new code
        and is only intended for backwards compatibility with existing
        .
        """
        ...
    
    async def start_reauth_flow(self, hass: HomeAssistant, context: dict[str, Any] | None = ..., data: dict[str, Any] | None = ...) -> ConfigFlowResult:
        """Start a reauthentication flow."""
        ...
    
    async def start_reconfigure_flow(self, hass: HomeAssistant, *, show_advanced_options: bool = ...) -> ConfigFlowResult:
        """Start a reconfiguration flow."""
        ...
    


async def start_reauth_flow(hass: HomeAssistant, entry: ConfigEntry, context: dict[str, Any] | None = ..., data: dict[str, Any] | None = ...) -> ConfigFlowResult:
    """Start a reauthentication flow for a config entry.

    This helper method should be aligned with `ConfigEntry._async_init_reauth`.
    """
    ...

def patch_yaml_files(files_dict, endswith=...): # -> _patch[Callable[..., StringIO | TextIOWrapper[_WrappedBuffer]]]:
    """Patch load_yaml with a dictionary of yaml files."""
    ...

@contextmanager
def assert_setup_component(count, domain=...): # -> Generator[dict[Any, Any], Any, None]:
    """Collect valid configuration from setup_component.

    - count: The amount of valid platforms that should be setup
    - domain: The domain to count is optional. It can be automatically
              determined most of the time

    Use as a context manager around setup.setup_component
        with assert_setup_component(0) as result_config:
            setup_component(hass, domain, start_config)
            # using result_config is optional
    """
    ...

def mock_restore_cache(hass: HomeAssistant, states: Sequence[State]) -> None:
    """Mock the DATA_RESTORE_CACHE."""
    ...

def mock_restore_cache_with_extra_data(hass: HomeAssistant, states: Sequence[tuple[State, Mapping[str, Any]]]) -> None:
    """Mock the DATA_RESTORE_CACHE."""
    ...

async def async_mock_restore_state_shutdown_restart(hass: HomeAssistant) -> rs.RestoreStateData:
    """Mock shutting down and saving restore state and restoring."""
    ...

async def async_mock_load_restore_state_from_storage(hass: HomeAssistant) -> None:
    """Mock loading restore state from storage.

    hass_storage must already be mocked.
    """
    ...

class MockEntity(entity.Entity):
    """Mock Entity class."""
    def __init__(self, **values: Any) -> None:
        """Initialize an entity."""
        ...
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        ...
    
    @property
    def capability_attributes(self) -> Mapping[str, Any] | None:
        """Info about capabilities."""
        ...
    
    @property
    def device_class(self) -> str | None:
        """Info how device should be classified."""
        ...
    
    @property
    def device_info(self) -> dr.DeviceInfo | None:
        """Info how it links to a device."""
        ...
    
    @property
    def entity_category(self) -> entity.EntityCategory | None:
        """Return the entity category."""
        ...
    
    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        ...
    
    @property
    def has_entity_name(self) -> bool:
        """Return the has_entity_name name flag."""
        ...
    
    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        ...
    
    @property
    def entity_registry_visible_default(self) -> bool:
        """Return if the entity should be visible when first added to the entity registry."""
        ...
    
    @property
    def icon(self) -> str | None:
        """Return the suggested icon."""
        ...
    
    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        ...
    
    @property
    def should_poll(self) -> bool:
        """Return the ste of the polling."""
        ...
    
    @property
    def supported_features(self) -> int | None:
        """Info about supported features."""
        ...
    
    @property
    def translation_key(self) -> str | None:
        """Return the translation key."""
        ...
    
    @property
    def unique_id(self) -> str | None:
        """Return the unique ID of the entity."""
        ...
    
    @property
    def unit_of_measurement(self) -> str | None:
        """Info on the units the entity state is in."""
        ...
    


@contextmanager
def mock_storage(data: dict[str, Any] | None = ...) -> Generator[dict[str, Any]]:
    """Mock storage.

    Data is a dict {'key': {'version': version, 'data': data}}

    Written data will be converted to JSON to ensure JSON parsing works.
    """
    ...

async def flush_store(store: storage.Store) -> None:
    """Make sure all delayed writes of a store are written."""
    ...

async def get_system_health_info(hass: HomeAssistant, domain: str) -> dict[str, Any]:
    """Get system health info."""
    ...

@contextmanager
def mock_config_flow(domain: str, config_flow: type[ConfigFlow]) -> Iterator[None]:
    """Mock a config flow handler."""
    ...

def mock_integration(hass: HomeAssistant, module: MockModule, built_in: bool = ..., top_level_files: set[str] | None = ...) -> loader.Integration:
    """Mock an integration."""
    ...

def mock_platform(hass: HomeAssistant, platform_path: str, module: Mock | MockPlatform | None = ..., built_in=...) -> None:
    """Mock a platform.

    platform_path is in form hue.config_flow.
    """
    ...

def async_capture_events(hass: HomeAssistant, event_name: EventType[_DataT] | str) -> list[Event[_DataT]]:
    """Create a helper that captures events."""
    ...

@callback
def async_mock_signal[*_Ts](hass: HomeAssistant, signal: SignalType[*_Ts] | str) -> list[tuple[*_Ts]]:
    """Catch all dispatches to a signal."""
    ...

_SENTINEL = ...
class _HA_ANY:
    """A helper object that compares equal to everything.

    Based on unittest.mock.ANY, but modified to not show up in pytest's equality
    assertion diffs.
    """
    _other = ...
    def __eq__(self, other: object) -> bool:
        """Test equal."""
        ...
    
    def __ne__(self, other: object) -> bool:
        """Test not equal."""
        ...
    
    def __repr__(self) -> str:
        """Return repr() other to not show up in pytest quality diffs."""
        ...
    


ANY = ...
def raise_contains_mocks(val: Any) -> None:
    """Raise for mocks."""
    ...

@callback
def async_get_persistent_notifications(hass: HomeAssistant) -> dict[str, pn.Notification]:
    """Get the current persistent notifications."""
    ...

def async_mock_cloud_connection_status(hass: HomeAssistant, connected: bool) -> None:
    """Mock a signal the cloud disconnected."""
    ...

def import_and_test_deprecated_constant_enum(caplog: pytest.LogCaptureFixture, module: ModuleType, replacement: Enum, constant_prefix: str, breaks_in_ha_version: str) -> None:
    """Import and test deprecated constant replaced by a enum.

    - Import deprecated enum
    - Assert value is the same as the replacement
    - Assert a warning is logged
    - Assert the deprecated constant is included in the modules.__dir__()
    - Assert the deprecated constant is included in the modules.__all__()
    """
    ...

def import_and_test_deprecated_constant(caplog: pytest.LogCaptureFixture, module: ModuleType, constant_name: str, replacement_name: str, replacement: Any, breaks_in_ha_version: str) -> None:
    """Import and test deprecated constant replaced by a value.

    - Import deprecated constant
    - Assert value is the same as the replacement
    - Assert a warning is logged
    - Assert the deprecated constant is included in the modules.__dir__()
    - Assert the deprecated constant is included in the modules.__all__()
    """
    ...

def import_and_test_deprecated_alias(caplog: pytest.LogCaptureFixture, module: ModuleType, alias_name: str, replacement: Any, breaks_in_ha_version: str) -> None:
    """Import and test deprecated alias replaced by a value.

    - Import deprecated alias
    - Assert value is the same as the replacement
    - Assert a warning is logged
    - Assert the deprecated alias is included in the modules.__dir__()
    - Assert the deprecated alias is included in the modules.__all__()
    """
    ...

def help_test_all(module: ModuleType) -> None:
    """Test module.__all__ is correctly set."""
    ...

def extract_stack_to_frame(extract_stack: list[Mock]) -> FrameType:
    """Convert an extract stack to a frame list."""
    ...

def setup_test_component_platform(hass: HomeAssistant, domain: str, entities: Iterable[Entity], from_config_entry: bool = ..., built_in: bool = ...) -> MockPlatform:
    """Mock a test component platform for ."""
    ...

async def snapshot_platform(hass: HomeAssistant, entity_registry: er.EntityRegistry, snapshot: SnapshotAssertion, config_entry_id: str) -> None:
    """Snapshot a platform."""
    ...

def reset_translation_cache(hass: HomeAssistant, components: list[str]) -> None:
    """Reset translation cache for specified components.

    Use this if you are mocking a core component (for example via
    mock_integration), to ensure that the mocked translations are not
    persisted in the shared session cache.
    """
    ...

