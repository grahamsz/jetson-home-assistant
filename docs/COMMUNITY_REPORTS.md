# Community reports and schedule controls

## User-supplied Reddit report, received November 4, 2026

The user supplied a comment from a person running a local bridge against Jetson's cloud API since August. The commenter reports about three months of daily hardware use. This is community-reported evidence, separate from this project's static analysis, mock tests, and directly observed production GETs. No source URL, equipment/firmware versions, or captured command responses were supplied, and these statements have not been independently reproduced here.

| Reported operation | Request / behavior |
| --- | --- |
| HVAC mode | `POST /v1/zones/{id}/hvac/mode` with `{"value":"Heat"}`; Off/Heat/Cool/Auto/FanOnly reportedly work |
| Temperature target | `POST /v1/zones/{id}/ambientTemperature/setpoint` with a numeric value, for example `{"value":21.5}` |
| Circulation | `PATCH /v1/zones/{id}/circulation/settings` with `{"fanSpeed":1,"fanOnDuration":30}`; duration is minutes/hour, with 0/15/30/45/60 used by this bridge |
| Resume weekly schedule | `POST /v1/schedules/{id}/resume` with `{"kind":"Weekly"}` |
| Zone schedule state | The live zone status reportedly supplies `schedule.id`, `schedule.kind`, and `schedule.status`, including Weekly/Active and Weekly/Paused |
| Manual overrides | Changing a setting in the app reportedly pauses the weekly schedule until explicitly resumed |
| Installation header | The bridge reportedly omitted `X-App-Install-ID` while using app-version 1.2.7 and an iOS user agent; API requests and auth refresh worked from August through November |
| Energy coverage | This install's Emporia Vue main clamps are reportedly on the service conductors after the main breaker, so Main readings appear to represent whole-home use; a utility-meter comparison was still pending |

These command paths/bodies, circulation limits, schedule fields, and resume kind are consistent with recovered app evidence. The report adds practical hardware experience rather than introducing new endpoint names. The header observation supports that it was optional in that bridge's context; it does not establish a permanent or universal backend rule. The integration retains its generated installation ID. Main remains a neutral label because measurement coverage depends on clamp placement and wiring.

## HA model implemented in 0.7.0

A small set of controls uses HA's existing entity types:

- A **Schedule paused** binary sensor that reads the current zone's reported schedule status. Missing/unknown schedule data must stay unavailable or unknown, rather than implying Active.
- A **Resume schedule** button that uses the currently reported schedule ID and kind, then refreshes zone status. It should not assume every zone has a Weekly schedule or automatically undo a deliberate manual override.
- A **Circulation minutes per hour** number entity, using the recovered integer range 0–60. The commenter's 15-minute increments are a preference, not a demonstrated API restriction. Its effect depends on the separately configured circulation mode; setting minutes alone must not silently change that mode.

These entities were proposals in 0.6.1 and are implemented in 0.7.0; see [schedule and circulation behavior](SCHEDULES.md). The existing integration also implements HVAC/fan commands. No new commands were sent to the user's hardware while incorporating this report or building the controls.

For editing weekly programs, keep Jetson's native schedule editor initially. HA's [Schedule helper](https://www.home-assistant.io/integrations/schedule/) edits local weekly time blocks and can trigger automations, but does not synchronize or edit a vendor's schedules by itself. A separate HA-managed program could issue Jetson controls, subject to the reported pause behavior. A native Jetson editor would additionally need to model shared presets/zones, vacation precedence, timezone/DST behavior, and pause/resume semantics; those need more evidence before attempting two-way synchronization.
