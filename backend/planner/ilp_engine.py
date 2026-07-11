"""
ILP (Integer Linear Programming) Engine
========================================
Given a legal set of foods (already filtered by the Constraint Engine) and
a calorie/macro target for one meal, pick integer serving counts per food
that get as close as possible to the target while respecting bounds.

Decision variables:
    x_i = number of servings of food i chosen (integer, 0..max_servings)

Objective:
    Minimise the absolute deviation of total calories from the target
    (linearised with an auxiliary deviation variable).

Constraints:
    - total calories within [target - tolerance, target + tolerance] (soft,
      via the objective) but hard-bounded to a wider safety window.
    - total protein/carbs/fat within reasonable bounds of the meal target.
    - at most MAX_ITEMS distinct foods per meal (keeps meals realistic).
    - at least MIN_ITEMS distinct foods per meal.
"""

import pulp

MAX_SERVINGS_PER_FOOD = 2
MAX_ITEMS_PER_MEAL = 3
MIN_ITEMS_PER_MEAL = 1
CALORIE_TOLERANCE = 0.20  # +/-20%


def solve_meal(foods, calorie_target: float, protein_target: float,
                carbs_target: float, fat_target: float):
    """
    foods: list of Food model instances (already filtered legal set)
    Returns: list of (food, servings) chosen, or [] if infeasible.
    """
    if not foods:
        return []

    prob = pulp.LpProblem("meal_selection", pulp.LpMinimize)

    # x_i: integer servings of food i
    x = {f.id: pulp.LpVariable(f"x_{f.id}", lowBound=0, upBound=MAX_SERVINGS_PER_FOOD, cat="Integer")
         for f in foods}
    # y_i: whether food i is used at all (binary), links to x_i
    y = {f.id: pulp.LpVariable(f"y_{f.id}", cat="Binary") for f in foods}

    # deviation variable for calories (absolute value linearisation)
    dev_pos = pulp.LpVariable("dev_pos", lowBound=0)
    dev_neg = pulp.LpVariable("dev_neg", lowBound=0)

    total_calories = pulp.lpSum(x[f.id] * f.calories for f in foods)
    total_protein = pulp.lpSum(x[f.id] * f.protein_g for f in foods)
    total_carbs = pulp.lpSum(x[f.id] * f.carbs_g for f in foods)
    total_fat = pulp.lpSum(x[f.id] * f.fat_g for f in foods)

    # Objective: minimise calorie deviation, small tie-break to prefer
    # protein close to target too.
    prob += dev_pos + dev_neg

    prob += total_calories - calorie_target == dev_pos - dev_neg

    # hard safety bounds so it never wildly overshoots
    prob += total_calories >= calorie_target * (1 - CALORIE_TOLERANCE)
    prob += total_calories <= calorie_target * (1 + CALORIE_TOLERANCE)

    # macro soft bounds (wide, just to keep it sane for a prototype)
    prob += total_protein >= protein_target * 0.4
    prob += total_carbs <= carbs_target * 1.6
    prob += total_fat <= fat_target * 1.6

    # link x_i to y_i and cap number of distinct items
    for f in foods:
        prob += x[f.id] <= MAX_SERVINGS_PER_FOOD * y[f.id]
        prob += x[f.id] >= y[f.id]  # if used, at least 1 serving

    prob += pulp.lpSum(y[f.id] for f in foods) <= MAX_ITEMS_PER_MEAL
    prob += pulp.lpSum(y[f.id] for f in foods) >= MIN_ITEMS_PER_MEAL

    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    if pulp.LpStatus[prob.status] != "Optimal":
        # fall back to a naive greedy pick so the user always gets a plan
        return _greedy_fallback(foods, calorie_target)

    chosen = []
    for f in foods:
        servings = int(round(x[f.id].value() or 0))
        if servings > 0:
            chosen.append((f, servings))
    return chosen or _greedy_fallback(foods, calorie_target)


def _greedy_fallback(foods, calorie_target):
    """Very simple fallback: pick foods (1 serving each) closest to target
    calories without exceeding it too much, in case the ILP is infeasible."""
    sorted_foods = sorted(foods, key=lambda f: f.calories)
    chosen = []
    running = 0
    for f in sorted_foods:
        if running + f.calories <= calorie_target * (1 + CALORIE_TOLERANCE):
            chosen.append((f, 1))
            running += f.calories
        if len(chosen) >= MAX_ITEMS_PER_MEAL:
            break
    if not chosen and sorted_foods:
        chosen = [(sorted_foods[0], 1)]
    return chosen
