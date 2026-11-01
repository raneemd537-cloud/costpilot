"""Deterministic product cost and pricing formulas.

Money inputs and outputs are Decimal values rounded to cents using HALF_UP.
Percentages are expressed as percentage points (for example, 20 means 20%).
"""

from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

CENT = Decimal("0.01")
HUNDRED = Decimal("100")


def money(value, field="amount", *, minimum=Decimal("0")):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number")
    if not number.is_finite() or number < minimum:
        raise ValueError(f"{field} must be at least {minimum}")
    return number.quantize(CENT, rounding=ROUND_HALF_UP)


def percent(value, field="percentage", *, maximum=Decimal("100")):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number")
    if not number.is_finite() or number < 0 or number > maximum:
        raise ValueError(f"{field} must be between 0 and {maximum}")
    return number


def _ratio_percent(numerator, denominator):
    if denominator == 0:
        return None
    return (numerator * HUNDRED / denominator).quantize(CENT, rounding=ROUND_HALF_UP)


def _discounted_unit_price(original_price, discount):
    return (original_price * (HUNDRED - discount) / HUNDRED).quantize(CENT, rounding=ROUND_HALF_UP)


def _revenue_at(original_price, discount, quantity):
    return _discounted_unit_price(original_price, discount) * quantity


def calculate_product(unit_cost, quantity, expenses, selling_price, discount_percent,
                      target_profit_amount=None, target_profit_percent=None,
                      target_basis="margin"):
    """Calculate full-quantity result and unit prices.

    Margin target uses profit / selling price. Markup target uses profit / cost.
    Discounted final price is original price * (1 - discount/100).
    """
    unit_cost = money(unit_cost, "unit cost")
    selling_price = money(selling_price, "selling price")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("quantity must be a positive whole number")
    discount = percent(discount_percent, "discount", maximum=HUNDRED)
    expense_total = sum((money(value, "expense") for value in expenses), Decimal("0.00"))
    purchase_total = (unit_cost * quantity).quantize(CENT, rounding=ROUND_HALF_UP)
    total_cost = purchase_total + expense_total
    final_unit_price = (selling_price * (HUNDRED - discount) / HUNDRED).quantize(CENT, rounding=ROUND_HALF_UP)
    revenue = final_unit_price * quantity
    profit = revenue - total_cost
    margin = _ratio_percent(profit, revenue)
    return_on_cost = _ratio_percent(profit, total_cost)
    break_even = None
    if discount < HUNDRED:
        break_even = (total_cost / quantity * HUNDRED / (HUNDRED - discount)).quantize(CENT, rounding=ROUND_HALF_UP)
        while _revenue_at(break_even, discount, quantity) < total_cost:
            break_even += CENT
        while break_even >= CENT and _revenue_at(break_even - CENT, discount, quantity) >= total_cost:
            break_even -= CENT

    fixed_target = None
    if target_profit_amount is not None:
        fixed_target = money(target_profit_amount, "target profit")
    fixed_price = None
    if fixed_target is not None and discount < HUNDRED:
        fixed_price = ((total_cost + fixed_target) / quantity * HUNDRED / (HUNDRED - discount)).quantize(CENT, rounding=ROUND_HALF_UP)
        def reaches_fixed(price):
            return _revenue_at(price, discount, quantity) - total_cost >= fixed_target
        while not reaches_fixed(fixed_price):
            fixed_price += CENT
        while fixed_price >= CENT and reaches_fixed(fixed_price - CENT):
            fixed_price -= CENT

    target_pct = None
    if target_profit_percent is not None:
        target_pct = percent(target_profit_percent, "target profit percentage", maximum=Decimal("10000"))
    if target_basis not in ("margin", "markup"):
        raise ValueError("target_basis must be margin or markup")
    target_price = None
    if target_pct is not None and discount < HUNDRED and total_cost > 0:
        fraction = target_pct / HUNDRED
        if target_basis == "margin":
            if fraction < 1:
                target_revenue = total_cost / (1 - fraction)
                target_price = (target_revenue / quantity * HUNDRED / (HUNDRED - discount)).quantize(CENT, rounding=ROUND_HALF_UP)
                def reaches_margin(price):
                    revenue_at_price = _revenue_at(price, discount, quantity)
                    return revenue_at_price - total_cost >= fraction * revenue_at_price
                while not reaches_margin(target_price):
                    target_price += CENT
                while target_price >= CENT and reaches_margin(target_price - CENT):
                    target_price -= CENT
        else:
            target_cost = total_cost * (1 + fraction)
            target_price = (target_cost / quantity * HUNDRED / (HUNDRED - discount)).quantize(CENT, rounding=ROUND_HALF_UP)
            def reaches_markup(price):
                return _revenue_at(price, discount, quantity) - total_cost >= fraction * total_cost
            while not reaches_markup(target_price):
                target_price += CENT
            while target_price >= CENT and reaches_markup(target_price - CENT):
                target_price -= CENT

    return {
        "purchase_total": purchase_total,
        "expense_total": expense_total,
        "total_cost": total_cost,
        "final_unit_price": final_unit_price,
        "revenue": revenue,
        "profit": profit.quantize(CENT, rounding=ROUND_HALF_UP),
        "margin_percent": margin,
        "return_on_cost_percent": return_on_cost,
        "break_even_unit_price": break_even,
        "target_fixed_unit_price": fixed_price,
        "target_percent_unit_price": target_price,
        "target_basis": target_basis,
        "status": "profit" if profit > 0 else "loss" if profit < 0 else "break_even",
    }


def allocate_shared_expense(amount, products, basis):
    """Allocate shared expense cents proportionally, conserving every cent.

    Ties use stable input order (largest fractional remainder method).
    """
    amount = money(amount, "shared expense")
    if basis not in ("quantity", "purchase_value", "weight"):
        raise ValueError("unsupported allocation basis")
    weights = []
    for product in products:
        if basis == "quantity":
            try:
                weight = Decimal(str(product.get("quantity", 0)))
            except InvalidOperation:
                raise ValueError("quantity must be a positive whole number")
            if not weight.is_finite() or weight <= 0 or weight != weight.to_integral_value():
                raise ValueError("quantity must be a positive whole number")
        elif basis == "purchase_value":
            weight = money(product.get("purchase_value", 0), "purchase value")
        else:
            try:
                weight = Decimal(str(product.get("weight", 0)))
            except InvalidOperation:
                raise ValueError("weight must be a valid number")
            if not weight.is_finite() or weight < 0:
                raise ValueError("weight must be nonnegative")
        if weight < 0:
            raise ValueError("allocation weights must be nonnegative")
        weights.append(weight)
    total_weight = sum(weights, Decimal("0"))
    if not products or total_weight <= 0:
        raise ValueError("allocation basis requires positive data")
    cents = int((amount / CENT).to_integral_value(rounding=ROUND_DOWN))
    quotas = [Decimal(cents) * weight / total_weight for weight in weights]
    assigned = [int(q.to_integral_value(rounding=ROUND_DOWN)) for q in quotas]
    remainder = cents - sum(assigned)
    order = sorted(range(len(quotas)), key=lambda i: (quotas[i] - assigned[i], -i), reverse=True)
    for i in order[:remainder]:
        assigned[i] += 1
    return {product["id"]: (Decimal(value) * CENT).quantize(CENT) for product, value in zip(products, assigned)}
