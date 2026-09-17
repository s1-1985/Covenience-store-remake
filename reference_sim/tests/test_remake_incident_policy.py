import random
import unittest

from conveni_sim.remake_incident_policy import RemakeBalancedIncidentPolicy
from conveni_sim.store_events import FireOrRobberyRisk
from conveni_sim.store_value import NO_SECURITY_FACILITY_COVERAGE, SecurityFacilityCoverage


class RemakeIncidentPolicyFireOrRobberyTests(unittest.TestCase):
    def test_no_risk_factors_means_never(self):
        policy = RemakeBalancedIncidentPolicy(
            fire_or_robbery_base_probability=1.0, rng=random.Random(0)
        )
        protected = FireOrRobberyRisk(
            security_coverage=SecurityFacilityCoverage(police_box_area_tiles=1),
            store_popularity=10,
            store_security_value=50,
        )
        self.assertFalse(policy.fire_or_robbery_occurs_today(protected))

    def test_zero_probability_never_occurs_even_when_eligible(self):
        policy = RemakeBalancedIncidentPolicy(
            fire_or_robbery_base_probability=0.0, rng=random.Random(0)
        )
        unprotected = FireOrRobberyRisk(
            security_coverage=NO_SECURITY_FACILITY_COVERAGE,
            store_popularity=10,
            store_security_value=50,
        )
        for _ in range(50):
            self.assertFalse(policy.fire_or_robbery_occurs_today(unprotected))

    def test_certain_probability_always_occurs_when_eligible(self):
        policy = RemakeBalancedIncidentPolicy(
            fire_or_robbery_base_probability=1.0, rng=random.Random(0)
        )
        unprotected = FireOrRobberyRisk(
            security_coverage=NO_SECURITY_FACILITY_COVERAGE,
            store_popularity=10,
            store_security_value=50,
        )
        self.assertTrue(policy.fire_or_robbery_occurs_today(unprotected))

    def test_popularity_exceeding_security_increases_rate_over_many_rolls(self):
        # Both are unprotected (risk_factors_present True via is_unprotected
        # either way); only high_risk also trips popularity_exceeds_security,
        # which should apply the extra multiplier and fire more often.
        low_risk = FireOrRobberyRisk(
            security_coverage=NO_SECURITY_FACILITY_COVERAGE,
            store_popularity=10,
            store_security_value=90,
        )
        high_risk = FireOrRobberyRisk(
            security_coverage=NO_SECURITY_FACILITY_COVERAGE,
            store_popularity=90,
            store_security_value=10,
        )
        policy_low = RemakeBalancedIncidentPolicy(fire_or_robbery_base_probability=0.3, rng=random.Random(1))
        policy_high = RemakeBalancedIncidentPolicy(fire_or_robbery_base_probability=0.3, rng=random.Random(1))

        low_count = sum(1 for _ in range(300) if policy_low.fire_or_robbery_occurs_today(low_risk))
        high_count = sum(1 for _ in range(300) if policy_high.fire_or_robbery_occurs_today(high_risk))

        self.assertLess(low_count, high_count)


class RemakeIncidentPolicyShopliftingTests(unittest.TestCase):
    def test_not_eligible_means_never(self):
        policy = RemakeBalancedIncidentPolicy(shoplifting_base_probability=1.0, rng=random.Random(0))
        self.assertFalse(policy.shoplifting_occurs_today(customer_manner_value=50, store_security_value=80))

    def test_eligible_and_certain_probability_occurs(self):
        policy = RemakeBalancedIncidentPolicy(shoplifting_base_probability=1.0, rng=random.Random(0))
        self.assertTrue(policy.shoplifting_occurs_today(customer_manner_value=80, store_security_value=50))

    def test_eligible_but_zero_probability_never_occurs(self):
        policy = RemakeBalancedIncidentPolicy(shoplifting_base_probability=0.0, rng=random.Random(0))
        for _ in range(50):
            self.assertFalse(
                policy.shoplifting_occurs_today(customer_manner_value=80, store_security_value=50)
            )


if __name__ == "__main__":
    unittest.main()
