import unittest

from conveni_sim.checkout_anger_penalty import (
    CHECKOUT_ANGER_AFFECTED_SKILLS,
    CHECKOUT_ANGER_SKILL_DELTA,
    CheckoutAngerPenaltyRuntime,
)
from conveni_sim.staff import StaffSkill, StoreStaffRoster


class CheckoutAngerPenaltyTests(unittest.TestCase):
    def make_roster(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            stamina_max=10,
            runtime_skills={
                StaffSkill.EDUCATION: 70,
                StaffSkill.REGISTER: 20,
                StaffSkill.REPLENISHMENT: 30,
                StaffSkill.SECURITY: 40,
                StaffSkill.CLEANING: 50,
                StaffSkill.SERVICE: 60,
            },
        )
        return roster

    def minimums(self, value=0):
        return {skill: value for skill in CHECKOUT_ANGER_AFFECTED_SKILLS}

    def test_record_captures_minus_two_event_without_mutating_skills(self):
        roster = self.make_roster()
        runtime = CheckoutAngerPenaltyRuntime(roster)
        before = dict(roster.staff_member("s1").runtime_skills)

        event = runtime.record("s1")

        self.assertEqual(event.delta, CHECKOUT_ANGER_SKILL_DELTA)
        self.assertEqual(event.delta, -2)
        self.assertFalse(event.resolved)
        self.assertEqual(dict(roster.staff_member("s1").runtime_skills), before)
        self.assertEqual(runtime.unresolved_events, (event,))

    def test_resolution_applies_minus_two_to_only_recovered_affected_skills(self):
        roster = self.make_roster()
        runtime = CheckoutAngerPenaltyRuntime(roster)
        event = runtime.record("s1")

        runtime.resolve(event.sequence, minimum_by_skill=self.minimums())

        staff = roster.staff_member("s1")
        self.assertEqual(staff.skill_value(StaffSkill.REGISTER), 18)
        self.assertEqual(staff.skill_value(StaffSkill.REPLENISHMENT), 28)
        self.assertEqual(staff.skill_value(StaffSkill.SECURITY), 38)
        self.assertEqual(staff.skill_value(StaffSkill.CLEANING), 48)
        self.assertEqual(staff.skill_value(StaffSkill.SERVICE), 58)
        self.assertEqual(staff.skill_value(StaffSkill.EDUCATION), 70)
        self.assertEqual(staff.stamina_current, 10)
        self.assertTrue(event.resolved)
        self.assertEqual(runtime.unresolved_events, ())

    def test_explicit_minimum_controls_boundary_without_assuming_zero_floor(self):
        roster = self.make_roster()
        staff = roster.staff_member("s1")
        staff.runtime_skills[StaffSkill.REGISTER] = 5
        runtime = CheckoutAngerPenaltyRuntime(roster)
        event = runtime.record("s1")
        minimums = self.minimums()
        minimums[StaffSkill.REGISTER] = 4

        runtime.resolve(event.sequence, minimum_by_skill=minimums)

        self.assertEqual(staff.skill_value(StaffSkill.REGISTER), 4)

    def test_missing_minimum_rejects_without_partial_mutation(self):
        roster = self.make_roster()
        runtime = CheckoutAngerPenaltyRuntime(roster)
        event = runtime.record("s1")
        before = dict(roster.staff_member("s1").runtime_skills)
        incomplete = self.minimums()
        del incomplete[StaffSkill.SECURITY]

        with self.assertRaises(ValueError):
            runtime.resolve(event.sequence, minimum_by_skill=incomplete)

        self.assertEqual(dict(roster.staff_member("s1").runtime_skills), before)
        self.assertFalse(event.resolved)

    def test_unknown_affected_skill_rejects_without_partial_mutation(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={
                StaffSkill.REGISTER: 20,
                StaffSkill.REPLENISHMENT: 30,
                StaffSkill.CLEANING: 50,
                StaffSkill.SERVICE: 60,
            },
        )
        runtime = CheckoutAngerPenaltyRuntime(roster)
        event = runtime.record("s1")
        before = dict(roster.staff_member("s1").runtime_skills)

        with self.assertRaises(ValueError):
            runtime.resolve(event.sequence, minimum_by_skill=self.minimums())

        self.assertEqual(dict(roster.staff_member("s1").runtime_skills), before)
        self.assertFalse(event.resolved)

    def test_stale_event_rejects_atomically(self):
        roster = self.make_roster()
        runtime = CheckoutAngerPenaltyRuntime(roster)
        event = runtime.record("s1")
        staff = roster.staff_member("s1")
        staff.runtime_skills[StaffSkill.CLEANING] = 51
        before = dict(staff.runtime_skills)

        with self.assertRaises(ValueError):
            runtime.resolve(event.sequence, minimum_by_skill=self.minimums())

        self.assertEqual(dict(staff.runtime_skills), before)
        self.assertFalse(event.resolved)


if __name__ == "__main__":
    unittest.main()
