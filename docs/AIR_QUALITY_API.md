# Separate air-quality current and history endpoints

Authorized GETs on **November 4, 2026 (America/Denver)** established two additional routes absent from the app-callsite inventory. Both returned HTTP 200. These are observed response contracts, not a complete vendor specification; see [live OpenAPI](live-openapi.json).

## Current readings

```http
GET /v1/zones/{zoneId}/airQuality/current
```

The full-access response contains `access`, `timezone` (an IANA name), and `current`. Current fields include overall classification, `lastUpdatedAt`, nullable `fanRunStartedAt`, and CO₂/PM2.5/TVOC objects with `value`, `level`, `measuredAt`, and `settling`. The existing ppm, μg/m³, and ppb interpretation follows the recovered types. This route returns the current readings without the history array seen in the combined `/airQuality` response.

A successful HTTP request does not establish a fresh sample; use the source timestamp and settling flags. Only full-access responses were captured here. Limited-access shapes and entitlement behavior on this separate route remain unverified.

## History query

```http
GET /v1/zones/{zoneId}/airQuality/history?startAt=2026-11-04T23:00:00Z&endAt=2026-11-05T01:00:00Z&granularity=hour
```

The dates above illustrate a two-hour UTC range; URL-encode query values in clients. All three parameters are required:

| Parameter | Observed accepted form |
| --- | --- |
| `startAt` | Absolute timestamp; UTC timestamps with an offset were accepted |
| `endAt` | Absolute timestamp; UTC timestamps with an offset were accepted |
| `granularity` | `hour`, `day`, or `month`; all three returned HTTP 200 for the tested two-hour range |

Omitting the parameters returned HTTP 400 with `VALIDATION_ERROR` and specific errors naming these fields. A deliberately nonexistent sibling path returned 404. No request body or guessed POST was used.

| Response field | Observed structure |
| --- | --- |
| `access`, `timezone`, `granularity` | Access classification, system timezone, selected granularity |
| `start`, `end` | Requested bounds represented in the system's local offset |
| `earliestDataAt` | Reported earliest available timestamp; not a retention guarantee |
| `buckets[]` | Start/end, coverage, overall classification, and CO₂/PM2.5/TVOC value/level objects |
| `summary.overall` | Average classification and a peak classification with start/end |
| `summary.co2`, `.pm25`, `.tvoc` | Average value/level and peak value/level with start/end |

The hourly query returned two buckets. Day and month queries over the same short range each returned one clipped bucket. Bucket starts preserved the requested start's seconds/milliseconds; they were not necessarily aligned to wall-clock hour boundaries. Only `coverage: sampled` was observed.

Changing granularity changed both bucket and summary values. The returned peaks matched a returned bucket in these samples, suggesting bucket-level rather than instantaneous sample peaks; that is an inference, not a verified aggregation specification. Do not assume a simple average of rounded bucket values reproduces the backend's summary. Empty ranges, gaps, timezone/DST boundaries, long spans, range limits, and retention policies remain untested.

## Search scope and sensor assignment

The round recorded 70 authenticated reads, including baseline/negative controls and parameter variants. It tested 57 distinct new candidate paths: the two AQ routes worked and the other 55 returned 404. Discovery/telemetry/signal routes and temperature/humidity/circulation/pressure variants at zone or system scope did not reveal additional measurements. This does not prove that no other route exists or that a route cannot be gated by hardware, role, or firmware.

The account still reported one zone. Its ReturnAir TEMCO-AQM and SupplyAir TEMCO-TH were both assigned to that zone and the same indoor unit. Their generic equipment `/status` responses again contained only `health.faults: []`. The AQ routes remain zone-scoped and contain no physical source-sensor ID, so they do not establish separate supply/return readings or the sensor arrangement for a hypothetical two-zone installation.

The integration still uses its existing combined `/airQuality` poll in 0.7.0. No polling/control behavior was changed during this search, and no device commands were sent. These new routes are documented for further development; history is not imported into Recorder.
