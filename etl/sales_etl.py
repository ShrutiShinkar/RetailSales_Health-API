import pandas as pd
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_FOLDER / "data" / "Amazon Sale Report.csv"
OUTPUT_FOLDER = PROJECT_FOLDER / "output"

OUTPUT_FOLDER.mkdir(exist_ok=True)

# extract, Transform and Load (ETL) process
print("Reading raw sales dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Raw rows loaded: {len(df)}")

df = df[
    [
        "Order ID",
        "Date",
        "Status",
        "Fulfilment",
        "Category",
        "Qty",
        "Amount",
        "ship-state"
    ]
].copy()

# Convert date column
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")


# Create month column
df["Month"] = df["Date"].dt.to_period("M").astype(str)


# Convert quantity and amount to numeric values
df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0)

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)


# Clean text columns
df["Status"] = df["Status"].fillna("Unknown")
df["Fulfilment"] = df["Fulfilment"].fillna("Unknown")
df["Category"] = df["Category"].fillna("Unknown")
df["ship-state"] = df["ship-state"].fillna("Unknown")


# Create a business outcome classification
df["Sales_Outcome"] = df["Status"].apply(
    lambda x: "Revenue At Risk"
    if str(x).strip().lower() == "cancelled"
    else "Operational / Successful"
)

#Aggregate 
aggregated_sales = (
    df.groupby(
        [
            "Month",
            "ship-state",
            "Fulfilment",
            "Status",
            "Sales_Outcome"
        ],
        as_index=False
    )
    .agg(
        Total_Orders=("Order ID", "nunique"),
        Total_Units=("Qty", "sum"),
        Total_Revenue=("Amount", "sum")
    )
)


# Rename region column for a cleaner analytics output
aggregated_sales.rename(
    columns={
        "ship-state": "Region"
    },
    inplace=True
)


# Round revenue values
aggregated_sales["Total_Revenue"] = aggregated_sales[
    "Total_Revenue"
].round(2)

OUTPUT_FILE = OUTPUT_FOLDER / "sales_health_aggregated.csv"

aggregated_sales.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nETL PIPELINE COMPLETED SUCCESSFULLY")
print("-----------------------------------")
print(f"Aggregated rows created: {len(aggregated_sales)}")
print(f"Output saved to: {OUTPUT_FILE}")

print("\nSample Output:")
print(aggregated_sales.head(10))