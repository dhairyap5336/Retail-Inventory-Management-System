import pandas as pd

def heuristic_inventory(data, budget):

    df = data.copy()

    df["Profit"] = df["Selling_Price"] - df["Cost_Price"]

    df = df.sort_values(by="Profit", ascending=False)

    total_cost = 0
    selected_products = []

    for _, row in df.iterrows():

        if total_cost + row["Cost_Price"] <= budget:

            selected_products.append(row["Product"])

            total_cost += row["Cost_Price"]

    return selected_products