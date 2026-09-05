import unittest

from conveni_sim.staff import StaffSkill, StaffTask, StoreStaffRoster


class StaffGrowthOpportunityTests(unittest.TestCase):
    def test_checkout_replenish_and_clean_create_matching_growth_opportunities(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")

        roster.record_completed_work("s1", StaffTask.CHECKOUT)
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        roster.record_completed_work("s1", StaffTask.CLEAN)

        self.assertEqual(
            tuple(opportunity.skill for opportunity in roster.growth_opportunities),
            (
                StaffSkill.REGISTER,
                StaffSkill.REPLENISHMENT,
                StaffSkill.CLEANING,
            ),
        )
        self.assertEqual(
            tuple(opportunity.work_event_count for opportunity in roster.growth_opportunities),
            (1, 1, 1),
        )

    def test_growth_trigger_does_not_invent_unknown_skill_values(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")

        roster.record_completed_work("s1", StaffTask.CHECKOUT)
        opportunity = roster.growth_opportunities[-1]

        self.assertIsNone(opportunity.before_value)
        self.assertIsNone(opportunity.base_cap)
        self.assertIsNone(staff.skill_value(StaffSkill.REGISTER))
        self.assertFalse(opportunity.resolved)

    def test_subordinate_growth_snapshot_records_current_manager_education(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "manager",
            manager=True,
            runtime_skills={StaffSkill.EDUCATION: 95},
        )
        roster.add_staff(
            "worker",
            runtime_skills={StaffSkill.REGISTER: 12},
            base_skill_caps={StaffSkill.REGISTER: 80},
        )

        roster.record_completed_work("worker", StaffTask.CHECKOUT)
        opportunity = roster.growth_opportunities[-1]

        self.assertEqual(opportunity.manager_staff_id, "manager")
        self.assertEqual(opportunity.manager_education, 95)
        self.assertEqual(opportunity.before_value, 12)
        self.assertEqual(opportunity.base_cap, 80)

    def test_manager_own_work_does_not_treat_manager_as_own_supervisor(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "manager",
            manager=True,
            runtime_skills={
                StaffSkill.EDUCATION: 90,
                StaffSkill.CLEANING: 20,
            },
        )

        roster.record_completed_work("manager", StaffTask.CLEAN)
        opportunity = roster.growth_opportunities[-1]

        self.assertIsNone(opportunity.manager_staff_id)
        self.assertIsNone(opportunity.manager_education)

    def test_explicit_resolution_updates_skill_without_inventing_delta(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.REPLENISHMENT: 30},
            base_skill_caps={StaffSkill.REPLENISHMENT: 70},
        )
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        opportunity = roster.growth_opportunities[-1]

        resolved = roster.resolve_growth_opportunity(
            opportunity.sequence,
            after_value=31,
        )

        self.assertTrue(resolved.resolved)
        self.assertEqual(resolved.resolved_after, 31)
        self.assertEqual(staff.skill_value(StaffSkill.REPLENISHMENT), 31)
        self.assertEqual(roster.unresolved_growth_opportunities, ())

    def test_normal_work_resolution_cannot_exceed_known_base_cap(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.CLEANING: 49},
            base_skill_caps={StaffSkill.CLEANING: 50},
        )
        roster.record_completed_work("s1", StaffTask.CLEAN)
        sequence = roster.growth_opportunities[-1].sequence

        with self.assertRaises(ValueError):
            roster.resolve_growth_opportunity(sequence, after_value=51)

    def test_growth_opportunity_cannot_be_resolved_twice(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.REGISTER: 10},
            base_skill_caps={StaffSkill.REGISTER: 20},
        )
        roster.record_completed_work("s1", StaffTask.CHECKOUT)
        sequence = roster.growth_opportunities[-1].sequence
        roster.resolve_growth_opportunity(sequence, after_value=11)

        with self.assertRaises(ValueError):
            roster.resolve_growth_opportunity(sequence, after_value=12)

    def test_runtime_skill_can_start_above_base_cap_for_prior_event_boosts(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff(
            "s1",
            runtime_skills={StaffSkill.SERVICE: 82},
            base_skill_caps={StaffSkill.SERVICE: 75},
        )

        self.assertEqual(staff.skill_value(StaffSkill.SERVICE), 82)
        self.assertEqual(staff.skill_cap(StaffSkill.SERVICE), 75)


if __name__ == "__main__":
    unittest.main()
