import unittest

from conveni_sim.rival import RivalStoreRole
from conveni_sim.scenario_initial_state import (
    FirstTitlePlatform,
    FirstTitleScenario,
    RivalStoreSeed,
    build_rival_chain_from_scenario_seeds,
    rival_topology_evidence,
    validate_rival_seeds,
)


class ScenarioInitialRivalStateTests(unittest.TestCase):
    def test_ps_middle_recovers_exact_hq_plus_two_branch_topology(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.MIDDLE,
        )

        self.assertEqual(evidence.exact_store_count, 3)
        self.assertEqual(
            sorted(role.value for role in evidence.exact_roles or ()),
            ["branch", "branch", "headquarters"],
        )
        self.assertIsNone(evidence.revision)

    def test_ps_advanced_recovers_headquarters_only(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.ADVANCED,
        )

        self.assertEqual(evidence.exact_store_count, 1)
        self.assertEqual(evidence.exact_roles, (RivalStoreRole.HEADQUARTERS,))

    def test_ps_beginner_requires_a_branch_without_inventing_total_count(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.BEGINNER,
        )

        self.assertIsNone(evidence.exact_store_count)
        self.assertIsNone(evidence.exact_roles)
        self.assertEqual(evidence.required_roles, (RivalStoreRole.BRANCH,))

        validate_rival_seeds(
            evidence,
            (
                RivalStoreSeed("branch-1", RivalStoreRole.BRANCH, "parcel-b"),
                RivalStoreSeed("hq", RivalStoreRole.HEADQUARTERS, "parcel-hq"),
            ),
        )

        with self.assertRaises(ValueError):
            validate_rival_seeds(
                evidence,
                (RivalStoreSeed("hq", RivalStoreRole.HEADQUARTERS, "parcel-hq"),),
            )

    def test_saturn_does_not_inherit_playstation_topology(self):
        for scenario in FirstTitleScenario:
            evidence = rival_topology_evidence(FirstTitlePlatform.SEGA_SATURN, scenario)
            self.assertIsNone(evidence.exact_store_count)
            self.assertIsNone(evidence.exact_roles)
            self.assertEqual(evidence.required_roles, ())

    def test_middle_rejects_wrong_role_count_before_runtime_creation(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.MIDDLE,
        )
        seeds = (
            RivalStoreSeed("hq", RivalStoreRole.HEADQUARTERS, "parcel-hq"),
            RivalStoreSeed("branch-1", RivalStoreRole.BRANCH, "parcel-b1"),
        )

        with self.assertRaises(ValueError):
            build_rival_chain_from_scenario_seeds(
                "rival-a",
                evidence=evidence,
                seeds=seeds,
            )

    def test_concrete_locations_remain_external_data(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.MIDDLE,
        )
        seeds = (
            RivalStoreSeed("rival-hq", RivalStoreRole.HEADQUARTERS, "observed-parcel-7"),
            RivalStoreSeed("rival-2", RivalStoreRole.BRANCH, "observed-parcel-12"),
            RivalStoreSeed("rival-3", RivalStoreRole.BRANCH, "observed-parcel-18"),
        )

        chain = build_rival_chain_from_scenario_seeds(
            "rival-a",
            evidence=evidence,
            seeds=seeds,
            source="PS middle observed setup",
        )

        self.assertEqual(len(chain.active_stores), 3)
        self.assertEqual(chain.store("rival-hq").location_id, "observed-parcel-7")
        self.assertEqual(chain.history[0].source, "PS middle observed setup")

    def test_exact_topology_validation_is_order_independent(self):
        evidence = rival_topology_evidence(
            FirstTitlePlatform.PLAYSTATION,
            FirstTitleScenario.MIDDLE,
        )
        validate_rival_seeds(
            evidence,
            (
                RivalStoreSeed("branch-1", RivalStoreRole.BRANCH, "parcel-b1"),
                RivalStoreSeed("hq", RivalStoreRole.HEADQUARTERS, "parcel-hq"),
                RivalStoreSeed("branch-2", RivalStoreRole.BRANCH, "parcel-b2"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
