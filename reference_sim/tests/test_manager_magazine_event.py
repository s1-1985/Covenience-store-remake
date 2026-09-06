import unittest

from conveni_sim.manager_magazine_event import ManagerMagazineEventRuntime
from conveni_sim.staff import StaffSkill, StoreStaffRoster


class ManagerMagazineEventRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.staff = StoreStaffRoster()
        self.staff.add_staff(
            "manager",
            manager=True,
            runtime_skills={
                StaffSkill.EDUCATION: 40,
                StaffSkill.CLEANING: 55,
            },
        )
        self.runtime = ManagerMagazineEventRuntime(self.staff)

    def test_recording_event_does_not_invent_skill_gain(self) -> None:
        item = self.runtime.record_feature_event(
            observed_cleaning=90,
            source="first-title dedicated research",
        )

        self.assertEqual(item.manager_staff_id, "manager")
        self.assertEqual(item.observed_cleaning, 90)
        self.assertFalse(item.resolved)
        self.assertEqual(self.staff.staff_member("manager").skill_value(StaffSkill.EDUCATION), 40)
        self.assertEqual(len(self.runtime.unresolved_opportunities), 1)

    def test_resolution_applies_only_explicit_observed_values(self) -> None:
        item = self.runtime.record_feature_event(
            source="observed magazine event",
        )
        resolved = self.runtime.resolve_opportunity(
            item.sequence,
            after_skills={StaffSkill.EDUCATION: 45},
        )

        manager = self.staff.staff_member("manager")
        self.assertTrue(resolved.resolved)
        self.assertEqual(manager.skill_value(StaffSkill.EDUCATION), 45)
        self.assertEqual(manager.skill_value(StaffSkill.CLEANING), 55)
        self.assertEqual(self.runtime.unresolved_opportunities, ())

    def test_no_manager_cannot_record_feature(self) -> None:
        roster = StoreStaffRoster()
        runtime = ManagerMagazineEventRuntime(roster)
        with self.assertRaises(ValueError):
            runtime.record_feature_event(source="observation")

    def test_resolution_cannot_reduce_known_skill(self) -> None:
        item = self.runtime.record_feature_event(source="observation")
        with self.assertRaises(ValueError):
            self.runtime.resolve_opportunity(
                item.sequence,
                after_skills={StaffSkill.EDUCATION: 39},
            )


if __name__ == "__main__":
    unittest.main()
