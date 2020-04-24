import logging

import json
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.components.mqtt import valid_subscribe_topic
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN

DOMAIN = "mqtt_climate_sync"

CONF_TOPIC = "topic"

EVENT_STATE_CHANGED = "mqtt_climate_sync_state_changed"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_ENTITY_ID): cv.entity_domain(CLIMATE_DOMAIN),
                        vol.Required(CONF_TOPIC): valid_subscribe_topic,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Setup the mqtt_climate_sync component."""
    mqtt = hass.components.mqtt

    for conf in config[DOMAIN]:
        climate_sync = ClimateSync(hass, conf)
        await climate_sync.async_subscribe_to_topic(mqtt)

    return True


class ClimateSync:
    """The ClimateSync class."""

    def __init__(self, hass, config):
        """Initialize class."""

        self.hass = hass

        self.entity_id = config.get(CONF_ENTITY_ID)
        self.topic = config.get(CONF_TOPIC)

    async def async_subscribe_to_topic(self, mqtt):
        await mqtt.async_subscribe(self.topic, self.handle_message)

    def handle_message(self, msg):
        """Handle MQTT messages."""

        data = json.loads(msg.payload)
        entity_state = self.hass.states.get(self.entity_id)

        if entity_state is None:
            _LOGGER.warning("Entity doesn't exist")
            return True

        if "IrReceived" in data:
            if "IRHVAC" in data["IrReceived"]:
                if "manufacturer" in entity_state.attributes:
                    if (
                        data["IrReceived"]["IRHVAC"]["Vendor"].casefold()
                        == entity_state.attributes["manufacturer"].casefold()
                    ):
                        self.sync_climate(data["IrReceived"]["IRHVAC"])
                    else:
                        _LOGGER.debug(
                            'IRHVAC vendor doesn"t match climate entity"s manufacturer'
                        )
                else:
                    _LOGGER.warning("Entity has no manufacturer data")
            else:
                _LOGGER.debug("IR data received has no IRHVAC attribute")

    def sync_climate(self, irhvac):
        """Sync IRHVAC data with climate entity."""

        mode = irhvac["Mode"].casefold()
        temp = irhvac["Temp"]
        fanSpeed = irhvac["FanSpeed"].casefold()

        if mode == "auto":
            mode = "heat_cool"

        if fanSpeed == "min":
            fanSpeed = "low"

        if fanSpeed == "max":
            fanSpeed = "high"

        if irhvac["Turbo"] == "On":
            fanSpeed = "turbo"

        attributes = self.hass.states.get(self.entity_id).attributes.copy()
        attributes["temperature"] = temp
        attributes["fan_mode"] = fanSpeed

        turned = "off"
        if self.hass.states.get(self.entity_id).state == "off" and mode != "off":
            turned = "on"

        self.hass.bus.fire(
            EVENT_STATE_CHANGED,
            {
                "turned": turned,
                "state": mode,
                "temperature": temp,
                "fan_mode": fanSpeed,
            },
        )

        self.hass.states.set(self.entity_id, mode, attributes)
