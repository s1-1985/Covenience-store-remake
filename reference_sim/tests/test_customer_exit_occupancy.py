import unittest

from conveni_sim.customer import CustomerLifecycleHarness, CustomerState
from conveni_sim.store_grid import GridPoint, StoreGrid
from conveni_sim.traffic import DynamicTrafficHarness


class CustomerExitOccupancyTests(unittest.TestCase):
    def test_exited_customer_releases_shared_exit_cell_for_following_customer(self):
        traffic = DynamicTrafficHarness(StoreGrid(3, 3))
        customers = CustomerLifecycleHarness(traffic)
        exit_point = GridPoint(2, 0)

        customers.add_customer(
            "a",
            entry_point=GridPoint(0, 0),
            exit_point=exit_point,
        )
        customers.add_customer(
            "b",
            entry_point=GridPoint(0, 1),
            exit_point=exit_point,
        )

        for _ in range(10):
            customers.tick()
            if customers.customer("a").state is CustomerState.EXITED:
                break
        self.assertEqual(customers.customer("a").state, CustomerState.EXITED)
        with self.assertRaises(KeyError):
            traffic.agent("a")

        for _ in range(10):
            customers.tick()
            if customers.customer("b").state is CustomerState.EXITED:
                break
        self.assertEqual(customers.customer("b").state, CustomerState.EXITED)
        with self.assertRaises(KeyError):
            traffic.agent("b")

        # Historical sessions remain queryable even after their physical agents
        # have left the store occupancy map.
        self.assertEqual(len(customers.customers), 2)


if __name__ == "__main__":
    unittest.main()
