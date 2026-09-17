import random
import unittest

from conveni_sim.remake_staff_growth import RemakeBalancedStaffGrowthResolver
from conveni_sim.staff import StaffSkill, StaffTask, StoreStaffRoster
from conveni_sim.staff_growth_resolution import StaffGrowthResolutionStatus


class RemakeBalancedStaffGrowthResolverTests(unittest.TestCase):
    def test_resolves_previously_unsupported_checkout_pairs(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.REGISTER: 10, StaffSkill.SERVICE: 10},
            base_skill_caps={StaffSkill.REGISTER: 50, StaffSkill.SERVICE: 50},
        )
        roster.record_completed_work("s1", StaffTask.CHECKOUT)

        results = RemakeBalancedStaffGrowthResolver(roster, rng=random.Random(0)).resolve_all_pending()

        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.status is StaffGrowthResolutionStatus.RESOLVED for r in results))
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.REGISTER), 11)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.SERVICE), 11)

    def test_resolves_all_replenish_and_clean_pairs(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={
                StaffSkill.REPLENISHMENT: 5,
                StaffSkill.CLEANING: 5,
                StaffSkill.SECURITY: 5,
            },
            base_skill_caps={
                StaffSkill.REPLENISHMENT: 50,
                StaffSkill.CLEANING: 50,
                StaffSkill.SECURITY: 50,
            },
        )
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        roster.record_completed_work("s1", StaffTask.CLEAN)

        results = RemakeBalancedStaffGrowthResolver(roster, rng=random.Random(0)).resolve_all_pending()

        self.assertEqual(len(results), 5)  # replenish(3) + clean(2)
        self.assertEqual(roster.unresolved_growth_opportunities, ())
        # cleaning/security are each targeted by both replenish and clean
        # (see WORK_GROWTH_SKILL); both opportunities must compound against
        # the live value (5 -> 6 -> 7), not both apply +1 from the same
        # stale creation-time snapshot (which would leave it at 6).
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.REPLENISHMENT), 6)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.CLEANING), 7)
        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.SECURITY), 7)

    def test_never_exceeds_base_cap(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.CLEANING: 50},
            base_skill_caps={StaffSkill.CLEANING: 50},
        )
        roster.record_completed_work("s1", StaffTask.CLEAN)

        RemakeBalancedStaffGrowthResolver(roster, rng=random.Random(0)).resolve_all_pending()

        self.assertEqual(roster.staff_member("s1").skill_value(StaffSkill.CLEANING), 50)

    def test_manager_education_can_add_a_bonus_point(self):
        roster = StoreStaffRoster()
        roster.add_staff("manager", manager=True, runtime_skills={StaffSkill.EDUCATION: 100})
        roster.add_staff(
            "worker",
            runtime_skills={StaffSkill.CLEANING: 5},
            base_skill_caps={StaffSkill.CLEANING: 50},
        )
        roster.record_completed_work("worker", StaffTask.CLEAN)
        opportunity = next(
            o for o in roster.growth_opportunities if o.skill is StaffSkill.CLEANING
        )
        self.assertEqual(opportunity.manager_education, 100)

        # rng.random() < 1.0 always true -> bonus always applies at education=100
        resolver = RemakeBalancedStaffGrowthResolver(roster, rng=random.Random(0))
        resolver.resolve_opportunity(opportunity)

        self.assertEqual(roster.staff_member("worker").skill_value(StaffSkill.CLEANING), 7)

    def test_no_manager_means_no_bonus(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "worker",
            runtime_skills={StaffSkill.CLEANING: 5},
            base_skill_caps={StaffSkill.CLEANING: 50},
        )
        roster.record_completed_work("worker", StaffTask.CLEAN)
        opportunity = next(
            o for o in roster.growth_opportunities if o.skill is StaffSkill.CLEANING
        )
        self.assertIsNone(opportunity.manager_education)

        resolver = RemakeBalancedStaffGrowthResolver(roster, rng=random.Random(0))
        resolver.resolve_opportunity(opportunity)

        self.assertEqual(roster.staff_member("worker").skill_value(StaffSkill.CLEANING), 6)


if __name__ == "__main__":
    unittest.main()
