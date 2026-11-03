"""Sign in and inspect selected readings/capabilities; never send device commands."""

import argparse
import asyncio
import importlib
import json
import sys
import types
from getpass import getpass
from pathlib import Path
from uuid import uuid4

import aiohttp

package = types.ModuleType("jetson_probe_protocol")
package.__path__ = [str(Path(__file__).resolve().parents[1] / "custom_components" / "jetson_home")]
sys.modules[package.__name__] = package
api = importlib.import_module("jetson_probe_protocol.api")
models = importlib.import_module("jetson_probe_protocol.models")


def numeric_limits(limits):
    result = {key: models.number(limits.get(key)) for key in ("min", "max")}
    precision = limits.get("precision")
    result["precision"] = (
        {unit: models.number(precision.get(unit)) for unit in ("celsius", "fahrenheit")}
        if isinstance(precision, dict)
        else models.number(precision)
    )
    return result


def summarize(snapshot):
    """Export a fixed field list; never raw responses, names, IDs, or credentials."""
    return {
        "system_count": len(snapshot.systems),
        "zone_count": len(snapshot.zones),
        "hub_count": sum(len(system.boards) for system in snapshot.systems.values()),
        "air_quality_monitor_count": sum(
            item.get("model") == "TEMCO-AQM"
            for system in snapshot.systems.values()
            for item in system.equipment
        ),
        "energy_monitor_count": sum(
            item.get("type") == "EnergyMonitor"
            for system in snapshot.systems.values()
            for item in system.equipment
        ),
        "zones": [
            {
                "zone_number": index,
                "online": zone.online,
                "current_temperature_c": zone.current_temperature,
                "target_temperature_c": zone.target_temperature,
                "hvac_mode": zone.mode
                if zone.mode in ("Off", "Heat", "Cool", "Auto", "FanOnly")
                else None,
                "hvac_status": zone.action
                if zone.action
                in ("Off", "Cooling", "Heating", "Circulating", "Dehumidifying", "Unknown")
                else None,
                "temperature_limits": numeric_limits(zone.temperature_capabilities),
                "current_humidity_percent": zone.current_humidity,
                "humidifier_control_advertised": zone.supports_humidifier,
                "humidity_limits": numeric_limits(zone.humidity_limits),
                "fan_speed_max": zone.fan_max,
                "air_quality_access": zone.air_quality_access,
                "air_quality_overall": zone.air_quality_overall,
                "co2_ppm": zone.pollutant("co2"),
                "pm25_ug_m3": zone.pollutant("pm25"),
                "tvoc_ppb": zone.pollutant("tvoc"),
            }
            for index, zone in enumerate(snapshot.zones.values(), 1)
        ],
    }


async def run(args):
    async with aiohttp.ClientSession() as session:
        client = api.JetsonClient(session, install_id=str(uuid4()))
        print("Requesting a Jetson sign-in email. Copy its link without opening it.")
        await client.request_magic_link(args.email.strip())
        link = await asyncio.to_thread(getpass, "Paste the new link or token (hidden): ")
        token = api.token_from_link(link, args.email.strip())
        await client.verify_magic_link(args.email.strip(), token)
        result = summarize(await client.get_snapshot())
        output = json.dumps(result, indent=2)
        print(output)
        if args.output:
            await asyncio.to_thread(Path(args.output).write_text, output + "\n", encoding="utf-8")
            print(
                "Saved selected readings/capabilities. Account/device identifiers and tokens are omitted."
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Existing Jetson Home account email")
    parser.add_argument(
        "--output", help="Optional JSON file containing only selected readings/capabilities"
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args))
    except (api.JetsonError, ValueError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
