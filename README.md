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

### Notes
  * This component currently syncs only the hvac mode (off, cool, heat, fan only, etc.), fan speed (low, medium, high, auto, etc.) and temperature attributes.
  * The MQTT telemetry data needs to be in HVAC (the Tasmota JSON structure looks like this: `{"IrReceived":{"Protocol":"GREE","Bits":64,"Data":"0x0x0904405002200090","Repeat":0,"IRHVAC":{"Vendor":"GREE","Model":1,"Power":"On","Mode":"Cool","Celsius":"On","Temp":20, ...`)
