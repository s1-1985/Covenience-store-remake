import unittest

from conveni_sim.staff import StaffSkill, StaffTask, StoreStaffRoster
from conveni_sim.staff_growth_resolution import (
    EvidenceBackedStaffGrowthResolver,
    StaffGrowthResolutionStatus,
)


class StaffGrowthResolutionTests(unittest.TestCase):
    def test_replenish_and_clean_resolve_plus_one_up_to_known_cap(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={
                StaffSkill.REPLENISHMENT: 5,
                StaffSkill.CLEANING: 7,
            },
            base_skill_caps={
                StaffSkill.REPLENISHMENT: 6,
                StaffSkill.CLEANING: 7,
            },
        )
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        roster.record_completed_work("s1", StaffTask.CLEAN)

        results = EvidenceBackedStaffGrowthResolver(roster).resolve_supported_pending()

        self.assertEqual([result.status for result in results], [
            StaffGrowthResolutionStatus.RESOLVED,
            StaffGrowthResolutionStatus.RESOLVED,
        ])
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.REPLENISHMENT), 6)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.CLEANING), 7)
        self.assertEqual(roster.unresolved_growth_opportunities, ())

    def test_checkout_growth_remains_unresolved_because_increment_is_unknown(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.REGISTER: 10},
            base_skill_caps={StaffSkill.REGISTER: 20},
        )
        roster.record_completed_work("s1", StaffTask.CHECKOUT)

        results = EvidenceBackedStaffGrowthResolver(roster).resolve_supported_pending()

        self.assertEqual(results, ())
        self.assertEqual(len(roster.unresolved_growth_opportunities), 1)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.REGISTER), 10)

    def test_missing_cap_keeps_supported_growth_pending(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.REPLENISHMENT: 10},
        )
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        resolver = EvidenceBackedStaffGrowthResolver(roster)

        result = resolver.resolve_supported_pending()[0]

        self.assertEqual(result.status, StaffGrowthResolutionStatus.UNKNOWN_BASE_CAP)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.REPLENISHMENT), 10)
        self.assertEqual(len(roster.unresolved_growth_opportunities), 1)

    def test_value_above_normal_cap_is_not_reduced_by_normal_growth(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.CLEANING: 12},
            base_skill_caps={StaffSkill.CLEANING: 10},
        )
        roster.record_completed_work("s1", StaffTask.CLEAN)

        result = EvidenceBackedStaffGrowthResolver(roster).resolve_supported_pending()[0]

        self.assertEqual(result.status, StaffGrowthResolutionStatus.ABOVE_BASE_CAP)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.CLEANING), 12)
        self.assertEqual(len(roster.unresolved_growth_opportunities), 1)


if __name__ == "__main__":
    unittest.main()
