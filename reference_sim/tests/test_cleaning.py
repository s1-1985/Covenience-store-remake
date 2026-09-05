import unittest

from conveni_sim.cleaning import DirtGenerationPolicy, StoreCleaningRuntime
from conveni_sim.staff import StaffCondition, StaffTask, StoreStaffRoster
from conveni_sim.store_grid import GridPoint, StoreGrid


class CleaningRuntimeTests(unittest.TestCase):
    def test_dirt_only_appears_from_explicit_events_by_default(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        self.assertEqual(cleaning.dirty_cells, frozenset())
        cleaning.mark_dirty((GridPoint(1, 1),))
        self.assertEqual(cleaning.dirty_cells, frozenset({GridPoint(1, 1)}))

    def test_duplicate_dirt_event_does_not_duplicate_cell(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        first = cleaning.mark_dirty((GridPoint(1, 1),))
        second = cleaning.mark_dirty((GridPoint(1, 1),))
        self.assertEqual(first, (GridPoint(1, 1),))
        self.assertEqual(second, ())
        self.assertEqual(len(cleaning.dirty_cells), 1)

    def test_clean_removes_only_currently_dirty_cells(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        cleaning.mark_dirty((GridPoint(1, 1), GridPoint(2, 1)))
        result = cleaning.clean((GridPoint(1, 1), GridPoint(5, 5)))
        self.assertEqual(result.cleaned_cells, (GridPoint(1, 1),))
        self.assertEqual(cleaning.dirty_cells, frozenset({GridPoint(2, 1)}))

    def test_successful_staff_clean_records_one_work_event(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        cleaning.mark_dirty((GridPoint(1, 1), GridPoint(2, 1)))
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")
        roster.assign_task("s1", StaffTask.CLEAN, target_id="floor")

        cleaning.clean(
            (GridPoint(1, 1), GridPoint(2, 1)),
            staff_roster=roster,
            staff_id="s1",
        )

        self.assertEqual(staff.completed_count(StaffTask.CLEAN), 1)

    def test_cleaning_no_dirt_does_not_fake_work_event(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")
        cleaning.clean(
            (GridPoint(1, 1),),
            staff_roster=roster,
            staff_id="s1",
        )
        self.assertEqual(staff.completed_count(StaffTask.CLEAN), 0)

    def test_explicit_stamina_cost_can_exhaust_cleaning_staff(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        cleaning.mark_dirty((GridPoint(1, 1),))
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=1)
        roster.assign_task("s1", StaffTask.CLEAN, target_id="floor")

        cleaning.clean(
            (GridPoint(1, 1),),
            staff_roster=roster,
            staff_id="s1",
            stamina_cost=1,
            break_room_target_id="break-room",
        )

        self.assertEqual(staff.stamina_current, 0)
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)

    def test_default_policy_does_not_assume_ss_cleaning_100_rule(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        added = cleaning.mark_dirty(
            (GridPoint(1, 1),),
            store_cleaning_value=100,
        )
        self.assertEqual(added, (GridPoint(1, 1),))

    def test_ss_style_cleaning_100_suppression_can_be_enabled_explicitly(self):
        cleaning = StoreCleaningRuntime(
            StoreGrid(3, 3),
            dirt_policy=DirtGenerationPolicy(suppress_at_cleaning_value_or_above=100),
        )
        added = cleaning.mark_dirty(
            (GridPoint(1, 1),),
            store_cleaning_value=100,
        )
        self.assertEqual(added, ())
        self.assertEqual(cleaning.dirty_cells, frozenset())

    def test_configured_suppression_requires_cleaning_value(self):
        cleaning = StoreCleaningRuntime(
            StoreGrid(3, 3),
            dirt_policy=DirtGenerationPolicy(suppress_at_cleaning_value_or_above=100),
        )
        with self.assertRaises(ValueError):
            cleaning.mark_dirty((GridPoint(1, 1),))


if __name__ == "__main__":
    unittest.main()
