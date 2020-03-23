import logging
import json

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mqtt_climate_sync"

CONF_TOPIC = "topic"
CONF_CLIMATE = "climate"

def setup(hass, config):
    mqtt = hass.components.mqtt
    
    topic = config[DOMAIN].get(CONF_TOPIC)
    climate = config[DOMAIN].get(CONF_CLIMATE)

    def message_received(msg):
        data = json.loads(msg.payload)
        climateState = hass.states.get(climate)

        if climateState is None:
            _LOGGER.warning('Entity doesn\'t exist')
            return True

        if 'IrReceived' in data:
            if 'IRHVAC' in data['IrReceived']:
                if 'manufacturer' in climateState.attributes:
                    if data['IrReceived']['IRHVAC']['Vendor'].casefold() == climateState.attributes['manufacturer'].casefold():
                        sync_climate(data['IrReceived']['IRHVAC'])
                    else:
                        _LOGGER.warning('IRHVAC vendor doesn\'t match climate entity\'s manufacturer')
                else:
                    _LOGGER.warning('Entity has no manufacturer data (maybe not of climate domain)')
            else:
                _LOGGER.warning('IR data received has no IRHVAC attribute')

    def sync_climate(irhvac):
        mode = irhvac['Mode'].casefold()
        temp = irhvac['Temp']
        fanSpeed = irhvac['FanSpeed'].casefold()

        if mode == 'auto':
            mode = 'heat_cool'

        if fanSpeed == 'min':
            fanSpeed = 'low'

        if fanSpeed == 'max':
            fanSpeed = 'high'

        if irhvac['Turbo'] == 'On':
            fanSpeed = 'turbo'

        attributes = hass.states.get(climate).attributes.copy()
        attributes['temperature'] = temp
        attributes['fan_mode'] = fanSpeed

        turned = 'off'
        if hass.states.get(climate).state == 'off' and mode != 'off':
            turned = 'on'

        hass.bus.fire("mqtt_climate_sync_changed_state", {"turned": turned, "state": mode, "temperature": temp, "fan_mode": fanSpeed})

        hass.states.set(climate, mode, attributes)

    mqtt.subscribe(topic, message_received)

    return True