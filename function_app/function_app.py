import azure.functions as func
import logging
import json
import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import StringIO

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# COMMON FUNCTION: LOAD DATA AND CALCULATE KPIs

def calculate_sales_kpis():

    logging.info("Starting Retail Sales KPI calculation.")

    # Get Azure Storage connection string
    connection_string = os.environ["AzureWebJobsStorage"]

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    # Access container
    container_client = blob_service_client.get_container_client(
        "sales-data"
    )

    # Access aggregated ETL output
    blob_client = container_client.get_blob_client(
        "sales_health_aggregated.csv"
    )

    # Download CSV data
    downloaded_blob = blob_client.download_blob()

    csv_data = downloaded_blob.content_as_text()

    # Load data into Pandas
    df = pd.read_csv(StringIO(csv_data))

    logging.info(
        "Successfully loaded aggregated sales data from Azure Blob Storage."
    )

    # KPI CALCULATIONS

    total_revenue = float(df["Total_Revenue"].sum())

    total_units = int(df["Total_Units"].sum())

    total_orders = int(df["Total_Orders"].sum())


    # Top revenue region
    region_sales = (
        df.groupby("Region")["Total_Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_region = region_sales.index[0]

    top_region_revenue = float(
        region_sales.iloc[0]
    )


    # Revenue at risk
    cancelled_data = df[
        df["Sales_Outcome"] == "Revenue At Risk"
    ]

    revenue_at_risk = float(
        cancelled_data["Total_Revenue"].sum()
    )

    cancelled_orders = int(
        cancelled_data["Total_Orders"].sum()
    )


    # Cancellation rate
    cancellation_rate = round(
        (cancelled_orders / total_orders) * 100,
        2
    ) if total_orders > 0 else 0


    # SALES HEALTH SCORE

    sales_health_score = round(
        max(0, 100 - (cancellation_rate * 2)),
        2
    )


    if sales_health_score >= 85:
        health_status = "Healthy"

    elif sales_health_score >= 70:
        health_status = "Needs Attention"

    else:
        health_status = "At Risk"


    # PRIORITY REGION

    if not cancelled_data.empty:

        risk_by_region = (
            cancelled_data
            .groupby("Region")["Total_Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        priority_region = risk_by_region.index[0]

    else:

        priority_region = (
            "No significant risk detected"
        )


    # KPI RESPONSE

    response = {

        "project": (
            "Retail Sales Health & Revenue Recovery API"
        ),

        "sales_snapshot": {

            "total_revenue": round(
                total_revenue,
                2
            ),

            "total_orders": total_orders,

            "total_units": total_units
        },


        "performance": {

            "top_region": top_region,

            "top_region_revenue": round(
                top_region_revenue,
                2
            )
        },


        "revenue_risk": {

            "revenue_at_risk": round(
                revenue_at_risk,
                2
            ),

            "cancelled_orders": cancelled_orders,

            "cancellation_rate_percent":
                cancellation_rate
        },


        "sales_health": {

            "score": sales_health_score,

            "status": health_status,

            "priority_region":
                priority_region
        }
    }


    logging.info(
        "Sales Health KPI calculation completed successfully."
    )

    return response


# HTTP TRIGGER

@app.route(route="sales-health")
def sales_health(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(
        "Retail Sales Health API request received."
    )

    try:

        response = calculate_sales_kpis()

        return func.HttpResponse(

            json.dumps(
                response,
                indent=4
            ),

            mimetype="application/json",

            status_code=200
        )

    except Exception as e:

        logging.error(
            f"Error processing sales data: {str(e)}"
        )

        return func.HttpResponse(

            json.dumps({
                "error": str(e)
            }),

            mimetype="application/json",

            status_code=500
        )


# TIMER TRIGGER
# RUNS AUTOMATICALLY EVERY HOUR

@app.schedule(
    schedule="0 * * * * *",
    arg_name="timer",
    use_monitor=True
)
def scheduled_sales_kpi(timer: func.TimerRequest) -> None:

    logging.info(
        "Scheduled Sales KPI execution started."
    )

    try:

        response = calculate_sales_kpis()

        logging.info(
            "Scheduled Sales KPI execution completed."
        )

        logging.info(
            json.dumps(
                response,
                indent=4
            )
        )

    except Exception as e:

        logging.error(
            f"Scheduled execution failed: {str(e)}"
        )