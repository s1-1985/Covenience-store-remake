import unittest

from conveni_sim.cleaning import (
    DirtGenerationPolicy,
    InteriorEditDirtResetPolicy,
    StoreCleaningRuntime,
)
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

    def test_interior_edit_does_not_clear_dirt_without_explicit_compatibility_policy(self):
        cleaning = StoreCleaningRuntime(StoreGrid(3, 3))
        cleaning.mark_dirty((GridPoint(2, 1), GridPoint(1, 1)))

        result = cleaning.enter_interior_edit(is_closed_for_business=True)

        self.assertFalse(result.reset_applied)
        self.assertEqual(result.cleared_cells, ())
        self.assertEqual(
            cleaning.dirty_cells,
            frozenset({GridPoint(1, 1), GridPoint(2, 1)}),
        )

    def test_observed_closed_store_interior_edit_reset_can_be_enabled_explicitly(self):
        cleaning = StoreCleaningRuntime(
            StoreGrid(3, 3),
            interior_edit_policy=InteriorEditDirtResetPolicy(
                clear_floor_dirt_when_closed=True,
            ),
        )
        cleaning.mark_dirty((GridPoint(2, 1), GridPoint(1, 1)))

        result = cleaning.enter_interior_edit(is_closed_for_business=True)

        self.assertTrue(result.reset_applied)
        self.assertEqual(
            result.cleared_cells,
            (GridPoint(1, 1), GridPoint(2, 1)),
        )
        self.assertEqual(result.dirty_cells_remaining, 0)
        self.assertEqual(cleaning.dirty_cells, frozenset())
        self.assertEqual(cleaning.history, ())
        self.assertEqual(cleaning.interior_edit_history, (result,))

    def test_interior_edit_reset_policy_does_not_clear_while_store_is_open(self):
        cleaning = StoreCleaningRuntime(
            StoreGrid(3, 3),
            interior_edit_policy=InteriorEditDirtResetPolicy(
                clear_floor_dirt_when_closed=True,
            ),
        )
        cleaning.mark_dirty((GridPoint(1, 1),))

        result = cleaning.enter_interior_edit(is_closed_for_business=False)

        self.assertFalse(result.reset_applied)
        self.assertEqual(result.cleared_cells, ())
        self.assertEqual(cleaning.dirty_cells, frozenset({GridPoint(1, 1)}))

    def test_interior_edit_reset_does_not_record_staff_cleaning_work(self):
        cleaning = StoreCleaningRuntime(
            StoreGrid(3, 3),
            interior_edit_policy=InteriorEditDirtResetPolicy(
                clear_floor_dirt_when_closed=True,
            ),
        )
        cleaning.mark_dirty((GridPoint(1, 1),))
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")

        cleaning.enter_interior_edit(is_closed_for_business=True)

        self.assertEqual(staff.completed_count(StaffTask.CLEAN), 0)


if __name__ == "__main__":
    unittest.main()
