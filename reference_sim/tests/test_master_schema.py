import unittest

from conveni_sim.baseline_data import FIXTURES
from conveni_sim.master_audit import (
    aggregate_completion,
    audit_customer_archetype,
    audit_fixture,
    audit_product,
    audit_staff,
)
from conveni_sim.models import (
    CustomerArchetypeDefinition,
    EvidenceLevel,
    EvidenceValue,
    ProductDefinition,
    StaffDefinition,
)


class MasterSchemaTests(unittest.TestCase):
    def ev(self, value):
        return EvidenceValue(value, EvidenceLevel.CONFIRMED_VISUAL, "unit-test source")

    def test_unknown_product_fields_remain_none_and_audit_as_zero(self):
        product = ProductDefinition("unknown-product")
        result = audit_product(product)
        self.assertEqual(result.completion_ratio, 0.0)
        self.assertFalse(result.complete)
        self.assertEqual(len(result.unknown_fields), 4)

    def test_product_core_fields_can_be_filled_with_evidence_values(self):
        product = ProductDefinition(
            "sample-product",
            category=self.ev("bread"),
            procurement_cost_yen=self.ev(100),
            standard_retail_price_yen=self.ev(120),
            compatible_fixture_ids=self.ev(("ambient_shelf",)),
        )
        result = audit_product(product)
        self.assertTrue(result.complete)
        self.assertEqual(result.completion_ratio, 1.0)

    def test_audit_rejects_unlabeled_raw_master_value(self):
        product = ProductDefinition("bad", category="bread")
        with self.assertRaises(TypeError):
            audit_product(product)

    def test_existing_plant_anchor_reports_only_currently_known_core_fields(self):
        plant = next(fixture for fixture in FIXTURES if fixture.id == "potted_plant")
        result = audit_fixture(plant)
        self.assertEqual(set(result.known_fields), {"footprint", "maintenance_yen_per_day"})
        self.assertIn("purchase_price_yen", result.unknown_fields)
        self.assertIn("capacity", result.unknown_fields)
        self.assertIn("compatible_product_categories", result.unknown_fields)
        self.assertIn("interaction_sides", result.unknown_fields)

    def test_customer_archetype_numeric_behavior_can_remain_entirely_unknown(self):
        archetype = CustomerArchetypeDefinition("student")
        result = audit_customer_archetype(archetype)
        self.assertEqual(result.completion_ratio, 0.0)
        self.assertEqual(len(result.unknown_fields), 5)

    def test_partial_customer_evidence_does_not_require_inventing_other_fields(self):
        archetype = CustomerArchetypeDefinition(
            "student",
            origin_building_affinities=self.ev(("school",)),
        )
        result = audit_customer_archetype(archetype)
        self.assertEqual(result.known_fields, ("origin_building_affinities",))
        self.assertAlmostEqual(result.completion_ratio, 0.2)

    def test_unknown_staff_row_keeps_all_runtime_and_hiring_values_unknown(self):
        result = audit_staff(StaffDefinition("unknown-staff"))
        self.assertEqual(result.completion_ratio, 0.0)
        self.assertEqual(len(result.unknown_fields), 11)

    def test_staff_hiring_and_runtime_fields_are_audited_separately(self):
        staff = StaffDefinition(
            "sample-staff",
            stamina=self.ev(80),
            academic_background=self.ev(90),
            agility=self.ev(70),
            sociability=self.ev(60),
            education=self.ev(85),
            register_skill=self.ev(40),
        )
        result = audit_staff(staff)
        self.assertEqual(
            set(result.known_fields),
            {"stamina", "academic_background", "agility", "sociability", "education", "register_skill"},
        )
        self.assertIn("replenishment_skill", result.unknown_fields)
        self.assertIn("security_skill", result.unknown_fields)

    def test_aggregate_completion_counts_fields_not_rows(self):
        empty = audit_product(ProductDefinition("empty"))
        complete = audit_product(
            ProductDefinition(
                "complete",
                category=self.ev("bread"),
                procurement_cost_yen=self.ev(100),
                standard_retail_price_yen=self.ev(120),
                compatible_fixture_ids=self.ev(("ambient_shelf",)),
            )
        )
        self.assertEqual(aggregate_completion((empty, complete)), 0.5)


if __name__ == "__main__":
    unittest.main()
