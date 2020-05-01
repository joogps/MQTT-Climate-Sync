# MQTT Climate Sync
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant component for syncing IRHVAC messages received by [Tasmota](https://tasmota.github.io/docs/Tasmota-IR/#sending-irhvac-commands) IR transmitters/receivers with climate entities. 

For an all-in-one solution, I highly suggest you to use the [Tasmota-IRHVAC component](https://github.com/hristo-atanasov/Tasmota-IRHVAC).

## Installation and configuration
  1. You can install the integration either by searching for it in [HACS](https://hacs.xyz) or by adding the `custom_components/mqtt_climate_sync` folder to your local `custom_components` folder (if it doesn't exist you can create it).
  2. Add the following code to `configuration.yaml`, where `YOUR_MQTT_TOPIC` is the MQTT topic where your IR receiver sends the received signals (for example, `ir-receiver/tele/RESULT`), and `YOUR_CLIMATE_ENTITY` is the entity you want to sync (for example, `climate.air_conditioner`). If you need to, you can add multiple configurations with dashes (`-`).
```yaml
  mqtt_climate_sync:
    entity_id: YOUR_CLIMATE_ENTITY
    topic: YOUR_MQTT_TOPIC
```
```yaml
  mqtt_climate_sync: # With multiple configurations
    - entity_id: YOUR_CLIMATE_ENTITY_1
      topic: YOUR_MQTT_TOPIC_1
    - entity_id: YOUR_CLIMATE_ENTITY_2
      topic: YOUR_MQTT_TOPIC_2
```

## Events
Every time the component syncs IR data, it fires an event called `mqtt_climate_sync_state_changed`. This events contains a `turned` attribute, which returns `on` or `off`, `state` which is equal to the climate entity's state, `temperature`, which is equal to the temperature and `fan_mode`, which is equal to the fan mode. With this event, you can set up automations like this one, which sends a notification to your mobile phone when your air conditioner is turned on with a remote control.
  ```yaml
    automation:
      alias: Air Conditioner turned on
      initial_state: true
      trigger:
        platform: event
        event_type: mqtt_climate_sync_state_changed
        event_data:
          turned: 'on'
      action:
        service: notify.mobile_app
        data:
          title: Air Conditioner turned on
          message: Your Air Conditioner was turned on with a remote control
  ```

## Notes
  * This component syncs only the HVAC mode (off, cool, heat, fan only, etc.), temperature and fan mode (low, medium, high, auto, etc.) attributes.
  * The MQTT data the component receives needs to be in HVAC (the Tasmota JSON structure looks like this: `{"IrReceived":{"Protocol":"GREE","Bits":64,"Data":"0x0x0904405002200090","Repeat":0,"IRHVAC":{"Vendor":"GREE","Model":1,"Power":"On","Mode":"Cool","Celsius":"On","Temp":20, ...`)
