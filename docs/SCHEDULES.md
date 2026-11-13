# Schedule status, resume, and circulation duration

Version 0.7.0 adds three zone-named entities under the existing system device. They read the already-polled zone status and add no background API requests. Known zones can gain these entities on a normal poll after the API first reports the relevant fields.

| Entity | Availability and behavior |
| --- | --- |
| Schedule paused | Binary sensor: on/Paused for `schedule.status: Paused`, off/Active for Active. An absent/empty schedule is unavailable; an unrecognized status remains unknown. Attributes identify the reported schedule ID and type. |
| Resume schedule | Configuration button. Created when a valid reported schedule ID and Weekly/Vacation kind exist. Available only while that reported schedule is paused and the zone is available. |
| Circulation minutes per hour | Configuration number, integer 0–60 with step 1 and an input box. Created when modern or legacy duration settings are reported. Missing/invalid values are unavailable, not zero. |

All three use the same system device and proper zone name. Names, labels, attributes, and control-validation errors are translated into English, Spanish, and French. Their stable unique-ID suffixes are `:schedule_paused`, `:resume_schedule`, and `:circulation_minutes` after `{systemId}:{zoneId}`.

## Resume behavior

The integration reads `schedule.id`, `schedule.kind`, and `schedule.status` from zone status. Pressing Resume schedule sends:

```http
POST /v1/schedules/{reportedScheduleId}/resume
Content-Type: application/json

{"kind":"Weekly"}
```

Vacation is sent only when Vacation is the currently reported kind. Weekly is never assumed for a missing or unknown kind. The client requires the recovered response `{"success":true}`; false, missing, or malformed success is an error.

The coordinator resolves the current cached schedule inside its shared command lock, rather than retaining an ID from entity creation. If the zone/schedule disappears, is offline, or is no longer paused before the command starts, the command is rejected. A successful request triggers a normal status refresh; the integration does not optimistically mark the schedule Active. No polling update or HVAC change automatically presses Resume.

A [community hardware report](COMMUNITY_REPORTS.md) says app changes pause the weekly schedule until it is resumed. These controls make that state visible and let the user explicitly resume it. The report confirms Weekly resume in that bridge; Vacation support follows the recovered request schema and has mock coverage, without an independent hardware test here.

## Circulation minutes per hour

Setting 30 sends only:

```http
PATCH /v1/zones/{zoneId}/circulation/settings
Content-Type: application/json

{"fanOnDuration":30}
```

The integration does not include `mode`, `fanSpeed`, or other settings in this request. It checks the returned circulation settings and matching duration, then requests a normal refresh. The cached number changes when the reported status changes, rather than optimistically after a click. Nonfinite, fractional, boolean, string, or out-of-range inputs are rejected.

The duration applies to the **Circulate** mode. The entity's attributes show the current circulation mode and the mode where the setting applies. A configured duration while Off or Continuous is not evidence that timed circulation is running. Use Jetson's app to change the circulation mode. The community contributor's 0/15/30/45/60 values are useful choices, while the recovered API supports every whole minute from 0 through 60.

## Editing weekly programs

Jetson's native schedule editor remains the place to edit its weekly programs, presets, and vacation settings. HA's [Schedule helper](https://www.home-assistant.io/integrations/schedule/) can drive separate HA automations, but does not synchronize with Jetson schedules by itself. Two-way editing would require decisions about shared presets/zones, vacation precedence, pause/resume behavior, and timezone/DST handling.

## Validation

Protocol tests check methods, payloads, identifier encoding, input validation, expected responses, and failure handling. Model/entity/coordinator adapters check changing schedule targets while a command waits, unknown/missing schedule state, circulation-only writes, no automatic resume, no optimistic changes, offline/removal/auth guards, dynamic discovery, and translations. These do not replace a live HA or physical-control test. No commands were sent to the user's hardware while building this release.

## Circulation control placement (0.9.1)

Circulation per hour is now a primary control, not a configuration-category entity.
It retains its entity ID and 0–60 minute range. The setting applies in Circulate
mode; changing minutes does not change mode or speed. Fan speed remains available
inside the thermostat card, without a duplicate selector. The Fan speed setting
sensor remains for history; Actual fan speed is measured operation. Labels are
localized into English, Spanish and French.
