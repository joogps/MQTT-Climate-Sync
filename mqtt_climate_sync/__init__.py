import logging
import json

DOMAIN = "mqtt_climate_sync"
DEPENDENCIES = ["mqtt"]

_LOGGER = logging.getLogger(__name__)

CONF_TOPIC = "topic"
CONF_CLIMATE = "climate"

def setup(hass, config):
    mqtt = hass.components.mqtt
    
    topic = config[DOMAIN].get(CONF_TOPIC)
    climate = config[DOMAIN].get(CONF_CLIMATE)

    def message_received(msg):
        data = json.loads(msg.payload)
        climateState = hass.states.get('climate.air_conditioner')

        if 'IrReceived' in data:
            if 'IRHVAC' in data['IrReceived']:
                if data['IrReceived']['IRHVAC']['Vendor'].casefold() == climateState.attributes['manufacturer'].casefold():
                    sync_climate(data['IrReceived']['IRHVAC'])

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

        hass.states.set(climate, mode, attributes)

    mqtt.subscribe(topic, message_received)

    return True