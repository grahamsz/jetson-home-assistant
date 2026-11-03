# Polling and manual configuration discovery

Version 0.3.0 keeps the discovered systems, hubs, equipment, and zones until startup/reload or an explicit configuration refresh. Routine measurements use that known configuration. A new installed system will not appear just because a normal temperature poll ran.

## Options menu

Open **Settings → Devices & services → Jetson Home**, then the account entry's configuration/options menu:

- **Polling interval** changes how often thermostat, temperature, humidity, fan, and permitted air-quality readings are updated. The default is 30 seconds; the range is 30–900 seconds. Saving a changed interval reloads the integration, which also performs startup discovery.
- **Refresh configuration** checks for added, removed, or renamed systems, hubs, equipment, and zones. It runs immediately, updates registered relationships, and notifies entity platforms without unloading the integration. Credentials and polling options are retained. A success message ends the options flow; recoverable errors allow a retry.

Use Refresh configuration after commissioning hardware, adding an air-quality monitor, changing a zone's equipment, or renaming a system/device in Jetson. Existing stable IDs are retained. Reported capabilities and air-quality access changes for known zones can still update during normal measurement polling.

## Requests by event

| Event | Reads | Applied changes |
| --- | --- | --- |
| Startup, integration reload, or Refresh configuration | `/v1/systems`, each system's `/boards`, `/equipment`, and `/zones`, then known zones' `/status` and eligible `/airQuality` | Full configuration and current measurements |
| Normal update | Known zones' `/status` and eligible `/airQuality` | Measurements, settings, activity, capabilities, and air-quality access |
| First normal update after the five-minute connectivity interval | Normal reads plus `/v1/systems` and configured systems' `/equipment` | Connection status and measurements; configuration identity, names, memberships, and gateway links stay as discovered |
| Successful thermostat/humidifier command | Existing write endpoint, followed by a requested normal refresh | Confirmed API measurements/settings; no forced discovery |
| Empty account between explicit refreshes | No discovery or measurement requests | Empty configuration retained |

Let `S` be configured systems, `Z` known zones, and `Q` zones with an associated reported TEMCO-AQM:

- Ordinary update: `Z + Q` reads.
- Connectivity update when `S > 0`: `Z + Q + 1 + S` reads.
- Full discovery: `1 + 3 × S + Z + Q` reads.

For one system, one zone, and air quality, this is **2** ordinary reads, **4** on a connectivity update, and **6** for a full scan. Authentication refresh/retry can add calls.

The connectivity timer is independent of discovery but uses the measurement coordinator's next update to execute. A 30-second polling interval normally gives connectivity checks about every five minutes; longer intervals run the check on the first update after the deadline. Commands may request an earlier update, while connectivity reads still respect their own minimum interval. There is no periodic full discovery timer.

The separate health reads are necessary because the recovered API embeds system/equipment connection status in inventory responses. Keeping an old Connected value indefinitely would misrepresent liveness. New objects returned by these health reads are ignored until explicit discovery; only known objects' status fields are applied. The backend itself also describes a five-minute equipment staleness window, so these diagnostics are not instantaneous.

## Failure and concurrency behavior

Discovery and measurement updates are serialized. Each successful measurement cycle builds a new snapshot, so a failed cycle cannot partly overwrite the last published data. A manual discovery failure in systems/zones/status leaves the last good configuration intact; it does not trigger full discovery on every later poll.

Optional equipment/board errors retain last-good inventory and are reported as an incomplete manual refresh so the user can retry. Successful parts and zone readings may still update. Failed equipment liveness reads make its connectivity diagnostics unavailable. A failed system-health read marks health as unavailable in diagnostics and allows successful zone reads to continue; command replies still determine whether the backend accepted or could deliver a change. Authentication failures continue to require reauthentication; rate limits continue to apply across operations.

A failed air-quality read clears that cycle's air-quality data, rather than presenting the prior value as current. A later successful response restores it, and full/limited access is reevaluated each poll. If a known zone is removed server-side, failed reads may make its entities unavailable until Refresh configuration or reload removes it from the active configuration. Registry records and existing automations are not automatically deleted.

The scheduling and protocol behavior have mock-server tests. The Home Assistant menu, registry updates, and physical equipment still need a live runtime check.
