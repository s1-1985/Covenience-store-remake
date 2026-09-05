import unittest

from conveni_sim.staff import StaffCondition, StaffTask, StoreStaffRoster


class StaffStaminaTests(unittest.TestCase):
    def test_work_events_can_be_counted_without_inventing_stamina_cost(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        roster.record_completed_work("s1", StaffTask.REPLENISH)
        roster.record_completed_work("s1", StaffTask.CLEAN)

        self.assertEqual(staff.completed_count(StaffTask.REPLENISH), 2)
        self.assertEqual(staff.completed_count(StaffTask.CLEAN), 1)
        self.assertFalse(staff.stamina_tracking_enabled)
        self.assertIsNone(staff.stamina_current)

    def test_explicit_stamina_cost_can_trigger_return_to_break_room(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=3)
        roster.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")

        roster.record_completed_work(
            "s1",
            StaffTask.CHECKOUT,
            stamina_cost=3,
            break_room_target_id="break-room",
        )

        self.assertEqual(staff.stamina_current, 0)
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(staff.task, StaffTask.RETURN_TO_BREAK_ROOM)
        self.assertEqual(staff.target_id, "break-room")

    def test_unavailable_staff_cannot_be_assigned_new_work(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1", stamina_max=1)
        roster.consume_stamina("s1", 1, break_room_target_id="break-room")

        with self.assertRaises(ValueError):
            roster.assign_task("s1", StaffTask.REPLENISH, target_id="shelf")

    def test_rest_requires_break_room_arrival_then_full_recovery(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=5)
        roster.consume_stamina("s1", 5, break_room_target_id="break-room")
        roster.arrive_at_break_room("s1")

        self.assertEqual(staff.condition, StaffCondition.RESTING)
        self.assertEqual(staff.task, StaffTask.REST)

        roster.recover_stamina("s1", 2)
        self.assertEqual(staff.stamina_current, 2)
        self.assertEqual(staff.condition, StaffCondition.RESTING)
        self.assertEqual(staff.task, StaffTask.REST)

        roster.recover_stamina("s1", 10)
        self.assertEqual(staff.stamina_current, 5)
        self.assertEqual(staff.condition, StaffCondition.AVAILABLE)
        self.assertEqual(staff.task, StaffTask.IDLE)
        self.assertIsNone(staff.target_id)

    def test_release_to_idle_does_not_cancel_exhaustion_transition(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=1)
        roster.consume_stamina("s1", 1, break_room_target_id="break-room")
        roster.release_to_idle("s1")

        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(staff.task, StaffTask.RETURN_TO_BREAK_ROOM)

    def test_unknown_stamina_rejects_explicit_consumption_instead_of_guessing(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        with self.assertRaises(ValueError):
            roster.consume_stamina("s1", 1)

    def test_recovery_amount_is_explicit_and_must_be_positive(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1", stamina_max=1)
        roster.consume_stamina("s1", 1)
        roster.arrive_at_break_room("s1")
        with self.assertRaises(ValueError):
            roster.recover_stamina("s1", 0)


if __name__ == "__main__":
    unittest.main()
