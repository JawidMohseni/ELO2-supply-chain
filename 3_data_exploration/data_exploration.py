"""
Supply Chain Data Exploration Script

This script performs comprehensive analysis of supply chain delays including:
- Data loading and validation
- Statistical analysis
- Visualizations (static and interactive)
- Risk identification
- Report generation
"""

import os
import warnings

# pylint: disable=import-error
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import seaborn as sns  # type: ignore

# pylint: enable=import-error

warnings.filterwarnings("ignore")

# Set display options for better output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 50)

# Set up plotting style
try:
    plt.style.use("seaborn-v0_8")
except OSError:
    try:
        plt.style.use("seaborn")
    except OSError:
        plt.style.use("default")
sns.set_palette("husl")

# Load the data - adjust path relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(
    script_dir, "..", "2_data_preparation", "orders_and_shipments_final_cleaned.csv"
)

# Check if file exists
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Data file not found at: {data_path}")

df = pd.read_csv(data_path)
print(f"Data loaded successfully from: {data_path}")

# Validate required columns exist
required_columns = [
    "Order Date",
    "Shipment Date",
    "Shipment Days - Scheduled",
    "Region",
    "Shipment Mode",
    "Product Department",
    "Product Category",
    "Customer Market",
    "Warehouse Country",
    "Customer Country",
    "Order Quantity",
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise KeyError(
        f"Missing required columns in dataset: {missing_columns}\n"
        f"Available columns: {list(df.columns)}"
    )

# Basic data exploration
print("=== DATA OVERVIEW ===")
print(f"Dataset shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== BASIC STATISTICS ===")
print(df.describe())

# Data preprocessing
# Convert date columns to datetime
print("\n=== DATA PREPROCESSING ===")
try:
    df["Order Date"] = pd.to_datetime(
        df["Order Date"], format="%m/%d/%Y", errors="coerce"
    )
    df["Shipment Date"] = pd.to_datetime(
        df["Shipment Date"], format="%m/%d/%Y", errors="coerce"
    )
    invalid_dates = df["Order Date"].isna().sum() + df["Shipment Date"].isna().sum()
    if invalid_dates > 0:
        print(
            f"Warning: {invalid_dates} rows have invalid dates that could not be parsed"
        )
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    # If format doesn't match, try inferring the format
    print(f"Warning: Date parsing with format failed: {e}")
    print("Attempting to parse dates without specific format...")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Shipment Date"] = pd.to_datetime(df["Shipment Date"], errors="coerce")

# Calculate actual shipment days (handle NaT values)
df["Shipment Days - Actual"] = (df["Shipment Date"] - df["Order Date"]).dt.days

# Validate that scheduled days is numeric
if not pd.api.types.is_numeric_dtype(df["Shipment Days - Scheduled"]):
    print("Warning: Converting 'Shipment Days - Scheduled' to numeric...")
    df["Shipment Days - Scheduled"] = pd.to_numeric(
        df["Shipment Days - Scheduled"], errors="coerce"
    )

# Calculate delay (positive = delayed, negative = early)
df["Delay Days"] = df["Shipment Days - Actual"] - df["Shipment Days - Scheduled"]

# Handle any NaN values that might have been introduced
missing_data_count = (
    df[["Order Date", "Shipment Date", "Delay Days"]].isnull().any(axis=1).sum()
)
print(f"\nRows with missing dates or delays: {missing_data_count}")

# Extract month and year for time analysis (only for valid dates)
df["Order Month"] = df["Order Date"].dt.month
df["Order Year"] = df["Order Date"].dt.year
df["Order Month-Year"] = df["Order Date"].dt.to_period("M")
# Handle any NaN values in month/year columns
df["Order Month"] = df["Order Month"].fillna(0).astype(int).replace(0, np.nan)
df["Order Year"] = df["Order Year"].fillna(0).astype(int).replace(0, np.nan)

print("\n=== DELAY STATISTICS ===")
# Use only valid delay values for statistics
valid_delays_stats = df["Delay Days"].dropna()
if len(valid_delays_stats) == 0:
    print("Warning: No valid delay data available!")
    delay_mean = delay_max = delay_min = delay_pct = 0
else:
    delay_mean = valid_delays_stats.mean()
    delay_max = valid_delays_stats.max()
    delay_min = valid_delays_stats.min()
    delay_pct = (valid_delays_stats > 0).mean() * 100

print(f"Average delay: {delay_mean:.2f} days")
print(f"Maximum delay: {delay_max:.2f} days")
print(f"Minimum delay: {delay_min:.2f} days")
print(f"Percentage of delayed shipments: {delay_pct:.2f}%")
print(f"Valid delay records: {df['Delay Days'].notna().sum()} out of {len(df)}")


# Create comprehensive visualizations
def create_supply_chain_visualizations(dataframe):  # pylint: disable=redefined-outer-name
    """
    Create comprehensive visualizations for global supply chain delay analysis
    """
    df = dataframe  # noqa: F841  # pylint: disable=redefined-outer-name
    plt.figure(figsize=(20, 16))

    # 1. Delay distribution
    plt.subplot(3, 3, 1)
    valid_delays_plot = df["Delay Days"].dropna()
    if len(valid_delays_plot) > 0:
        sns.histplot(data=df, x="Delay Days", bins=30, kde=True)
        plt.axvline(x=0, color="red", linestyle="--", label="On Time")
        delay_mean_val = valid_delays_plot.mean()
        plt.axvline(
            x=delay_mean_val,
            color="orange",
            linestyle="--",
            label=f"Mean: {delay_mean_val:.1f}",
        )
    plt.title("Distribution of Shipment Delays")
    plt.xlabel("Delay Days (Positive = Delayed)")
    plt.ylabel("Frequency")
    plt.legend()

    # 2. Delays by region
    plt.subplot(3, 3, 2)
    region_delays = (
        df.groupby("Region")["Delay Days"].mean().dropna().sort_values(ascending=False)
    )
    if len(region_delays) > 0:
        sns.barplot(x=region_delays.values, y=region_delays.index)
    plt.title("Average Delay by Region")
    plt.xlabel("Average Delay Days")

    # 3. Delays by shipment mode
    plt.subplot(3, 3, 3)
    mode_delays = (
        df.groupby("Shipment Mode")["Delay Days"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )
    if len(mode_delays) > 0:
        sns.barplot(x=mode_delays.values, y=mode_delays.index)
    plt.title("Average Delay by Shipment Mode")
    plt.xlabel("Average Delay Days")

    # 4. Delays by product department
    plt.subplot(3, 3, 4)
    dept_delays = (
        df.groupby("Product Department")["Delay Days"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )
    if len(dept_delays) > 0:
        sns.barplot(x=dept_delays.values, y=dept_delays.index)
    plt.title("Average Delay by Product Department")
    plt.xlabel("Average Delay Days")

    # 5. Monthly trend of delays
    plt.subplot(3, 3, 5)
    monthly_delays = df.groupby("Order Month-Year")["Delay Days"].mean().dropna()
    if len(monthly_delays) > 0:
        monthly_delays.plot(kind="line", marker="o")
    plt.title("Monthly Trend of Average Delays")
    plt.xlabel("Month-Year")
    plt.ylabel("Average Delay Days")
    plt.xticks(rotation=45)

    # 6. Delay by customer market
    plt.subplot(3, 3, 6)
    market_delays = (
        df.groupby("Customer Market")["Delay Days"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )
    if len(market_delays) > 0:
        sns.barplot(x=market_delays.values, y=market_delays.index)
    plt.title("Average Delay by Customer Market")
    plt.xlabel("Average Delay Days")

    # 7. Scheduled vs Actual shipment days
    plt.subplot(3, 3, 7)
    valid_data = df[["Shipment Days - Scheduled", "Shipment Days - Actual"]].dropna()
    if len(valid_data) > 0:
        plt.scatter(
            valid_data["Shipment Days - Scheduled"],
            valid_data["Shipment Days - Actual"],
            alpha=0.6,
        )
        max_val = valid_data["Shipment Days - Scheduled"].max()
        plt.plot([0, max_val], [0, max_val], "r--", label="Perfect Schedule")
        plt.legend()
    plt.xlabel("Scheduled Shipment Days")
    plt.ylabel("Actual Shipment Days")
    plt.title("Scheduled vs Actual Shipment Days")

    # 8. Delay patterns by warehouse country
    plt.subplot(3, 3, 8)
    warehouse_delays = (
        df.groupby("Warehouse Country")["Delay Days"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )
    if len(warehouse_delays) > 0:
        # Limit to top 20 for readability
        warehouse_delays = warehouse_delays.head(20)
        sns.barplot(x=warehouse_delays.values, y=warehouse_delays.index)
    plt.title("Average Delay by Warehouse Country")
    plt.xlabel("Average Delay Days")

    # 9. Order quantity vs delay
    plt.subplot(3, 3, 9)
    quantity_delays = df.groupby("Order Quantity")["Delay Days"].mean().dropna()
    if len(quantity_delays) > 0:
        # Limit to top 20 to avoid overcrowding
        quantity_delays = quantity_delays.head(20)
        sns.barplot(x=quantity_delays.index, y=quantity_delays.values)
        plt.title("Average Delay by Order Quantity (Top 20)")
        plt.xlabel("Order Quantity")
        plt.ylabel("Average Delay Days")
    else:
        plt.text(
            0.5,
            0.5,
            "No data available",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Average Delay by Order Quantity")

    plt.tight_layout()
    plt.show()


# Create the visualizations
try:
    create_supply_chain_visualizations(df)
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    print(f"\nWarning: Error creating visualizations: {e}")
    print("Continuing with other analyses...")


# Interactive visualizations with Plotly
def create_interactive_visualizations(dataframe):  # pylint: disable=redefined-outer-name
    """
    Create interactive visualizations using Plotly
    """
    df = dataframe  # noqa: F841  # pylint: disable=redefined-outer-name

    # 1. Global delay heatmap by region and shipment mode
    try:
        delay_heatmap_data = df.pivot_table(
            values="Delay Days", index="Region", columns="Shipment Mode", aggfunc="mean"
        ).fillna(0)

        if not delay_heatmap_data.empty:
            fig1 = px.imshow(
                delay_heatmap_data,
                title="Average Delay Days by Region and Shipment Mode",
                color_continuous_scale="RdBu_r",
                aspect="auto",
            )
            fig1.show()
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating heatmap: {e}")

    # 2. Time series of delays
    try:
        monthly_trend = (
            df.groupby("Order Month-Year")
            .agg({"Delay Days": "mean", "Order Quantity": "sum"})
            .reset_index()
        )
        if not monthly_trend.empty:
            monthly_trend["Order Month-Year"] = monthly_trend[
                "Order Month-Year"
            ].astype(str)
            monthly_trend = monthly_trend.dropna(subset=["Delay Days"])

            if not monthly_trend.empty:
                fig2 = px.line(
                    monthly_trend,
                    x="Order Month-Year",
                    y="Delay Days",
                    title="Monthly Trend of Average Delivery Delays",
                    markers=True,
                )
                fig2.show()
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating time series: {e}")

    # 3. Delay distribution by product category
    try:
        valid_categories = df["Product Category"].dropna()
        if len(valid_categories) > 0:
            top_categories = valid_categories.value_counts().head(10).index
            df_top_categories = df[
                df["Product Category"].isin(top_categories) & df["Delay Days"].notna()
            ]

            if not df_top_categories.empty:
                fig3 = px.box(
                    df_top_categories,
                    x="Product Category",
                    y="Delay Days",
                    title="Delay Distribution by Product Category (Top 10)",
                )
                fig3.update_xaxes(tickangle=45)
                fig3.show()
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating product category box plot: {e}")

    # 4. Regional performance comparison
    try:
        regional_stats = (
            df.groupby("Region")
            .agg({"Delay Days": ["mean", "std", "count"], "Order Quantity": "sum"})
            .round(2)
        )
        regional_stats.columns = [
            "Avg Delay",
            "Std Delay",
            "Order Count",
            "Total Quantity",
        ]
        regional_stats = regional_stats.dropna(subset=["Avg Delay"])
        regional_stats = regional_stats.sort_values("Avg Delay", ascending=False)

        if not regional_stats.empty:
            # Fill NaN in Std Delay with 0 for error bars
            regional_stats["Std Delay"] = regional_stats["Std Delay"].fillna(0)
            fig4 = px.bar(
                regional_stats.reset_index(),
                x="Region",
                y="Avg Delay",
                error_y="Std Delay",
                title="Regional Performance: Average Delay with Standard Deviation",
                color="Avg Delay",
                color_continuous_scale="RdYlBu_r",
            )
            fig4.show()
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating regional performance chart: {e}")


# Create interactive visualizations
try:
    create_interactive_visualizations(df)
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    print(f"\nWarning: Error creating interactive visualizations: {e}")
    print("Continuing with other analyses...")


# Advanced analytics
def perform_advanced_analytics(dataframe):  # pylint: disable=redefined-outer-name
    """
    Perform advanced analytics on the supply chain data
    """
    df = dataframe  # noqa: F841  # pylint: disable=redefined-outer-name
    print("\n=== ADVANCED ANALYTICS ===")

    # 1. Delay correlation analysis
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        # Filter out columns that are all NaN
        numeric_df = numeric_df.dropna(axis=1, how="all")

        if len(numeric_df.columns) > 1:
            correlation_matrix = numeric_df.corr()
            # Check if correlation matrix has valid data
            if not correlation_matrix.isna().all().all():
                plt.figure(figsize=(10, 8))
                sns.heatmap(
                    correlation_matrix, annot=True, cmap="coolwarm", center=0, fmt=".2f"
                )
                plt.title("Correlation Matrix of Numerical Variables")
                plt.tight_layout()
                plt.show()
            else:
                print("Correlation matrix contains only NaN values.")
        elif len(numeric_df.columns) == 1:
            print("Only one numerical column found. Cannot compute correlations.")
        else:
            print("No numerical columns found for correlation analysis")
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating correlation matrix: {e}")

    # 2. Risk analysis: identify high-risk routes
    print("\n=== HIGH-RISK SUPPLY CHAIN ROUTES ===")
    try:
        # Filter out rows with missing delay data
        valid_routes_df = df[
            df["Delay Days"].notna()
            & df["Warehouse Country"].notna()
            & df["Customer Country"].notna()
        ]

        if len(valid_routes_df) > 0:
            risk_routes = (
                valid_routes_df.groupby(["Warehouse Country", "Customer Country"])
                .agg({"Delay Days": ["mean", "count"], "Order Quantity": "sum"})
                .round(2)
            )

            risk_routes.columns = ["Avg Delay", "Shipment Count", "Total Quantity"]
            risk_routes = risk_routes.dropna(subset=["Avg Delay", "Shipment Count"])

            if len(risk_routes) > 0 and risk_routes["Avg Delay"].notna().any():
                high_risk_routes = risk_routes[
                    (risk_routes["Avg Delay"] > risk_routes["Avg Delay"].mean())
                    & (
                        risk_routes["Shipment Count"]
                        > risk_routes["Shipment Count"].quantile(0.5)
                    )
                ].sort_values("Avg Delay", ascending=False)

                print(f"Number of high-risk routes: {len(high_risk_routes)}")
                if len(high_risk_routes) > 0:
                    print(high_risk_routes.head(10))
                else:
                    print("No high-risk routes identified based on the criteria.")
            else:
                print("Insufficient data for risk route analysis.")
        else:
            print("No valid route data available for analysis.")
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error in risk route analysis: {e}")

    # 3. Seasonal analysis
    print("\n=== SEASONAL DELAY PATTERNS ===")
    try:
        valid_month_df = df[df["Order Month"].notna() & df["Delay Days"].notna()]
        if len(valid_month_df) > 0:
            monthly_delay_pattern = (
                valid_month_df.groupby("Order Month")["Delay Days"].mean().dropna()
            )
            if len(monthly_delay_pattern) > 0:
                plt.figure(figsize=(12, 6))
                monthly_delay_pattern.plot(kind="bar", color="skyblue")
                plt.title("Average Delay by Month (Seasonal Pattern)")
                plt.xlabel("Month")
                plt.ylabel("Average Delay Days")
                plt.xticks(rotation=0)
                plt.grid(axis="y", alpha=0.3)
                plt.show()
            else:
                print("No valid monthly delay data available for seasonal analysis.")
        else:
            print(
                "No data available for seasonal analysis (missing month or delay data)."
            )
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error in seasonal analysis: {e}")

    # 4. Product category risk analysis
    print("\n=== PRODUCT CATEGORY RISK ANALYSIS ===")
    try:
        valid_category_df = df[
            df["Delay Days"].notna() & df["Product Category"].notna()
        ]

        if len(valid_category_df) > 0:
            category_risk = (
                valid_category_df.groupby("Product Category")
                .agg({"Delay Days": ["mean", "std", "count"], "Order Quantity": "sum"})
                .round(2)
            )
            category_risk.columns = [
                "Avg Delay",
                "Std Delay",
                "Shipment Count",
                "Total Quantity",
            ]
            category_risk = category_risk.dropna(subset=["Avg Delay", "Shipment Count"])

            if len(category_risk) > 0:
                # Filter categories with sufficient data
                min_count = category_risk["Shipment Count"].quantile(0.5)
                if pd.notna(min_count) and min_count > 0:
                    high_risk_categories = category_risk[
                        category_risk["Shipment Count"] > min_count
                    ].nlargest(10, "Avg Delay")

                    if len(high_risk_categories) > 0:
                        print(high_risk_categories)
                    else:
                        print(
                            "No high-risk categories identified based on the criteria."
                        )
                else:
                    print("Insufficient data for category risk analysis.")
            else:
                print("No valid category data available for analysis.")
        else:
            print("No valid product category data available.")
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"Error in product category risk analysis: {e}")


# Perform advanced analytics
try:
    perform_advanced_analytics(df)
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    print(f"\nWarning: Error in advanced analytics: {e}")
    print("Continuing with summary...")


# Summary statistics and key insights
def generate_insights_summary(dataframe):  # pylint: disable=redefined-outer-name
    """
    Generate summary insights from the analysis
    """
    df = dataframe  # noqa: F841  # pylint: disable=redefined-outer-name
    print("\n" + "=" * 50)
    print("KEY INSIGHTS SUMMARY")
    print("=" * 50)

    # Overall performance
    valid_delays_summary = df["Delay Days"].dropna()
    if len(valid_delays_summary) > 0:
        on_time_rate = (valid_delays_summary <= 0).mean() * 100
        avg_delay = valid_delays_summary.mean()
    else:
        on_time_rate = 0
        avg_delay = 0

    print(" Overall Performance:")
    print(f"   • On-time delivery rate: {on_time_rate:.1f}%")
    print(f"   • Average delay: {avg_delay:.1f} days")
    print(f"   • Total shipments analyzed: {len(df):,}")

    # Worst performing regions
    region_delays = df.groupby("Region")["Delay Days"].mean().dropna()
    if len(region_delays) > 0:
        worst_regions = region_delays.nlargest(3)
        print("\n Highest Risk Regions:")
        for region, delay in worst_regions.items():
            print(f"   • {region}: {delay:.1f} days average delay")

        # Best performing regions
        best_regions = region_delays.nsmallest(3)
        print("\n Best Performing Regions:")
        for region, delay in best_regions.items():
            print(f"   • {region}: {delay:.1f} days average delay")

    # Shipment mode performance
    mode_delays = df.groupby("Shipment Mode")["Delay Days"].mean().dropna()
    if len(mode_delays) > 0:
        mode_performance = mode_delays.sort_values()
        print("\n Shipment Mode Performance:")
        for mode, delay in mode_performance.items():
            print(f"   • {mode}: {delay:.1f} days average delay")

    # High-risk products
    dept_delays = df.groupby("Product Department")["Delay Days"].mean().dropna()
    if len(dept_delays) > 0:
        high_risk_products = dept_delays.nlargest(3)
        print("\n High-Risk Product Departments:")
        for dept, delay in high_risk_products.items():
            print(f"   • {dept}: {delay:.1f} days average delay")

    # Seasonal insights
    monthly_delays = df.groupby("Order Month")["Delay Days"].mean().dropna()
    if len(monthly_delays) > 0:
        worst_month = monthly_delays.idxmax()
        best_month = monthly_delays.idxmin()
        print("\n Seasonal Patterns:")
        print(f"   • Worst month for delays: Month {worst_month}")
        print(f"   • Best month for deliveries: Month {best_month}")


# Generate insights summary
try:
    generate_insights_summary(df)
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    print(f"\nWarning: Error generating insights: {e}")


# Export key metrics for further analysis
def export_key_metrics(dataframe):  # pylint: disable=redefined-outer-name
    """
    Export key metrics and processed data for further analysis
    """
    df = dataframe  # noqa: F841  # pylint: disable=redefined-outer-name
    # Create summary dataframe
    valid_delays_export = df["Delay Days"].dropna()
    if len(valid_delays_export) > 0:
        summary_metrics = {
            "Total_Shipments": len(df),
            "On_Time_Rate": (valid_delays_export <= 0).mean(),
            "Avg_Delay_Days": valid_delays_export.mean(),
            "Max_Delay": valid_delays_export.max(),
            "Min_Delay": valid_delays_export.min(),
            "Delayed_Shipments_Pct": (valid_delays_export > 0).mean(),
            "Early_Shipments_Pct": (valid_delays_export < 0).mean(),
        }
    else:
        summary_metrics = {
            "Total_Shipments": len(df),
            "On_Time_Rate": 0.0,
            "Avg_Delay_Days": 0.0,
            "Max_Delay": 0.0,
            "Min_Delay": 0.0,
            "Delayed_Shipments_Pct": 0.0,
            "Early_Shipments_Pct": 0.0,
        }

    summary_df = pd.DataFrame([summary_metrics])
    export_output_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(export_output_dir, "supply_chain_summary_metrics.csv")
    processed_path = os.path.join(export_output_dir, "processed_supply_chain_data.csv")

    summary_df.to_csv(summary_path, index=False)

    # Export processed data with delays
    try:
        df.to_csv(processed_path, index=False)
        print("\n Data exported successfully:")
        print(f"   • {summary_path}")
        print(f"   • {processed_path}")
    except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
        print(f"\n Warning: Could not export processed data: {e}")
        # Still try to export summary
        try:
            summary_df.to_csv(summary_path, index=False)
            print(f"   • {summary_path} (summary only)")
        except (ValueError, KeyError, AttributeError, TypeError, OSError) as e2:  # pylint: disable=broad-exception-caught
            print(f"   Error: Could not export summary either: {e2}")


# Export metrics
try:
    export_key_metrics(df)
except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:  # pylint: disable=broad-exception-caught
    print(f"\nWarning: Error exporting metrics: {e}")

print("\n" + "=" * 50)
print("Analysis complete! Check the visualizations above.")
print("=" * 50)

# Print summary of outputs
print("\n=== OUTPUT SUMMARY ===")
output_dir = os.path.dirname(os.path.abspath(__file__))
summary_file = os.path.join(output_dir, "supply_chain_summary_metrics.csv")
processed_file = os.path.join(output_dir, "processed_supply_chain_data.csv")

if os.path.exists(summary_file):
    print(f"✓ Summary metrics saved: {summary_file}")
if os.path.exists(processed_file):
    print(f"✓ Processed data saved: {processed_file}")
print("\nScript execution completed successfully!")
