import unittest

from conveni_sim.save_state import SaveStateEnvelope


class SaveStateEnvelopeTests(unittest.TestCase):
    def test_round_trip_preserves_unknown_values_and_component_boundaries(self):
        state = SaveStateEnvelope.capture(
            schema_version=1,
            components={
                "clock": {"year": 1, "month": 8, "day": 4, "minute_of_day": 1439},
                "customer_share": {
                    "value": None,
                    "weather": "unknown",
                    "recalculation_pending": True,
                },
                "rival_ai": {"stores": [], "next_action": None},
            },
        )

        restored = SaveStateEnvelope.from_document(state.to_document())

        self.assertEqual(restored, state)
        self.assertIsNone(restored.component("customer_share")["value"])
        self.assertIsNone(restored.component("rival_ai")["next_action"])

    def test_missing_component_returns_none_instead_of_inventing_default(self):
        state = SaveStateEnvelope.capture(schema_version=1, components={})

        self.assertIsNone(state.component("future_guidebook_table"))

    def test_rejects_non_json_runtime_objects(self):
        with self.assertRaises(TypeError):
            SaveStateEnvelope.capture(
                schema_version=1,
                components={"staff": {"runtime": object()}},
            )

    def test_rejects_unversioned_or_future_envelope_shape(self):
        with self.assertRaises(TypeError):
            SaveStateEnvelope.from_document({"components": {}})

        with self.assertRaises(ValueError):
            SaveStateEnvelope.from_document(
                {"schema_version": 1, "components": {}, "guessed_formula": 0.42}
            )

    def test_capture_copies_nested_payloads(self):
        payload = {"events": [{"kind": "promotion", "amount_yen": None}]}
        state = SaveStateEnvelope.capture(schema_version=1, components={"events": payload})

        payload["events"][0]["amount_yen"] = 100000

        self.assertIsNone(state.component("events")["events"][0]["amount_yen"])


if __name__ == "__main__":
    unittest.main()
