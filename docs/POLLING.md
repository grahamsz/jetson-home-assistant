# Polling and manual configuration discovery

Version 0.3.0 keeps the discovered systems, hubs, equipment, and zones until startup/reload or an explicit configuration refresh. Routine measurements use that known configuration. A new installed system will not appear just because a normal temperature poll ran.

## Options menu

Open **Settings → Devices & services → Jetson Home**, then the account entry's configuration/options menu:

- **Polling interval** changes how often thermostat, temperature, humidity, fan, permitted air quality, power/energy, and unit-operation readings are updated. The default is 30 seconds; the range is 30–900 seconds. Saving a changed interval reloads the integration, which also performs startup discovery.
- **Refresh configuration** checks for added, removed, or renamed systems, hubs, equipment, and zones. It runs immediately, updates system devices and known equipment/zone membership, and notifies entity platforms without unloading the integration. Credentials and polling options are retained. A success message ends the options flow; recoverable errors allow a retry.

Use Refresh configuration after commissioning hardware, adding an air-quality monitor, changing a zone's equipment, or renaming a system/device in Jetson. Existing stable IDs are retained. Reported capabilities and air-quality access changes for known zones can still update during normal measurement polling.

From 0.4.0, systems are the HA devices and zone/equipment entities share their containing system device. The HVAC mode, fan mode, and HVAC activity history sensors read the same cached zone status and add no API calls; see [history sensors](HISTORY.md).

Version 0.6.0's Fan activity/current-speed sensors also use cached zone status. Heat-strip watts share the existing energy response. These additions and localization add no network requests or discovery scans.

Version 0.7.0's Schedule paused sensor, Resume schedule button, and Circulation minutes/hour number likewise use existing zone data. Known zones can gain these entities during normal polling. Resume and circulation-duration writes happen only on explicit user/service actions and request a normal refresh after success. They do not add background reads or automatically resume schedules after manual overrides; see [schedule controls](SCHEDULES.md).

## Requests by event

| Event | Reads | Applied changes |
| --- | --- | --- |
| Startup, integration reload, or Refresh configuration | `/v1/systems`, each system's `/boards`, `/equipment`, and `/zones`, then the normal measurement reads below | Full configuration and current measurements |
| Normal update | Known zones' `/status` and eligible `/airQuality`; energy/current for known systems with an EnergyMonitor; selected heat-pump units' `/heatpump/status` | Measurements, settings, activity, capabilities, air-quality access, power/energy, zone freshness/connectivity, and reported unit operation |
| First normal update after the five-minute connectivity interval | Normal reads plus `/v1/systems` and configured systems' `/equipment` | Connection status and measurements; configuration identity, names, memberships, and gateway links stay as discovered |
| Successful thermostat/humidifier command | Existing write endpoint, followed by a requested normal refresh | Confirmed API measurements/settings; no forced discovery |
| Empty account between explicit refreshes | No discovery or measurement requests | Empty configuration retained |

Let `S` be configured systems, `Z` known zones, `Q` zones with an associated reported TEMCO-AQM, `E` systems with a known EnergyMonitor, and `H` selected heat-pump units. Indoor/outdoor components are selected when present; a legacy aggregate HeatPump is used only when no components exist.

- Ordinary update: `Z + Q + E + H` reads.
- Connectivity update when `S > 0`: `Z + Q + E + H + 1 + S` reads.
- Full discovery: `1 + 3 × S + Z + Q + E + H` reads.

For one system, one zone, air quality, an energy monitor, and indoor/outdoor units, this is **5** ordinary reads, **7** on a connectivity update, and **9** for a full scan. Every energy sensor shares its system's response; additional load sensors add no requests. Zone history/freshness sensors also share existing responses. Authentication refresh/retry can add calls.

The connectivity timer is independent of discovery but uses the measurement coordinator's next update to execute. A 30-second polling interval normally gives connectivity checks about every five minutes; longer intervals run the check on the first update after the deadline. Commands may request an earlier update, while connectivity reads still respect their own minimum interval. There is no periodic full discovery timer.

The separate health reads are necessary because the recovered API embeds system/equipment connection status in inventory responses. Newer zone-status responses also contain connectivity; that current field takes priority over cached system health, including when it reports Unknown. New objects returned by health reads are ignored until explicit discovery; only known objects' status fields are applied. The backend itself also describes a five-minute equipment staleness window, so these diagnostics are not instantaneous.

## Failure and concurrency behavior

Discovery and measurement updates are serialized. Each successful measurement cycle builds a new snapshot, so a failed cycle cannot partly overwrite the last published data. A manual discovery failure in systems/zones/status leaves the last good configuration intact; it does not trigger full discovery on every later poll.

Optional equipment/board errors retain last-good inventory and are reported as an incomplete manual refresh so the user can retry. Successful parts and zone readings may still update. Failed equipment liveness reads make its connectivity diagnostics unavailable. A failed system-health read marks health as unavailable in diagnostics and allows successful zone reads to continue; command replies still determine whether the backend accepted or could deliver a change. Authentication failures continue to require reauthentication; rate limits continue to apply across operations.

A failed air-quality, energy, or unit-status read clears that optional response for the cycle and leaves successful thermostat updates running. Authentication failures and rate limits still propagate. A later successful response restores the readings. Energy freshness uses the source timestamps with a maximum age of the greater of five minutes or twice the configured interval; daily totals additionally require a consistent date and timezone. Air quality uses the app's one-hour timestamp cutoff and rejects settling/missing pollutants, invalid/missing/future timestamps. Full/limited access is reevaluated each poll. If a known zone is removed server-side, failed reads may make its entities unavailable until Refresh configuration or reload removes it from the active configuration. Registry records and existing automations are not automatically deleted.

The scheduling and protocol behavior have mock-server tests. The Home Assistant menu, registry updates, and physical equipment still need a live runtime check.
