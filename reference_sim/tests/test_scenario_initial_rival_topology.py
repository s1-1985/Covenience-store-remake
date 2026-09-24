import unittest

from conveni_sim.rival import RivalChainState, RivalStoreRole, RivalStoreState
from conveni_sim.scenario_initial_rival_topology import seed_rival_chain_for_scenario


class ScenarioInitialRivalTopologyTests(unittest.TestCase):
    def test_beginner_has_no_confirmed_role_order_to_seed_from(self):
        self.assertIsNone(seed_rival_chain_for_scenario("beginner"))

    def test_intermediate_seeds_one_headquarters_and_two_branches(self):
        runtime = seed_rival_chain_for_scenario("intermediate")

        self.assertEqual(runtime.state, RivalChainState.ACTIVE)
        roles = sorted(store.role.value for store in runtime.active_stores)
        self.assertEqual(roles, ["branch", "branch", "headquarters"])
        for store in runtime.active_stores:
            self.assertEqual(store.state, RivalStoreState.ACTIVE)

    def test_advanced_seeds_only_a_headquarters(self):
        runtime = seed_rival_chain_for_scenario("advanced")

        stores = runtime.active_stores
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].role, RivalStoreRole.HEADQUARTERS)

    def test_seeded_stores_can_still_close_and_reopen_like_any_other_rival_store(self):
        runtime = seed_rival_chain_for_scenario("intermediate")
        branch_id = next(
            store.store_id for store in runtime.active_stores if store.role is RivalStoreRole.BRANCH
        )

        runtime.close_store(branch_id, source="test: player price war")
        self.assertEqual(runtime.store(branch_id).state, RivalStoreState.CLOSED)

    def test_unknown_scenario_id_raises(self):
        with self.assertRaises(KeyError):
            seed_rival_chain_for_scenario("nonexistent")


if __name__ == "__main__":
    unittest.main()
