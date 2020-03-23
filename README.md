# MQTT-Climate-Sync
A Home Assistant component for syncing IR (HVAC) messages received by Tasmota ([tasmota-ir](https://github.com/arendst/Tasmota/wiki/Tasmota-IR)) MQTT transmitters/receivers with climate entities. Works great with the [SmartIr](https://github.com/smartHomeHub/SmartIR) component.

## Installation and configuration
  1. Add the `mqtt_climate_sync` folder to your `custom_components` folder (if it doesn't exist you can create it).
  2. Add the following code to `config.yaml`, where `YOUR_MQTT_TOPIC` is the MQTT topic where your IR receiver sends the received signals (for example, `ir-receiver/tele/RESULT`), and `YOUR_CLIMATE_ENTITY` is the entity you want to sync (for example, `climate.air_conditioner`) 
  ```yaml
    mqtt_climate_sync:
      topic: YOUR_MQTT_TOPIC
      climate: YOUR_CLIMATE_ENTITY
  ```

## Events
Every time the component syncs IR data, it fires an event called `mqtt_climate_sync_changed_state`. This events contains a `turned` property, which returns `on` or `off`, `state` which is equal to the climate entity's state, `temperature`, which is equal to the temperature and `fan_mode`, which is equal to the fan mode. With this event, you can set up automations like this one, which sends a notification to your mobile phone whenever your air conditioner is turned on.
  ```yaml
    automation:
      alias: Air Conditioner turned on
      initial_state: true
      trigger:
        platform: event
        event_type: mqtt_climate_sync_changed_state
        event_data:
          turned: 'on'
      action:
        service: notify.mobile_app
        data:
          title: Air Conditioner turned on
          message: Your Air Conditioner was turned on using a remote
  ```

## Notes
  * This component syncs only the hvac mode (off, cool, heat, fan only, etc.), temperature and fan mode (low, medium, high, auto, etc.) attributes.
  * The MQTT data the component receives needs to be in HVAC (the Tasmota JSON structure looks like this: `{"IrReceived":{"Protocol":"GREE","Bits":64,"Data":"0x0x0904405002200090","Repeat":0,"IRHVAC":{"Vendor":"GREE","Model":1,"Power":"On","Mode":"Cool","Celsius":"On","Temp":20, ...`)
