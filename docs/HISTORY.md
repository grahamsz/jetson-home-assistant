# HVAC and fan history sensors

Version 0.4.0 adds three read-only enum sensors per zone when the relevant features are reported. They live on the containing system device and use the zone name, such as Main HVAC mode, Main Fan mode, and Main HVAC activity.

| Sensor | States | Meaning |
| --- | --- | --- |
| HVAC mode | `off`, `heat`, `cool`, `heat_cool`, `fan_only` | Configured mode; Jetson Auto maps to HA `heat_cool` |
| Fan mode | `auto`, `1`, `2`, `3` | Selected fan-speed setting, not measured RPM or confirmation of airflow |
| HVAC activity | `off`, `idle`, `heating`, `cooling`, `fan`, `drying` | Reported current activity; unknown/unrecognized activity becomes an unknown state |

These sensors use the same mappings as the climate entity. For example, a thermostat set to Heat can have mode `heat` while activity is `idle`, and then change to `heating` when there is demand. The backend reports activity Off for both fully off and idle; the selected mode distinguishes them. A reported Dehumidifying activity maps to `drying` and does not establish a user-selectable Dry mode or humidity-control endpoint.

The sensors use the existing zone-status response and add no API requests. Their entity unique IDs are `{systemId}:{zoneId}:hvac_mode`, `:fan_mode`, and `:hvac_activity`. They are ordinary visible sensors, without numeric units or a numeric statistics state class.

With Home Assistant's [Recorder](https://www.home-assistant.io/integrations/recorder/) and History enabled, entity state changes can be viewed in History and timeline cards. Recording follows the instance's include/exclude filters and retention settings. These categorical sensors do not produce long-term numeric statistics or automatically backfill prior climate-attribute history.

Updates occur at the configured polling interval and after successful control requests. Short-lived changes between samples may be missed; no live push channel has been established. The state mappings have automated tests; actual Recorder behavior and displayed history need checking in HA.
