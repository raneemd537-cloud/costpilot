import unittest
from decimal import Decimal

from app.calculations import allocate_shared_expense, calculate_product


class CalculationTests(unittest.TestCase):
    def test_total_cost_profit_margins_break_even_and_targets(self):
        result = calculate_product(
            unit_cost="10", quantity=3, expenses=["3"], selling_price="20",
            discount_percent="10", target_profit_amount="12",
            target_profit_percent="20", target_basis="markup",
        )
        self.assertEqual(result["purchase_total"], Decimal("30.00"))
        self.assertEqual(result["total_cost"], Decimal("33.00"))
        self.assertEqual(result["final_unit_price"], Decimal("18.00"))
        self.assertEqual(result["revenue"], Decimal("54.00"))
        self.assertEqual(result["profit"], Decimal("21.00"))
        self.assertEqual(result["margin_percent"], Decimal("38.89"))
        self.assertEqual(result["return_on_cost_percent"], Decimal("63.64"))
        self.assertEqual(result["break_even_unit_price"], Decimal("12.22"))
        self.assertEqual(result["target_fixed_unit_price"], Decimal("16.67"))
        self.assertEqual(result["target_percent_unit_price"], Decimal("14.67"))

    def test_below_cost_and_zero_revenue_are_financial_losses(self):
        result = calculate_product("8", 2, [], "0", "0")
        self.assertEqual(result["profit"], Decimal("-16.00"))
        self.assertEqual(result["margin_percent"], None)
        self.assertEqual(result["status"], "loss")

    def test_shared_allocation_reconciles_cents_by_selected_basis(self):
        allocations = allocate_shared_expense("1.00", [
            {"id": "a", "quantity": 1, "purchase_value": "1", "weight": "1"},
            {"id": "b", "quantity": 2, "purchase_value": "2", "weight": "2"},
        ], "quantity")
        self.assertEqual(allocations, {"a": Decimal("0.33"), "b": Decimal("0.67")})
        self.assertEqual(sum(allocations.values()), Decimal("1.00"))

    def test_unavailable_basis_and_invalid_financial_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            allocate_shared_expense("2", [{"id": "a", "quantity": 1, "purchase_value": "0", "weight": "0"}], "weight")
        for args in [("2", 0, [], "3", "0"), ("-1", 2, [], "3", "0"), ("2", 2, [], "3", "100.01")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate_product(*args)

    def test_margin_target_basis_and_full_discount_do_not_invent_prices(self):
        margin = calculate_product("10", 1, [], "20", "0", target_profit_percent="25", target_basis="margin")
        markup = calculate_product("10", 1, [], "20", "0", target_profit_percent="25", target_basis="markup")
        self.assertEqual(margin["target_percent_unit_price"], Decimal("13.34"))
        self.assertEqual(markup["target_percent_unit_price"], Decimal("12.50"))
        fully_discounted = calculate_product("10", 1, [], "20", "100", target_profit_amount="5", target_profit_percent="25")
        self.assertEqual(fully_discounted["final_unit_price"], Decimal("0.00"))
        self.assertIsNone(fully_discounted["target_fixed_unit_price"])
        self.assertIsNone(fully_discounted["target_percent_unit_price"])
        self.assertIsNone(fully_discounted["break_even_unit_price"])

    def test_break_even_rounding_matches_the_discounted_unit_price_formula(self):
        result = calculate_product("0", 3, ["0.01"], "1", "0")
        self.assertEqual(result["break_even_unit_price"], Decimal("0.01"))

    def test_target_prices_round_up_until_the_actual_result_meets_target(self):
        result = calculate_product("0.01", 3, [], "0", "1", target_profit_amount="0.01")
        target_price = result["target_fixed_unit_price"]
        realized = calculate_product("0.01", 3, [], target_price, "1")
        self.assertGreaterEqual(realized["profit"], Decimal("0.01"))


if __name__ == "__main__":
    unittest.main()
