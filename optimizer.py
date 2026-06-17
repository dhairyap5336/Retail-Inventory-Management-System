import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum


def optimize_inventory(data, budget, storage_limit):

    # Create model
    model = LpProblem("Retail_Inventory_Optimization", LpMaximize)

    # Products
    products = data["Product"]

    # Decision variables
    stock = LpVariable.dicts("stock", products, lowBound=5, cat="Integer")

    # -----------------------------
    # CONSTRAINT 1: MAX LIMIT PER PRODUCT
    # -----------------------------
    max_limit = 80

    for p in products:
        model += stock[p] <= max_limit

    # -----------------------------
    # CONSTRAINT 2: FORCE MULTIPLE PRODUCTS (KEY FIX 🔥)
    # -----------------------------
    binary = LpVariable.dicts("select", products, cat="Binary")

    for p in products:
        model += stock[p] <= max_limit * binary[p]

    # At least 5 products must be selected
    model += lpSum(binary[p] for p in products) >= 5

    # -----------------------------
    # OBJECTIVE FUNCTION (MAX PROFIT)
    # -----------------------------
    profit_per_unit = data["Selling_Price"] - data["Cost_Price"]

    model += (
        lpSum(
            stock[p] * profit_per_unit.iloc[i]
            for i, p in enumerate(products)
        )
        - 0.005 * lpSum(stock[p] for p in products)  # small penalty for balance
    )

    # -----------------------------
    # CONSTRAINT 3: BUDGET
    # -----------------------------
    model += lpSum(
        stock[p] * data["Cost_Price"].iloc[i]
        for i, p in enumerate(products)
    ) <= budget

    # -----------------------------
    # CONSTRAINT 4: STORAGE
    # -----------------------------
    model += lpSum(
        stock[p] * data["Storage_Space"].iloc[i]
        for i, p in enumerate(products)
    ) <= storage_limit

    # -----------------------------
    # CONSTRAINT 5: DEMAND LIMIT (RELAXED)
    # -----------------------------
    for i, p in enumerate(products):
        model += stock[p] <= 0.6 * data["Forecast_Demand"].iloc[i]

    # -----------------------------
    # SOLVE MODEL
    # -----------------------------
    model.solve()

    # -----------------------------
    # RESULTS
    # -----------------------------
    results = []

    for p in products:
        results.append(int(stock[p].value()))

    data["Optimal_Stock"] = results

    data["Expected_Profit"] = (
        data["Optimal_Stock"]
        * (data["Selling_Price"] - data["Cost_Price"])
    )

    return data