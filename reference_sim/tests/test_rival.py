import unittest

from conveni_sim.rival import (
    RivalChainRuntime,
    RivalChainState,
    RivalStoreRole,
    RivalStoreState,
)


class RivalChainRuntimeTests(unittest.TestCase):
    def test_closed_branch_can_be_replaced_at_another_location_only_by_explicit_open(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "hq",
            role=RivalStoreRole.HEADQUARTERS,
            location_id="parcel-hq",
            source="scenario setup",
        )
        rival.open_store(
            "branch-1",
            role=RivalStoreRole.BRANCH,
            location_id="parcel-old",
            source="observed branch",
        )

        closed = rival.close_store("branch-1", source="observed closure")
        self.assertEqual(closed.state, RivalStoreState.CLOSED)
        self.assertEqual({store.store_id for store in rival.active_stores}, {"hq"})

        replacement = rival.open_store(
            "branch-2",
            role=RivalStoreRole.BRANCH,
            location_id="parcel-new",
            source="observed replacement opening",
        )
        self.assertEqual(replacement.location_id, "parcel-new")
        self.assertEqual(
            {store.store_id for store in rival.active_stores},
            {"hq", "branch-2"},
        )

    def test_branch_acquisition_is_recorded_without_price_formula(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "hq",
            role=RivalStoreRole.HEADQUARTERS,
            location_id="parcel-hq",
            source="scenario setup",
        )
        rival.open_store(
            "branch-1",
            role=RivalStoreRole.BRANCH,
            location_id="parcel-b",
            source="scenario setup",
        )

        acquired = rival.acquire_branch(
            "branch-1",
            acquired_by="player-chain",
            source="observed acquisition",
        )

        self.assertEqual(acquired.state, RivalStoreState.ACQUIRED)
        self.assertEqual(acquired.acquired_by, "player-chain")
        self.assertEqual(rival.state, RivalChainState.ACTIVE)

    def test_headquarters_acquisition_is_rejected(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "hq",
            role=RivalStoreRole.HEADQUARTERS,
            location_id="parcel-hq",
            source="scenario setup",
        )

        with self.assertRaises(ValueError):
            rival.acquire_branch(
                "hq",
                acquired_by="player-chain",
                source="invalid acquisition attempt",
            )

    def test_chain_becomes_extinct_only_after_no_active_store_remains(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "hq",
            role=RivalStoreRole.HEADQUARTERS,
            location_id="parcel-hq",
            source="scenario setup",
        )
        rival.open_store(
            "branch-1",
            role=RivalStoreRole.BRANCH,
            location_id="parcel-b",
            source="scenario setup",
        )
        rival.acquire_branch(
            "branch-1",
            acquired_by="player-chain",
            source="observed acquisition",
        )

        self.assertEqual(rival.state, RivalChainState.ACTIVE)
        rival.close_store("hq", source="observed headquarters closure")
        self.assertEqual(rival.state, RivalChainState.EXTINCT)

    def test_runtime_never_closes_store_from_unresolved_profit_information(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "branch-1",
            role=RivalStoreRole.BRANCH,
            location_id="parcel-b",
            source="scenario setup",
        )

        # There is intentionally no profit/loss update API that implicitly closes
        # a store. Closure criteria remain outside this runtime until recovered.
        self.assertEqual(rival.store("branch-1").state, RivalStoreState.ACTIVE)
        self.assertEqual(len(rival.history), 1)

    def test_duplicate_store_ids_and_second_headquarters_are_rejected(self):
        rival = RivalChainRuntime("rival-a")
        rival.open_store(
            "hq",
            role=RivalStoreRole.HEADQUARTERS,
            location_id="parcel-hq",
            source="scenario setup",
        )

        with self.assertRaises(ValueError):
            rival.open_store(
                "hq",
                role=RivalStoreRole.BRANCH,
                location_id="parcel-other",
                source="duplicate",
            )
        with self.assertRaises(ValueError):
            rival.open_store(
                "hq-2",
                role=RivalStoreRole.HEADQUARTERS,
                location_id="parcel-hq-2",
                source="second headquarters",
            )


if __name__ == "__main__":
    unittest.main()
