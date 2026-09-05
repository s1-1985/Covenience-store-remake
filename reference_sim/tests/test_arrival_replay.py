import unittest

from conveni_sim.arrival_replay import ObservedArrivalReplayer
from conveni_sim.arrival_schedule import ExplicitArrivalSchedule, ScheduledCustomerArrival
from conveni_sim.operating_time import SubdayClock
from conveni_sim.store_grid import GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class ExplicitArrivalReplayTests(unittest.TestCase):
    def test_schedule_only_emits_arrivals_due_at_current_game_time(self):
        schedule = ExplicitArrivalSchedule(
            (
                ScheduledCustomerArrival(10, "c1", GridPoint(0, 0), GridPoint(2, 2)),
                ScheduledCustomerArrival(20, "c2", GridPoint(0, 1), GridPoint(2, 1)),
            )
        )
        clock = SubdayClock()
        self.assertEqual(schedule.pop_due(clock), ())
        clock.advance_minutes(10)
        self.assertEqual(tuple(a.customer_id for a in schedule.pop_due(clock)), ("c1",))
        self.assertEqual(schedule.pending_count, 1)
        clock.advance_minutes(10)
        self.assertEqual(tuple(a.customer_id for a in schedule.pop_due(clock)), ("c2",))
        self.assertTrue(schedule.complete)

    def test_duplicate_customer_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            ExplicitArrivalSchedule(
                (
                    ScheduledCustomerArrival(1, "same", GridPoint(0, 0), GridPoint(1, 1)),
                    ScheduledCustomerArrival(2, "same", GridPoint(0, 1), GridPoint(1, 0)),
                )
            )

    def test_replayer_spawns_due_customer_without_demand_formula(self):
        runtime = StoreRuntimeHarness(
            StoreGrid(3, 3),
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(),
        )
        schedule = ExplicitArrivalSchedule(
            (
                ScheduledCustomerArrival(
                    8,
                    "observed-c1",
                    GridPoint(0, 0),
                    GridPoint(2, 2),
                ),
            )
        )
        replay = ObservedArrivalReplayer(runtime, schedule)

        self.assertEqual(replay.emit_due().spawned_customer_ids, ())
        runtime.advance_game_minutes(8)
        result = replay.emit_due()

        self.assertEqual(result.spawned_customer_ids, ("observed-c1",))
        self.assertEqual(runtime.customers.customer("observed-c1").customer_id, "observed-c1")
        self.assertTrue(schedule.complete)

    def test_late_polling_emits_all_overdue_arrivals_in_order(self):
        clock = SubdayClock()
        schedule = ExplicitArrivalSchedule(
            (
                ScheduledCustomerArrival(5, "a", GridPoint(0, 0), GridPoint(1, 1)),
                ScheduledCustomerArrival(7, "b", GridPoint(0, 1), GridPoint(1, 0)),
            )
        )
        clock.advance_minutes(10)
        due = schedule.pop_due(clock)
        self.assertEqual(tuple(a.customer_id for a in due), ("a", "b"))


if __name__ == "__main__":
    unittest.main()
