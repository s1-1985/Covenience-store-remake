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
        # RESOLVED 2026-09-17: replenish/clean each now also open a security
        # growth opportunity (and replenish a cleaning one) per the guide's
        # multi-skill diagram; none of those increments are evidence-backed,
        # so they stay unresolved even though replenishment/cleaning resolved.
        remaining = {(o.task, o.skill) for o in roster.unresolved_growth_opportunities}
        self.assertEqual(
            remaining,
            {
                (StaffTask.REPLENISH, StaffSkill.CLEANING),
                (StaffTask.REPLENISH, StaffSkill.SECURITY),
                (StaffTask.CLEAN, StaffSkill.SECURITY),
            },
        )

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
        # RESOLVED 2026-09-17: checkout now also opens a service growth
        # opportunity per the guide's multi-skill diagram; its increment is
        # equally unresolved, so both stay pending.
        self.assertEqual(len(roster.unresolved_growth_opportunities), 2)
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
        # RESOLVED 2026-09-17: the same replenish event also opened cleaning
        # and security growth opportunities (unresolved increment), on top
        # of replenishment's own UNKNOWN_BASE_CAP one.
        self.assertEqual(len(roster.unresolved_growth_opportunities), 3)

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
        # RESOLVED 2026-09-17: the same clean event also opened a security
        # growth opportunity (unresolved increment), on top of cleaning's
        # own ABOVE_BASE_CAP one.
        self.assertEqual(len(roster.unresolved_growth_opportunities), 2)


if __name__ == "__main__":
    unittest.main()
