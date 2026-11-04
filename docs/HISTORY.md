# HVAC and fan history sensors

Version 0.6.0 adds Fan activity and current Fan speed alongside the selected HVAC mode/Fan mode and HVAC activity sensors. They share the containing system device and use the zone name, such as Main fan activity. These are independent entities so Recorder can track changes over time.

| Sensor | Raw states | English display / meaning |
| --- | --- | --- |
| HVAC mode | `off`, `heat`, `cool`, `heat_cool`, `fan_only` | Selected HVAC mode; Jetson Auto maps to HA `heat_cool` |
| Fan mode | `auto`, `1`, `2`, `3` | Auto, Low, Medium, High: selected speed, not actual activity |
| HVAC activity | `off`, `idle`, `heating`, `cooling`, `fan`, `drying` | Reported current HVAC activity |
| Fan activity | `off`, `running` | Off, Running: current fan operation |
| Fan speed | `0`, `1`, `2`, `3` | Off, Low, Medium, High: reported current fan speed |

The user confirmed 1=Low, 2=Medium, 3=High. These are discrete speeds, not RPM or a percentage. Numeric string values remain stable for existing fan-mode automations, and climate commands still send the API's numeric values. Labels are localized in the UI; see [localization](LOCALIZATION.md).

Fan activity uses `features.circulation.fanSpeedStatus` when present: zero means stopped, and speeds 1–3 mean running. When that field is absent, `circulation.status` Off/Circulating supplies the fallback. Invalid, unknown, or missing readings stay unknown; an explicitly invalid speed does not fall back to a contradictory Off status. The selected circulation mode/speed and HVAC mode are not used as proof the fan is running. The current-speed sensor appears only when its source field is reported.

A thermostat set to Heat can have HVAC mode `heat` while HVAC activity is `idle`, then become `heating` when demand appears. The backend reports activity Off for both fully off and idle; the selected HVAC mode distinguishes them. Dehumidifying maps to `drying` and does not establish a selectable Dry mode or humidity-control endpoint.

All five sensors use the existing zone-status response and add no API requests. Their unique-ID suffixes are `:hvac_mode`, `:fan_mode`, `:hvac_activity`, `:fan_activity`, and `:fan_speed`, after `{systemId}:{zoneId}`. They have no numeric units or numeric statistics state class. Per-unit speed diagnostics use the same Low/Medium/High labels, while fan-level diagnostics retain their raw numbers because that scale is unverified.

With Home Assistant's [Recorder](https://www.home-assistant.io/integrations/recorder/) and History enabled, state changes can be viewed in History and timeline cards. Recording follows the instance's filters and retention settings. These sensors do not produce long-term numeric statistics or backfill earlier climate-attribute history.

Updates occur at the configured interval and after successful control requests. Short-lived changes between samples may be missed. Model and entity-adapter tests cover the mappings and independent states; actual Recorder behavior still needs checking in HA.
