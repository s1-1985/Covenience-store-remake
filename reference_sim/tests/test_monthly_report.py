import unittest

from conveni_sim.monthly_report import (
    MonthlyReportRuntime,
    MonthlyReportValues,
    MonthlySalesThresholdNotification,
)


class MonthlyReportRuntimeTests(unittest.TestCase):
    def test_report_delta_matches_observed_august_to_september_arithmetic(self):
        runtime = MonthlyReportRuntime()
        august = MonthlyReportValues(
            profit_loss_yen=-837_328,
            other_expenses_yen=500_000,
            town_population=2_338,
        )
        september = MonthlyReportValues(
            profit_loss_yen=-889_128,
            other_expenses_yen=6_200_000,
            town_population=2_401,
        )

        report = runtime.record_report(
            year=1,
            month=9,
            values=september,
            previous_values=august,
        )

        self.assertEqual(report.delta.profit_loss_yen, -51_800)
        self.assertEqual(report.delta.other_expenses_yen, 5_700_000)
        self.assertEqual(report.delta.town_population, 63)

    def test_unknown_report_fields_remain_unknown_instead_of_becoming_zero(self):
        runtime = MonthlyReportRuntime()
        report = runtime.record_report(
            year=1,
            month=10,
            values=MonthlyReportValues(town_population=2_401),
            previous_values=MonthlyReportValues(town_population=None),
        )

        self.assertIsNone(report.delta.profit_loss_yen)
        self.assertIsNone(report.delta.other_expenses_yen)
        self.assertIsNone(report.delta.town_population)

    def test_four_million_notification_is_recorded_explicitly_for_one_branch(self):
        runtime = MonthlyReportRuntime()
        notification = MonthlySalesThresholdNotification(
            store_id="branch-2",
            report_year=1,
            report_month=9,
            threshold_yen=4_000_000,
            previous_month_sales_yen=4_000_001,
        )

        runtime.record_sales_threshold_notification(notification)

        self.assertEqual(runtime.sales_notifications, (notification,))

    def test_threshold_record_does_not_infer_other_crossed_tiers(self):
        runtime = MonthlyReportRuntime()
        runtime.record_sales_threshold_notification(
            MonthlySalesThresholdNotification(
                store_id="branch-2",
                report_year=1,
                report_month=9,
                threshold_yen=4_000_000,
                previous_month_sales_yen=5_000_000,
            )
        )

        self.assertEqual(len(runtime.sales_notifications), 1)
        self.assertEqual(runtime.sales_notifications[0].threshold_yen, 4_000_000)

    def test_known_sales_must_strictly_exceed_observed_threshold_wording(self):
        with self.assertRaises(ValueError):
            MonthlySalesThresholdNotification(
                store_id="branch-2",
                report_year=1,
                report_month=9,
                threshold_yen=4_000_000,
                previous_month_sales_yen=4_000_000,
            )


if __name__ == "__main__":
    unittest.main()
