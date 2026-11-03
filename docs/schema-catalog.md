# Recovered schema catalog

309 named definitions reconstructed from declarative Zod schemas in Jetson Home 1.2.8. Names match app exports; an `Alternate` suffix distinguishes another bundled definition with the same name. Compiled module IDs are retained only as `x-source-module` provenance in JSON. Neither schema names nor those module IDs are sent to the API. A schema does not establish an HTTP route or permission to call it. [JSON definitions](recovered-schemas.json) preserve nesting, required fields, descriptions, and constraints. `?` marks optional fields; `null` is a separate allowed value.

Refinement callbacks were not executed. Their messages appear under `x-refinements`; transformations and JavaScript Date conversions remain annotations. The catalog is reference material, not a vendor specification.

## SystemMembership

```text
{role: 'Owner' | 'Member'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `role` | Yes | Role of the member in the system. |

## SystemMember

```text
{user: {id: string, email: string, name: string, onboardingCompleted: boolean}, role: 'Owner' | 'Member'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `user` | Yes | User that is a member. |
| `role` | Yes | Role of the member in the system. |

## SystemMemberInput

```text
{user: UserInput, role: 'Owner' | 'Member'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `user` | Yes |  |
| `role` | Yes | Role of the member in the system. |

## SystemMembershipRole

```text
'Owner' | 'Member'
```

## User

```text
{id: string, email: string, name: string, onboardingCompleted: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the user. |
| `email` | Yes | The email address of the user. |
| `name` | Yes | The name of the user. |
| `onboardingCompleted` | Yes | Whether the user has completed onboarding. |

## UserInput

```text
{email: string, name: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes | The email address of the user. |
| `name` | Yes | The name of the user. |

## Email

```text
string
```

## CreateEquipmentRequest

```text
{name?: string, installedAt?: string, model?: 'EMPORIA-VUE-3' | 'EM-001', serialNumber?: string, boardId?: BoardId, type: 'EnergyMonitor'} | {name?: string, installedAt?: string, model?: 'EV-001', serialNumber?: string, type: 'EvCharger'} | {name?: string, installedAt?: string, model?: 'HUM-3P', humidifierType?: 'Evaporative' | 'Steam', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId, zoneIds?: ZoneIds, type: 'Humidifier'} | {name?: string, installedAt?: string, model?: 'TEMCO-AQM' | 'TEMCO-TH', role?: 'ReturnAir' | 'SupplyAir', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId, zoneIds?: ZoneIds, type: 'Sensor'} | {name?: string, installedAt?: string, model?: 'THE-001', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId, zoneIds?: ZoneIds, type: 'Thermostat'}
```

## CreateEquipmentResponse

```text
EnergyMonitor | EvCharger | HeatPump | HeatPumpIdu | HeatPumpOdu | Humidifier | Sensor | Thermostat
```

## JetsonCareSubscription

```text
{tier: 'care' | 'care_plus' | 'none'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `tier` | Yes | The resolved JetsonCare tier the customer pays for; 'none' when the equipment has no paid plan. |

## EquipmentBase

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |

## EnergyMonitor

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'EnergyMonitor', model: 'EMPORIA-VUE-3' | 'EM-001', serialNumber: string | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Energy monitor model number |
| `serialNumber` | Yes | Manufacturer serial number. Null until supplied. |

## EvCharger

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'EvCharger', model: 'EV-001', serialNumber: string | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Charger model SKU. |
| `serialNumber` | Yes | Manufacturer serial number; used as the OCPP charge point ID. Null until supplied. |

## HeatPump

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'HeatPump', model: string, family: 'CDHP-HH1' | 'CDHP-HH2' | 'CDHP-AIR1'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Jetson model number |
| `family` | Yes | Jetson model family |

## HeatPumpIdu

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'HeatPumpIdu', model: string, family: 'CDHP-HH1' | 'CDHP-HH2' | 'CDHP-AIR1'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Jetson model number |
| `family` | Yes | Jetson model family |

## HeatPumpOdu

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'HeatPumpOdu', model: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Jetson ODU model number |

## Humidifier

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'Humidifier', model: 'HUM-3P', humidifierType: 'Evaporative' | 'Steam'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Humidifier model number |
| `humidifierType` | Yes | Humidifier technology type |

## Sensor

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'Sensor', model: 'TEMCO-AQM' | 'TEMCO-TH', role: 'ReturnAir' | 'SupplyAir'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Sensor model number |
| `role` | Yes | Sensor role |

## Thermostat

```text
{id: string, name: string, boardId: string | null, parentEquipmentId: string | null, zoneIds: Array<string>, installedAt: string | null, connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected', jetsonCare?: {tier: 'care' | 'care_plus' | 'none'}, type: 'Thermostat', model: 'THE-001'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the equipment. |
| `name` | Yes |  |
| `boardId` | Yes | ID of the board this equipment is attached to. |
| `parentEquipmentId` | Yes | ID of the parent equipment, if this is a peripheral. |
| `zoneIds` | Yes | IDs of the zones this equipment serves. |
| `installedAt` | Yes | When the equipment was physically installed. |
| `connectionStatus` | No | Whether the equipment is actively reporting. Resolved server-side using a 5-minute staleness window. Optional for rollback safety and for equipment types that do not report liveness yet. |
| `jetsonCare` | No | This equipment's resolved direct JetsonCare status; omitted when the subscription source is unavailable (status unknown). Direct subscription only — never granted by internal, service, or dogfood access. |
| `type` | Yes |  |
| `model` | Yes | Thermostat model number |

## Equipment

```text
EnergyMonitor | EvCharger | HeatPump | HeatPumpIdu | HeatPumpOdu | Humidifier | Sensor | Thermostat
```

## EquipmentStatus

```text
{connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `connectionStatus` | No | Connection status of the equipment. |

## ConnectionStatus

```text
'Unknown' | 'Connected' | 'Disconnected'
```

## EnergyMonitorDiscriminant

```text
{type: 'EnergyMonitor', model: 'EMPORIA-VUE-3' | 'EM-001'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Energy monitor model number |

## EvChargerDiscriminant

```text
{type: 'EvCharger', model: 'EV-001'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Charger model SKU. |

## HeatPumpDiscriminant

```text
{type: 'HeatPump', model: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Jetson model number |

## HeatPumpIduDiscriminant

```text
{type: 'HeatPumpIdu', model: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Jetson model number |

## HeatPumpOduDiscriminant

```text
{type: 'HeatPumpOdu', model: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Jetson ODU model number |

## HumidifierDiscriminant

```text
{type: 'Humidifier', model: 'HUM-3P'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Humidifier model number |

## SensorDiscriminant

```text
{type: 'Sensor', model: 'TEMCO-AQM' | 'TEMCO-TH'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Sensor model number |

## ThermostatDiscriminant

```text
{type: 'Thermostat', model: 'THE-001'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `model` | Yes | Thermostat model number |

## EquipmentDiscriminant

```text
EnergyMonitorDiscriminant | EvChargerDiscriminant | HeatPumpDiscriminant | HeatPumpIduDiscriminant | HeatPumpOduDiscriminant | HumidifierDiscriminant | SensorDiscriminant | ThermostatDiscriminant
```

## EnergyMonitorModel

```text
'EMPORIA-VUE-3' | 'EM-001'
```

## EquipmentType

```text
'EnergyMonitor' | 'EvCharger' | 'HeatPump' | 'HeatPumpIdu' | 'HeatPumpOdu' | 'Humidifier' | 'Sensor' | 'Thermostat'
```

## EvChargerModel

```text
'EV-001'
```

## HumidifierModel

```text
'HUM-3P'
```

## SensorModel

```text
'TEMCO-AQM' | 'TEMCO-TH'
```

## SensorRole

```text
'ReturnAir' | 'SupplyAir'
```

## ThermostatModel

```text
'THE-001'
```

## HeatPumpFamily

```text
'CDHP-HH1' | 'CDHP-HH2' | 'CDHP-AIR1'
```

## HumidifierType

```text
'Evaporative' | 'Steam'
```

## ParentEquipmentId

Parent equipment this peripheral attaches to.

```text
string
```

## BoardId

Board the equipment is attached to, for hub-attached equipment. Null means not attached.

```text
string | null
```

## ZoneIds

Zones the equipment serves.

```text
Array<string>
```

## EnergyMonitorInput

```text
{name: string, installedAt: string, model: 'EMPORIA-VUE-3' | 'EM-001', serialNumber: string, boardId: BoardId}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | Display name for the equipment.; minLength: 1 |
| `installedAt` | Yes | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | Yes | Energy monitor model number. |
| `serialNumber` | Yes | Manufacturer serial number. Omitted if unknown at creation.; minLength: 1 |
| `boardId` | Yes |  |

## EvChargerInput

```text
{name: string, installedAt: string, model: 'EV-001', serialNumber: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | Display name for the equipment.; minLength: 1 |
| `installedAt` | Yes | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | Yes | Charger model SKU. |
| `serialNumber` | Yes | Manufacturer serial number; used as the OCPP charge point ID. Omitted if unknown at creation.; minLength: 1 |

## HumidifierInput

```text
{name: string, installedAt: string, model: 'HUM-3P', humidifierType: 'Evaporative' | 'Steam', boardId: BoardId, parentEquipmentId: ParentEquipmentId, zoneIds: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | Display name for the equipment.; minLength: 1 |
| `installedAt` | Yes | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | Yes | Humidifier model number. |
| `humidifierType` | Yes | Humidifier technology type. |
| `boardId` | Yes |  |
| `parentEquipmentId` | Yes |  |
| `zoneIds` | Yes |  |

## SensorInput

```text
{name: string, installedAt: string, model: 'TEMCO-AQM' | 'TEMCO-TH', role: 'ReturnAir' | 'SupplyAir', boardId: BoardId, parentEquipmentId: ParentEquipmentId, zoneIds: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | Display name for the equipment.; minLength: 1 |
| `installedAt` | Yes | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | Yes | Sensor model number. |
| `role` | Yes | Sensor role. |
| `boardId` | Yes |  |
| `parentEquipmentId` | Yes |  |
| `zoneIds` | Yes |  |

## ThermostatInput

```text
{name: string, installedAt: string, model: 'THE-001', boardId: BoardId, parentEquipmentId: ParentEquipmentId, zoneIds: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | Display name for the equipment.; minLength: 1 |
| `installedAt` | Yes | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | Yes | Thermostat model number. |
| `boardId` | Yes |  |
| `parentEquipmentId` | Yes |  |
| `zoneIds` | Yes |  |

## DeleteEquipmentResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## ResultCode

```text
'ok'
```

## GetSignalSummaryRequest

```text
{start: string | string, end?: string, signals: Array<SignalName>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `start` | Yes | Start time: absolute time (ISO 8601) or negative relative duration (e.g. "-1h", "-24h", "-7d") |
| `end` | No | End time (ISO 8601). Defaults to current time. |
| `signals` | Yes | Signals to include in the response; minItems: 1 |

## NumericSummary

```text
{type: 'numeric', signal: SignalName, writeCount: integer, min: number | null, max: number | null, mean: number | null, firstSeen?: {value: SignalValue, timestamp: string}, lastSeen?: {value: SignalValue, timestamp: string}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `signal` | Yes |  |
| `writeCount` | Yes | minimum: 0 |
| `min` | Yes |  |
| `max` | Yes |  |
| `mean` | Yes |  |
| `firstSeen` | No |  |
| `lastSeen` | No |  |

## CategoricalSummary

```text
{type: 'categorical', signal: SignalName, writeCount: integer, durationByState: {}, transitionCount: integer, modeState: string | null, firstSeen?: {value: SignalValue, timestamp: string}, lastSeen?: {value: SignalValue, timestamp: string}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `signal` | Yes |  |
| `writeCount` | Yes | minimum: 0 |
| `durationByState` | Yes | Seconds spent in each distinct state. |
| `transitionCount` | Yes | minimum: 0 |
| `modeState` | Yes | Most-common state by duration, null if no data. |
| `firstSeen` | No |  |
| `lastSeen` | No |  |

## EventSummary

```text
{type: 'event', signal: SignalName, writeCount: integer, occurrenceCount: integer, distinctValues: Array<string>, totalActiveSeconds: number, firstOccurrence?: {value: SignalValue, timestamp: string}, lastOccurrence?: {value: SignalValue, timestamp: string}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes |  |
| `signal` | Yes |  |
| `writeCount` | Yes | minimum: 0 |
| `occurrenceCount` | Yes | Number of writes with a non-empty value.; minimum: 0 |
| `distinctValues` | Yes | Distinct non-empty values seen. |
| `totalActiveSeconds` | Yes | Total seconds during which any non-empty value was active.; minimum: 0 |
| `firstOccurrence` | No |  |
| `lastOccurrence` | No |  |

## SignalSummary

```text
NumericSummary | CategoricalSummary | EventSummary
```

## GetSignalSummaryResponse

```text
{systemId: string, start: string, end: string, summaries: Array<SignalSummary>, truncated: False} | {systemId: string, start: string, end: string, summaries: Array<SignalSummary>, truncated: True, totalEventCount: integer}
```

## RelativeOrAbsoluteTime

```text
string | string
```

## SignalName

```text
'indoorTemperature' | 'temperatureSetpoint' | 'indoorHumidity' | 'humiditySetpoint' | 'hvacMode' | 'hvacStatus' | 'fanSpeedSetting' | 'fanSpeedLevel' | 'diagnosticCodes' | 'outdoorTemperature' | 'outdoorHumidity' | 'windSpeed' | 'solarRadiation' | 'cloudCover' | 'windDirection' | 'surfacePressure'
```

## SignalValue

```text
number | string | null | Array<string>
```

## Aggregation

```text
'mean' | 'min' | 'max' | 'first' | 'last' | 'count' | 'mode' | 'distinct' | 'any'
```

## SignalType

```text
'numeric' | 'categorical' | 'event'
```

## GetSystemEventsRequest

```text
{start: string | string, end?: string, signals: Array<SignalName>, limit?: integer, order?: 'asc' | 'desc'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `start` | Yes | Start time: absolute time (ISO 8601) or negative relative duration (e.g. "-1h", "-24h", "-7d") |
| `end` | No | End time (ISO 8601). Defaults to current time. |
| `signals` | Yes | Signals to include in the response; minItems: 1 |
| `limit` | No | Maximum number of events to return. Hard cap is 10000.; minimum: 1; maximum: 10000; default: 1000 |
| `order` | No | Sort order. Defaults to desc (most recent first).; default: "desc" |

## SystemEvent

```text
{timestamp: string, signal: SignalName, value: SignalValue}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `timestamp` | Yes |  |
| `signal` | Yes |  |
| `value` | Yes |  |

## GetSystemEventsResponse

```text
{systemId: string, start: string, end: string, events: Array<SystemEvent>, truncated: False} | {systemId: string, start: string, end: string, events: Array<SystemEvent>, truncated: True, totalCount: integer}
```

## SignalSelector

```text
SignalName | {name: SignalName, aggregation?: 'mean' | 'min' | 'max' | 'first' | 'last' | 'count' | 'mode' | 'distinct' | 'any', alias?: string}
```

## GetSystemHistoryRequest

```text
{start: string | string, end?: string, signals: Array<SignalSelector>, maxDataPoints?: integer, bucketSize?: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `start` | Yes | Start time: absolute time (ISO 8601) or negative relative duration (e.g. "-1h", "-24h", "-7d") |
| `end` | No | End time (ISO 8601). Defaults to current time. |
| `signals` | Yes | Signals to include in the response; minItems: 1 |
| `maxDataPoints` | No | Max number of data points to return. Mutually exclusive with bucketSize.; minimum: 10; maximum: 5000 |
| `bucketSize` | No | Explicit bucket size in seconds. Mutually exclusive with maxDataPoints.; minimum: 10; maximum: 86400 |

Cross-field constraints: maxDataPoints and bucketSize are mutually exclusive.

## GetSystemHistoryResponse

```text
{systemId: string, start: string, end: string, intervalSeconds: number, timestamps: Array<string>, signals: {}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systemId` | Yes |  |
| `start` | Yes |  |
| `end` | Yes |  |
| `intervalSeconds` | Yes |  |
| `timestamps` | Yes |  |
| `signals` | Yes |  |

## GetSystemTransitionsRequest

```text
{start: string | string, end?: string, signals: Array<SignalName>, numericThreshold?: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `start` | Yes | Start time: absolute time (ISO 8601) or negative relative duration (e.g. "-1h", "-24h", "-7d") |
| `end` | No | End time (ISO 8601). Defaults to current time. |
| `signals` | Yes | Signals to include in the response; minItems: 1 |
| `numericThreshold` | No | For numeric signals: ignore changes smaller than this magnitude. Must be positive. Omit the field to disable jitter suppression.; exclusiveMinimum: 0 |

## SignalTransition

```text
{timestamp: string, signal: SignalName, from: SignalValue, to: SignalValue, durationSeconds: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `timestamp` | Yes | When the new value took effect. |
| `signal` | Yes |  |
| `from` | Yes |  |
| `to` | Yes |  |
| `durationSeconds` | Yes | How long the previous state lasted, in seconds, until this transition.; minimum: 0 |

## GetSystemTransitionsResponse

```text
{systemId: string, start: string, end: string, transitions: Array<SignalTransition>, truncated: False} | {systemId: string, start: string, end: string, transitions: Array<SignalTransition>, truncated: True, totalEventCount: integer}
```

## GetUserSystemsResponse

```text
{systems: Array<AdminSystem>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systems` | Yes | All systems the user has access to. |

## System

```text
{id: string, name: string, address?: {line1: string, line2?: string, city: string, county?: string, stateCode: string, countryCode: string, postalCode?: string, latitude: number, longitude: number}, settings: {temperatureUnit: 'Celsius' | 'Fahrenheit', ambientTemperatureSource: 'Internal' | 'External'}, featureChannel: 'general' | 'early_access' | 'internal'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | Unique ID |
| `name` | Yes | User-facing display name |
| `address` | No | Physical installation address |
| `settings` | Yes | Configuration settings |
| `featureChannel` | Yes | Feature channel for staged feature rollout. |

## SystemHealth

```text
{health: {connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `health` | Yes |  |

## SystemOverview

```text
{id: string, name: string, address?: {line1: string, line2?: string, city: string, county?: string, stateCode: string, countryCode: string, postalCode?: string, latitude: number, longitude: number}, settings: {temperatureUnit: 'Celsius' | 'Fahrenheit', ambientTemperatureSource: 'Internal' | 'External'}, featureChannel: 'general' | 'early_access' | 'internal', health: {connectionStatus?: 'Unknown' | 'Connected' | 'Disconnected'}, minBoardVersion: string | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | Unique ID |
| `name` | Yes | User-facing display name |
| `address` | No | Physical installation address |
| `settings` | Yes | Configuration settings |
| `featureChannel` | Yes | Feature channel for staged feature rollout. |
| `health` | Yes |  |
| `minBoardVersion` | Yes | Minimum board firmware version across all boards in the system. |

## AdminSystem

```text
{id: string, name: string, address?: {line1: string, line2?: string, city: string, county?: string, stateCode: string, countryCode: string, postalCode?: string, latitude: number, longitude: number}, settings: {temperatureUnit: 'Celsius' | 'Fahrenheit', ambientTemperatureSource: 'Internal' | 'External'}, featureChannel: 'general' | 'early_access' | 'internal', deploymentType: 'customer' | 'internal'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | Unique ID |
| `name` | Yes | User-facing display name |
| `address` | No | Physical installation address |
| `settings` | Yes | Configuration settings |
| `featureChannel` | Yes | Feature channel for staged feature rollout. |
| `deploymentType` | Yes | Deployment type of the system. |

## Address

```text
{line1: string, line2?: string, city: string, county?: string, stateCode: string, countryCode: string, postalCode?: string, latitude: number, longitude: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `line1` | Yes | minLength: 1 |
| `line2` | No |  |
| `city` | Yes | minLength: 1 |
| `county` | No |  |
| `stateCode` | Yes | minLength: 1 |
| `countryCode` | Yes | minLength: 1 |
| `postalCode` | No |  |
| `latitude` | Yes | minimum: -90; maximum: 90 |
| `longitude` | Yes | minimum: -180; maximum: 180 |

## DeploymentType

```text
'customer' | 'internal'
```

## FeatureChannel

```text
'general' | 'early_access' | 'internal'
```

## SystemSettings

```text
{temperatureUnit: 'Celsius' | 'Fahrenheit', ambientTemperatureSource: 'Internal' | 'External'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `temperatureUnit` | Yes | Preferred temperature unit for the system. |
| `ambientTemperatureSource` | Yes | Preferred ambient temperature source for the system. |

## AmbientTemperatureSource

```text
'Internal' | 'External'
```

## TemperatureUnit

```text
'Celsius' | 'Fahrenheit'
```

## DeleteUserByEmailResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## EmailPathParams

```text
{email: Email}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes |  |

## DeleteUserByIdResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## DeleteZoneResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## GetBoardBySerialNumberResponse

```text
{board: {id: string, serialNumber?: string, type: 'Arctic' | 'Alpha', systemId: string}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `board` | Yes | The board information. |

## Board

```text
{id: string, serialNumber?: string, type: 'Arctic' | 'Alpha'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | ID of the board. |
| `serialNumber` | No | Serial number of the board. |
| `type` | Yes | Type of the board. |

## BoardInput

```text
{serialNumber?: string, type: 'Arctic' | 'Alpha'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `serialNumber` | No | Serial number of the board. |
| `type` | Yes | Type of the board. |

## BoardType

```text
'Arctic' | 'Alpha'
```

## GetOperationalSummaryRequest

```text
{start: string | string, end?: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `start` | Yes | Start time: absolute time (ISO 8601) or negative relative duration (e.g. "-24h", "-7d") |
| `end` | No | End time (ISO 8601). Defaults to current time. |

## GetOperationalSummaryResponse

```text
{systemId: string, start: string, end: string, days: Array<{date: string, weather: {meanTemperatureC: number, minTemperatureC: number, maxTemperatureC: number, meanWindSpeedMs?: number, totalSolarRadiationWhm2?: number}, zones: Array<{zoneId: string, zoneName: string, meanTemperatureC: number, setpointMeanC: number, setpointRangeC: number}>, equipment: Array<{equipmentId: string, model: string, heatingRuntimeSec: number, coolingRuntimeSec: number, heatDeliveredWh?: number, heatEstimationMethod?: 'airflow_delta_t' | 'capacity_curve'}>}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systemId` | Yes |  |
| `start` | Yes |  |
| `end` | Yes |  |
| `days` | Yes |  |

## OperationalSummary

```text
{systemId: string, start: string, end: string, days: Array<{date: string, weather: {meanTemperatureC: number, minTemperatureC: number, maxTemperatureC: number, meanWindSpeedMs?: number, totalSolarRadiationWhm2?: number}, zones: Array<{zoneId: string, zoneName: string, meanTemperatureC: number, setpointMeanC: number, setpointRangeC: number}>, equipment: Array<{equipmentId: string, model: string, heatingRuntimeSec: number, coolingRuntimeSec: number, heatDeliveredWh?: number, heatEstimationMethod?: 'airflow_delta_t' | 'capacity_curve'}>}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systemId` | Yes |  |
| `start` | Yes |  |
| `end` | Yes |  |
| `days` | Yes |  |

## GetSystemBoardsResponseAlternate

```text
{boards: Array<Board>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `boards` | Yes | The list of system boards. |

## GetSystemMembersResponseAlternate

```text
{members: Array<SystemMember>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `members` | Yes | All members belonging to the system. |

## GetSystemZonesResponseAlternate

```text
{zones: Array<{id: string, name: string, equipmentIds: Array<string>}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zones` | Yes | Zones associated with the system. |

## GetSystemZonesStatusResponse

```text
{zones: Array<{id: string, name: string, equipmentIds: Array<string>, features: {ambientTemperature?: {currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}, circulation?: {status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}, humidity?: {status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}}}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zones` | Yes | Zones associated with the system. |

## Features

```text
{ambientTemperature?: {currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}, circulation?: {status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}, humidity?: {status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `ambientTemperature` | No | The status of the ambient temperature of a zone. |
| `circulation` | No | The status of the circulation of a zone. |
| `humidity` | No | The status of the humidity control of a zone. |

## AmbientTemperatureCapabilities

```text
{setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `setpoint` | Yes |  |

## AmbientTemperatureSettings

```text
{mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The current mode of the ambient temperature control. |
| `setpoint` | Yes | x-refinements: ["heatValue and coolValue must be provided together", "heatValue must not exceed coolValue"] |

## AmbientTemperature

```text
{currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `currentTemperature` | Yes | The current temperature, measured or computed, in celsius. |
| `currentDisplayTemperatureCelsius` | No | Display temperature in Celsius. |
| `currentDisplayTemperatureFahrenheit` | No | Display temperature in Fahrenheit. |
| `mode` | Yes | The current mode of the ambient temperature control. |
| `status` | Yes | The current operational status of the ambient temperature control. |
| `settings` | Yes | The current ambient temperature settings. |
| `capabilities` | Yes | The ambient temperature control capabilities. |
| `setpoint` | Yes | DEPRECATED. Use "settings.setpoint" and "capabilities.setpoint" instead. |
| `current` | Yes | DEPRECATED. Use "currentTemperature" instead. |
| `hvacMode` | Yes | DEPRECATED. Use "mode" instead. |
| `hvacStatus` | Yes | DEPRECATED. Use "status" instead. |

## AmbientTemperatureStatus

```text
'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'
```

## HvacMode

```text
'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly'
```

## TemperatureSetpoint

```text
{value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The setpoint for heating and cooling of the ambient temperature in Celsius. |
| `minValue` | Yes | The minimum value for the setpoint temperature in Celsius. |
| `maxValue` | Yes | The maximum value for the setpoint temperature in Celsius. |
| `precision` | Yes |  |
| `increment` | Yes |  |

## CirculationCapabilities

```text
{fanSpeedSetting: {max: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `fanSpeedSetting` | Yes |  |

## CirculationSettings

```text
{mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The circulation mode. 'Off' = no circulation, 'Circulate' = fan runs per fanOnDuration, 'Continuous' = fan runs always. |
| `fanSpeed` | Yes | The fan speed setting (1..MAX) or 'Auto'. |
| `fanOnDuration` | Yes | The desired time in minutes to run the fan per hour.; minimum: 0; maximum: 60 |
| `enabled` | No | DEPRECATED. Use "mode" instead. |

## Circulation

```text
{status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `status` | Yes | The status of the circulation system. |
| `fanSpeedStatus` | Yes | The current fan speed (0..MAX) |
| `settings` | Yes | The current circulation settings. |
| `capabilities` | Yes | The circulation control capabilities. |
| `enabled` | Yes | DEPRECATED. Use "settings.mode" instead. |
| `fanSpeedSetting` | Yes |  |
| `fanOnDurationSetting` | Yes |  |

## CirculationMode

```text
'Off' | 'Circulate' | 'Continuous'
```

## CirculationStatus

```text
'Off' | 'Circulating' | 'Unknown'
```

## FanSpeedSetting

```text
1 | 2 | 3 | 'Auto'
```

## FanSpeedStatus

```text
0 | 1 | 2 | 3
```

## HumidityCapabilities

```text
{modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `modes` | Yes | The supported humidity modes. |
| `setpoint` | Yes |  |

## HumiditySettings

```text
{mode: 'Off' | 'Humidify', setpoint: {value: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The current humidity control mode. |
| `setpoint` | Yes |  |

## Humidity

```text
{status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `status` | Yes | The current operational status of the humidity control. |
| `currentRelativeHumidity` | Yes | The current relative humidity percentage. |
| `currentDisplayRelativeHumidity` | Yes | The display-rounded current relative humidity percentage. |
| `settings` | Yes | The current humidity settings. |
| `capabilities` | No | The humidity control capabilities. |

## HumidityMode

The humidity control mode.

```text
'Off' | 'Humidify'
```

## HumidityStatus

The current operational status of the humidity control.

```text
'Off' | 'Humidifying'
```

## GetVacationResponseAlternate

```text
{vacation: Vacation | null, capabilities: {ambientTemperature: AmbientTemperatureCapability}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `vacation` | Yes | The vacation configuration for the system, or null if none has been set. |
| `capabilities` | Yes | Capabilities for the system. |

## AmbientTemperatureCapability

```text
{minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `minValue` | Yes | The minimum setpoint in Celsius that can be fulfilled. |
| `maxValue` | Yes | The maximum setpoint in Celsius that can be fulfilled. |
| `precision` | Yes |  |
| `increment` | Yes |  |

## VacationPreset

```text
{temperatureSetpoint: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `temperatureSetpoint` | Yes | Temperature setpoint in degrees Celsius. |

## Vacation

```text
{id: string, enabled: boolean, startAt: string, endAt: string, preset: {temperatureSetpoint: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the vacation. |
| `enabled` | Yes | Whether vacation is enabled. |
| `startAt` | Yes | Start of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `endAt` | Yes | End of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `preset` | Yes | Preset applied during the vacation period. |

## VacationInput

```text
{enabled: boolean, startAt: string, endAt: string, preset: {temperatureSetpoint: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `enabled` | Yes | Whether vacation is enabled. |
| `startAt` | Yes | Start of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `endAt` | Yes | End of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `preset` | Yes | Preset applied during the vacation period. |

## ProvisionSystemRequest

```text
{idempotencyKey?: string, name?: string, address: Address, systemNumber?: integer, rolloutGroup?: 'dev' | 'test' | 'dogfood' | 'beta' | 'ga', settings?: {temperatureUnit: 'Celsius' | 'Fahrenheit', ambientTemperatureSource: 'Internal' | 'External'}, zones?: Array<ZoneInput>, boards?: Array<BoardInput>, heatPumps?: Array<HeatPumpInput>, users?: Array<UserInput>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `idempotencyKey` | No | Client-supplied idempotency key; must uniquely identify one logical provisioning request. A request whose key matches a live system re-provisions that system — the rest of the payload is NOT re-applied — instead of creating a duplicate.; minLength: 1; maxLength: 200 |
| `name` | No | Friendly name of the system.; minLength: 1 |
| `address` | Yes |  |
| `systemNumber` | No | System number for multi-system homes.; exclusiveMinimum: 0 |
| `rolloutGroup` | No | Rollout cohort for the system; sets its deployment type, feature channel, and IoT thing group. Defaults to ga. |
| `settings` | No |  |
| `zones` | No | Zones to configure for the system.; minItems: 1; maxItems: 1 |
| `boards` | No | Boards belonging to the system. Requires a heat pump.; minItems: 1; maxItems: 1 |
| `heatPumps` | No | Heat pumps belonging to the system. When provided, provisions a hub, heat pump, and standard peripherals (energy monitor, sensors, thermostat). Omit to create a hub-less system with no board or equipment.; minItems: 1; maxItems: 1 |
| `users` | No | Users to attach to the system. |

## ProvisionSystemResponse

```text
{result: 'ok', systemId: string} | {result: 'partial_failure', systemId: string, failures: Array<?>}
```

## HeatPumpInput

```text
{name?: string, model: 'CDHP-HH1-2T' | 'CDHP-HH1-3T' | 'CDHP-HH1-4T' | 'CDHP-HH1-5T' | 'CDHP-HH2-2T' | 'CDHP-HH2-3T' | 'CDHP-HH2-4T' | 'CDHP-HH2-5T' | 'CDHP-AIR1-1P5T' | 'CDHP-AIR1-2T' | 'CDHP-AIR1-3T' | 'CDHP-AIR1-3T2F' | 'CDHP-AIR1-4T' | 'CDHP-AIR1-5T', hasHeatStrip?: boolean, heatStripPowerKw?: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name |
| `model` | Yes | Jetson model number |
| `hasHeatStrip` | No | Whether the heat pump has an electric heat strip |
| `heatStripPowerKw` | No | Nominal power of the heat strip in kW |

## HeatPumpModel

```text
'CDHP-HH1-2T' | 'CDHP-HH1-3T' | 'CDHP-HH1-4T' | 'CDHP-HH1-5T' | 'CDHP-HH2-2T' | 'CDHP-HH2-3T' | 'CDHP-HH2-4T' | 'CDHP-HH2-5T' | 'CDHP-AIR1-1P5T' | 'CDHP-AIR1-2T' | 'CDHP-AIR1-3T' | 'CDHP-AIR1-3T2F' | 'CDHP-AIR1-4T' | 'CDHP-AIR1-5T'
```

## RolloutGroup

```text
'dev' | 'test' | 'dogfood' | 'beta' | 'ga'
```

## Zone

```text
{id: string, name: string, equipmentIds: Array<string>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the zone. |
| `name` | Yes | The name of the zone. |
| `equipmentIds` | Yes | IDs of the equipment serving this zone. |

## ZoneInput

```text
{name: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | The name of the zone. |

## ProvisionExistingSystemRequest

```text
{systemNumber?: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systemNumber` | No | System number for multi-system homes.; exclusiveMinimum: 0 |

## RefreshSystemManifestResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## RepairConfigRequest

```text
{systemNumber?: integer, overwriteHubConfig?: boolean, overwriteHeatPumpConfig?: boolean, overwriteCertificates?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systemNumber` | No | Optional hint to narrow config matching or set config location for new configs.; exclusiveMinimum: 0 |
| `overwriteHubConfig` | No | Overwrite hub-config even if it already exists.; default: false |
| `overwriteHeatPumpConfig` | No | Overwrite heat-pump-config even if it already exists.; default: false |
| `overwriteCertificates` | No | Regenerate and overwrite certificates even if they already exist.; default: false |

## RepairConfigResponse

```text
{result: 'ok' | 'partial_failure' | 'error', systemId: string, systemSlug: string, action: 'repaired' | 'created' | 'skipped', components: {hubConfig: {status: 'written'} | {status: 'skipped'} | {status: 'error', error: string}, heatPumpConfig: {status: 'written'} | {status: 'skipped'} | {status: 'error', error: string}, certificates: {status: 'written'} | {status: 'skipped'} | {status: 'error', error: string}}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |
| `systemId` | Yes |  |
| `systemSlug` | Yes |  |
| `action` | Yes |  |
| `components` | Yes |  |

## SetSystemRolloutGroupRequest

```text
{rolloutGroup: 'dev' | 'test' | 'dogfood' | 'beta' | 'ga'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `rolloutGroup` | Yes | Rollout cohort to move the system into. |

## RolloutGroupThingType

```text
'system' | 'board' | 'equipment'
```

## RolloutGroupThingResult

```text
{thingName: string, thingType: RolloutGroupThingType, outcome: 'moved' | 'unchanged' | 'missing'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `thingName` | Yes | IoT thing name. |
| `thingType` | Yes |  |
| `outcome` | Yes | moved — group membership changed; unchanged — already in the target group; missing — no such IoT thing, nothing to move. |

## RolloutGroupThingFailure

```text
{thingName: string, thingType: RolloutGroupThingType, error: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `thingName` | Yes | IoT thing name. |
| `thingType` | Yes |  |
| `error` | Yes | Failure reason. Re-issue the same request to retry; the operation is idempotent. |

## SetSystemRolloutGroupResponse

```text
{result: 'ok', system: AdminSystem, things: Array<RolloutGroupThingResult>} | {result: 'partial_failure', system: AdminSystem, things: Array<RolloutGroupThingResult>, failures: Array<RolloutGroupThingFailure>}
```

## RefreshSystemSchedulesResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |

## RefreshHeatPumpSettingsResponse

```text
{result: 'ok' | 'failed'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the refresh operation. |

## RefreshAllHeatPumpSettingsResponse

```text
{result: 'ok' | 'partial_errors', refreshed: integer, failed: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the bulk refresh operation. |
| `refreshed` | Yes | Number of heat pumps successfully refreshed.; minimum: 0 |
| `failed` | Yes | Number of heat pumps that failed to refresh.; minimum: 0 |

## RegisterInstallerRequest

```text
{email: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes | Email address to authorize for installer access. |

## RegisterInstallerResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |

## RemoveSystemMemberResponseAlternate

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | Whether the member was successfully removed from the system |

## UpdateBoardRequestAlternate

```text
{type?: 'Arctic' | 'Alpha', serialNumber?: string, installedAt?: string, cloudConnectionExpected?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | No | The type of the board. |
| `serialNumber` | No | The serial number of the board. |
| `installedAt` | No | When the board was physically installed. |
| `cloudConnectionExpected` | No | Whether the board is expected to connect to the cloud. |

## UpdateBoardResponseAlternate

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the update operation. |

## UpdateHumidifierFields

```text
{name?: string, installedAt?: string, model?: 'HUM-3P', humidifierType?: 'Evaporative' | 'Steam', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId | null, zoneIds?: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name for the equipment.; minLength: 1 |
| `installedAt` | No | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | No | Humidifier model number. |
| `humidifierType` | No | Humidifier technology type. |
| `boardId` | No |  |
| `parentEquipmentId` | No | Parent equipment this peripheral attaches to. Null detaches. |
| `zoneIds` | No |  |

## UpdateEquipmentRequest

```text
{name?: string, installedAt?: string, model?: 'EMPORIA-VUE-3' | 'EM-001', serialNumber?: string, boardId?: BoardId, type: 'EnergyMonitor'} | {name?: string, installedAt?: string, model?: 'EV-001', serialNumber?: string, type: 'EvCharger'} | {name?: string, installedAt?: string, model?: 'HUM-3P', humidifierType?: 'Evaporative' | 'Steam', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId | null, zoneIds?: ZoneIds, type: 'Humidifier'} | {name?: string, installedAt?: string, model?: 'TEMCO-AQM' | 'TEMCO-TH', role?: 'ReturnAir' | 'SupplyAir', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId | null, zoneIds?: ZoneIds, type: 'Sensor'} | {name?: string, installedAt?: string, model?: 'THE-001', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId | null, zoneIds?: ZoneIds, type: 'Thermostat'}
```

Cross-field constraints: At least one field must be provided.

## UpdateEquipmentResponse

```text
EnergyMonitor | EvCharger | HeatPump | HeatPumpIdu | HeatPumpOdu | Humidifier | Sensor | Thermostat
```

## UpdateEquipmentZonesRequest

```text
{zoneIds: Array<string>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zoneIds` | Yes | IDs of the zones this equipment should serve. |

## UpdateEquipmentZonesResponse

```text
{zoneIds: Array<string>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zoneIds` | Yes | IDs of the zones this equipment now serves. |

## UpdateHeatPumpRequest

```text
{model?: HeatPumpModel, name?: string, heatStrip?: {powerKw: number}, boardId?: string | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `model` | No |  |
| `name` | No |  |
| `heatStrip` | No |  |
| `boardId` | No | Board ID the heat pump is attached to. Set to null to detach. |

Cross-field constraints: At least one field must be provided.

## UpdateHeatPumpResponse

```text
{equipment: CreateEquipmentResponse}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipment` | Yes |  |

## UpdateHumidifierRequest

```text
{name?: string, installedAt?: string, model?: 'HUM-3P', humidifierType?: 'Evaporative' | 'Steam', boardId?: BoardId, parentEquipmentId?: ParentEquipmentId | null, zoneIds?: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name for the equipment.; minLength: 1 |
| `installedAt` | No | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | No | Humidifier model number. |
| `humidifierType` | No | Humidifier technology type. |
| `boardId` | No |  |
| `parentEquipmentId` | No | Parent equipment this peripheral attaches to. Null detaches. |
| `zoneIds` | No |  |

Cross-field constraints: At least one field must be provided.

## UpdateHumidifierResponse

```text
{humidifier: Humidifier}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `humidifier` | Yes |  |

## UpdateSystemMemberRequestAlternate

```text
{member: {user?: {name?: string}, role: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes |  |

## UpdateSystemMemberResponseAlternate

```text
{member: {user: {id: string, email: string, name: string, onboardingCompleted: boolean}, role: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes | Member updated on the system. |

## UpsertBoardRequestAlternate

```text
{type: 'Arctic' | 'Alpha', serialNumber?: string, installedAt?: string, cloudConnectionExpected?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes | The type of the board to upsert. |
| `serialNumber` | No | The serial number of the board to upsert. |
| `installedAt` | No | When the board was physically installed. |
| `cloudConnectionExpected` | No | Whether the board is expected to connect to the cloud. |

## UpsertBoardResponseAlternate

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the upsert operation. |

## UpsertUserRequest

```text
{userInfo: UserInput}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `userInfo` | Yes |  |

## UpsertUserResponse

```text
{result: 'ok', user: User}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result code of the operation. |
| `user` | Yes |  |

## BoardPeripherals

```text
{thermostats: Array<{isConnected: boolean, firmwareVersion: string}>, energyMonitors: Array<{isConnected: boolean}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `thermostats` | Yes | Thermostats connected to the board. |
| `energyMonitors` | Yes | Energy monitors connected to the board. |

## ConfigFile

```text
{name: string, size: integer, lastModified: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | The name of the file. |
| `size` | Yes | The size of the file in bytes.; minimum: 0 |
| `lastModified` | Yes | The last modified timestamp in ISO format. |

## ConfigSearchQuery

```text
{q: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `q` | Yes | Search query term.; minLength: 2; maxLength: 100 |

## GetConfigFilesResponse

```text
{files: Array<ConfigFile>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `files` | Yes | List of files in the specified folder. |

## GetApplicationFirmwareParams

```text
{version: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `version` | Yes | Application firmware version tag (e.g., 1.4.4); pattern: "^\\d+\\.\\d+\\.\\d+$" |

## HubModel

```text
'HUB-001'
```

## GetApplicationFirmwareVersionsResponse

```text
{stable: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `stable` | Yes | Current stable firmware version |

## GetConfigFoldersResponse

```text
{folders: Array<string>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `folders` | Yes | List of config folder names. |

## EnergyMonitorEm001Provisioning

```text
{equipmentId: string, systemId: string, caCert: string, deviceCert: string, deviceKey: string, type: 'EnergyMonitor', model: 'EM-001', mqttEndpoint: string, timezone: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipmentId` | Yes | ID of the equipment being provisioned. |
| `systemId` | Yes | ID of the system the equipment belongs to. |
| `caCert` | Yes | Amazon root CA certificate (PEM). |
| `deviceCert` | Yes | Device certificate (PEM). |
| `deviceKey` | Yes | Device private key (PEM). |
| `type` | Yes |  |
| `model` | Yes |  |
| `mqttEndpoint` | Yes | AWS IoT Core MQTT data endpoint. |
| `timezone` | Yes | IANA timezone of the system address (e.g., America/Los_Angeles). |

## EvChargerEv001Provisioning

```text
{equipmentId: string, systemId: string, caCert: string, deviceCert: string, deviceKey: string, type: 'EvCharger', model: 'EV-001', chargePointId: string, csmsEndpoint: string, basicAuthPassword: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipmentId` | Yes | ID of the equipment being provisioned. |
| `systemId` | Yes | ID of the system the equipment belongs to. |
| `caCert` | Yes | Amazon root CA certificate (PEM). |
| `deviceCert` | Yes | Device certificate (PEM). |
| `deviceKey` | Yes | Device private key (PEM). |
| `type` | Yes |  |
| `model` | Yes |  |
| `chargePointId` | Yes | OCPP charge point identity (the charger serial number). |
| `csmsEndpoint` | Yes | CSMS websocket endpoint the charge point connects to for OCPP. |
| `basicAuthPassword` | Yes | OCPP basic-auth password for the charge point.; minLength: 32 |

## EnergyMonitorProvisioning

```text
EnergyMonitorEm001Provisioning
```

## EvChargerProvisioning

```text
EvChargerEv001Provisioning
```

## GetEquipmentProvisioningResponse

```text
EnergyMonitorProvisioning | EvChargerProvisioning
```

## GetSystemEquipmentResponse

```text
{equipment: Array<CreateEquipmentResponse>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipment` | Yes | All equipment belonging to the system. |

## GetSystemEquipmentResponseAlternate

```text
{equipment: Array<CreateEquipmentResponse>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipment` | Yes | All equipment belonging to the system. |

## GetSystemStatusResponse

```text
{heatPumps: Array<{id: string, family: 'CDHP-HH1' | 'CDHP-HH2' | 'CDHP-AIR1', connections: Array<HeatPumpConnection>, iduFirmwareVersion: string, oduFirmwareVersion: string, iduFaultCodes: Array<string>, oduFaultCodes: Array<string>}>, boards: Array<{id: string, isConnected: boolean, appFirmwareVersion: string, bootFirmwareVersion: string, peripherals: {thermostats: Array<{isConnected: boolean, firmwareVersion: string}>, energyMonitors: Array<{isConnected: boolean}>}}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `heatPumps` | Yes | Heat pumps in the system. Array for multiple HPs on a system in the future. 0 or 1 for now. |
| `boards` | Yes | Boards in the system. |

## HeatPumpConnection

```text
{type: 'xye' | 'modbus', target: 'idu' | 'odu', isConnected: boolean, address?: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes | Type of the connection (e.g., xye, modbus). |
| `target` | Yes | The target of the connection (e.g., idu, odu). |
| `isConnected` | Yes | Whether the connection is currently established. |
| `address` | No | The logical address of the connected device. |

## GetSystemZoneStatusResponse

```text
{zones: Array<{id: string, status: {features: {ambientTemperature?: {currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}, circulation?: {status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}, humidity?: {status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}}, schedule?: {id: string, kind: 'Weekly' | 'Vacation', status: 'Active' | 'Paused'}}}>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zones` | Yes | List of zone statuses for the requested system. |

## ZoneStatus

```text
{features: {ambientTemperature?: {currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}, circulation?: {status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}, humidity?: {status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}}, schedule?: {id: string, kind: 'Weekly' | 'Vacation', status: 'Active' | 'Paused'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `features` | Yes | All features available to access or operate on the zone. |
| `schedule` | No | Schedule currently affecting the zone. |

## ZoneSchedule

```text
{id: string, kind: 'Weekly' | 'Vacation', status: 'Active' | 'Paused'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the schedule. |
| `kind` | Yes | Whether the zone is currently following a weekly schedule or vacation mode. |
| `status` | Yes | The status of the zone. |

## ZoneScheduleKind

```text
'Weekly' | 'Vacation'
```

## ZoneScheduleStatus

```text
'Active' | 'Paused'
```

## SearchConfigFoldersResponse

```text
{results: Array<string>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `results` | Yes | List of folder names matching the search term. |

## UpdateBoardRequest

```text
{type?: 'Arctic' | 'Alpha', serialNumber?: string, installedAt?: string, cloudConnectionExpected?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | No | The type of the board. |
| `serialNumber` | No | The serial number of the board. |
| `installedAt` | No | When the board was physically installed. |
| `cloudConnectionExpected` | No | Whether the board is expected to connect to the cloud. |

## UpdateBoardResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the update operation. |

## UpsertBoardRequest

```text
{type: 'Arctic' | 'Alpha', serialNumber: string, installedAt?: string, cloudConnectionExpected?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes | The type of the board to create. |
| `serialNumber` | Yes | The serial number of the board to create. |
| `installedAt` | No | When the board was physically installed. |
| `cloudConnectionExpected` | No | Whether the board is expected to connect to the cloud. |

## UpsertBoardResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | The result of the upsert operation. |

## AddSystemMemberRequest

```text
{member: {user: UserInput, role: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes | Member to add to the system |

## AddSystemMemberResponse

```text
{member: {user: {id: string, email: string, name: string, onboardingCompleted: boolean}, role: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes | Member added to the system |

## Co2

CO2 concentration in ppm.

```text
number
```

## Pm25

PM2.5 concentration in µg/m³.

```text
number
```

## Tvoc

TVOC concentration in ppb.

```text
number
```

## AirQualityLevel

Air quality classification, derived from a pollutant concentration (or the worst across pollutants).

```text
'excellent' | 'good' | 'fair' | 'poor' | 'unhealthy'
```

## AirQualityEntitlement

A paid entitlement that gates the detailed air quality data.

```text
'jetson_care'
```

## Co2Reading

```text
{value: Co2 | null, level: AirQualityLevel | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The measured concentration, or null if there is no current reading. |
| `level` | Yes | The classification of this reading, or null if there is no reading. |

## Pm25Reading

```text
{value: Pm25 | null, level: AirQualityLevel | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The measured concentration, or null if there is no current reading. |
| `level` | Yes | The classification of this reading, or null if there is no reading. |

## TvocReading

```text
{value: Tvoc | null, level: AirQualityLevel | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The measured concentration, or null if there is no current reading. |
| `level` | Yes | The classification of this reading, or null if there is no reading. |

## AirQualityPeriod

```text
{startTime: string, endTime: string, overall: AirQualityLevel | null, co2: {value: Co2 | null, level: AirQualityLevel | null}, pm25: {value: Pm25 | null, level: AirQualityLevel | null}, tvoc: {value: Tvoc | null, level: AirQualityLevel | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `startTime` | Yes | The start of this period as an ISO 8601 timestamp with timezone offset. |
| `endTime` | Yes | The end of this period as an ISO 8601 timestamp with timezone offset. |
| `overall` | Yes | The overall classification for this period, or null if no data. |
| `co2` | Yes | The average CO2 reading for this period. |
| `pm25` | Yes | The average PM2.5 reading for this period. |
| `tvoc` | Yes | The average TVOC reading for this period. |

## AirQualityOverall

```text
{lastUpdatedAt: string | null, overall: AirQualityLevel | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `lastUpdatedAt` | Yes | ISO 8601 timestamp of the most recent sensor reading in system local time, or null if no data. |
| `overall` | Yes | The overall air quality classification, or null if no data. |

## AirQualityCurrent

```text
{lastUpdatedAt: string | null, overall: AirQualityLevel | null, co2: {value: Co2 | null, level: AirQualityLevel | null}, pm25: {value: Pm25 | null, level: AirQualityLevel | null}, tvoc: {value: Tvoc | null, level: AirQualityLevel | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `lastUpdatedAt` | Yes | ISO 8601 timestamp of the most recent sensor reading in system local time, or null if no data. |
| `overall` | Yes | The overall air quality classification, or null if no data. |
| `co2` | Yes | The current CO2 reading. |
| `pm25` | Yes | The current PM2.5 reading. |
| `tvoc` | Yes | The current TVOC reading. |

## AirQualityFull

```text
{access: 'full', current: {lastUpdatedAt: string | null, overall: AirQualityLevel | null, co2: {value: Co2 | null, level: AirQualityLevel | null}, pm25: {value: Pm25 | null, level: AirQualityLevel | null}, tvoc: {value: Tvoc | null, level: AirQualityLevel | null}}, history: Array<AirQualityPeriod>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `access` | Yes |  |
| `current` | Yes | The latest reading, with per-pollutant detail. |
| `history` | Yes | Per-period averages, oldest to newest; granularity may vary (e.g. 24h, 6h). |

## AirQualityLimited

```text
{access: 'limited', missingEntitlement: 'jetson_care', current: {lastUpdatedAt: string | null, overall: AirQualityLevel | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `access` | Yes |  |
| `missingEntitlement` | Yes | The entitlement the caller needs to unlock the detailed data (what to upsell). |
| `current` | Yes | The latest overall reading; per-pollutant detail requires JetsonCare. |

## AirQuality

Air quality for a zone. `full` (JetsonCare) carries per-pollutant readings and history; `limited` returns only the overall level and the entitlement to upsell.

```text
AirQualityFull | AirQualityLimited
```

## AirQualityBand

```text
{level: AirQualityLevel, min: number, max: number | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `level` | Yes |  |
| `min` | Yes | Inclusive lower bound, in the pollutant unit. |
| `max` | Yes | Exclusive upper bound, or null for the open-ended top band. |

## PollutantScale

```text
{unit: string, displayRange: {min: number, max: number}, bands: Array<AirQualityBand>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `unit` | Yes | Display unit for the pollutant, e.g. "ppm". |
| `displayRange` | Yes | Axis range for the scale bar; may be narrower than the open-ended top band. |
| `bands` | Yes | Classification bands, ascending, covering the display range. |

## AirQualityClassification

```text
{co2: PollutantScale, pm25: PollutantScale, tvoc: PollutantScale}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `co2` | Yes |  |
| `pm25` | Yes |  |
| `tvoc` | Yes |  |

## AmbientTemperatureMode

```text
'Off' | 'Heat' | 'Cool' | 'Auto'
```

## AppScheme

```text
'jetsonhome' | 'jetsonhomedev' | 'jetsoninstaller' | 'jetsoninstallerdev'
```

## ClaimSystemRequest

```text
{}
```

## ClaimSystemResponse

```text
{result: 'ok'} | {result: 'error', message?: string}
```

## CreateHumidifierRequest

```text
{name?: string, installedAt?: string, model?: 'HUM-3P', humidifierType?: 'Evaporative' | 'Steam', boardId?: BoardId, parentEquipmentId?: string | null, zoneIds?: ZoneIds}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name for the humidifier. |
| `installedAt` | No | When the equipment was physically installed. Set-once: cannot be changed once set. |
| `model` | No | Humidifier model number. |
| `humidifierType` | No | Humidifier technology type. |
| `boardId` | No |  |
| `parentEquipmentId` | No | ID of the parent heat pump equipment. |
| `zoneIds` | No |  |

## CreateHumidifierResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |

## CreateSchedulePresetRequest

```text
{name: string, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null, isDefaultPreset?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | The name of the preset.; minLength: 1; maxLength: 255; x-refinements: ["Callback validation (inspect bytecode)"] |
| `temperatureSetpoint` | Yes | The temperature setpoint of the preset in degrees Celsius. |
| `temperatureMode` | No | The temperature mode override, or null to use system default. |
| `fanSpeed` | No | The fan speed override, or null to use system default. |
| `quiet` | No | Whether to run in quiet mode, or null to use system default. |
| `isDefaultPreset` | No | Whether this preset is the default preset. |

## CreateSchedulePresetResponse

```text
{preset: {id: string, name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `preset` | Yes | The created schedule preset. |

## SchedulePreset

```text
{id: string, name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the preset. |
| `name` | Yes | The name of the preset.; minLength: 1; maxLength: 255; x-refinements: ["Callback validation (inspect bytecode)"] |
| `isDefault` | Yes | Whether this preset is the system default. |
| `temperatureSetpoint` | Yes | The temperature setpoint of the preset in degrees Celsius. |
| `temperatureMode` | No | The temperature mode override, or null to use system default. |
| `fanSpeed` | No | The fan speed override, or null to use system default. |
| `quiet` | No | Whether to run in quiet mode, or null to use system default. |

## SchedulePresetInput

```text
{name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | Yes | The name of the preset.; minLength: 1; maxLength: 255; x-refinements: ["Callback validation (inspect bytecode)"] |
| `isDefault` | Yes | Whether this preset is the system default. |
| `temperatureSetpoint` | Yes | The temperature setpoint of the preset in degrees Celsius. |
| `temperatureMode` | No | The temperature mode override, or null to use system default. |
| `fanSpeed` | No | The fan speed override, or null to use system default. |
| `quiet` | No | Whether to run in quiet mode, or null to use system default. |

## CreateScheduleRequest

```text
{type: 'sleep' | 'away' | 'custom', weekly: Array<ScheduleWeeklyEvent>, zones: Array<string>, enabled: boolean, name?: string, preset: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes | The type of schedule. |
| `weekly` | Yes | The weekly events of the schedule. |
| `zones` | Yes | IDs of the zones this schedule applies to. |
| `enabled` | Yes | Whether the schedule is enabled. |
| `name` | No | Optional schedule name. Defaults to the preset name if omitted. |
| `preset` | Yes | ID of the preset to use for this schedule. |

## CreateScheduleResponse

```text
{schedule: {id: string, name: string, createdAt: string, type: 'sleep' | 'away' | 'custom', preset: {id: string, name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}, weekly: Array<ScheduleWeeklyEvent>, zoneIds: Array<string>, zones: Array<{id: string}>, enabled: boolean}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `schedule` | Yes | The created schedule. |

## Schedule

```text
{id: string, name: string, createdAt: string, type: 'sleep' | 'away' | 'custom', preset: {id: string, name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}, weekly: Array<ScheduleWeeklyEvent>, zoneIds: Array<string>, zones: Array<{id: string}>, enabled: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `id` | Yes | The ID of the schedule. |
| `name` | Yes | The name of the schedule. |
| `createdAt` | Yes | ISO 8601 timestamp of when the schedule was created. |
| `type` | Yes | The type of schedule. |
| `preset` | Yes | The preset applied by the schedule. |
| `weekly` | Yes | The weekly events of the schedule. |
| `zoneIds` | Yes | IDs of the zones this schedule applies to. |
| `zones` | Yes | The list of zones affected by the schedule. |
| `enabled` | Yes | Whether the schedule is enabled. |

## ScheduleInput

```text
{type: 'sleep' | 'away' | 'custom', weekly: Array<ScheduleWeeklyEvent>, zones: Array<string>, enabled: boolean, name?: string, preset: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | Yes | The type of schedule. |
| `weekly` | Yes | The weekly events of the schedule. |
| `zones` | Yes | IDs of the zones this schedule applies to. |
| `enabled` | Yes | Whether the schedule is enabled. |
| `name` | No | Optional schedule name. Defaults to the preset name if omitted. |
| `preset` | Yes | ID of the preset to use for this schedule. |

## ScheduleWeeklyEvent

```text
{day: integer, startTime: string, endTime?: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `day` | Yes | The day of the week of the event (1=Monday, 7=Sunday).; minimum: 1; maximum: 7 |
| `startTime` | Yes | The beginning time in ISO 8601 format of the schedule window on the given day. |
| `endTime` | No | The optional end time in ISO 8601 format of the schedule window. |

## DeleteSchedulePresetResponse

```text
{success: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `success` | Yes | Whether the preset was successfully deleted. |

## PauseScheduleRequest

```text
{kind?: 'Weekly' | 'Vacation'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `kind` | No | Whether the target is a weekly schedule or a vacation. Defaults to Weekly when omitted.; default: "Weekly" |

## PauseScheduleResponse

```text
{success: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `success` | Yes | Whether the schedule was successfully paused. |

## ScheduleKind

```text
'Weekly' | 'Vacation'
```

## DeleteScheduleResponse

```text
{success: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `success` | Yes | Whether the schedule was successfully deleted. |

## EmptyRequestQuery

```text
{}
```

## GetAirQualityResponse

Air quality for a zone. `full` (JetsonCare) carries per-pollutant readings and history; `limited` returns only the overall level and the entitlement to upsell.

```text
AirQualityFull | AirQualityLimited
```

## GetAirQualityClassificationResponse

```text
{co2: PollutantScale, pm25: PollutantScale, tvoc: PollutantScale}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `co2` | Yes |  |
| `pm25` | Yes |  |
| `tvoc` | Yes |  |

## GetAllSchedulesResponse

```text
{schedules: Array<Schedule>, limits: {maxSchedules: integer}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `schedules` | Yes | All schedules configured for the system. |
| `limits` | Yes | Server-enforced limits relevant to schedule creation. |

## GetCurrentUserResponse

```text
{user: User}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `user` | Yes |  |

## EnergyCurrentLoad

```text
{equipmentId: string, type: 'EnergyMonitor' | 'EvCharger' | 'HeatPump' | 'HeatPumpIdu' | 'HeatPumpOdu' | 'Humidifier' | 'Sensor' | 'Thermostat', name: string, powerW: number | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipmentId` | Yes | The id of the equipment this load corresponds to. |
| `type` | Yes | The type of equipment (an EquipmentType value, e.g. HeatPump, EvCharger). |
| `name` | Yes | The human-readable name of the equipment. |
| `powerW` | Yes | The instantaneous power draw of this load in watts, or null if its source is offline. |

## EnergyCurrentLive

```text
{asOf: string | null, totalMainPowerW: number | null, loads: Array<EnergyCurrentLoad>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `asOf` | Yes | ISO 8601 UTC timestamp (Z) of the latest sample contributing to these live values, or null if no data is available. |
| `totalMainPowerW` | Yes | Most recent power reading in watts as of asOf |
| `loads` | Yes | Every monitored load with its instantaneous power. Empty when nothing is monitored yet. |

## EnergyCurrentToday

```text
{date: string, asOf: string | null, totalMainEnergyKwh: number | null}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `date` | Yes | The current system-local civil day (YYYY-MM-DD). Always present, even when no data exists yet. |
| `asOf` | Yes | ISO 8601 UTC timestamp (Z) of the latest sample contributing to today, or null if no data exists for today. |
| `totalMainEnergyKwh` | Yes | kWh energy usage or null if no data for that date |

## GetEnergyCurrentResponse

```text
{live: {asOf: string | null, totalMainPowerW: number | null, loads: Array<EnergyCurrentLoad>}, today: {date: string, asOf: string | null, totalMainEnergyKwh: number | null}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `live` | Yes | Instantaneous live home usage. |
| `today` | Yes | Today's accumulated home energy. |

## GetEquipmentHeatPumpStatusResponse

```text
{health: HeatPumpHealth}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `health` | Yes |  |

## HeatPumpHealth

```text
{connectionStatus: ConnectionStatus, operationalStatus: OperationalStatus, faults: Array<EquipmentFault>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `connectionStatus` | Yes |  |
| `operationalStatus` | Yes |  |
| `faults` | Yes |  |

## FaultCategory

```text
'Notice' | 'Warning' | 'ServiceRequired' | 'Critical'
```

## EquipmentFault

```text
{code: string, category: FaultCategory, summary?: string, description?: string, helpUrl?: string, type: 'Equipment', equipmentId: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `code` | Yes |  |
| `category` | Yes |  |
| `summary` | No | Short human-readable statement of what the fault is. |
| `description` | No | What the fault means and what the homeowner should do about it. |
| `helpUrl` | No | Link to a help-center document about this fault. |
| `type` | Yes |  |
| `equipmentId` | Yes |  |

## SystemFault

```text
{code: string, category: FaultCategory, summary?: string, description?: string, helpUrl?: string, type: 'System'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `code` | Yes |  |
| `category` | Yes |  |
| `summary` | No | Short human-readable statement of what the fault is. |
| `description` | No | What the fault means and what the homeowner should do about it. |
| `helpUrl` | No | Link to a help-center document about this fault. |
| `type` | Yes |  |

## Fault

```text
EquipmentFault | SystemFault
```

## OperationalStatus

```text
'Unknown' | 'Active' | 'ErrorOther'
```

## EquipmentHealth

```text
{faults: Array<EquipmentFault>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `faults` | Yes |  |

## GetEquipmentStatusResponse

```text
{health: EquipmentHealth}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `health` | Yes |  |

## GetSchedulePresetsResponse

```text
{presets: Array<SchedulePreset>, capabilities: {ambientTemperature: AmbientTemperatureCapability}, limits: {maxPresets: integer}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `presets` | Yes | All schedule presets configured for the system. |
| `capabilities` | Yes | Capabilities for the system. |
| `limits` | Yes | Server-enforced limits relevant to preset creation. |

## GetSystemBoardsResponse

```text
{boards: Array<Board>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `boards` | Yes | All boards belonging to the system. |

## GetSystemMembersResponse

```text
{members: Array<SystemMember>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `members` | Yes | All members belonging to the system. |

## GetSystemSettingsResponse

```text
{settings: SystemSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## GetSystemsResponse

```text
{systems: Array<SystemOverview>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `systems` | Yes | All systems available to the user. |

## GetClaimPreviewResponse

```text
{label: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `label` | Yes |  |

## GetSystemZonesResponse

```text
{zones: Array<Zone>}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zones` | Yes | All zones configured for the system. |

## GetVacationResponse

```text
{vacation: Vacation | null, capabilities: {ambientTemperature: AmbientTemperatureCapability}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `vacation` | Yes | The vacation configuration for the system, or null if none has been set. |
| `capabilities` | Yes | Capabilities for the system. |

## GetZoneStatusResponse

```text
{features: {ambientTemperature?: {currentTemperature: number, currentDisplayTemperatureCelsius?: number, currentDisplayTemperatureFahrenheit?: number, mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', status: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown', settings: {mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}, capabilities: {setpoint: {min: number, max: number, precision: {celsius: number, fahrenheit: number}}}, setpoint: {value: number, minValue: number, maxValue: number, precision: {celsius: number, fahrenheit: number}, increment: {celsius: number, fahrenheit: number}}, current: number, hvacMode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', hvacStatus: 'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'}, circulation?: {status: 'Off' | 'Circulating' | 'Unknown', fanSpeedStatus: 0 | 1 | 2 | 3, settings: {mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}, capabilities: {fanSpeedSetting: {max: number}}, enabled: boolean, fanSpeedSetting: {value: 1 | 2 | 3 | 'Auto'}, fanOnDurationSetting: {value: integer | null}}, humidity?: {status: 'Off' | 'Humidifying', currentRelativeHumidity: number, currentDisplayRelativeHumidity: number, settings: {mode: 'Off' | 'Humidify', setpoint: {value: number}}, capabilities?: {modes: Array<HumidityMode>, setpoint: {min: number, max: number, precision: number}}}}, schedule?: {id: string, kind: 'Weekly' | 'Vacation', status: 'Active' | 'Paused'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `features` | Yes | All features available to access or operate on the zone. |
| `schedule` | No | Schedule currently affecting the zone. |

## HeatPumpCommand

```text
'heatStripStart' | 'heatStripStop' | 'clearFault'
```

## HeatPumpCommandPathParams

```text
{equipment_id: string, command: HeatPumpCommand}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `equipment_id` | Yes |  |
| `command` | Yes |  |

## HeatPumpEmptyArgs

```text
{}
```

## HeatPumpClearFaultArgs

```text
{faultCode: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `faultCode` | Yes |  |

## HeatPumpCommandRequest

```text
{}
```

## HeatPumpCommandResponse

```text
{result: 'ok'} | {result: 'unreachable', error?: string}
```

## HeatPumpHeatStripSettings

```text
{enabled: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `enabled` | Yes |  |

## HeatPumpSettings

```text
{heatStrip?: {enabled: boolean}, heatingTemperatureOffset: number, coolingTemperatureOffset: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `heatStrip` | No |  |
| `heatingTemperatureOffset` | Yes | minimum: -10; maximum: 10 |
| `coolingTemperatureOffset` | Yes | minimum: -10; maximum: 10 |

## UpdateHeatPumpSettingsRequest

```text
{heatStrip?: {enabled: boolean}, heatingTemperatureOffset?: number, coolingTemperatureOffset?: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `heatStrip` | No |  |
| `heatingTemperatureOffset` | No | minimum: -10; maximum: 10 |
| `coolingTemperatureOffset` | No | minimum: -10; maximum: 10 |

Cross-field constraints: At least one setting must be provided.

## UpdateHeatPumpSettingsResponse

```text
{settings: HeatPumpSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## GetHeatPumpSettingsResponse

```text
{settings: HeatPumpSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## HvacStatus

```text
'Off' | 'Cooling' | 'Heating' | 'Circulating' | 'Dehumidifying' | 'Unknown'
```

## RefreshTokenRequest

```text
{refreshToken: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `refreshToken` | Yes | The refresh token obtained from sign-in or a previous refresh.; minLength: 1 |

## RefreshTokenResponse

```text
{accessToken: string, expiresIn: number, refreshToken: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `accessToken` | Yes | The new access token for authenticated requests. |
| `expiresIn` | Yes | The number of seconds until the access token expires. |
| `refreshToken` | Yes | The refresh token to use for the next refresh. |

## RegisterUserRequest

```text
{email: string, givenName: string, familyName: string, appScheme?: 'jetsonhome' | 'jetsonhomedev' | 'jetsoninstaller' | 'jetsoninstallerdev'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes | The email address of the user. |
| `givenName` | Yes | The first name of the user. |
| `familyName` | Yes | The last name of the user. |
| `appScheme` | No | The requesting build's deep-link scheme, so the magic link reopens the install that requested it. |

## RegisterUserResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |

## RemoveSystemMemberResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes | Whether the member was successfully removed from the system |

## ResumeScheduleRequest

```text
{kind?: 'Weekly' | 'Vacation'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `kind` | No | Whether the target is a weekly schedule or a vacation. Defaults to Weekly when omitted.; default: "Weekly" |

## ResumeScheduleResponse

```text
{success: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `success` | Yes | Whether the schedule was successfully resumed. |

## SetAmbientTemperatureModeRequest

```text
{value: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The desired HVAC mode for the zone. |

## SetAmbientTemperatureModeResponse

```text
{result: 'ok'} | {result: 'unreachable', error?: string}
```

## SetHvacModeRequest

```text
{value: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | Yes | The desired HVAC mode for the zone. |

## SetHvacModeResponse

```text
{result: 'ok'} | {result: 'unreachable', error?: string}
```

## SignInRequest

```text
{email: string, appScheme?: 'jetsonhome' | 'jetsonhomedev' | 'jetsoninstaller' | 'jetsoninstallerdev'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes | The email address of the user to sign in. |
| `appScheme` | No | The requesting build's deep-link scheme, so the magic link reopens the install that requested it. |

## SignInResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |

## SetAmbientTemperatureSetpointRequest

```text
{value?: number, heatValue?: number, coolValue?: number}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `value` | No | The desired ambient temperature setpoint in Celsius; applies to both heat and cool targets. |
| `heatValue` | No | The desired heat-to temperature target in Celsius. |
| `coolValue` | No | The desired cool-to temperature target in Celsius. |

Cross-field constraints: heatValue and coolValue must be provided together; Either value or heatValue/coolValue must be provided; heatValue must not exceed coolValue

## SetAmbientTemperatureSetpointResponse

```text
{result: 'ok'} | {result: 'unreachable', error?: string}
```

## SetCirculationSettingsRequest

```text
{enabled: boolean, fanSpeedSetting: 1 | 2 | 3 | 'Auto', fanOnDurationSetting: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `enabled` | Yes | Whether the circulation system is enabled. |
| `fanSpeedSetting` | Yes | The setpoint for fan speed (1..MAX) or 'Auto' |
| `fanOnDurationSetting` | Yes | Target duration to run the fan in minutes per hour.; minimum: 0; maximum: 60 |

## SetCirculationSettingsResponse

```text
{result: 'ok'} | {result: 'unreachable', error?: string}
```

## ThermostatSettings

```text
{darkModeEnabled: boolean, idleBrightnessPercent: integer, activeBrightnessPercent: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `darkModeEnabled` | Yes |  |
| `idleBrightnessPercent` | Yes | minimum: 0; maximum: 100 |
| `activeBrightnessPercent` | Yes | minimum: 0; maximum: 100 |

## UpdateThermostatSettingsRequest

```text
{darkModeEnabled?: boolean, idleBrightnessPercent?: integer, activeBrightnessPercent?: integer}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `darkModeEnabled` | No |  |
| `idleBrightnessPercent` | No | minimum: 0; maximum: 100 |
| `activeBrightnessPercent` | No | minimum: 0; maximum: 100 |

Cross-field constraints: At least one setting must be provided.

## UpdateThermostatSettingsResponse

```text
{settings: ThermostatSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## GetThermostatSettingsResponse

```text
{settings: ThermostatSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## UpdateAmbientTemperatureSettingsRequest

```text
{mode?: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint?: {value: number, heatValue?: number, coolValue?: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | No | The current mode of the ambient temperature control. |
| `setpoint` | No | x-refinements: ["heatValue and coolValue must be provided together", "heatValue must not exceed coolValue"] |

Cross-field constraints: At least one setting must be provided

## UpdateAmbientTemperatureSettingsResponse

```text
{mode: 'Off' | 'Heat' | 'Cool' | 'Auto' | 'FanOnly', setpoint: {value: number, heatValue?: number, coolValue?: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The current mode of the ambient temperature control. |
| `setpoint` | Yes | x-refinements: ["heatValue and coolValue must be provided together", "heatValue must not exceed coolValue"] |

## UpdateCirculationSettingsRequest

```text
{mode?: 'Off' | 'Circulate' | 'Continuous', fanSpeed?: 1 | 2 | 3 | 'Auto', fanOnDuration?: integer, enabled?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | No | The circulation mode. 'Off' = no circulation, 'Circulate' = fan runs per fanOnDuration, 'Continuous' = fan runs always. |
| `fanSpeed` | No | The fan speed setting (1..MAX) or 'Auto'. |
| `fanOnDuration` | No | The desired time in minutes to run the fan per hour.; minimum: 0; maximum: 60 |
| `enabled` | No | DEPRECATED. Use "mode" instead. |

Cross-field constraints: At least one setting must be provided; "mode" and "enabled" cannot be used together. Use "mode" instead of "enabled".

## UpdateCirculationSettingsResponse

```text
{mode: 'Off' | 'Circulate' | 'Continuous', fanSpeed: 1 | 2 | 3 | 'Auto', fanOnDuration: integer, enabled?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The circulation mode. 'Off' = no circulation, 'Circulate' = fan runs per fanOnDuration, 'Continuous' = fan runs always. |
| `fanSpeed` | Yes | The fan speed setting (1..MAX) or 'Auto'. |
| `fanOnDuration` | Yes | The desired time in minutes to run the fan per hour.; minimum: 0; maximum: 60 |
| `enabled` | No | DEPRECATED. Use "mode" instead. |

## UpdateCurrentUserRequest

```text
{onboardingCompleted: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `onboardingCompleted` | Yes | Whether the user has completed onboarding. |

## UpdateCurrentUserResponse

```text
{user: User}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `user` | Yes |  |

## UpdateHumiditySettingsRequest

```text
{mode?: 'Off' | 'Humidify', setpoint?: {value: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | No | The current humidity control mode. |
| `setpoint` | No |  |

Cross-field constraints: At least one setting must be provided

## UpdateHumiditySettingsResponse

```text
{mode: 'Off' | 'Humidify', setpoint: {value: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `mode` | Yes | The current humidity control mode. |
| `setpoint` | Yes |  |

## UpdateSchedulePresetRequest

```text
{name?: string, temperatureSetpoint?: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null, isDefaultPreset?: boolean}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | The name of the preset.; minLength: 1; maxLength: 255; x-refinements: ["Callback validation (inspect bytecode)"] |
| `temperatureSetpoint` | No | The temperature setpoint of the preset in degrees Celsius. |
| `temperatureMode` | No | The temperature mode override, or null to use system default. |
| `fanSpeed` | No | The fan speed override, or null to use system default. |
| `quiet` | No | Whether to run in quiet mode, or null to use system default. |
| `isDefaultPreset` | No | Whether this preset is the default preset. |

Cross-field constraints: No fields to update provided

## UpdateSchedulePresetResponse

```text
{preset: SchedulePreset}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `preset` | Yes |  |

## UpdateScheduleRequest

```text
{type?: 'sleep' | 'away' | 'custom', weekly?: Array<ScheduleWeeklyEvent>, zones?: Array<string>, enabled?: boolean, name?: string, preset?: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `type` | No | The type of schedule. |
| `weekly` | No | The weekly events of the schedule. |
| `zones` | No | IDs of the zones this schedule applies to. |
| `enabled` | No | Whether the schedule is enabled. |
| `name` | No | Optional schedule name. Defaults to the preset name if omitted. |
| `preset` | No | ID of the preset to use for this schedule. |

## UpdateScheduleResponse

```text
{schedule: {id: string, name: string, createdAt: string, type: 'sleep' | 'away' | 'custom', preset: {id: string, name: string, isDefault: boolean, temperatureSetpoint: number, temperatureMode?: AmbientTemperatureMode | null, fanSpeed?: FanSpeedSetting | null, quiet?: boolean | null}, weekly: Array<ScheduleWeeklyEvent>, zoneIds: Array<string>, zones: Array<{id: string}>, enabled: boolean}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `schedule` | Yes | The updated schedule. |

## UpdateSystemRequest

```text
{name?: string, address?: {line1: string, line2?: string, city: string, county?: string, stateCode: string, countryCode: string, postalCode?: string, latitude: number, longitude: number}, settings?: {temperatureUnit?: 'Celsius' | 'Fahrenheit', ambientTemperatureSource?: 'Internal' | 'External'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name for the system.; minLength: 1; maxLength: 255 |
| `address` | No | Postal address for the system. Admin only. |
| `settings` | No | System settings to update for the system. Admin only. |

## UpdateSystemResponse

```text
{system: System}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `system` | Yes |  |

## UpdateSystemMemberRequest

```text
{member: {user?: {name?: string}, role?: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes |  |

## UpdateSystemMemberResponse

```text
{member: {user: {id: string, email: string, name: string, onboardingCompleted: boolean}, role: 'Owner' | 'Member'}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `member` | Yes | Member updated on the system. |

## UpdateSystemSettingsRequest

```text
{temperatureUnit?: 'Celsius' | 'Fahrenheit', ambientTemperatureSource?: 'Internal' | 'External'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `temperatureUnit` | No | Preferred temperature unit for the system. |
| `ambientTemperatureSource` | No | Preferred ambient temperature source for the system. |

## UpdateSystemSettingsResponse

```text
{settings: SystemSettings}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `settings` | Yes |  |

## UpdateVacationRequest

```text
{enabled: boolean, startAt: string, endAt: string, preset: {temperatureSetpoint: number}}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `enabled` | Yes | Whether vacation is enabled. |
| `startAt` | Yes | Start of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `endAt` | Yes | End of vacation period as system-local datetime, no timezone offset (YYYY-MM-DDTHH:MM:SS).; x-local-datetime: true; x-refinements: ["Must be a system-local datetime with no timezone offset (YYYY-MM-DDTHH:MM:SS)"] |
| `preset` | Yes | Preset applied during the vacation period. |

## UpdateVacationResponse

```text
{result: 'ok'}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `result` | Yes |  |

## UpdateZoneRequest

```text
{name?: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `name` | No | Display name for the zone.; minLength: 1; maxLength: 255 |

## UpdateZoneResponse

```text
{zone: Zone}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `zone` | Yes |  |

## VerifyMagicLinkRequest

```text
{email: string, token: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `email` | Yes | The email address to send the authentication link to. |
| `token` | Yes | The token provided via magic link |

## VerifyMagicLinkResponse

```text
{userId: string, accessToken: string, expiresIn: number, refreshToken: string}
```

| Field | Required | Description / constraints |
| --- | --- | --- |
| `userId` | Yes | The unique identifier for the authenticated user. |
| `accessToken` | Yes | The access token for authenticated requests. |
| `expiresIn` | Yes | The number of seconds until the access token expires. |
| `refreshToken` | Yes | The refresh token used to obtain a new access token. |
