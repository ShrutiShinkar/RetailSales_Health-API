# Retail Sales Health & Revenue Recovery API

A cloud-based retail sales analytics project that processes sales data and provides key business insights through Azure Functions.

## Features

- Python-based ETL processing using Pandas
- Processed data stored in Azure Blob Storage
- HTTP API for sales health and revenue insights
- Timer-triggered function for scheduled KPI monitoring
- Application monitoring using Azure Application Insights

## Tech Stack

- Python
- Pandas
- Azure Functions
- Azure Blob Storage
- Azure Application Insights
- Azure CLI
- Visual Studio Code

## Project Workflow

```text
Amazon Sales Dataset
        ↓
Python ETL
        ↓
Processed Sales Data
        ↓
Azure Blob Storage
        ↓
Azure Functions
   ↙              ↘
Sales Health API   Scheduled KPI Monitoring

## API Endpoint

Sales Health API:

https://retailsaleshealthapi8216.azurewebsites.net/api/sales-health

The API provides insights such as:

Total revenue, orders, and units
Top-performing region
Revenue at risk
Cancelled orders and cancellation rate
Sales health score and status

## Azure Functions
sales_health — HTTP-triggered API for sales insights
scheduled_sales_kpi — Timer-triggered KPI monitoring

## Project Structure
data/          # Raw dataset
etl/           # ETL script
function_app/  # Azure Function application
output/        # Processed dataset