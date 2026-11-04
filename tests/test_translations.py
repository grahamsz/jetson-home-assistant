"""Translation completeness and the stable API values used by automations."""

import json
import re
import unittest
from pathlib import Path
from string import Formatter

from protocol_loader import models, telemetry

ROOT = Path(__file__).resolve().parents[1] / "custom_components/jetson_home"


def leaves(value, prefix=""):
    if isinstance(value, dict):
        return {
            path: text
            for key, item in value.items()
            for path, text in leaves(item, f"{prefix}.{key}").items()
        }
    return {prefix: value}


def fields(text):
    return {field for _, field, _, _ in Formatter().parse(text) if field}


class TranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogs = {
            language: json.loads(
                (ROOT / "translations" / f"{language}.json").read_text(encoding="utf-8")
            )
            for language in ("en", "es", "fr")
        }

    def test_complete_catalogs_and_matching_placeholders(self):
        english = leaves(self.catalogs["en"])
        for language, catalog in self.catalogs.items():
            localized = leaves(catalog)
            self.assertEqual(english.keys(), localized.keys(), language)
            for key, value in localized.items():
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip(), (language, key))
                self.assertNotIn("[%key:", value)
                self.assertEqual(fields(english[key]), fields(value), (language, key))
        self.assertEqual(
            json.loads((ROOT / "strings.json").read_text(encoding="utf-8")), self.catalogs["en"]
        )

    def test_entity_keys_and_enum_states_have_all_localizations(self):
        for catalog in self.catalogs.values():
            for domain in catalog["entity"].values():
                for key in domain:
                    self.assertRegex(key, r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
            sensors = catalog["entity"]["sensor"]
            for key, options in models.STATUS_SENSOR_OPTIONS.items():
                self.assertEqual(set(sensors[key]["state"]), set(options))
            for field, options in telemetry.SPEED_OPERATION_OPTIONS.items():
                self.assertEqual(set(sensors[f"operation_{field.lower()}"]["state"]), set(options))
            self.assertEqual(set(sensors["air_quality"]["state"]), set(models.AIR_QUALITY_LEVELS))

    def test_fan_numbers_display_named_speeds_in_each_language(self):
        for language, labels in (
            ("en", ("Low", "Medium", "High")),
            ("es", ("Baja", "Media", "Alta")),
            ("fr", ("Basse", "Moyenne", "Élevée")),
        ):
            catalog = self.catalogs[language]
            fan = catalog["entity"]["sensor"]["fan_mode"]["state"]
            self.assertEqual(tuple(fan[str(speed)] for speed in (1, 2, 3)), labels)
            self.assertEqual(
                catalog["entity"]["climate"]["thermostat"]["state_attributes"]["fan_mode"]["state"],
                fan,
            )

    def test_flow_and_error_messages_are_translated(self):
        english = leaves(self.catalogs["en"])
        for language in ("es", "fr"):
            for key, value in leaves(self.catalogs[language]).items():
                if key.startswith((".config.", ".options.", ".exceptions.")):
                    self.assertNotEqual(value, english[key], (language, key))

    def test_control_exception_keys_exist_in_all_languages(self):
        keys = set()
        for path in ROOT.glob("*.py"):
            keys.update(re.findall(r'user_error\("([a-z_]+)"', path.read_text(encoding="utf-8")))
        self.assertTrue(keys)
        for catalog in self.catalogs.values():
            self.assertTrue(keys <= catalog["exceptions"].keys())


if __name__ == "__main__":
    unittest.main()
