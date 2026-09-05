import unittest

from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.traffic import AgentStatus, CongestionPolicy, DynamicTrafficHarness


class DynamicTrafficTests(unittest.TestCase):
    def test_agents_cannot_start_on_same_cell(self):
        harness = DynamicTrafficHarness(StoreGrid(3, 3))
        harness.add_agent("a", GridPoint(0, 0))
        with self.assertRaises(ValueError):
            harness.add_agent("b", GridPoint(0, 0))

    def test_two_agents_contending_for_same_cell_both_wait(self):
        harness = DynamicTrafficHarness(StoreGrid(3, 2))
        agent_a = harness.add_agent("a", GridPoint(0, 0))
        agent_b = harness.add_agent("b", GridPoint(2, 0))
        harness.set_point_goal("a", GridPoint(1, 0))
        harness.set_point_goal("b", GridPoint(1, 0))

        result = harness.tick()

        self.assertEqual(set(result.blocked), {"a", "b"})
        self.assertEqual(agent_a.position, GridPoint(0, 0))
        self.assertEqual(agent_b.position, GridPoint(2, 0))

    def test_blocker_can_make_a_one_subcell_corridor_unreachable(self):
        grid = StoreGrid(3, 1)
        grid.set_static_blocked(GridPoint(x, 1) for x in range(grid.width_subcells))
        harness = DynamicTrafficHarness(grid)
        agent = harness.add_agent("a", GridPoint(0, 0))
        harness.add_agent("blocker", GridPoint(1, 0))

        harness.set_point_goal("a", GridPoint(3, 0))
        self.assertEqual(agent.status, AgentStatus.UNREACHABLE)

        harness.remove_agent("blocker")
        harness.set_point_goal("a", GridPoint(3, 0))
        self.assertEqual(agent.status, AgentStatus.MOVING)
        harness.tick()
        self.assertEqual(agent.position, GridPoint(1, 0))

    def test_fixture_goal_ends_on_interaction_edge(self):
        grid = StoreGrid(4, 4)
        grid.place_fixture(
            instance_id="shelf-1",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        harness = DynamicTrafficHarness(grid)
        agent = harness.add_agent("a", GridPoint(0, 0))
        harness.set_fixture_goal("a", "shelf-1")

        for _ in range(20):
            harness.tick()
            if agent.status is AgentStatus.ARRIVED:
                break

        self.assertEqual(agent.status, AgentStatus.ARRIVED)
        self.assertIn(agent.position, grid.interaction_cells("shelf-1"))
        self.assertNotIn(agent.position, grid.placements[0].occupied_cells)

    def test_reroute_policy_can_avoid_a_new_dynamic_blocker(self):
        harness = DynamicTrafficHarness(
            StoreGrid(4, 3),
            policy=CongestionPolicy(reroute_after_blocked_ticks=1),
        )
        agent = harness.add_agent("a", GridPoint(0, 0))
        harness.set_point_goal("a", GridPoint(5, 0))
        harness.add_agent("blocker", GridPoint(1, 0))

        result = harness.tick()

        self.assertIn("a", result.blocked)
        self.assertEqual(agent.status, AgentStatus.MOVING)
        self.assertGreaterEqual(len(agent.path), 2)
        self.assertNotEqual(agent.path[1], GridPoint(1, 0))

    def test_default_policy_does_not_invent_a_reroute_threshold(self):
        harness = DynamicTrafficHarness(StoreGrid(3, 2))
        agent = harness.add_agent("a", GridPoint(0, 0))
        harness.set_point_goal("a", GridPoint(4, 0))
        harness.add_agent("blocker", GridPoint(1, 0))

        harness.tick()

        self.assertEqual(agent.status, AgentStatus.BLOCKED)
        self.assertEqual(agent.blocked_ticks, 1)

    def test_wait_counter_accumulates_while_blocked(self):
        harness = DynamicTrafficHarness(StoreGrid(3, 2))
        agent = harness.add_agent("a", GridPoint(0, 0))
        harness.set_point_goal("a", GridPoint(4, 0))
        harness.add_agent("blocker", GridPoint(1, 0))

        harness.tick()
        harness.tick()

        self.assertEqual(agent.total_wait_ticks, 2)
        self.assertEqual(agent.blocked_ticks, 2)

    def test_unreachable_when_static_layout_has_no_route(self):
        grid = StoreGrid(3, 2)
        grid.set_static_blocked(GridPoint(1, y) for y in range(grid.height_subcells))
        harness = DynamicTrafficHarness(grid)
        agent = harness.add_agent("a", GridPoint(0, 0))

        harness.set_point_goal("a", GridPoint(4, 0))

        self.assertEqual(agent.status, AgentStatus.UNREACHABLE)


if __name__ == "__main__":
    unittest.main()
