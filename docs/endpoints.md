# HTTP callsite inventory

All 43 operations below are confirmed in app callsites. 12 have observed HTTP 200 results from authorized checks on November 3–4, 2026. Five earlier response schemas matched auth/empty-account data; newer populated responses were observed without full schema revalidation and may extend the recovered types.

The live-discovered energy/current and generic equipment-status routes are additional to this table. See [live OpenAPI](live-openapi.json), [energy](ENERGY.md), and [status/pressure findings](LIVE_TELEMETRY.md). The combined inventory has 45 unique method/path combinations.

See [API guide](API.md) for semantics, [validation details](VALIDATION.md) for live-test limits, and [schema catalog](schema-catalog.md) for field definitions.

| Method | Path | Request schema | Success schema | App function / decoded source line | Live check |
| --- | --- | --- | --- | --- | --- |
| POST | `/v1/auth/register` | RegisterUserRequest | RegisterUserResponse | `register`, L803230 | Not tested |
| POST | `/v1/install/auth/register` | RegisterUserRequest | RegisterUserResponse | `registerInstaller`, L803375 | Not tested |
| POST | `/v1/auth/sign-in/magic-link` | SignInRequest | SignInResponse | `requestMagicLink`, L803565 | HTTP 200; schema not checked |
| POST | `/v1/install/auth/sign-in/magic-link` | SignInRequest | SignInResponse | `requestInstallerMagicLink`, L803791 | Not tested |
| POST | `/v1/auth/verify/magic-link` | VerifyMagicLinkRequest | VerifyMagicLinkResponse | `verifyMagicLink`, L804017 | HTTP 200; schema matched |
| POST | `/v1/auth/refresh` | RefreshTokenRequest | RefreshTokenResponse | `refreshAccessToken`, L803014 | HTTP 200; schema matched |
| GET | `/v1/users/me` | — | GetCurrentUserResponse | `getCurrentUser`, L921736 | HTTP 200; schema matched |
| PATCH | `/v1/users/me` | UpdateCurrentUserRequest | UpdateCurrentUserResponse | `updateCurrentUser`, L921796 | Not tested |
| GET | `/v1/systems` | — | GetSystemsResponse | `getSystems`, L921674 | HTTP 200; schema not checked |
| GET | `/v1/systems/{systemId}/equipment` | — | GetSystemEquipmentResponse | `getSystemEquipment`, L921859 | HTTP 200; schema not checked |
| GET | `/v1/systems/{systemId}/boards` | — | GetSystemBoardsResponse | `getSystemBoards`, L921928 | HTTP 200; schema not checked |
| GET | `/v1/systems/{systemId}/zones` | — | GetSystemZonesResponse | `getSystemZones`, L921997 | HTTP 200; schema not checked |
| GET | `/v1/airQuality/classification` | — | GetAirQualityClassificationResponse | `getAirQualityClassification`, L922066 | HTTP 200; schema matched |
| GET | `/v1/systems/{systemId}/members` | — | GetSystemMembersResponse | `getSystemMembers`, L922126 | Not tested |
| POST | `/v1/systems/{systemId}/members` | AddSystemMemberRequest | AddSystemMemberResponse | `upsertSystemMember`, L922195 | Not tested |
| PATCH | `/v1/systems/{systemId}/members/{memberId}` | UpdateSystemMemberRequest | UpdateSystemMemberResponse | `upsertSystemMember`, L922195 | Not tested |
| DELETE | `/v1/systems/{systemId}/members/{memberId}` | — | RemoveSystemMemberResponse | `removeSystemMember`, L922344 | Not tested |
| GET | `/v1/equipment/{equipmentId}/heatpump/status` | — | GetEquipmentHeatPumpStatusResponse | `getEquipmentHeatPumpStatus`, L922422 | HTTP 200; schema not checked |
| GET | `/v1/zones/{zoneId}/status` | — | GetZoneStatusResponse | `getZoneStatus`, L922491 | HTTP 200; schema not checked |
| GET | `/v1/zones/{zoneId}/airQuality` | — | GetAirQualityResponse | `getAirQuality`, L922560 | HTTP 200; schema not checked |
| POST | `/v1/zones/{zoneId}/hvac/mode` | SetHvacModeRequest | SetHvacModeResponse | `setZoneHvacMode`, L922629 | Not tested |
| POST | `/v1/zones/{zoneId}/ambientTemperature/setpoint` | SetAmbientTemperatureSetpointRequest | SetAmbientTemperatureSetpointResponse | `setZoneAmbientTemperatureSetpoint`, L922701 | Not tested |
| GET | `/v1/systems/{systemId}/schedules` | — | GetAllSchedulesResponse | `getSystemSchedules`, L922774 | Not tested |
| POST | `/v1/systems/{systemId}/schedules` | CreateScheduleRequest | CreateScheduleResponse | `upsertSchedule`, L922843 | Not tested |
| PATCH | `/v1/schedules/{scheduleId}` | UpdateScheduleRequest | UpdateScheduleResponse | `upsertSchedule`, L922843 | Not tested |
| DELETE | `/v1/schedules/{scheduleId}` | — | DeleteScheduleResponse | `deleteSchedule`, L922958 | Not tested |
| POST | `/v1/schedules/{scheduleId}/pause` | PauseScheduleRequest | PauseScheduleResponse | `pauseSchedule`, L923033 | Not tested |
| POST | `/v1/schedules/{scheduleId}/resume` | ResumeScheduleRequest | ResumeScheduleResponse | `resumeSchedule`, L923108 | Not tested |
| GET | `/v1/systems/{systemId}/schedules/presets` | — | GetSchedulePresetsResponse | `getSchedulePresets`, L923183 | Not tested |
| POST | `/v1/systems/{systemId}/schedules/presets` | CreateSchedulePresetRequest | CreateSchedulePresetResponse | `upsertPreset`, L923252 | Not tested |
| PATCH | `/v1/schedules/presets/{presetId}` | UpdateSchedulePresetRequest | UpdateSchedulePresetResponse | `upsertPreset`, L923252 | Not tested |
| DELETE | `/v1/schedules/presets/{presetId}` | — | DeleteSchedulePresetResponse | `deletePreset`, L923383 | Not tested |
| PATCH | `/v1/zones/{zoneId}/circulation/settings` | UpdateCirculationSettingsRequest | UpdateCirculationSettingsResponse | `updateCirculationSettings`, L923474 | Not tested |
| PATCH | `/v1/zones/{zoneId}/humidity/settings` | UpdateHumiditySettingsRequest | UpdateHumiditySettingsResponse | `updateHumiditySettings`, L923545 | Not tested |
| PATCH | `/v1/systems/{systemId}` | UpdateSystemRequest | UpdateSystemResponse | `patchSystem`, L923616 | Not tested |
| GET | `/v1/systems/{systemId}/settings` | — | GetSystemSettingsResponse | `getSystemSettings`, L923688 | Not tested |
| PATCH | `/v1/systems/{systemId}/settings` | UpdateSystemSettingsRequest | UpdateSystemSettingsResponse | `patchSystemSettings`, L923757 | Not tested |
| GET | `/v1/systems/{systemId}/claim/preview` | — | GetClaimPreviewResponse | `getClaimPreview`, L923828 | Not tested |
| POST | `/v1/systems/{systemId}/claim` | ClaimSystemRequest | ClaimSystemResponse | `claimSystem`, L923897 | Not tested |
| GET | `/v1/equipment/{equipmentId}/thermostat/settings` | — | GetThermostatSettingsResponse | `getThermostatSettings`, L923967 | Not tested |
| PATCH | `/v1/equipment/{equipmentId}/thermostat/settings` | UpdateThermostatSettingsRequest | UpdateThermostatSettingsResponse | `patchThermostatSettings`, L924036 | Not tested |
| GET | `/v1/systems/{systemId}/vacation` | — | GetVacationResponse | `getVacation`, L924107 | Not tested |
| PUT | `/v1/systems/{systemId}/vacation` | UpdateVacationRequest | UpdateVacationResponse | `upsertVacation`, L924176 | Not tested |
