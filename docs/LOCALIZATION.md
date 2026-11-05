# English, Spanish, and French

The integration ships complete `en`, `es`, and `fr` catalogs, including 0.7.0's schedule-paused status, resume button, and circulation-minutes control. French uses Canadian terminology such as courriel and thermopompe. The catalogs translate setup and reauthentication, options and refresh messages, default entity names, known enum states, attribute labels, and control-validation errors. User-supplied system, zone, load, and equipment names remain as configured in Jetson.

Fan mode keeps raw states `auto`, `1`, `2`, `3` for existing automations and sends the same API command values. The displayed labels are:

| Value | English | Spanish | French |
| --- | --- | --- | --- |
| Auto | Auto | Automático | Automatique |
| 1 | Low | Baja | Basse |
| 2 | Medium | Media | Moyenne |
| 3 | High | Alta | Élevée |

Current-speed sensors also show 0 as Off / Apagado / Arrêt. Fan activity displays Off/Running with the corresponding translation. Unknown speed values remain unknown, with the per-unit raw value available as an attribute. Other firmware diagnostic strings, such as `constantAirflow` and `Current`, retain their API spelling; they are diagnostic codes rather than translated enum states. A command failure can include the original protocol error detail inside a localized message.

Home Assistant resolves default entity names using its server language; state and flow labels use the relevant UI language. Set your preferred language in HA. Existing custom names and entity IDs are retained, and a language change does not rewrite existing entity IDs. Existing names may need to be edited separately after changing language. See [HA's naming rules](https://contributors.home-assistant.io/core/entities/naming/) and [translation rules](https://contributors.home-assistant.io/core/integrations/translations/).

The rename from Whole-home power to Main power preserves the original unique ID and history. An existing entity ID may still contain the old wording. The per-load label includes “load” so an indoor load named Main is distinguishable from Main power. Translated names use placeholders for proper names, and an explicit configuration refresh updates those placeholders after a rename.

Tests check matching keys and placeholders across languages, all supported enum labels, localized control errors, and entity metadata. These are catalog/adapter checks, not a live HA frontend test. The stale-air-quality behavior is unchanged in every language.
